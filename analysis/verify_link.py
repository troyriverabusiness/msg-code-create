import pandas as pd
from pathlib import Path

DATA_DIR = Path("../datachaos/20251201_fahrplaene_gesamtdeutschland_gtfs")

def verify_link():
    print("Loading routes and trips...")
    routes = pd.read_csv(DATA_DIR / "routes.txt")
    trips = pd.read_csv(DATA_DIR / "trips.txt", dtype={'trip_short_name': str})

    # 1. Explore ICE (Route Type 101)
    print("\n--- Exploring Route Type 101 (High Speed Rail) ---")
    ice_routes = routes[routes['route_type'] == 101]
    print(f"Found {len(ice_routes)} routes with type 101.")
    print("Sample route_short_names:", ice_routes['route_short_name'].unique()[:10])
    
    ice_route_ids = ice_routes['route_id'].unique()
    ice_trips = trips[trips['route_id'].isin(ice_route_ids)]
    print(f"Found {len(ice_trips)} trips for type 101.")
    
    # Check for 690 in trip_short_name (exact or contained)
    # The XML had n="690". GTFS might have "690" or "ICE 690" or "000690".
    match_690 = ice_trips[ice_trips['trip_short_name'].str.contains("690", na=False)]
    if not match_690.empty:
        print("Found '690' in trip_short_name for type 101 trips:")
        print(match_690[['trip_id', 'trip_short_name', 'trip_headsign']].head())
    else:
        print("Did not find '690' in trip_short_name for type 101 trips.")
        print("Sample trip_short_names:", ice_trips['trip_short_name'].head(10).tolist())

    # 2. Explore RB82
    print("\n--- Exploring RB82 ---")
    rb82_routes = routes[routes['route_short_name'] == 'RB82']
    if not rb82_routes.empty:
        rb82_trips = trips[trips['route_id'].isin(rb82_routes['route_id'])]
        print(f"Found {len(rb82_trips)} RB82 trips.")
        # XML had n="25169" for RB82
        match_25169 = rb82_trips[rb82_trips['trip_short_name'].str.contains("25169", na=False)]
        if not match_25169.empty:
             print("Found '25169' in RB82 trips:")
             print(match_25169[['trip_id', 'trip_short_name']].head())
        else:
             print("Did not find '25169' in RB82 trips.")
             print("Sample RB82 trip_short_names:", rb82_trips['trip_short_name'].head().tolist())

if __name__ == "__main__":
    verify_link()
