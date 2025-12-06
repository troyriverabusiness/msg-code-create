import sqlite3
import pandas as pd
from pathlib import Path
import re
import glob
import os

DB_PATH = Path(__file__).parent.parent / "data" / "travel.db"
DATA_DIR = Path(__file__).parent.parent.parent / "datachaos" / "deutsche-bahn-data"

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS delay_patterns (
            train_number TEXT,
            station_name TEXT,
            hour_of_day INTEGER,
            avg_delay REAL,
            sample_size INTEGER,
            PRIMARY KEY (train_number, station_name, hour_of_day)
        )
    """)
    conn.commit()

def extract_train_number(train_name):
    # Matches "ICE 690", "RE 12345", "S 1"
    match = re.search(r'\d+', str(train_name))
    return match.group(0) if match else None

def ingest_data():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    create_table(conn)
    
    parquet_files = sorted(glob.glob(str(DATA_DIR / "*.parquet")))
    print(f"Found {len(parquet_files)} parquet files.")
    
    # We only process the last 3 months to keep it fast and relevant
    # Or maybe just one file for the demo to be super fast?
    # Let's try to process all but limit rows if needed.
    # Actually, let's process the latest file first: data-2024-10.parquet (from ls output)
    # Wait, ls output showed up to 2025-11? No, that's future data?
    # Ah, the ls output showed files named data-2024-07 to data-2025-11.
    # Wait, data-2025-11? Is that prediction data? Or is the file name just month based and they have future schedules?
    # The user said "for delays". Usually historical data is past.
    # Maybe the dataset contains both?
    # Let's inspect "data-2024-10.parquet" as it is recent past (assuming now is Dec 2025? No, now is Dec 2024? User metadata says 2025-12-06).
    # Wait, user metadata says "The current local time is: 2025-12-06".
    # So 2024-10 is past. 2025-11 is future?
    # If the dataset has future data, maybe it has planned schedules?
    # But we want *delays*. Future data won't have delays (unless it's predicted).
    # Let's check `delay_in_min` in a future file.
    
    # For now, let's process 2024-10 and 2024-11 (recent past relative to 2025? No wait).
    # If today is 2025-12-06.
    # Then 2024-10 is over a year ago.
    # 2025-11 is last month.
    # So we should process 2025-10 and 2025-11.
    
    files_to_process = [f for f in parquet_files if "2025-10" in f or "2025-11" in f]
    
    if not files_to_process:
        print("No recent files found (looking for 2025-10, 2025-11). Processing all 2025 files...")
        files_to_process = [f for f in parquet_files if "2025" in f]
        
    print(f"Processing {len(files_to_process)} files: {[os.path.basename(f) for f in files_to_process]}")
    
    for file_path in files_to_process:
        print(f"Reading {os.path.basename(file_path)}...")
        try:
            df = pd.read_parquet(file_path, columns=['station_name', 'train_name', 'time', 'delay_in_min'])
            
            # Filter out rows with no delay info
            df = df.dropna(subset=['delay_in_min', 'train_name'])
            
            # Extract train number
            df['train_number'] = df['train_name'].apply(extract_train_number)
            df = df.dropna(subset=['train_number'])
            
            # Extract hour
            df['time'] = pd.to_datetime(df['time'])
            df['hour_of_day'] = df['time'].dt.hour
            
            # Group and aggregate
            print("Aggregating...")
            agg_df = df.groupby(['train_number', 'station_name', 'hour_of_day']).agg(
                avg_delay=('delay_in_min', 'mean'),
                sample_size=('delay_in_min', 'count')
            ).reset_index()
            
            # Write to DB
            print(f"Writing {len(agg_df)} patterns to DB...")
            # Use chunks if necessary, but pandas to_sql is okay for this size
            agg_df.to_sql('delay_patterns', conn, if_exists='append', index=False, method='multi', chunksize=1000)
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    print("Ingestion complete.")
    
    # Verify
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM delay_patterns")
    count = cursor.fetchone()[0]
    print(f"Total patterns in DB: {count}")
    
    cursor.execute("SELECT * FROM delay_patterns ORDER BY sample_size DESC LIMIT 5")
    print("Top patterns:")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()

if __name__ == "__main__":
    ingest_data()
