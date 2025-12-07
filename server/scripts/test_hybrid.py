from server.service.connections import get_connections
from server.models.connection_schema import ConnectionsRequest

def test_hybrid_flow():
    print("Testing Hybrid Flow...")
    
    # Test Case: Hainichen to Niederwiesa (Known Route)
    req = ConnectionsRequest(
        origin="Hainichen, Bahnhof",
        destination="Niederwiesa",
        date="2025-12-12T04:30:00"
    )
    
    print(f"Request: {req.origin} -> {req.destination} at {req.date}")
    
    try:
        response = get_connections(req)
        
        if not response.journeys:
            print("FAILED: No journeys found.")
            return
            
        journey = response.journeys[0]
        print(f"SUCCESS: Found journey {journey.id}")
        print(f" - Start: {journey.startStation.name}")
        print(f" - End: {journey.endStation.name}")
        print(f" - Legs: {len(journey.legs)}")
        for leg in journey.legs:
            print(f"   - {leg.train.name}: {leg.origin.name} -> {leg.destination.name} (Delay: {leg.delayInMinutes} min, Path: {len(leg.train.path)} stops)")
            if leg.train.path:
                first_stop = leg.train.path[0]
                print(f"     First stop: {first_stop.station.name} (Arr: {first_stop.arrivalTime}, Dep: {first_stop.departureTime}, Pl: {first_stop.platform})")
            
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hybrid_flow()
