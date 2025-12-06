from server.service.connections import get_connections
from server.models.connection_schema import ConnectionsRequest

def test_hybrid_flow():
    print("Testing Hybrid Flow...")
    
    # Test Case: Frankfurt to Munich (Major Hubs)
    req = ConnectionsRequest(
        origin="Frankfurt (Main) Hbf",
        destination="München Hbf",
        date="2025-12-12T14:00:00"
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
        print(f" - Trains: {len(journey.trains)}")
        for train in journey.trains:
            print(f"   - {train.name}: {train.startLocation.name} -> {train.endLocation.name}")
            
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hybrid_flow()
