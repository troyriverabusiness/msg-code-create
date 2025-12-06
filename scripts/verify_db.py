import sqlite3
from pathlib import Path

DB_PATH = Path("server/data/travel.db")

def check_db():
    if not DB_PATH.exists():
        print("❌ Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ["routes", "trips", "platforms", "stations"]
    print("📊 Database Stats:")
    print("-" * 20)
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ {table}: {count} rows")
        except sqlite3.OperationalError:
            print(f"❌ {table}: Table missing!")
            
    conn.close()

if __name__ == "__main__":
    check_db()
