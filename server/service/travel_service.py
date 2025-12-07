import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from ..models import RouteOption, PlatformInfo, StationInfo, Leg, Train, Station, Stop

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
            
        # Also try "Frankfurt (Main) Hbf" -> "Frankfurt(Main)Hbf" (remove spaces)
        # But DB seems to have spaces "Frankfurt (Main) Hauptbahnhof"
        
        row = None
        for term in search_terms:
            cursor = self.conn.execute(
                "SELECT stop_id, parent_station FROM stations WHERE stop_name LIKE ? LIMIT 1", 
                (f"%{term}%",)
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

    def find_routes(self, start_name: str, end_name: str, time_str: str = None) -> List[RouteOption]:
        start_ids = self.get_all_station_ids(start_name)
        end_ids = self.get_all_station_ids(end_name)
        
        if not start_ids or not end_ids:
            return []

        # Create placeholders for IN clause
        start_ph = ','.join(['?'] * len(start_ids))
        end_ph = ','.join(['?'] * len(end_ids))

        # Find direct connections (MVP: SQL Join)
        # Join stop_times for start and end on trip_id
        query = f"""
            SELECT 
                t.trip_id,
                t.trip_short_name, -- Train Number
                r.route_short_name,
                t.trip_headsign,
                st1.departure_time as start_time,
                st2.arrival_time as end_time,
                s1.stop_name as start_station,
                s2.stop_name as end_station,
                p.name as platform_name,
                p.height as platform_height
            FROM trips t
            JOIN routes r ON t.route_id = r.route_id
            JOIN stop_times st1 ON t.trip_id = st1.trip_id
            JOIN stop_times st2 ON t.trip_id = st2.trip_id
            JOIN stations s1 ON st1.stop_id = s1.stop_id
            JOIN stations s2 ON st2.stop_id = s2.stop_id
            LEFT JOIN platforms p ON st1.stop_id = p.global_id -- NeTEx enrichment
            WHERE st1.stop_id IN ({start_ph}) 
              AND st2.stop_id IN ({end_ph})
              AND st1.stop_sequence < st2.stop_sequence
        """
        params = start_ids + end_ids
        
        if time_str:
            query += " AND st1.departure_time >= ?"
            params.append(time_str)
            
        query += " ORDER BY st1.departure_time LIMIT 5"
        
        cursor = self.conn.execute(query, params)
        routes = []
        
        for row in cursor:
            # Calculate delay (Simulation)
            train_number = row['trip_short_name'] or ""
            delay = self.simulation.get_delay(train_number)
            
            # Adjust time
            # Simple string manipulation for MVP (assuming HH:MM:SS)
            # In real app, use datetime
            scheduled = row['start_time']
            real_time = scheduled # TODO: Add delay minutes to time string
            
            # Accessibility logic (Stub based on platform height/pathways)
            access = "Unknown"
            if row['platform_height']:
                access = f"Platform height: {row['platform_height']}cm"
            
            routes.append(RouteOption(
                trip_id=row['trip_id'],
                line_name=row['route_short_name'],
                start_station=row['start_station'],
                end_station=row['end_station'],
                scheduled_departure=scheduled,
                real_time_departure=real_time, 
                arrival=row['end_time'],
                delay_minutes=delay,
                platform=PlatformInfo(
                    name=row['platform_name'] or "Unknown",
                    accessibility=access
                ),
                occupancy="Medium" # TODO: Simulate
            ))
            
        return routes

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
                t.trip_headsign,
                st1.departure_time as start_time,
                st2.arrival_time as end_time,
                s1.stop_name as start_station,
                s1.stop_id as start_id,
                s2.stop_name as end_station,
                s2.stop_id as end_id,
                p.name as platform_name,
                p.height as platform_height
            FROM trips t
            JOIN routes r ON t.route_id = r.route_id
            JOIN stop_times st1 ON t.trip_id = st1.trip_id
            JOIN stop_times st2 ON t.trip_id = st2.trip_id
            JOIN stations s1 ON st1.stop_id = s1.stop_id
            JOIN stations s2 ON st2.stop_id = s2.stop_id
            LEFT JOIN platforms p ON st1.stop_id = p.global_id
            WHERE st1.stop_id IN ({start_ph}) 
              AND st2.stop_id IN ({end_ph})
              AND st1.stop_sequence < st2.stop_sequence
              AND st1.departure_time >= ?
            ORDER BY st1.departure_time LIMIT 10
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
                    # Simple deterministic platform: (int(stop_id) % 20) + 1
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

            train = Train(
                name=row['route_short_name'],
                trainNumber=row['trip_short_name'] or "",
                startLocation=Station(name=row['start_station'], eva=row['start_id']),
                endLocation=Station(name=row['end_station'], eva=row['end_id']),
                departureTime=row['start_time'],
                arrivalTime=row['end_time'],
                path=path_stations, 
                platform=0, 
                wagons=self.simulation.get_load(row['trip_short_name'] or "")
            )
            
            # Get delay
            delay = self.simulation.get_delay(train.trainNumber)
            
            legs.append(Leg(
                origin=Station(name=row['start_station'], eva=row['start_id']),
                destination=Station(name=row['end_station'], eva=row['end_id']),
                train=train,
                departureTime=row['start_time'],
                arrivalTime=row['end_time'],
                delayInMinutes=delay
            ))
            
        return legs



