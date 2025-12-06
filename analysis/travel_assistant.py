import pandas as pd
import networkx as nx
from pathlib import Path
import datetime

DATA_DIR = Path("../datachaos/20251201_fahrplaene_gesamtdeutschland_gtfs")

class TravelAssistant:
    def __init__(self):
        print("Initializing Travel Assistant...")
        self.load_data()
        
    def load_data(self):
        print("Loading GTFS data (Trains only)...")
        # 1. Load Routes (Filter for Trains)
        routes = pd.read_csv(DATA_DIR / "routes.txt")
        train_types = [100, 101, 102, 106, 109] # ICE, IC, RE, RB, S-Bahn
        self.routes = routes[routes['route_type'].isin(train_types)]
        valid_route_ids = set(self.routes['route_id'])
        print(f"Loaded {len(self.routes)} train routes.")

        # 2. Load Stops (Basic info)
        self.stops = pd.read_csv(DATA_DIR / "stops.txt", usecols=['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'wheelchair_boarding'])
        # Create a lookup for name -> id (simplified, taking first match)
        self.stop_name_to_id = self.stops.groupby('stop_name')['stop_id'].first().to_dict()
        self.stop_id_to_name = self.stops.set_index('stop_id')['stop_name'].to_dict()
        
        # 3. Load Trips (Filter by valid routes)
        trips = pd.read_csv(DATA_DIR / "trips.txt", usecols=['route_id', 'trip_id', 'trip_headsign', 'service_id'])
        self.trips = trips[trips['route_id'].isin(valid_route_ids)]
        self.valid_trip_ids = set(self.trips['trip_id'])
        print(f"Loaded {len(self.trips)} train trips.")

        # 4. Load Stop Times (Only for valid trips)
        # This is the heavy part. For a prototype, we might limit to a sample or load efficiently.
        # We'll load a subset of columns.
        print("Loading Stop Times (this takes memory)...")
        chunksize = 5_000_000
        dfs = []
        for chunk in pd.read_csv(DATA_DIR / "stop_times.txt", 
                               usecols=['trip_id', 'stop_id', 'stop_sequence', 'arrival_time', 'departure_time'],
                               chunksize=chunksize):
            # Filter
            chunk = chunk[chunk['trip_id'].isin(self.valid_trip_ids)]
            dfs.append(chunk)
        
        self.stop_times = pd.concat(dfs)
        print(f"Loaded {len(self.stop_times)} stop_times entries.")
        
        # Optimize: Sort by trip and sequence
        self.stop_times.sort_values(['trip_id', 'stop_sequence'], inplace=True)

    def find_station_ids(self, search_name):
        """Returns a list of all stop_ids matching the name (parent + children)"""
        # 1. Find all stops with this name (partial match)
        matches = self.stops[self.stops['stop_name'].str.contains(search_name, case=False, na=False, regex=False)]
        
        if matches.empty:
            return []
        
        # If "Hauptbahnhof" is in search, prioritize it
        if "hauptbahnhof" in search_name.lower():
             hbf = matches[matches['stop_name'].str.contains("Hauptbahnhof", case=False)]
             if not hbf.empty:
                 matches = hbf
        
        # Get all IDs
        found_ids = matches['stop_id'].tolist()
        
        # Filter to only those present in our filtered stop_times (optimization)
        # We need a set of used stop_ids. 
        # Since we didn't store that explicitly, let's just return all found IDs 
        # and let the merge step handle it (it will just be empty for unused ones).
        return found_ids

    def find_direct_connections(self, start_name, end_name, time_string=None):
        """
        Finds direct trains from Start to End.
        time_string: "HH:MM:SS" (optional filter)
        """
        start_ids = self.find_station_ids(start_name)
        end_ids = self.find_station_ids(end_name)
        
        if not start_ids or not end_ids:
            return f"Error: Could not find station IDs for '{start_name}' or '{end_name}'"

        print(f"Searching connections from '{start_name}' ({len(start_ids)} possible IDs) to '{end_name}' ({len(end_ids)} possible IDs)...")
        
        # Find trips that contain both stops
        # 1. Get trips at start (any of the start IDs)
        trips_at_start = self.stop_times[self.stop_times['stop_id'].isin(start_ids)][['trip_id', 'departure_time', 'stop_sequence']]
        trips_at_start = trips_at_start.rename(columns={'stop_sequence': 'start_seq', 'departure_time': 'start_time'})
        
        # 2. Get trips at end (any of the end IDs)
        trips_at_end = self.stop_times[self.stop_times['stop_id'].isin(end_ids)][['trip_id', 'arrival_time', 'stop_sequence']]
        trips_at_end = trips_at_end.rename(columns={'stop_sequence': 'end_seq', 'arrival_time': 'end_time'})
        
        # 3. Merge
        connections = pd.merge(trips_at_start, trips_at_end, on='trip_id')
        
        # 4. Filter: End must be after Start
        connections = connections[connections['end_seq'] > connections['start_seq']]
        
        # 5. Filter by time if provided
        if time_string:
            connections = connections[connections['start_time'] >= time_string]
            
        # 6. Join with Trip/Route info
        connections = pd.merge(connections, self.trips, on='trip_id')
        connections = pd.merge(connections, self.routes[['route_id', 'route_short_name', 'route_long_name']], on='route_id')
        
        # Sort by departure time
        connections.sort_values('start_time', inplace=True)
        
        return connections.head(10) # Return top 10

    def get_station_accessibility(self, station_name):
        ids = self.find_station_ids(station_name)
        if not ids:
            return "Station not found."
        
        # Just take the first one for info
        stop_id = ids[0]
        info = self.stops[self.stops['stop_id'] == stop_id].iloc[0]
        
        # Wheelchair boarding: 0=Unknown, 1=Yes, 2=No
        status_map = {0: "Unknown", 1: "Yes (Barrier-free)", 2: "No"}
        access_status = status_map.get(info['wheelchair_boarding'], "Unknown")
        
        return {
            "name": info['stop_name'],
            "wheelchair_access": access_status,
            "lat": info['stop_lat'],
            "lon": info['stop_lon']
        }

def main():
    assistant = TravelAssistant()
    
    # Test Case 1: Accessibility
    print("\n--- Accessibility Check ---")
    station = "Frankfurt (Main) Hauptbahnhof"
    print(f"Info for {station}:")
    print(assistant.get_station_accessibility(station))
    
    # Test Case 2: Routing
    print("\n--- Routing Check ---")
    start = "Frankfurt (Main) Hauptbahnhof"
    end = "Berlin Hauptbahnhof" 
    
    connections = assistant.find_direct_connections(start, end, time_string="08:00:00")
    
    if isinstance(connections, str):
        print(connections)
    elif connections.empty:
        print("No direct connections found.")
    else:
        print(f"Found {len(connections)} connections:")
        for _, row in connections.iterrows():
            print(f"[{row['route_short_name']}] Dep: {row['start_time']} -> Arr: {row['end_time']} (Headsign: {row['trip_headsign']})")

if __name__ == "__main__":
    main()
