import sqlite3
from pathlib import Path

DB_PATH = Path("server/data/travel.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    stations = ["Frankfurt (Main) Hauptbahnhof", "Berlin Hauptbahnhof"]
    
    print("Checking stations...")
    for s in stations:
        cursor = conn.execute("SELECT stop_id, stop_name FROM stations WHERE stop_name LIKE ?", (f"%{s}%",))
        rows = cursor.fetchall()
        if rows:
            for r in rows:
                print(f"Found: {r['stop_name']} (ID: {r['stop_id']})")
        else:
            print(f"Not found: {s}")
            
    print("\nChecking stop_times for Berlin Hbf...")
    # Get all IDs for Berlin Hbf
    cursor = conn.execute("SELECT stop_id FROM stations WHERE stop_name LIKE '%Berlin Hauptbahnhof%'")
    berlin_ids = [r['stop_id'] for r in cursor.fetchall()]
    
    # Check if any of these IDs appear in stop_times
    placeholders = ','.join(['?'] * len(berlin_ids))
    cursor = conn.execute(f"SELECT * FROM stop_times WHERE stop_id IN ({placeholders}) LIMIT 5", berlin_ids)
    for r in cursor:
        print(dict(r))

    conn.close()

if __name__ == "__main__":
    main()
