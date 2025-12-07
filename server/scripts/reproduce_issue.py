import sys
import os
import asyncio
from datetime import datetime

# Add parent directory to path to import server modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.service.travel_service import TravelService

async def reproduce():
    service = TravelService()
    
    origin = "Frankfurt Hauptbahnhof"
    destination = "Hamburg Hauptbahnhof"
    via = ["Köln Hauptbahnhof"]
    min_transfer_time = 180 # minutes
    time_str = "2025-12-07T08:00:00"
    
    print(f"Searching for routes: {origin} -> {destination} via {via} at {time_str} with min_transfer {min_transfer_time}m")
    
    try:
        routes = service.find_routes(
            start_name=origin,
            end_name=destination,
            time_str=time_str,
            via=via,
            min_transfer_time=min_transfer_time
        )
        
        print(f"Found {len(routes)} routes.")
        for i, route in enumerate(routes):
            print(f"Route {i+1}:")
            for leg in route.legs:
                print(f"  {leg.train.name} ({leg.origin.name} -> {leg.destination.name})")
                print(f"    Dep: {leg.departureTime}, Arr: {leg.arrivalTime}")
            print(f"  Total Duration: {route.totalTime} min")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reproduce())
