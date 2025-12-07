
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from server.service.travel_service import TravelService

def test_duplicates():
    service = TravelService()
    print("Searching for routes from Frankfurt to Munich...")
    
    # Use the name that works in DB
    start = "Frankfurt (Main) Hauptbahnhof" 
    end = "München Hbf"
    time = "10:00:00"
    
    start_ids = service.get_all_station_ids(start)
    end_ids = service.get_all_station_ids(end)
    print(f"Start IDs for '{start}': {start_ids}")
    if 'de:06412:10:14:4' in start_ids:
        print("FOUND de:06412:10:14:4 in start_ids")
    else:
        print("MISSING de:06412:10:14:4 in start_ids")
    print(f"End IDs for '{end}': {end_ids}")
    
    journeys = service.find_routes(start, end, time)
    
    print(f"Found {len(journeys)} journeys:")
    for j in journeys:
        leg = j.legs[0]
        print(f"  {leg.train.name} ({leg.train.trainNumber}): {leg.departureTime} -> {leg.arrivalTime}")

if __name__ == "__main__":
    test_duplicates()
