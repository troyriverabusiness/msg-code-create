import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "travel.db"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "top_stations.json"

def calculate_connectivity():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Calculating station connectivity (number of trips)...")
    # Count how many unique trips stop at each station
    # We group by station name to aggregate platforms (e.g. "Berlin Hbf (tief)" and "Berlin Hbf")
    # Actually, let's keep it simple first: Count by stop_id, but maybe we should aggregate by parent?
    # The GraphService currently uses stop_id.
    # Let's count by stop_id for now, but also fetch the name.
    
    # Aggregate by parent_station (or stop_id if no parent) to collapse platforms
    query = """
        SELECT 
            COALESCE(s.parent_station, s.stop_id) as canonical_id,
            MIN(s.stop_name) as name, -- Pick one name (usually they are similar)
            COUNT(st.trip_id) as trip_count
        FROM stations s
        JOIN stop_times st ON s.stop_id = st.stop_id
        GROUP BY canonical_id
        ORDER BY trip_count DESC
        LIMIT 600
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    top_stations = []
    print(f"Found {len(rows)} stations (aggregated). Top 10:")
    
    for i, row in enumerate(rows):
        station = {
            "id": row[0],
            "name": row[1],
            "score": row[2]
        }
        top_stations.append(station)
        if i < 10:
            print(f" - {station['name']} ({station['score']} trips)")

    # Filter out pure local transport if needed? 
    # For now, high frequency usually means important.
    
    print(f"Saving top {len(top_stations)} stations to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w") as f:
        json.dump(top_stations, f, indent=2)
        
    conn.close()
    print("Done.")

if __name__ == "__main__":
    calculate_connectivity()
