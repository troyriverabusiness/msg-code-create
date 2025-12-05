import pandas as pd
from pathlib import Path

DATA_DIR = Path("../datachaos/20251201_fahrplaene_gesamtdeutschland_gtfs")

def check_stops():
    stops = pd.read_csv(DATA_DIR / "stops.txt", usecols=['stop_name'])
    
    print("--- Searching for Frankfurt ---")
    frankfurt = stops[stops['stop_name'].str.contains("Frankfurt", na=False)]
    print(frankfurt['stop_name'].head(20).tolist())
    
    print("\n--- Searching for Berlin ---")
    berlin = stops[stops['stop_name'].str.contains("Berlin", na=False)]
    print(berlin['stop_name'].unique()[:20].tolist())

if __name__ == "__main__":
    check_stops()
