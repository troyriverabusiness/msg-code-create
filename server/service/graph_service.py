import sqlite3
import networkx as nx
from pathlib import Path
from typing import List, Dict, Optional
import json
import os

DB_PATH = Path(__file__).parent.parent / "data" / "travel.db"
CACHE_PATH = Path(__file__).parent.parent / "data" / "graph_cache.json"
TOP_STATIONS_PATH = Path(__file__).parent.parent / "data" / "top_stations.json"

class GraphService:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.load_graph()

    def _get_conn(self):
        return sqlite3.connect(DB_PATH, check_same_thread=False)

    def load_graph(self):
        """
        Loads the graph from cache or builds it from the DB.
        """
        if CACHE_PATH.exists():
            print("Loading graph from cache...")
            try:
                with open(CACHE_PATH, "r") as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
                print(f"Graph loaded: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges.")
                return
            except Exception as e:
                print(f"Failed to load cache: {e}. Rebuilding...")

        self.build_graph()

    def build_graph(self):
        """
        Builds the graph from GTFS data.
        1. Loads top stations (nodes).
        2. Iterates through stop_times to find connections (edges).
        3. Caches the graph.
        """
        print("Building graph from database...")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Load Top Stations
        print("Loading top stations...")
        if not TOP_STATIONS_PATH.exists():
            print("Error: top_stations.json not found. Run calculate_connectivity.py first.")
            return

        with open(TOP_STATIONS_PATH, "r") as f:
            top_stations_list = json.load(f)
            
        stations = {s['id']: s for s in top_stations_list}
        
        # Add nodes to graph
        print("Fetching station coordinates...")
        placeholders = ','.join(['?'] * len(stations))
        cursor.execute(f"SELECT stop_id, stop_lat, stop_lon FROM stations WHERE stop_id IN ({placeholders})", list(stations.keys()))
        
        for row in cursor.fetchall():
            stop_id = row['stop_id']
            if stop_id in stations:
                self.graph.add_node(stop_id, name=stations[stop_id]['name'], pos=(row['stop_lon'], row['stop_lat']), score=stations[stop_id]['score'])

        print(f"Added {self.graph.number_of_nodes()} top stations to graph.")

        # 2. Build Stop Mapping (stop_id -> canonical_id)
        # We need to map every stop_id in the system to its parent (if it exists) so we can link trips to the top stations.
        print("Building stop mapping...")
        cursor.execute("SELECT stop_id, parent_station FROM stations")
        stop_map = {}
        for row in cursor:
            # If parent exists, use it. Else use stop_id.
            canonical = row['parent_station'] if row['parent_station'] else row['stop_id']
            stop_map[row['stop_id']] = canonical

        # 3. Find trips connecting these stations
        print("Fetching trip data...")
        
        chunk_size = 500000
        cursor.execute("SELECT count(*) FROM stop_times")
        total_rows = cursor.fetchone()[0]
        print(f"Processing {total_rows} stop_times entries...")
        
        cursor.execute("SELECT trip_id, stop_id, arrival_time, departure_time, stop_sequence FROM stop_times ORDER BY trip_id, stop_sequence")
        
        current_trip_id = None
        trip_stops = []
        
        count = 0
        while True:
            rows = cursor.fetchmany(chunk_size)
            if not rows:
                break
                
            for row in rows:
                trip_id = row['trip_id']
                
                if trip_id != current_trip_id:
                    # Process previous trip
                    if current_trip_id and len(trip_stops) >= 2:
                        self._add_trip_to_graph(trip_stops)
                    current_trip_id = trip_id
                    trip_stops = []
                
                # Map stop_id to canonical
                s_id = row['stop_id']
                canonical_id = stop_map.get(s_id, s_id)
                
                # Only add if it's a top station
                if canonical_id in stations:
                    trip_stops.append({
                        'stop_id': canonical_id,
                        'arrival_time': row['arrival_time'],
                        'departure_time': row['departure_time']
                    })
            
            count += len(rows)
            print(f"Processed {count}/{total_rows} rows...", end='\r')
            
        # Process last trip
        if current_trip_id and len(trip_stops) >= 2:
            self._add_trip_to_graph(trip_stops)
            
        print("\nGraph build complete.")
        print(f"Graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges.")
        
        # Save to cache
        self.save_cache()

    def _add_trip_to_graph(self, stops: List[Dict]):
        # stops is a list of dicts with stop_id (canonical), arrival_time, departure_time
        for i in range(len(stops) - 1):
            u = stops[i]
            v = stops[i+1]
            
            if u['stop_id'] == v['stop_id']:
                continue # Skip self-loops (e.g. platform change within same station)
                
            weight = self._calculate_duration(u['departure_time'], v['arrival_time'])
            
            # Add edge or update weight (min weight)
            if self.graph.has_edge(u['stop_id'], v['stop_id']):
                current_weight = self.graph[u['stop_id']][v['stop_id']]['weight']
                if weight < current_weight:
                    self.graph[u['stop_id']][v['stop_id']]['weight'] = weight
            else:
                self.graph.add_edge(u['stop_id'], v['stop_id'], weight=weight)

    def _calculate_duration(self, start_time_str: str, end_time_str: str) -> int:
        """Calculates duration in minutes, handling midnight crossing."""
        try:
            t1 = self._parse_time(start_time_str)
            t2 = self._parse_time(end_time_str)
            duration = t2 - t1
            if duration < 0:
                duration += 24 * 60 # Handle midnight crossing
            return duration
        except:
            return 30 # Default fallback

    def _parse_time(self, time_str: str) -> int:
        """Converts HH:MM:SS to minutes from midnight."""
        parts = time_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])

    def find_intermediate_stations(self, origin_name: str, destination_name: str) -> List[str]:
        """
        Finds interesting intermediate stations between origin and destination.
        """
        # 1. Resolve names to IDs
        origin_id = self._find_node_by_name(origin_name)
        dest_id = self._find_node_by_name(destination_name)
        
        if not origin_id or not dest_id:
            print(f"Could not resolve {origin_name} or {destination_name}")
            return []
            
        # 2. Find paths
        try:
            # Use shortest path on WEIGHT (time)
            # This avoids the "direct edge is shortest" issue if the direct train is actually slower (unlikely)
            # But if there is a direct ICE, it will be the shortest path.
            
            # We want to find "via" options.
            # Strategy: Find the shortest path. Then find paths that are slightly longer.
            # Or: Remove the direct edge and find shortest path?
            
            # 1. Shortest Path (Time)
            shortest_path = nx.shortest_path(self.graph, origin_id, dest_id, weight='weight')
            
            intermediates = set()
            if len(shortest_path) > 2:
                intermediates.update(shortest_path[1:-1])
                
            # 2. Alternative Paths (Time + 20%)
            # We use k_shortest_paths or similar. 
            # Simple approach: simple paths with cutoff is too slow/broad.
            # Better: shortest_simple_paths (returns generator)
            
            try:
                path_gen = nx.shortest_simple_paths(self.graph, origin_id, dest_id, weight='weight')
                
                # Get baseline duration
                baseline_duration = nx.path_weight(self.graph, shortest_path, weight='weight')
                max_duration = baseline_duration * 1.2 # 20% buffer
                
                count = 0
                for path in path_gen:
                    if count > 5: break # Limit to top 5 paths
                    
                    duration = nx.path_weight(self.graph, path, weight='weight')
                    if duration > max_duration:
                        break
                        
                    if len(path) > 2:
                        # Add major stations from this path
                        # Filter by score? Or just add all?
                        # Let's add all for now, the graph is already filtered to top stations.
                        intermediates.update(path[1:-1])
                    
                    count += 1
            except Exception as e:
                print(f"Pathfinding warning: {e}")
            
            # Convert back to names and sort by score
            results = []
            for stop_id in intermediates:
                node = self.graph.nodes[stop_id]
                results.append({
                    "name": node['name'],
                    "score": node.get('score', 0)
                })
            
            # Sort by score descending
            results.sort(key=lambda x: x['score'], reverse=True)
            
            return [r['name'] for r in results]
            
        except nx.NetworkXNoPath:
            return []

    def _find_node_by_name(self, name: str) -> Optional[str]:
        name_lower = name.lower().replace(" hbf", " hauptbahnhof").replace(" (main)", "")
        
        candidates = []
        for node, data in self.graph.nodes(data=True):
            node_name = data['name'].lower().replace(" hbf", " hauptbahnhof").replace(" (main)", "")
            if name_lower in node_name or node_name in name_lower:
                candidates.append(node)
        
        if not candidates:
            return None
            
        # Return the candidate with the highest degree (most connected)
        # This avoids picking a disconnected bus stop platform
        best_node = max(candidates, key=lambda n: self.graph.degree(n))
        return best_node

    def save_cache(self):
        # Convert sets to lists for JSON serialization
        data = nx.node_link_data(self.graph)
        print(f"Graph data keys: {data.keys()}")
        
        links_key = 'links' if 'links' in data else 'edges'
        if links_key in data:
            for link in data[links_key]:
                if 'lines' in link and isinstance(link['lines'], set):
                    link['lines'] = list(link['lines'])
        else:
            print("Warning: No links/edges found in graph data.")
        
        try:
            with open(CACHE_PATH, "w") as f:
                json.dump(data, f)
            print("Graph cached.")
        except Exception as e:
            print(f"Failed to cache graph: {e}")

if __name__ == "__main__":
    g = GraphService()
    
    print("Sample Stations:")
    for i, (node, data) in enumerate(g.graph.nodes(data=True)):
        if i < 10:
            print(f" - {data['name']}")
            
    print("\nTest: Frankfurt -> München")
    stops = g.find_intermediate_stations("Frankfurt (Main) Hbf", "München Hbf")
    print(stops)
