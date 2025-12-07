import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "travel.db"

def check_stations():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print("Searching for stations with 'Frankfurt'...")
    cursor = conn.execute("SELECT stop_id, stop_name FROM stations WHERE stop_name LIKE '%Frankfurt%'")
    for row in cursor:
        print(f"ID: {row['stop_id']}, Name: {row['stop_name']}")
        
    print("\nSearching for stations with 'Köln'...")
    cursor = conn.execute("SELECT stop_id, stop_name FROM stations WHERE stop_name LIKE '%Köln%'")
    for row in cursor:
        print(f"ID: {row['stop_id']}, Name: {row['stop_name']}")

    print("\nSearching for stations with 'Hamburg'...")
    cursor = conn.execute("SELECT stop_id, stop_name FROM stations WHERE stop_name LIKE '%Hamburg%'")
    for row in cursor:
        print(f"ID: {row['stop_id']}, Name: {row['stop_name']}")

if __name__ == "__main__":
    check_stations()
