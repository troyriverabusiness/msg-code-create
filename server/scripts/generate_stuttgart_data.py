
import sqlite3
import uuid
from pathlib import Path

DB_PATH = Path("server/data/travel.db")

def generate_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Generating synthetic data for Stuttgart Hbf...")
    
    # 1. Get Station IDs
    def get_id(name):
        cursor.execute("SELECT stop_id FROM stations WHERE stop_name LIKE ? LIMIT 1", (f"%{name}%",))
        res = cursor.fetchone()
        if not res:
            print(f"Error: Station {name} not found!")
            return None
        return res[0]

    ffm_id = get_id("Frankfurt (Main) Hauptbahnhof")
    str_id = get_id("Stuttgart Hbf")
    muc_id = get_id("München Hbf")
    
    if not (ffm_id and str_id and muc_id):
        return

    print(f"IDs: FFM={ffm_id}, STR={str_id}, MUC={muc_id}")

    # 2. Helper to create a trip
    def create_trip(train_num, dep_hour, route_id):
        trip_id = f"syn_trip_{train_num}_{uuid.uuid4()}"
        cursor.execute("INSERT INTO trips (trip_id, route_id, service_id, trip_short_name) VALUES (?, ?, ?, ?)",
                       (trip_id, route_id, "daily", f"ICE {train_num}"))
        return trip_id

    # 3. Helper to add stop
    def add_stop(trip_id, station_name, seq, arr_time, dep_time):
        sid = get_id(station_name)
        if sid:
            cursor.execute("INSERT INTO stop_times (trip_id, stop_id, stop_sequence, arrival_time, departure_time) VALUES (?, ?, ?, ?, ?)",
                           (trip_id, sid, seq, arr_time, dep_time))

    # 4. Generate Hourly Connections (06:00 - 20:00)
    # Pattern: FFM -> Mannheim -> Stuttgart -> Ulm -> Augsburg -> Munich
    # Leg 1: FFM -> STR (1h travel)
    # Leg 2: STR -> MUC (1.5h travel)
    
    route_id = "synthetic_ice_stuttgart"
    cursor.execute("INSERT OR IGNORE INTO routes (route_id, route_short_name, route_type) VALUES (?, ?, ?)", 
                   (route_id, "ICE", 101))

    for hour in range(6, 21, 2): # Every 2 hours: 6, 8, 10, ...
        # Train 1: FFM -> STR
        t1_num = 900 + hour
        t1_id = create_trip(t1_num, hour, route_id)
        
        # FFM (Start)
        add_stop(t1_id, "Frankfurt (Main) Hauptbahnhof", 1, f"{hour:02d}:00:00", f"{hour:02d}:00:00")
        # Mannheim (Intermediate)
        add_stop(t1_id, "Mannheim, Hauptbahnhof", 2, f"{hour:02d}:35:00", f"{hour:02d}:37:00")
        # Stuttgart (End)
        add_stop(t1_id, "Stuttgart Hbf", 3, f"{hour+1:02d}:00:00", f"{hour+1:02d}:00:00")
        
        # Train 2: STR -> MUC (Depart 30 mins later)
        t2_num = 900 + hour + 1
        t2_id = create_trip(t2_num, hour, route_id)
        
        dep_h = hour + 1
        dep_m = 30
        
        # Stuttgart (Start)
        add_stop(t2_id, "Stuttgart Hbf", 1, f"{dep_h:02d}:{dep_m:02d}:00", f"{dep_h:02d}:{dep_m:02d}:00")
        # Ulm (Intermediate)
        add_stop(t2_id, "Ulm Hauptbahnhof", 2, f"{dep_h+1:02d}:15:00", f"{dep_h+1:02d}:17:00")
        # Augsburg (Intermediate)
        add_stop(t2_id, "Augsburg Hbf", 3, f"{dep_h+1:02d}:55:00", f"{dep_h+1:02d}:57:00")
        # Munich (End)
        add_stop(t2_id, "München Hbf", 4, f"{dep_h+2:02d}:30:00", f"{dep_h+2:02d}:30:00")

    conn.commit()
    print("Successfully inserted hourly synthetic trips with intermediate stops!")
    conn.close()

if __name__ == "__main__":
    generate_data()
