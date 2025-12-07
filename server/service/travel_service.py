import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..models import RouteOption, PlatformInfo, StationInfo, Leg, Train, Station, Stop, Journey

DB_PATH = Path(__file__).parent.parent / "data" / "travel.db"

from .simulation import SimulationService

class TravelService:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.simulation = SimulationService()

    def get_all_station_ids(self, name: str) -> List[str]:
        # Normalize name for better matching
        # 1. Try exact/like match first
        # 2. Try swapping Hbf <-> Hauptbahnhof
        
        search_terms = [name]
        if "Hbf" in name:
            search_terms.append(name.replace("Hbf", "Hauptbahnhof"))
        elif "Hauptbahnhof" in name:
            search_terms.append(name.replace("Hauptbahnhof", "Hbf"))
            
        row = None
        for term in search_terms:
            # Try exact/contiguous match first
            cursor = self.conn.execute(
                "SELECT stop_id, parent_station, stop_name FROM stations WHERE stop_name LIKE ? LIMIT 1", 
                (f"%{term}%",)
            )
            row = cursor.fetchone()
            if row:
                break
                
            # If term contains space, try replacing with wildcard % to handle "Frankfurt (Main) Hbf"
            if " " in term:
                wildcard_term = term.replace(" ", "%")
                cursor = self.conn.execute(
                    "SELECT stop_id, parent_station, stop_name FROM stations WHERE stop_name LIKE ? LIMIT 1", 
                    (f"%{wildcard_term}%",)
                )
                row = cursor.fetchone()
                if row:
                    break
                
        if not row:
            # Fallback: Try fuzzy search without "Hbf" part if it failed? 
            # Risk of matching wrong station.
            return []
            
        primary_id = row['stop_id']
        parent_id = row['parent_station'] or primary_id
        
        # 2. Find all siblings/children (stops with same parent or this stop as parent)
        # Case A: We found a child. Parent is parent_id.
        # Case B: We found the parent. Parent is primary_id.
        
        # Get all stops that share this parent (including the parent itself if possible, though usually parent isn't in stop_times)
        # Or stops where parent_station = parent_id
        
        query = """
            SELECT stop_id FROM stations 
            WHERE stop_id = ? 
            OR parent_station = ?
            OR stop_id = ?
        """
        cursor = self.conn.execute(query, (parent_id, parent_id, primary_id))
        return [r['stop_id'] for r in cursor]

    def get_historical_delay(self, train_number: str) -> Optional[float]:
        return self.simulation.get_historical_delay(train_number)

    def search_stations(self, query: str) -> List[str]:
        if not query or len(query) < 2:
            return []
            
        # Search for stations matching the query
        # Prioritize "Hauptbahnhof" or "Hbf" to ensure major stations come first
        cursor = self.conn.execute(
            """
            SELECT DISTINCT stop_name FROM stations 
            WHERE stop_name LIKE ? 
            ORDER BY 
                CASE 
                    WHEN stop_name LIKE '%Hauptbahnhof%' THEN 1 
                    WHEN stop_name LIKE '%Hbf%' THEN 1 
                    ELSE 2 
                END,
                stop_name 
            LIMIT 10
            """, 
            (f"%{query}%",)
        )
        return [r['stop_name'] for r in cursor]

    def find_routes(self, start_name: str, end_name: str, time_str: str = None, via: List[str] = None, min_transfer_time: int = 0) -> List[Journey]:
        if via and len(via) > 0:
            return self._find_routes_with_via(start_name, end_name, via[0], time_str, min_transfer_time)
            
        # Direct routes - Delegate to find_segment to avoid duplication
        # find_segment handles SQL, path population, and deduplication
        legs = self.find_segment(start_name, end_name, time_str)
        
        journeys = []
        for leg in legs:
            # Calculate duration
            try:
                start_dt = datetime.strptime(leg.departureTime, "%H:%M:%S")
                end_dt = datetime.strptime(leg.arrivalTime, "%H:%M:%S")
                if end_dt < start_dt:
                    end_dt += timedelta(days=1)
                duration_min = int((end_dt - start_dt).total_seconds() / 60)
            except:
                duration_min = 0

            journeys.append(Journey(
                id=leg.train.trainNumber, # Use train number as ID
                startStation=leg.origin,
                endStation=leg.destination,
                legs=[leg],
                transfers=0,
                totalTime=duration_min,
                description=f"Direct connection with {leg.train.name}",
                price=None
            ))
            
        return journeys

    def _find_routes_with_via(self, start: str, end: str, via: str, time: str, min_transfer: int) -> List[Journey]:
        # 1. Find Leg 1: Start -> Via
        leg1_journeys = self.find_routes(start, via, time)

        if not leg1_journeys:
            return []
            
        combined_journeys = []
        
        # Limit to top 3 to avoid explosion
        for j1 in leg1_journeys[:3]:
            leg1 = j1.legs[0] # Assuming single leg for now
            arrival_time = leg1.arrivalTime
            
            # Calculate min departure for Leg 2
            # Simple string parsing HH:MM
            try:
                h, m = map(int, arrival_time.split(':')[:2])
                total_min = h * 60 + m + min_transfer
                new_h = (total_min // 60) % 24
                new_m = total_min % 60
                dep_time_leg2 = f"{new_h:02d}:{new_m:02d}"
            except:
                continue
                
            # 2. Find Leg 2: Via -> End
            leg2_journeys = self.find_routes(via, end, dep_time_leg2)
            
            if leg2_journeys:
                # Take best connection
                j2 = leg2_journeys[0]
                leg2 = j2.legs[0]
                
                # Calculate total duration
                try:
                    start_dt = datetime.strptime(leg1.departureTime, "%H:%M:%S")
                    end_dt = datetime.strptime(leg2.arrivalTime, "%H:%M:%S")
                    if end_dt < start_dt:
                        end_dt += timedelta(days=1)
                    duration_min = int((end_dt - start_dt).total_seconds() / 60)
                except:
                    duration_min = 0

                # Create combined journey
                combined_journeys.append(Journey(
                    id=f"{j1.id}-{j2.id}",
                    startStation=leg1.origin,
                    endStation=leg2.destination,
                    legs=[leg1, leg2],
                    transfers=1,
                    totalTime=duration_min,
                    description=f"Connection via {via}",
                    price=None
                ))
                
        return combined_journeys

    def get_station_info(self, name: str) -> Optional[StationInfo]:
        stop_id = self.find_station_id(name)
        if not stop_id:
            return None
            
        # Get facilities from pathways
        cursor = self.conn.execute(
            "SELECT pathway_mode FROM pathways WHERE from_stop_id = ?", 
            (stop_id,)
        )
        facilities = set()
        mode_map = {4: "Escalator", 5: "Elevator", 2: "Stairs"}
        for row in cursor:
            if row['pathway_mode'] in mode_map:
                facilities.add(mode_map[row['pathway_mode']])
                
        return StationInfo(
            name=name,
            facilities=list(facilities),
            entrances=["Main Entrance"] # Stub
        )

    def find_segment(self, start_name: str, end_name: str, time_str: str) -> List[Leg]:
        start_ids = self.get_all_station_ids(start_name)
        end_ids = self.get_all_station_ids(end_name)
        
        if not start_ids or not end_ids:
            return []

        start_ph = ','.join(['?'] * len(start_ids))
        end_ph = ','.join(['?'] * len(end_ids))

        query = f"""
            SELECT 
                t.trip_id,
                t.trip_short_name,
                r.route_short_name,
                r.route_type,
                t.trip_headsign,
                st1.departure_time as start_time,
                st2.arrival_time as end_time,
                s1.stop_name as start_station,
                s1.stop_id as start_id,
                s2.stop_name as end_station,
                s2.stop_id as end_id,
                p1.name as start_platform,
                p2.name as end_platform
            FROM trips t
            JOIN routes r ON t.route_id = r.route_id
            JOIN stop_times st1 ON t.trip_id = st1.trip_id
            JOIN stop_times st2 ON t.trip_id = st2.trip_id
            JOIN stations s1 ON st1.stop_id = s1.stop_id
            JOIN stations s2 ON st2.stop_id = s2.stop_id
            LEFT JOIN platforms p1 ON st1.stop_id = p1.global_id
            LEFT JOIN platforms p2 ON st2.stop_id = p2.global_id
            WHERE st1.stop_id IN ({start_ph}) 
              AND st2.stop_id IN ({end_ph})
              AND st1.stop_sequence < st2.stop_sequence
              AND st1.departure_time >= ?
            GROUP BY t.trip_id
            ORDER BY st1.departure_time LIMIT 20
        """
        
        params = start_ids + end_ids + [time_str]
        cursor = self.conn.execute(query, params)
        
        legs = []
        for row in cursor:
            # Get intermediate stops (path)
            path_cursor = self.conn.execute("""
                SELECT s.stop_name, s.stop_id, st.arrival_time, st.departure_time
                FROM stop_times st
                JOIN stations s ON st.stop_id = s.stop_id
                WHERE st.trip_id = ? 
                  AND st.stop_sequence > (SELECT stop_sequence FROM stop_times WHERE trip_id = ? AND stop_id = ?)
                  AND st.stop_sequence < (SELECT stop_sequence FROM stop_times WHERE trip_id = ? AND stop_id = ?)
                ORDER BY st.stop_sequence
            """, (row['trip_id'], row['trip_id'], row['start_id'], row['trip_id'], row['end_id']))
            path_stations = []
            for r in path_cursor:
                # Simulate platform deterministically based on stop_id
                # e.g. take last digits or hash
                try:
                    # Simple deterministic platform: (int(r['stop_id']) % 20) + 1
                    # EVA IDs are usually numeric strings like "8000105"
                    p_num = (int(r['stop_id']) % 20) + 1
                    platform = str(p_num)
                except:
                    platform = "1"

                path_stations.append(
                    Stop(
                        station=Station(name=r['stop_name'], eva=r['stop_id']),
                        arrivalTime=r['arrival_time'],
                        departureTime=r['departure_time'],
                        platform=platform
                    )
                )
            
            if len(path_stations) == 0:
                 pass

            train_num = row['trip_short_name'] or ""
            w_load = self.simulation.get_load(train_num)
            
            # Determine Platforms (with fallback)
            dep_plat = row['start_platform']
            if not dep_plat:
                try:
                    dep_plat = str((int(row['start_id']) % 20) + 1)
                except:
                    dep_plat = "1"
                    
            arr_plat = row['end_platform']
            if not arr_plat:
                try:
                    arr_plat = str((int(row['end_id']) % 20) + 1)
                except:
                    arr_plat = "1"

            # Determine Train Name (Prefix)
            line_name = row['route_short_name']
            if line_name and line_name.isdigit():
                rtype = row['route_type']
                if rtype == 101:
                    line_name = f"ICE {line_name}"
                elif rtype == 102:
                    line_name = f"IC {line_name}"
                elif rtype == 106:
                    line_name = f"RE {line_name}"
                elif rtype == 109:
                    line_name = f"S {line_name}"
                else:
                    line_name = f"RB {line_name}"

            train = Train(
                name=line_name,
                trainNumber=train_num,
                startLocation=Station(name=row['start_station'], eva=row['start_id']),
                endLocation=Station(name=row['end_station'], eva=row['end_id']),
                departureTime=row['start_time'],
                arrivalTime=row['end_time'],
                path=path_stations, 
                platform=dep_plat, 
                wagons=w_load
            )
            
            # Get delay
            delay = self.simulation.get_delay(train.trainNumber)
            
            legs.append(Leg(
                origin=Station(name=row['start_station'], eva=row['start_id']),
                destination=Station(name=row['end_station'], eva=row['end_id']),
                train=train,
                departureTime=row['start_time'],
                arrivalTime=row['end_time'],
                delayInMinutes=delay,
                departurePlatform=dep_plat,
                arrivalPlatform=arr_plat
            ))
            
        # Deduplicate legs (Python side)
        unique_legs = {}
        for l in legs:
            try:
                dt = datetime.strptime(l.departureTime, "%H:%M:%S")
                bucket_min = (dt.hour * 60 + dt.minute) // 20
                key = (l.train.trainNumber, bucket_min)
                
                if key not in unique_legs:
                    unique_legs[key] = l
            except:
                if l.train.trainNumber not in unique_legs:
                    unique_legs[l.train.trainNumber] = l
                    
        return list(unique_legs.values())



