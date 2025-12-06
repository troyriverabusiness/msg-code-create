import networkx as nx
from datetime import datetime
from server.service.graph_service import GraphService
from server.service.linker_service import LinkerService
from server.models.journey import Journey, Station, Train, StationChange
from server.models.connection_schema import ConnectionsRequest, ConnectionsResponse

graph_service = GraphService()
linker_service = LinkerService()

def get_connections_example(request: ConnectionsRequest) -> ConnectionsResponse:
    # TODO: Implement actual connection logic
    return ConnectionsResponse(journeys=[journey_examples.journey1, journey_examples.journey2])


def get_connections(request: ConnectionsRequest) -> ConnectionsResponse:
    origin = request.origin
    destination = request.destination
    date = datetime.fromisoformat(request.date) if request.date else datetime.now()
    
    # 1. Find Intermediate Stations / Path
    # For MVP, we just find one path for now.
    # In reality, we'd find multiple paths.
    
    # We use find_intermediate_stations to get a list of station names on the path
    # But we actually need the full path to find trips.
    # GraphService needs a method to return the path segments.
    # For now, let's assume find_intermediate_stations returns names, and we try to find direct trips between them.
    
    # Actually, GraphService.find_intermediate_stations returns names of STOPOVERS.
    # We need the full sequence of transfers.
    
    # Let's simplify:
    # 1. Ask GraphService for a path (list of station IDs/Names)
    # 2. For each segment (A -> B), ask LinkerService for a trip.
    
    # We need to expose a "get_path" method in GraphService or use the graph directly.
    # Let's use the graph directly since we are in the same process.
    
    origin_id = graph_service._find_node_by_name(origin)
    dest_id = graph_service._find_node_by_name(destination)
    
    print(f"DEBUG: Origin: {origin} -> {origin_id}")
    print(f"DEBUG: Dest: {destination} -> {dest_id}")
    
    if not origin_id or not dest_id:
        print("DEBUG: Failed to resolve stations")
        return ConnectionsResponse(journeys=[])
        
    try:
        path = nx.shortest_path(graph_service.graph, origin_id, dest_id, weight='weight')
        print(f"DEBUG: Path found: {len(path)} nodes")
    except Exception as e:
        print(f"DEBUG: Pathfinding failed: {e}")
        return ConnectionsResponse(journeys=[])
        
    # Now we have a path of station IDs: [Frankfurt, Fulda, Kassel, ...]
    # We need to find trips that cover these segments.
    # This is the "Routing" part which is complex.
    # For the Hackathon, we might just look for direct trips between major hops?
    
    # Let's try to find a trip from Start to End.
    # If not, try Start -> Middle -> End.
    
    # Simplified Logic:
    # Just return a dummy journey that follows the path, with "Simulated" trains.
    # We use LinkerService to find *any* train for the segments if possible.
    
    # TODO: Real implementation needs a proper routing algorithm (CSA/Raptor).
    # For now, we construct a single Journey object based on the graph path.
    
    # Placeholder variables for the new Journey constructor
    trains = [] # This will be populated in the loop below
    changes = [] # This will be populated in the loop below
    total_duration = 120 # Placeholder for now
    
    journey = Journey(
        id="j_1",
        startStation=Station(name=origin, eva=origin_id),
        endStation=Station(name=destination, eva=dest_id),
        trains=trains,
        changes=changes,
        totalTime=total_duration,
        description=f"Hybrid route via {len(changes)} transfers."
    )
    
    # Construct segments
    # This is a placeholder loop
    current_time_str = date.strftime("%H:%M:%S")
    
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        u_name = graph_service.graph.nodes[u]['name']
        v_name = graph_service.graph.nodes[v]['name']
        
        # Find real trips
        trips = linker_service.find_trips(u, v, request.date, current_time_str)
        
        if not trips:
            print(f"DEBUG: No trips found between {u_name} and {v_name} after {current_time_str}")
            # For now, abort if any segment fails. 
            # In future, we could try to find alternative paths or use simulation.
            return ConnectionsResponse(journeys=[])
            
        # Pick the first one for now (greedy approach)
        best_trip = trips[0]
        
        train = Train(
            name=f"Trip {best_trip['trip_id']}", # We don't have train number yet
            trainNumber=best_trip['trip_id'],
            startLocation=Station(name=u_name, eva=u),
            endLocation=Station(name=v_name, eva=v),
            departureTime=best_trip['departure_time'],
            arrivalTime=best_trip['arrival_time'],
            type="ICE", # Placeholder
            platform=int(best_trip.get('origin_platform', 1)),
            wagons=[],
            path=[]
        )
        journey.trains.append(train)
        
        # Update current time for next segment with 5 minute buffer
        # Parse arrival time
        fmt = "%H:%M:%S"
        arrival_dt = datetime.strptime(best_trip['arrival_time'], fmt)
        # Add 5 minutes
        from datetime import timedelta
        next_min_time = arrival_dt + timedelta(minutes=5)
        current_time_str = next_min_time.strftime(fmt)
        
        # Add transfer if not first segment
        if i > 0:
            prev_arrival = journey.trains[-2].arrivalTime
            curr_departure = train.departureTime
            
            # Calculate difference in minutes
            t1 = datetime.strptime(prev_arrival, fmt)
            t2 = datetime.strptime(curr_departure, fmt)
            diff_minutes = int((t2 - t1).total_seconds() / 60)
            
            journey.changes.append(StationChange(
                station=Station(name=u_name, eva=u),
                timeMinutes=diff_minutes,
                arrivalTime=prev_arrival,
                departureTime=curr_departure,
                platform=str(train.platform)
            ))
        
    return ConnectionsResponse(journeys=[journey])