import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "travel.db"

def check_names():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    names_to_check = ["Cologne", "Munich", "Nuremberg", "Vienna", "Köln", "München"]
    
    print(f"Checking names: {names_to_check}")
    
    for name in names_to_check:
        print(f"\nSearching for '{name}':")
        cursor.execute("SELECT stop_name FROM stations WHERE stop_name LIKE ? LIMIT 5", (f"%{name}%",))
        rows = cursor.fetchall()
        found = [r['stop_name'] for r in rows]
        if found:
            print(f"  Found: {found}")
        else:
            print(f"  NOT FOUND")

if __name__ == "__main__":
    check_names()
