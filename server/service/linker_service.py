import sqlite3
from typing import Optional, Dict, List

class LinkerService:
    def __init__(self, db_path="server/data/travel.db"):
        self.db_path = db_path

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def find_trip_id(self, train_category: str, train_number: str) -> Optional[str]:
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

    def get_trip_details(self, trip_id: str) -> Dict:
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
