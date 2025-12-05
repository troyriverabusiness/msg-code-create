import os
import pandas as pd
from pathlib import Path

# Path to the GTFS data
DATA_DIR = Path("../datachaos/20251201_fahrplaene_gesamtdeutschland_gtfs")

def analyze_file(filepath):
    print(f"--- Analyzing {filepath.name} ---")
    file_size_mb = filepath.stat().st_size / (1024 * 1024)
    print(f"Size: {file_size_mb:.2f} MB")

    try:
        # Read first few rows to get columns and sample
        df_preview = pd.read_csv(filepath, nrows=5)
        print("Columns:", list(df_preview.columns))
        print("Preview:")
        print(df_preview)
        
        # Count rows efficiently
        if file_size_mb > 100: # For large files, count lines without loading all to RAM
            print("Large file detected, counting lines...")
            with open(filepath, 'rb') as f:
                row_count = sum(1 for _ in f) - 1 # Subtract header
            print(f"Total Rows: {row_count}")
        else:
            df = pd.read_csv(filepath)
            print(f"Total Rows: {len(df)}")
            
            # Specific checks for certain files
            if filepath.name == 'agency.txt':
                print(f"Agencies: {df['agency_name'].nunique()}")
            elif filepath.name == 'routes.txt':
                print(f"Routes: {df['route_id'].nunique()}")
                print(f"Route Types: {df['route_type'].value_counts().to_dict()}")
            elif filepath.name == 'stops.txt':
                print(f"Stops: {df['stop_id'].nunique()}")
                
    except Exception as e:
        print(f"Error analyzing {filepath.name}: {e}")
    
    print("\n")

def main():
    if not DATA_DIR.exists():
        print(f"Directory not found: {DATA_DIR}")
        return

    files = sorted([f for f in DATA_DIR.iterdir() if f.is_file() and f.suffix == '.txt'])
    
    print(f"Found {len(files)} GTFS files in {DATA_DIR}\n")
    
    for file in files:
        analyze_file(file)

if __name__ == "__main__":
    main()
