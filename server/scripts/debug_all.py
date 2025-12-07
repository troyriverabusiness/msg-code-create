
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from server.service.travel_service import TravelService
from server.service.journey_service import JourneyService

def test_deduplication():
    print("\n--- Testing Deduplication (find_segment) ---")
    service = TravelService()
    start = "Frankfurt (Main) Hauptbahnhof"
    end = "München Hbf"
    time = "10:50:00"
    
    legs = service.find_segment(start, end, time)
    print(f"Found {len(legs)} legs:")
    for l in legs:
        print(f"  {l.train.name} ({l.train.trainNumber}): {l.departureTime} -> {l.arrivalTime}")

def test_via_routing():
    print("\n--- Testing Via Routing (JourneyService) ---")
    service = JourneyService()
    start = "Frankfurt (Main) Hauptbahnhof"
    end = "München Hbf"
    via = "Stuttgart Hbf"
    time = "08:00:00"
    
    journeys = service.find_routes(start, end, time, via=via, min_transfer_time=20)
    print(f"Found {len(journeys)} journeys via {via}:")
    for j in journeys:
        print(f"  Journey: {j.description} ({j.totalTime} min)")
        for leg in j.legs:
            print(f"    - {leg.train.name}: {leg.origin.name} (Pl. {leg.departurePlatform}) -> {leg.destination.name} (Pl. {leg.arrivalPlatform}) ({leg.departureTime}-{leg.arrivalTime})")
            for stop in leg.train.path:
                print(f"      * Stop: {stop.station.name} (Arr: {stop.arrivalTime}, Dep: {stop.departureTime})")

def check_early_trains():
    print("\n--- Checking Early Trains (08:00 - 10:00) ---")
    service = TravelService()
    start = "Frankfurt (Main) Hauptbahnhof"
    end = "München Hbf"
    time = "08:00:00"
    
    legs = service.find_segment(start, end, time)
    print(f"Found {len(legs)} legs starting from {time}:")
    for l in legs:
        print(f"  {l.train.name} ({l.train.trainNumber}): {l.departureTime} -> {l.arrivalTime}")

if __name__ == "__main__":
    # test_deduplication()
    test_via_routing()
    # check_early_trains()
