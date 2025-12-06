import sqlite3
import networkx as nx
from pathlib import Path
from typing import List, Dict, Optional
import json
import os

DB_PATH = Path(__file__).parent.parent / "data" / "travel.db"
CACHE_PATH = Path(__file__).parent.parent / "data" / "graph_cache.json"

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
        Builds a simplified graph of Hbf/Major stations.
        """
        print("Building graph from database...")
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Select Major Stations (Hbf)
        print("Fetching major stations...")
        cursor.execute("""
            SELECT stop_id, stop_name, stop_lat, stop_lon 
            FROM stations 
            WHERE stop_name LIKE '%Hbf%' OR stop_name LIKE '%Hauptbahnhof%'
        """)
        stations = {row['stop_id']: dict(row) for row in cursor.fetchall()}
        
        for stop_id, data in stations.items():
            self.graph.add_node(stop_id, name=data['stop_name'], pos=(data['stop_lon'], data['stop_lat']))

        print(f"Found {len(stations)} major stations.")

        # 2. Find trips connecting these stations
        # We want trips that visit at least 2 major stations.
        # This query gets all stop_times for major stations, ordered by trip and sequence.
        print("Fetching connections...")
        placeholders = ','.join(['?'] * len(stations))
        query = f"""
            SELECT st.trip_id, st.stop_id, st.stop_sequence, st.departure_time, r.route_short_name
            FROM stop_times st
            JOIN trips t ON st.trip_id = t.trip_id
            JOIN routes r ON t.route_id = r.route_id
            WHERE st.stop_id IN ({placeholders})
            ORDER BY st.trip_id, st.stop_sequence
        """
        
        # SQLite limit on variables is usually 999 or 32766. 1118 stations might be too many for IN clause.
        # Alternative: Filter in Python or use a temp table.
        # Given the hackathon nature, let's try to filter in SQL but if it fails, we iterate.
        # Actually, let's just select ALL stop_times for trips that have 'ICE', 'IC', 'EC', 'RE' in route name?
        # Or better: Just iterate over all trips that touch Hbfs.
        
        # Let's try a safer approach: 
        # Get all trips that have at least 2 stops in our station set.
        
        # Optimization: Create a set of Hbf IDs in python.
        hbf_ids = set(stations.keys())
        
        # Query all stop times is too big.
        # Let's use a subquery to find relevant trips first.
        
        # "SELECT trip_id FROM stop_times WHERE stop_id IN (...)" is still the same problem.
        
        # Workaround: Chunk the IDs.
        hbf_id_list = list(hbf_ids)
        chunk_size = 500
        relevant_trips = set()
        
        for i in range(0, len(hbf_id_list), chunk_size):
            chunk = hbf_id_list[i:i+chunk_size]
            ph = ','.join(['?'] * len(chunk))
            cursor.execute(f"SELECT DISTINCT trip_id FROM stop_times WHERE stop_id IN ({ph})", chunk)
            relevant_trips.update(row['trip_id'] for row in cursor.fetchall())
            
        print(f"Found {len(relevant_trips)} relevant trips.")
        
        # Now fetch stop times for these trips, but ONLY for the Hbf stations.
        # We can iterate trips or fetch in chunks.
        
        # Let's fetch all stop_times for these trips.
        # To avoid massive query, let's process in chunks of trips.
        trip_list = list(relevant_trips)
        
        edge_count = 0
        
        for i in range(0, len(trip_list), chunk_size):
            chunk = trip_list[i:i+chunk_size]
            ph = ','.join(['?'] * len(chunk))
            
            q = f"""
                SELECT st.trip_id, st.stop_id, st.stop_sequence, st.departure_time, r.route_short_name
                FROM stop_times st
                JOIN trips t ON st.trip_id = t.trip_id
                JOIN routes r ON t.route_id = r.route_id
                WHERE st.trip_id IN ({ph})
                ORDER BY st.trip_id, st.stop_sequence
            """
            cursor.execute(q, chunk)
            rows = cursor.fetchall()
            
            current_trip = None
            trip_stops = []
            
            for row in rows:
                if row['trip_id'] != current_trip:
                    # Process previous trip
                    if current_trip and len(trip_stops) > 1:
                        self._add_path_to_graph(trip_stops)
                    
                    current_trip = row['trip_id']
                    trip_stops = []
                
                if row['stop_id'] in hbf_ids:
                    trip_stops.append(row)
            
            # Process last trip
            if current_trip and len(trip_stops) > 1:
                self._add_path_to_graph(trip_stops)
                
        print(f"Graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges.")
        
        # Save to cache
        self.save_cache()

    def _add_path_to_graph(self, stops: List[sqlite3.Row]):
        """
        Adds edges between consecutive Hbf stops in a trip.
        """
        for i in range(len(stops) - 1):
            u = stops[i]
            v = stops[i+1]
            
            u_id = u['stop_id']
            v_id = v['stop_id']
            line = u['route_short_name']
            
            # Calculate weight (time difference)
            try:
                t1 = self._parse_time(u['departure_time'])
                t2 = self._parse_time(v['departure_time'])
                duration = t2 - t1
                if duration < 0: duration += 24 * 60 # Handle midnight crossing roughly
            except:
                duration = 30 # Default fallback
            
            if self.graph.has_edge(u_id, v_id):
                # Update existing edge
                data = self.graph[u_id][v_id]
                data['lines'].add(line)
                # Keep the minimum duration
                if duration < data['weight']:
                    data['weight'] = duration
            else:
                self.graph.add_edge(u_id, v_id, lines={line}, weight=duration)

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
            
            # Let's get the shortest weighted path first.
            shortest_path = nx.shortest_path(self.graph, origin_id, dest_id, weight='weight')
            
            intermediates = set()
            if len(shortest_path) > 2:
                intermediates.update(shortest_path[1:-1])
                
            # Also try to find paths that are "hops" (ignoring weight) to see topological intermediates
            # Limit to length 3 or 4 to avoid explosion
            simple_paths = list(nx.all_simple_paths(self.graph, origin_id, dest_id, cutoff=3))
            for path in simple_paths:
                if len(path) > 2:
                    intermediates.update(path[1:-1])
            
            # Convert back to names
            results = []
            for stop_id in intermediates:
                name = self.graph.nodes[stop_id]['name']
                results.append(name)
                
            return list(results)
            
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
