from server.service.travel_service import TravelService
import json

def test_via():
    service = TravelService()
    
    print("Testing Munich -> Hamburg via Cologne (min transfer 180 mins)...")
    journeys = service.find_routes(
        "München Hbf", 
        "Hamburg Hbf", 
        "08:00", 
        via=["Köln Hbf"], 
        min_transfer_time=180
    )
    
    if not journeys:
        print("No journeys found!")
        return

    for i, journey in enumerate(journeys):
        print(f"\nJourney {i+1}:")
        for leg in journey.legs:
            print(f"  {leg.train.name}: {leg.origin.name} ({leg.departureTime}) -> {leg.destination.name} ({leg.arrivalTime})")
            
        # Verify transfer time
        if len(journey.legs) >= 2:
            arr1 = journey.legs[0].arrivalTime
            dep2 = journey.legs[1].departureTime
            
            h1, m1 = map(int, arr1.split(':')[:2])
            h2, m2 = map(int, dep2.split(':')[:2])
            
            min1 = h1 * 60 + m1
            min2 = h2 * 60 + m2
            
            diff = min2 - min1
            print(f"  Transfer time: {diff} minutes (Expected >= 180)")

if __name__ == "__main__":
    test_via()
