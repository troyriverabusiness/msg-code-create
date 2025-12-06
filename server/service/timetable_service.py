import os
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional

class TimetableService:
    BASE_URL = "https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1"

    def __init__(self):
        # Primary Keys (Troy)
        self.troy_client_id = os.environ.get("TROY_API_CLIENT")
        self.troy_api_key = os.environ.get("TROY_API_KEY")
        
        # Fallback Keys (Lars)
        self.lars_client_id = os.environ.get("LARS_API_CLIENT")
        self.lars_api_key = os.environ.get("LARS_API_KEY")
        
        if not self.troy_client_id or not self.troy_api_key:
            print("Warning: TROY_API_CLIENT or TROY_API_KEY not set. TimetableService will not work.")

    def _make_request(self, endpoint: str) -> Optional[str]:
        # Try with Troy's keys first
        result = self._execute_request(endpoint, self.troy_client_id, self.troy_api_key)
        if result:
            return result
            
        # If failed, try with Lars's keys
        if self.lars_client_id and self.lars_api_key:
            print(f"⚠️ Primary API key failed for {endpoint}. Switching to fallback (Lars)...")
            return self._execute_request(endpoint, self.lars_client_id, self.lars_api_key)
            
        return None

    def _execute_request(self, endpoint: str, client_id: str, api_key: str) -> Optional[str]:
        if not client_id or not api_key:
            return None

        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "DB-Client-ID": client_id,
            "DB-Api-Key": api_key,
            "Accept": "application/xml"
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
        """
        Fetches the scheduled timetable for a given station (EVA) and hour.
        """
        date_str = date.strftime("%y%m%d")
        hour_str = date.strftime("%H")
        endpoint = f"/plan/{eva_no}/{date_str}/{hour_str}"
        
        xml_data = self._make_request(endpoint)
        if not xml_data:
            return []

        return self._parse_timetable_xml(xml_data)

    def get_realtime_changes(self, eva_no: str) -> List[Dict]:
        """
        Fetches real-time changes (fchg) for a given station (EVA).
        """
        endpoint = f"/fchg/{eva_no}"
        
        xml_data = self._make_request(endpoint)
        if not xml_data:
            return []

        return self._parse_timetable_xml(xml_data)

    def get_station_board(self, eva_no: str, date: datetime) -> List[Dict]:
        """
        Returns a merged station board (Plan + Realtime Changes).
        """
        # 1. Fetch Plan
        plan_stops = self.get_timetable(eva_no, date)
        
        # 2. Fetch Changes
        changes_stops = self.get_realtime_changes(eva_no)
        
        # 3. Merge
        # Map changes by ID for fast lookup
        changes_map = {s["id"]: s for s in changes_stops}
        
        merged_board = []
        for stop in plan_stops:
            stop_id = stop["id"]
            
            # Only care about departures for a station board
            if not stop["departure"]:
                continue
                
            departure = stop["departure"]
            
            # Check for changes
            change = changes_map.get(stop_id)
            real_time_info = {}
            
            if change and change.get("departure"):
                ch_dp = change["departure"]
                
                # Check for delay (ct = changed time)
                if ch_dp.get("ct"):
                    real_time_info["time"] = ch_dp.get("ct")
                    # Calculate delay in minutes if possible
                    try:
                        planned = datetime.strptime(departure["time"], "%y%m%d%H%M")
                        actual = datetime.strptime(ch_dp.get("ct"), "%y%m%d%H%M")
                        delay_min = int((actual - planned).total_seconds() / 60)
                        real_time_info["delay"] = delay_min
                    except:
                        pass
                
                # Check for platform change (cp = changed platform)
                if ch_dp.get("cp"):
                    real_time_info["platform"] = ch_dp.get("cp")
                    
                # Check for messages
                if ch_dp.get("delay_msg"):
                     real_time_info["messages"] = ch_dp.get("delay_msg")

            # Construct final object
            board_entry = {
                "id": stop_id,
                "train": stop["trip_label"] or f"{departure['line']}",
                "direction": stop["departure"]["path"].split("|")[-1] if stop["departure"]["path"] else "Unknown",
                "time": departure["time"], # Planned Time
                "platform": departure["platform"], # Planned Platform
                "real_time": real_time_info # Contains 'time', 'delay', 'platform' if changed
            }
            merged_board.append(board_entry)
            
        # Sort by actual time (or planned if no actual)
        merged_board.sort(key=lambda x: x["real_time"].get("time", x["time"]))
        
        return merged_board

    def _parse_timetable_xml(self, xml_data: str) -> List[Dict]:
        """
        Parses the Timetables API XML format.
        """
        try:
            root = ET.fromstring(xml_data)
            stops = []
            
            # Iterate over 's' (stop/journey) elements
            for s in root.findall("s"):
                stop_info = {
                    "id": s.get("id"),
                    "eva": s.get("eva"),
                    "arrival": None,
                    "departure": None,
                    "trip_label": None 
                }
                
                # Parse Arrival 'ar'
                ar = s.find("ar")
                if ar is not None:
                    stop_info["arrival"] = {
                        "line": ar.get("l"), 
                        "time": ar.get("pt"), # Planned time
                        "ct": ar.get("ct"),   # Changed time
                        "platform": ar.get("pp"), # Planned platform
                        "cp": ar.get("cp"),   # Changed platform
                        "path": ar.get("ppth"), 
                        "delay_msg": ar.find("m").get("t") if ar.find("m") is not None else None 
                    }
                    if ar.get("l"):
                         stop_info["trip_label"] = ar.get("l")

                # Parse Departure 'dp'
                dp = s.find("dp")
                if dp is not None:
                    stop_info["departure"] = {
                        "line": dp.get("l"),
                        "time": dp.get("pt"),
                        "ct": dp.get("ct"),
                        "platform": dp.get("pp"),
                        "cp": dp.get("cp"),
                        "path": dp.get("ppth"),
                        "delay_msg": dp.find("m").get("t") if dp.find("m") is not None else None
                    }
                    if dp.get("l") and not stop_info["trip_label"]:
                         stop_info["trip_label"] = dp.get("l")
                
                # Trip Label from 'tl'
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
