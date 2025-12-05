import sqlite3
import pandas as pd
from pathlib import Path
import time

# Configuration
GTFS_DIR = Path("datachaos/20251201_fahrplaene_gesamtdeutschland_gtfs")
DB_PATH = Path("server/data/travel.db")
SCHEMA_PATH = Path("server/data/schema.sql")

# Train Route Types (ICE, IC, RE, RB, S-Bahn)
TRAIN_TYPES = [100, 101, 102, 106, 109]

def init_db():
    print(f"Initializing database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
    return conn

def ingest_routes(conn):
    print("Loading routes.txt...")
    df = pd.read_csv(GTFS_DIR / "routes.txt", dtype=str)
    
    # Filter for trains
    df['route_type'] = pd.to_numeric(df['route_type'], errors='coerce')
    train_routes = df[df['route_type'].isin(TRAIN_TYPES)].copy()
    
    print(f"Filtered {len(train_routes)} train routes from {len(df)} total.")
    
    train_routes[['route_id', 'route_short_name', 'route_long_name', 'route_type']].to_sql(
        'routes', conn, if_exists='replace', index=False, method='multi', chunksize=500
    )
    return set(train_routes['route_id'])

def ingest_trips(conn, valid_route_ids):
    print("Loading trips.txt...")
    df = pd.read_csv(GTFS_DIR / "trips.txt", dtype=str)
    
    # Filter by valid routes
    valid_trips = df[df['route_id'].isin(valid_route_ids)].copy()
    
    print(f"Filtered {len(valid_trips)} train trips from {len(df)} total.")
    
    # Ensure columns match schema
    valid_trips = valid_trips[['trip_id', 'route_id', 'service_id', 'trip_headsign', 'trip_short_name', 'direction_id']]
    
    valid_trips.to_sql('trips', conn, if_exists='replace', index=False, method='multi', chunksize=500)
    return set(valid_trips['trip_id'])

def ingest_stop_times(conn, valid_trip_ids):
    print("Loading stop_times.txt (this may take a while)...")
    # Read in chunks to handle memory
    chunk_size = 500000
    valid_stop_ids = set()
    
    # Create table first (empty) to append to
    conn.execute("DELETE FROM stop_times") 
    
    total_rows = 0
    for chunk in pd.read_csv(GTFS_DIR / "stop_times.txt", chunksize=chunk_size, dtype=str):
        # Filter
        filtered_chunk = chunk[chunk['trip_id'].isin(valid_trip_ids)].copy()
        
        if not filtered_chunk.empty:
            # Collect valid stop IDs
            valid_stop_ids.update(filtered_chunk['stop_id'])
            
            # Select columns
            cols = ['trip_id', 'stop_id', 'stop_sequence', 'arrival_time', 'departure_time', 'stop_headsign', 'pickup_type', 'drop_off_type']
            # Handle missing cols if any
            for c in cols:
                if c not in filtered_chunk.columns:
                    filtered_chunk[c] = None
            
            filtered_chunk[cols].to_sql('stop_times', conn, if_exists='append', index=False, method='multi', chunksize=500)
            total_rows += len(filtered_chunk)
            print(f"Processed {total_rows} stop_times...", end='\r')
            
    print(f"\nLoaded {total_rows} stop_times.")
    return valid_stop_ids

def ingest_stops(conn, valid_stop_ids):
    print("Loading stops.txt...")
    df = pd.read_csv(GTFS_DIR / "stops.txt", dtype=str)
    
    # Filter: Keep stops used in trips OR parent stations of used stops
    # First, get used stops
    used_stops = df[df['stop_id'].isin(valid_stop_ids)].copy()
    
    # Get their parents
    parent_ids = used_stops['parent_station'].dropna().unique()
    parents = df[df['stop_id'].isin(parent_ids)].copy()
    
    final_stops = pd.concat([used_stops, parents]).drop_duplicates(subset='stop_id')
    
    print(f"Filtered {len(final_stops)} relevant stops/stations from {len(df)} total.")
    
    # Map columns
    final_stops['wheelchair_boarding'] = pd.to_numeric(final_stops['wheelchair_boarding'], errors='coerce').fillna(0)
    
    cols = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'wheelchair_boarding', 'parent_station']
    final_stops[cols].to_sql('stations', conn, if_exists='replace', index=False, method='multi', chunksize=500)
    
    return set(final_stops['stop_id'])

def ingest_transfers(conn, valid_stop_ids):
    print("Loading transfers.txt...")
    if not (GTFS_DIR / "transfers.txt").exists():
        print("No transfers.txt found.")
        return

    df = pd.read_csv(GTFS_DIR / "transfers.txt", dtype=str)
    
    # Filter for valid stops
    df = df[df['from_stop_id'].isin(valid_stop_ids) & df['to_stop_id'].isin(valid_stop_ids)]
    
    print(f"Loaded {len(df)} transfers.")
    
    cols = ['from_stop_id', 'to_stop_id', 'transfer_type', 'min_transfer_time']
    # Handle missing cols
    if 'min_transfer_time' not in df.columns:
        df['min_transfer_time'] = None
        
    df[cols].to_sql('transfers', conn, if_exists='replace', index=False, method='multi', chunksize=500)

def ingest_pathways(conn, valid_stop_ids):
    print("Loading pathways.txt...")
    if not (GTFS_DIR / "pathways.txt").exists():
        print("No pathways.txt found.")
        return

    df = pd.read_csv(GTFS_DIR / "pathways.txt", dtype=str)
    
    # Filter
    df = df[df['from_stop_id'].isin(valid_stop_ids) & df['to_stop_id'].isin(valid_stop_ids)]
    
    print(f"Loaded {len(df)} pathways.")
    
    cols = ['pathway_id', 'from_stop_id', 'to_stop_id', 'pathway_mode', 'is_bidirectional', 'traversal_time']
    df[cols].to_sql('pathways', conn, if_exists='replace', index=False, method='multi', chunksize=500)

def main():
    start_time = time.time()
    conn = init_db()
    
    try:
        # 1. Routes
        valid_route_ids = ingest_routes(conn)
        
        # 2. Trips
        valid_trip_ids = ingest_trips(conn, valid_route_ids)
        
        # 3. Stop Times
        valid_stop_ids = ingest_stop_times(conn, valid_trip_ids)
        
        # 4. Stops
        ingest_stops(conn, valid_stop_ids)
        
        # 5. Transfers
        ingest_transfers(conn, valid_stop_ids)
        
        # 6. Pathways
        ingest_pathways(conn, valid_stop_ids)
        
        print(f"\nIngestion complete in {time.time() - start_time:.2f} seconds.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
