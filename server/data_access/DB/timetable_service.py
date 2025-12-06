import os
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional

from server.models.train import Train
from server.models.station import Station


class TimetableService:
    BASE_URL = "https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1"

    def __init__(self):
        self.troy_client_id = os.environ.get("TROY_CLIENT_ID")
        self.troy_api_key = os.environ.get("TROY_API_KEY")
        self.lars_client_id = os.environ.get("LARS_CLIENT_ID")
        self.lars_api_key = os.environ.get("LARS_API_KEY")

        if not self.troy_client_id or not self.troy_api_key:
            print(
                "Warning: TROY_CLIENT_ID or TROY_API_KEY not set. TimetableService will not work."
            )

    def _make_request(self, endpoint: str) -> Optional[str]:
        result = self._execute_request(endpoint, self.troy_client_id, self.troy_api_key)
        if result:
            return result

        if self.lars_client_id and self.lars_api_key:
            print(
                f"⚠️ Primary API key failed for {endpoint}. Switching to fallback (Lars)..."
            )
            return self._execute_request(
                endpoint, self.lars_client_id, self.lars_api_key
            )

        return None

    def _execute_request(
        self, endpoint: str, client_id: str, api_key: str
    ) -> Optional[str]:
        if not client_id or not api_key:
            return None

        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "DB-Client-ID": client_id,
            "DB-Api-Key": api_key,
            "Accept": "application/xml",
        }

        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            print(f"HTTP Error fetching {url}: {e.code} {e.reason}")
            return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_timetable(self, eva_no: str, date: datetime) -> List[Dict]:
        date_str = date.strftime("%y%m%d")
        hour_str = date.strftime("%H")
        endpoint = f"/plan/{eva_no}/{date_str}/{hour_str}"

        xml_data = self._make_request(endpoint)
        if not xml_data:
            return []

        return self._parse_timetable_xml(xml_data)

    def get_realtime_changes(self, eva_no: str) -> List[Dict]:
        endpoint = f"/fchg/{eva_no}"

        xml_data = self._make_request(endpoint)
        if not xml_data:
            return []

        return self._parse_timetable_xml(xml_data)

    def get_station_board(self, eva_no: str, date: datetime) -> List[Dict]:
        # Fetch plan and changes
        plan_stops = self.get_timetable(eva_no, date)
        changes_stops = self.get_realtime_changes(eva_no)

        # Merge changes by ID
        changes_map = {s["id"]: s for s in changes_stops}

        merged_board = []
        for stop in plan_stops:
            stop_id = stop["id"]

            # Only care about departures for station board
            if not stop["departure"]:
                continue

            departure = stop["departure"]
            change = changes_map.get(stop_id)
            real_time_info = {}

            if change and change.get("departure"):
                ch_dp = change["departure"]

                # Check for delay (ct = changed time)
                if ch_dp.get("ct"):
                    real_time_info["time"] = ch_dp.get("ct")
                    try:
                        planned = datetime.strptime(departure["time"], "%y%m%d%H%M")
                        actual = datetime.strptime(ch_dp.get("ct"), "%y%m%d%H%M")
                        delay_min = int((actual - planned).total_seconds() / 60)
                        real_time_info["delay"] = delay_min
                    except:
                        pass

                # Check for platform change
                if ch_dp.get("cp"):
                    real_time_info["platform"] = ch_dp.get("cp")

                # Check for messages
                if ch_dp.get("delay_msg"):
                    real_time_info["messages"] = ch_dp.get("delay_msg")

            board_entry = {
                "id": stop_id,
                "train": stop["trip_label"] or f"{departure['line']}",
                "direction": stop["departure"]["path"].split("|")[-1]
                if stop["departure"]["path"]
                else "Unknown",
                "time": departure["time"],
                "platform": departure["platform"],
                "real_time": real_time_info,
            }
            merged_board.append(board_entry)

        # Sort by actual time (or planned if no actual)
        merged_board.sort(key=lambda x: x["real_time"].get("time", x["time"]))

        return merged_board

    def _parse_timetable_xml(self, xml_data: str) -> List[Dict]:
        try:
            root = ET.fromstring(xml_data)
            stops = []

            for s in root.findall("s"):
                stop_info = {
                    "id": s.get("id"),
                    "eva": s.get("eva"),
                    "arrival": None,
                    "departure": None,
                    "trip_label": None,
                }

                # Parse arrival
                ar = s.find("ar")
                if ar is not None:
                    stop_info["arrival"] = {
                        "line": ar.get("l"),
                        "time": ar.get("pt"),
                        "ct": ar.get("ct"),
                        "platform": ar.get("pp"),
                        "cp": ar.get("cp"),
                        "path": ar.get("ppth"),
                        "delay_msg": ar.find("m").get("t")
                        if ar.find("m") is not None
                        else None,
                    }
                    if ar.get("l"):
                        stop_info["trip_label"] = ar.get("l")

                # Parse departure
                dp = s.find("dp")
                if dp is not None:
                    stop_info["departure"] = {
                        "line": dp.get("l"),
                        "time": dp.get("pt"),
                        "ct": dp.get("ct"),
                        "platform": dp.get("pp"),
                        "cp": dp.get("cp"),
                        "path": dp.get("ppth"),
                        "delay_msg": dp.find("m").get("t")
                        if dp.find("m") is not None
                        else None,
                    }
                    if dp.get("l") and not stop_info["trip_label"]:
                        stop_info["trip_label"] = dp.get("l")

                # Trip label from 'tl'
                tl = s.find("tl")
                if tl is not None:
                    cat = tl.get("c")
                    num = tl.get("n")
                    if cat and num:
                        stop_info["trip_label"] = f"{cat} {num}"

                stops.append(stop_info)

            return stops

        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
            return []

    def get_trains_for_station(
        self,
        station: Station,
        date: datetime,
        include_arrivals: bool = True,
        include_departures: bool = True,
    ) -> List[Train]:
        """
        Get all trains at a station as Train model objects.

        Args:
            station: The station to query
            date: The date/time to query for
            include_arrivals: Include arriving trains
            include_departures: Include departing trains

        Returns:
            List of Train objects with timing and route information
        """
        # Get raw timetable data
        plan_stops = self.get_timetable(str(station.eva), date)
        changes_stops = self.get_realtime_changes(str(station.eva))

        # Create a map of changes for quick lookup
        changes_map = {s["id"]: s for s in changes_stops}

        trains = []

        for stop in plan_stops:
            stop_id = stop["id"]
            trip_label = stop.get("trip_label", "Unknown")
            change = changes_map.get(stop_id)

            # Extract train category from trip label (e.g., "ICE" from "ICE 920")
            train_category = None
            if trip_label:
                parts = trip_label.split()
                if parts:
                    train_category = parts[0]

            # Process departures
            if include_departures and stop.get("departure"):
                dep = stop["departure"]
                train = self._create_train_from_departure(
                    stop_id=stop_id,
                    trip_label=trip_label,
                    train_category=train_category,
                    departure=dep,
                    station=station,
                    change=change,
                )
                if train:
                    trains.append(train)

            # Process arrivals
            if include_arrivals and stop.get("arrival") and not stop.get("departure"):
                # Only add pure arrivals (trains terminating here)
                arr = stop["arrival"]
                train = self._create_train_from_arrival(
                    stop_id=stop_id,
                    trip_label=trip_label,
                    train_category=train_category,
                    arrival=arr,
                    station=station,
                    change=change,
                )
                if train:
                    trains.append(train)

        # Sort by departure time
        trains.sort(key=lambda t: t.departureTime or t.arrivalTime or datetime.max)

        return trains

    def _create_train_from_departure(
        self,
        stop_id: str,
        trip_label: str,
        train_category: Optional[str],
        departure: Dict,
        station: Station,
        change: Optional[Dict],
    ) -> Optional[Train]:
        """Create a Train object from departure data."""
        try:
            # Parse departure time
            dep_time_str = departure.get("time")
            if not dep_time_str:
                return None

            dep_time = datetime.strptime(dep_time_str, "%y%m%d%H%M")

            # Check for real-time changes
            actual_dep_time = None
            delay_minutes = 0

            if change and change.get("departure"):
                ch_dep = change["departure"]
                if ch_dep.get("ct"):
                    try:
                        actual_dep_time = datetime.strptime(ch_dep["ct"], "%y%m%d%H%M")
                        delay_minutes = int(
                            (actual_dep_time - dep_time).total_seconds() / 60
                        )
                    except:
                        pass

            # Parse the path (stations after this stop)
            path_stations = []
            path_str = departure.get("path", "")
            if path_str:
                for station_name in path_str.split("|"):
                    # We don't have EVA numbers for path stations, use 0 as placeholder
                    path_stations.append(Station(name=station_name.strip(), eva=0))

            # Determine end location (last station in path)
            end_location = path_stations[-1] if path_stations else station

            # Parse platform
            platform = None
            platform_str = departure.get("platform")
            if platform_str:
                # Platform can be like "1a", extract just the number
                try:
                    platform = int("".join(filter(str.isdigit, platform_str)) or 0)
                except:
                    platform = None

            return Train(
                trainNumber=trip_label or "Unknown",
                trainId=stop_id,
                trainCategory=train_category,
                startLocation=station,
                endLocation=end_location,
                departureTime=dep_time,
                arrivalTime=None,  # We don't know arrival time at destination from this data
                actualDepartureTime=actual_dep_time,
                actualArrivalTime=None,
                path=[station] + path_stations,
                platform=platform,
                wagons=[],
                delayMinutes=delay_minutes,
            )
        except Exception as e:
            print(f"Error creating train from departure: {e}")
            return None

    def _create_train_from_arrival(
        self,
        stop_id: str,
        trip_label: str,
        train_category: Optional[str],
        arrival: Dict,
        station: Station,
        change: Optional[Dict],
    ) -> Optional[Train]:
        """Create a Train object from arrival data (for terminating trains)."""
        try:
            # Parse arrival time
            arr_time_str = arrival.get("time")
            if not arr_time_str:
                return None

            arr_time = datetime.strptime(arr_time_str, "%y%m%d%H%M")

            # Check for real-time changes
            actual_arr_time = None
            delay_minutes = 0

            if change and change.get("arrival"):
                ch_arr = change["arrival"]
                if ch_arr.get("ct"):
                    try:
                        actual_arr_time = datetime.strptime(ch_arr["ct"], "%y%m%d%H%M")
                        delay_minutes = int(
                            (actual_arr_time - arr_time).total_seconds() / 60
                        )
                    except:
                        pass

            # Parse the path (stations before this stop - where the train came from)
            path_stations = []
            path_str = arrival.get("path", "")
            if path_str:
                for station_name in path_str.split("|"):
                    path_stations.append(Station(name=station_name.strip(), eva=0))

            # Start location is first station in the arrival path
            start_location = path_stations[0] if path_stations else station

            # Parse platform
            platform = None
            platform_str = arrival.get("platform")
            if platform_str:
                try:
                    platform = int("".join(filter(str.isdigit, platform_str)) or 0)
                except:
                    platform = None

            return Train(
                trainNumber=trip_label or "Unknown",
                trainId=stop_id,
                trainCategory=train_category,
                startLocation=start_location,
                endLocation=station,
                departureTime=None,
                arrivalTime=arr_time,
                actualDepartureTime=None,
                actualArrivalTime=actual_arr_time,
                path=path_stations + [station],
                platform=platform,
                wagons=[],
                delayMinutes=delay_minutes,
            )
        except Exception as e:
            print(f"Error creating train from arrival: {e}")
            return None
