from typing import List, Optional
from datetime import datetime, timedelta
from ..models import Journey, Leg, Station
from .travel_service import TravelService
from .graph_service import GraphService
import uuid

class JourneyService:
    def __init__(self):
        self.travel_service = TravelService()
        self.graph_service = GraphService()

    def find_routes(self, origin: str, destination: str, time: str) -> List[Journey]:
        journeys = []
        
        # 1. Try Direct Connection
        direct_legs = self.travel_service.find_segment(origin, destination, time)
        for leg in direct_legs:
            journeys.append(self._create_journey([leg]))
            
        # 2. Try 1-Transfer Connections
        # Get intermediate candidates
        candidates = self.graph_service.find_intermediate_stations(origin, destination)
        
        # Limit candidates to avoid explosion
        candidates = candidates[:3] 
        
        for transfer_station in candidates:
            # Leg 1: Origin -> Transfer
            leg1_options = self.travel_service.find_segment(origin, transfer_station, time)
            
            for l1 in leg1_options:
                # Calculate arrival at transfer + buffer (e.g. 5 mins)
                try:
                    arrival_dt = self._parse_time(l1.arrivalTime)
                    min_departure_dt = arrival_dt + timedelta(minutes=5)
                    min_departure_str = min_departure_dt.strftime("%H:%M:%S")
                    
                    # Leg 2: Transfer -> Destination
                    leg2_options = self.travel_service.find_segment(transfer_station, destination, min_departure_str)
                    
                    for l2 in leg2_options:
                        # Create Journey
                        # TODO: Propagate delays.
                        # If l1 has delay, l1.arrivalTime increases.
                        # min_departure_dt must be calculated from REAL arrival time.
                        
                        # Update legs with delay info
                        # We already have delay from TravelService (populated in find_segment)
                        # But we might want to refresh it or just use it.
                        # Since find_segment calls simulation, l1.delayInMinutes and l2.delayInMinutes should be set.
                        
                        delay1 = l1.delayInMinutes
                        delay2 = l2.delayInMinutes
                        
                        real_arrival_l1 = arrival_dt + timedelta(minutes=delay1)
                        real_departure_l2 = self._parse_time(l2.departureTime) + timedelta(minutes=delay2)
                        
                        # Check if transfer is still possible (e.g. 5 min buffer)
                        if real_departure_l2 < real_arrival_l1 + timedelta(minutes=5):
                            continue # Transfer broken by delay
                            
                        journeys.append(self._create_journey([l1, l2]))
                except Exception as e:
                    # print(f"Error processing transfer at {transfer_station}: {e}")
                    continue
                    
        # Sort by total time
        journeys.sort(key=lambda j: j.totalTime)
        
        return journeys[:10] # Return top 10

    def _create_journey(self, legs: List[Leg]) -> Journey:
        start = legs[0].origin
        end = legs[-1].destination
        
        # Calculate total time
        start_dt = self._parse_time(legs[0].departureTime)
        end_dt = self._parse_time(legs[-1].arrivalTime)
        
        # Handle midnight crossing for duration calculation if not already handled by _parse_time days
        # But _parse_time uses dummy date (1900-01-01), so if end_dt < start_dt it means next day
        # However, our new _parse_time handles >24h.
        
        if end_dt < start_dt:
             end_dt += timedelta(days=1)
             
        duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
        
        journey = Journey(
            id=str(uuid.uuid4()),
            startStation=start,
            endStation=end,
            legs=legs,
            transfers=len(legs) - 1,
            totalTime=duration_minutes,
            description=f"{len(legs)-1} Transfers" if len(legs) > 1 else "Direct"
        )
        
        journey.aiInsight = self._generate_ai_insight(journey)
        return journey

    def _parse_time(self, time_str: str) -> datetime:
        """
        Parses HH:MM:SS, handling hours >= 24.
        Returns a datetime object (using today as base date, or tomorrow/etc for >24h).
        """
        parts = time_str.split(':')
        h = int(parts[0])
        m = int(parts[1])
        s = int(parts[2]) if len(parts) > 2 else 0
        
        days_delta = 0
        if h >= 24:
            days_delta = h // 24
            h = h % 24
            
        dt = datetime.strptime(f"{h:02d}:{m:02d}:{s:02d}", "%H:%M:%S")
        return dt + timedelta(days=days_delta)

    def _generate_ai_insight(self, journey: Journey) -> str:
        """
        Simulates an AI evaluation of the journey.
        """
        reasons = []
        
        # 1. Punctuality
        max_delay = 0
        for leg in journey.legs:
            if leg.delayInMinutes > max_delay:
                max_delay = leg.delayInMinutes
        
        if max_delay == 0:
            reasons.append("Typically very punctual.")
        elif max_delay < 5:
            reasons.append("Usually on time with minor fluctuations.")
        elif max_delay < 15:
            reasons.append("Moderate delays expected on this route.")
        else:
            reasons.append("High risk of delay, plan accordingly.")

        # 2. Transfers
        if journey.transfers == 0:
            reasons.append("Direct connection - most relaxed option.")
        elif journey.transfers == 1:
            reasons.append("Single transfer required.")
            
        # 3. Crowd / Comfort (Simulated)
        train_types = [leg.train.name for leg in journey.legs]
        if any("ICE" in t for t in train_types):
            reasons.append("High-speed comfort with ICE.")
        
        return "AI Analysis: " + " ".join(reasons)
