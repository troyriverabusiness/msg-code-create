import sqlite3
from typing import Optional, Dict, List
from datetime import datetime
from server.data_access.DB.timetable_service import TimetableService
from server.service.simulation import SimulationService

class LinkerService:
    def __init__(self, db_path="server/data/travel.db"):
        self.db_path = db_path
        self.timetable_service = TimetableService()
        self.simulation_service = SimulationService()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def find_trip_id(self, train_category: str, train_number: str, date: datetime) -> Optional[str]:
        """
        Finds the GTFS trip_id for a given train category (ICE, RE) and number (690).
        """
        # 1. Normalize Train Number (Pad to 6 digits)
        # e.g. "690" -> "000690"
        padded_number = train_number.zfill(6)
        
        conn = self._get_conn()
        cursor = conn.cursor()
        
        try:
            # 2. Query trips with this number
            query = """
                SELECT t.trip_id, r.route_short_name 
                FROM trips t
                JOIN routes r ON t.route_id = r.route_id
                WHERE t.trip_short_name = ?
            """
            cursor.execute(query, (padded_number,))
            results = cursor.fetchall()
            
            if not results:
                return None
                
            # 3. Filter by Category (fuzzy match)
            # e.g. match "ICE" in "ICE" or "RE" in "RE 1"
            for trip_id, route_name in results:
                if train_category.lower() in route_name.lower():
                    return trip_id
            
            # Fallback: Return first match if no category match (or just return None)
            # For MVP, let's return the first one if we have results but no category match,
            # but logging a warning would be good.
            return results[0][0]
            
        except Exception as e:
            print(f"Linker Error: {e}")
            return None
        finally:
            conn.close()

    def get_trip_details(self, trip_id: str, date: datetime) -> Dict:
        """
        Fetches full details for a trip.
        Hybrid Logic:
        - If date is today: Use TimetableService (Live)
        - If date is future: Use SimulationService (Static + Fake Delay)
        """
        is_today = date.date() == datetime.now().date()
        
        if is_today:
            # Try to get live data
            # We need the EVA number of a station on the trip to query the API.
            # But TimetableService needs EVA. We only have trip_id.
            # We can get the static stops first, then query live data for the start station?
            # Or just use the static data and enrich it?
            pass
            
        # For MVP, we always fetch static data first as the base
        static_details = self._get_static_trip_details(trip_id)
        if not static_details:
            return {}
            
        if is_today:
            # Enrich with Live Data
            # TODO: Implement live enrichment properly.
            # For now, we just return static.
            # Real implementation would query TimetableService for the start station of the trip
            # and find this specific train to get live delays.
            pass
        else:
            # Simulate Delay
            # TODO: Use Data-Driven Simulation here later.
            # For now, use the simple random simulation.
            delay = self.simulation_service.get_delay(static_details['train'])
            if delay > 0:
                static_details['messages'] = [f"Simulated delay: +{delay} min"]
                # Adjust times? Or just add delay field?
    def get_trip_details(self, trip_id: str) -> Dict:
        """
        Get details for a specific trip (stops, times).
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.stop_name, st.arrival_time, st.departure_time, st.stop_sequence
            FROM stop_times st
            JOIN stations s ON st.stop_id = s.stop_id
            WHERE st.trip_id = ?
            ORDER BY st.stop_sequence
        """, (trip_id,))
        
        stops = []
        for row in cursor.fetchall():
            stops.append({
                "name": row[0],
                "arrival": row[1],
                "departure": row[2]
            })
            
        conn.close()
        
        return {
            "trip_id": trip_id,
            "stops": stops
        }

    def find_trips(self, origin_id: str, dest_id: str, date_str: str, min_time: str) -> List[Dict]:
        """
        Find trips that go from origin to destination after min_time on the given date.
        Returns a list of dicts with trip details.
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # TODO: Handle date (service_id) filtering. For now, we assume all trips run every day 
        # or we rely on the fact that we are just looking for *any* valid connection in the static schedule.
        # In a real implementation, we would join with calendar/calendar_dates.
        
        query = """
            SELECT 
                t.trip_id,
                st1.departure_time as start_time,
                st2.arrival_time as end_time,
                st1.stop_id as origin_stop,
                st2.stop_id as dest_stop
            FROM stop_times st1
            JOIN stop_times st2 ON st1.trip_id = st2.trip_id
            JOIN trips t ON st1.trip_id = t.trip_id
            WHERE st1.stop_id IN (SELECT stop_id FROM stations WHERE parent_station = ? OR stop_id = ?)
              AND st2.stop_id IN (SELECT stop_id FROM stations WHERE parent_station = ? OR stop_id = ?)
              AND st1.stop_sequence < st2.stop_sequence
              AND st1.departure_time >= ?
            ORDER BY st1.departure_time
            LIMIT 5
        """
        
        cursor.execute(query, (origin_id, origin_id, dest_id, dest_id, min_time))
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "trip_id": row[0],
                "departure_time": row[1],
                "arrival_time": row[2],
                "origin_platform": "1", # Default, as we don't have platform info in stop_times yet
                "dest_platform": "1"
            })
            
        return results

    def _get_static_trip_details(self, trip_id: str) -> Dict:
        """
        Fetches full details for a trip from GTFS (Stops, Times, Accessibility).
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        try:
            # Get Route Info
            cursor.execute("""
                SELECT r.route_short_name, t.trip_headsign 
                FROM trips t
                JOIN routes r ON t.route_id = r.route_id
                WHERE t.trip_id = ?
            """, (trip_id,))
            route_row = cursor.fetchone()
            if not route_row:
                return {}
                
            route_name, headsign = route_row
            
            # Get Stops
            cursor.execute("""
                SELECT s.stop_name, st.arrival_time, st.departure_time, s.wheelchair_boarding
                FROM stop_times st
                JOIN stations s ON st.stop_id = s.stop_id
                WHERE st.trip_id = ?
                ORDER BY st.stop_sequence
            """, (trip_id,))
            
            stops = []
            for row in cursor.fetchall():
                stops.append({
                    "station": row[0],
                    "arrival": row[1],
                    "departure": row[2],
                    "wheelchair": row[3] == 1 # 1=Yes
                })
                
            return {
                "trip_id": trip_id,
                "train": route_name,
                "headsign": headsign,
                "stops": stops
            }
            
        except Exception as e:
            print(f"Linker Details Error: {e}")
            return {}
        finally:
            conn.close()
