import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import gc

# Path to the GTFS data
DATA_DIR = Path("../datachaos/20251201_fahrplaene_gesamtdeutschland_gtfs")
OUTPUT_FILE = Path("gtfs_dashboard.html")

def load_basic_files():
    print("Loading basic GTFS files...")
    agencies = pd.read_csv(DATA_DIR / "agency.txt")
    routes = pd.read_csv(DATA_DIR / "routes.txt")
    stops = pd.read_csv(DATA_DIR / "stops.txt", usecols=['stop_id', 'stop_name', 'stop_lat', 'stop_lon'])
    return agencies, routes, stops

def get_busiest_stops(stops_df, valid_trip_ids=None, top_n=20):
    print("Analyzing stop_times.txt for busiest stops (this may take a moment)...")
    stop_times_path = DATA_DIR / "stop_times.txt"
    
    # Process in chunks to handle 3GB file safely
    chunksize = 5_000_000
    stop_counts = pd.Series(dtype=int)
    
    # optimize: convert valid_trip_ids to set for O(1) lookup if provided
    if valid_trip_ids is not None and not isinstance(valid_trip_ids, set):
        valid_trip_ids = set(valid_trip_ids)
    
    for chunk in pd.read_csv(stop_times_path, usecols=['trip_id', 'stop_id'], chunksize=chunksize):
        if valid_trip_ids is not None:
            # Filter chunk by trip_id
            chunk = chunk[chunk['trip_id'].isin(valid_trip_ids)]
        
        counts = chunk['stop_id'].value_counts()
        stop_counts = stop_counts.add(counts, fill_value=0)
        print(f"Processed {chunksize} rows...")
    
    print("Finished processing stop_times.")
    
    # Get top N
    top_stops = stop_counts.sort_values(ascending=False).head(top_n)
    top_stops_df = top_stops.reset_index()
    top_stops_df.columns = ['stop_id', 'stop_count']
    
    # Join with stop names
    result = pd.merge(top_stops_df, stops_df, on='stop_id', how='left')
    return result

def create_dashboard():
    agencies, routes, stops = load_basic_files()
    
    # FILTER: Focus on Trains (ICE, IC, RE, RB, S-Bahn)
    # 100: Railway Service
    # 101: High Speed Rail (ICE)
    # 102: Long Distance Trains (IC/EC)
    # 106: Regional Rail (RE/RB)
    # 109: Suburban Railway (S-Bahn)
    train_types = [100, 101, 102, 106, 109]
    routes = routes[routes['route_type'].isin(train_types)]
    print(f"Filtered to {len(routes)} train routes.")

    # Filter stops to only those used by these routes
    print("Loading trips to filter for train connections...")
    trips = pd.read_csv(DATA_DIR / "trips.txt", usecols=['route_id', 'trip_id'])
    
    # Filter trips by valid routes
    valid_route_ids = set(routes['route_id'])
    train_trips = trips[trips['route_id'].isin(valid_route_ids)]
    valid_trip_ids = set(train_trips['trip_id'])
    print(f"Found {len(valid_trip_ids)} trips for the selected train routes.")
    
    del trips
    gc.collect()

    # 1. Route Type Distribution
    route_type_map = {
        100: 'Railway Service', 
        101: 'High Speed Rail (ICE)', 
        102: 'Long Distance (IC/EC)', 
        106: 'Regional Rail (RE/RB)', 
        109: 'S-Bahn'
    }
    routes['type_name'] = routes['route_type'].map(lambda x: route_type_map.get(x, f"Type {x}"))
    route_counts = routes['type_name'].value_counts().reset_index()
    route_counts.columns = ['Type', 'Count']
    
    fig_routes = px.pie(route_counts, values='Count', names='Type', 
                        title='Distribution of Train Types (ICE, IC, RE, RB, S-Bahn)',
                        color='Type',
                        color_discrete_map={
                            'High Speed Rail (ICE)': '#EF4444', # Red
                            'Long Distance (IC/EC)': '#F59E0B', # Amber
                            'Regional Rail (RE/RB)': '#10B981', # Green
                            'S-Bahn': '#3B82F6', # Blue
                            'Railway Service': '#6B7280' # Gray
                        })
    
    # 2. Top Agencies by Route Count
    agency_route_counts = routes['agency_id'].value_counts().reset_index()
    agency_route_counts.columns = ['agency_id', 'route_count']
    agency_route_counts = pd.merge(agency_route_counts, agencies[['agency_id', 'agency_name']], on='agency_id', how='left')
    top_agencies = agency_route_counts.head(15)
    
    fig_agencies = px.bar(top_agencies, x='route_count', y='agency_name', orientation='h', 
                          title='Top 15 Train Operators',
                          labels={'route_count': 'Number of Routes', 'agency_name': 'Agency'})
    fig_agencies.update_layout(yaxis={'categoryorder':'total ascending'})

    # 3. Busiest Stops (Filtered for Trains)
    busiest_stops = get_busiest_stops(stops, valid_trip_ids=valid_trip_ids, top_n=20)
    
    fig_stops = px.bar(busiest_stops, x='stop_count', y='stop_name', orientation='h',
                       title='Top 20 Busiest Train Stations',
                       labels={'stop_count': 'Total Departures/Arrivals', 'stop_name': 'Station'},
                       hover_data=['stop_id'])
    fig_stops.update_layout(yaxis={'categoryorder':'total ascending'})

    # 4. Map of Busiest Stops
    fig_map = px.scatter_mapbox(busiest_stops, lat="stop_lat", lon="stop_lon", hover_name="stop_name",
                                hover_data=["stop_count"],
                                color_discrete_sequence=["#EF4444"], zoom=5, height=600,
                                size="stop_count", size_max=30,
                                title="Map of Top 20 Busiest Train Stations")
    fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

    # Combine into HTML
    print("Generating HTML report...")
    with open(OUTPUT_FILE, 'w') as f:
        f.write("<html><head><title>German Train Network Analysis</title></head><body>")
        f.write("<h1 style='font-family:sans-serif; text-align:center;'>German Train Network Analysis (ICE/IC + RE/RB)</h1>")
        f.write(fig_routes.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(fig_agencies.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(fig_stops.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(fig_map.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write("</body></html>")
    
    print(f"Dashboard saved to {OUTPUT_FILE.resolve()}")

if __name__ == "__main__":
    create_dashboard()
