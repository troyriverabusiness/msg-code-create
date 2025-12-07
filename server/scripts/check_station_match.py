import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "travel.db"

def check_station_match():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    name = "Frankfurt HBF"
    print(f"Testing match for: '{name}'")
    
    # Test 1: Exact LIKE
    print("\nTest 1: LIKE %name%")
    cursor.execute("SELECT stop_name FROM stations WHERE stop_name LIKE ?", (f"%{name}%",))
    rows = cursor.fetchall()
    print(f"Matches: {[r['stop_name'] for r in rows]}")
    
    # Test 2: Wildcard spaces
    print("\nTest 2: Wildcard spaces")
    wildcard_term = name.replace(" ", "%")
    print(f"Term: '{wildcard_term}'")
    cursor.execute("SELECT stop_name FROM stations WHERE stop_name LIKE ?", (f"%{wildcard_term}%",))
    rows = cursor.fetchall()
    print(f"Matches: {[r['stop_name'] for r in rows]}")
    
    # Test 3: Case insensitive check (manual)
    print("\nTest 3: Manual lower()")
    cursor.execute("SELECT stop_name FROM stations WHERE lower(stop_name) LIKE ?", (f"%{name.lower()}%",))
    rows = cursor.fetchall()
    print(f"Matches: {[r['stop_name'] for r in rows]}")

    # Test 4: Check actual Frankfurt names
    print("\nTest 4: Actual Frankfurt stations")
    cursor.execute("SELECT stop_name FROM stations WHERE stop_name LIKE '%Frankfurt%' LIMIT 20")
    rows = cursor.fetchall()
    print(f"Found: {[r['stop_name'] for r in rows]}")

if __name__ == "__main__":
    check_station_match()
