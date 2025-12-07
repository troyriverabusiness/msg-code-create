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

    def find_routes(self, origin: str, destination: str, time: str, via: List[str] = None, min_transfer_time: int = 0) -> List[Journey]:
        journeys = []
        
        # If via is provided, use TravelService's via logic directly
        # If via is provided, use TravelService's via logic directly
        if via and len(via) > 0:
            # Note: TravelService expects a list of via stations
            journeys = self.travel_service.find_routes(origin, destination, time, via=via, min_transfer_time=min_transfer_time)
        else:
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
        
        top_journeys = journeys[:10]
        
        # Generate AI Insights ONLY for the top 3 to save time/cost
        print(f"Generating AI insights for top {min(3, len(top_journeys))} journeys...")
        for i in range(min(3, len(top_journeys))):
            top_journeys[i].aiInsight = self._generate_ai_insight(top_journeys[i])
            
        return top_journeys

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
        
        # journey.aiInsight = self._generate_ai_insight(journey) # Moved to find_routes for performance
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
        Generates a real AI evaluation of the journey using Bedrock.
        """
        try:
            # 1. Prepare Journey Data for Prompt
            legs_info = []
            risk_analysis = []
            
            for i, leg in enumerate(journey.legs):
                hist_delay = self.travel_service.get_historical_delay(leg.train.trainNumber)
                delay_info = f"(Current Delay: {leg.delayInMinutes} min)"
                if hist_delay is not None:
                    delay_info += f" [Historical Avg: {hist_delay:.1f} min]"
                
                legs_info.append(f"- Leg {i+1}: {leg.train.name} ({leg.origin.name} -> {leg.destination.name}) {delay_info}")
                
                # Analyze Transfer Risk (if not last leg)
                if i < len(journey.legs) - 1:
                    next_leg = journey.legs[i+1]
                    
                    # Calculate scheduled transfer time
                    try:
                        arr = self._parse_time(leg.arrivalTime)
                        dep = self._parse_time(next_leg.departureTime)
                        if dep < arr:
                            dep += timedelta(days=1)
                        transfer_min = int((dep - arr).total_seconds() / 60)
                        
                        risk_msg = f"Transfer at {leg.destination.name}: {transfer_min} min available."
                        
                        if hist_delay and hist_delay > (transfer_min - 5):
                            risk_msg += f" WARNING: Incoming train has avg delay of {hist_delay:.1f} min, making this transfer VERY RISKY."
                        elif hist_delay and hist_delay > 5:
                            risk_msg += f" CAUTION: Incoming train has avg delay of {hist_delay:.1f} min."
                        else:
                            risk_msg += " Safe transfer."
                            
                        risk_analysis.append(risk_msg)
                    except:
                        pass

            legs_str = "\n".join(legs_info)
            risk_str = "\n".join(risk_analysis)
            
            prompt = f"""
            Analyze this train journey and provide a concise, data-driven insight (max 2 sentences).
            
            Journey Details:
            - Total Time: {journey.totalTime} min
            - Transfers: {journey.transfers}
            - Legs:
            {legs_str}
            
            Transfer Analysis:
            {risk_str}
            
            INSTRUCTIONS:
            1. Use the "Historical Avg" data to predict likely delays.
            2. If a transfer is risky based on historical data, EXPLICITLY warn the user (e.g., "High risk of missing connection at Köln due to typical delays of 26min").
            3. If the route is historically punctual, mention it as a "reliable connection".
            4. Do NOT be generic. Use the numbers provided.
            
            Output ONLY the insight text.
            """
            
            # 2. Call Bedrock
            # We use a fresh instance or a shared one. For now, creating a fresh one is safer for statelessness,
            # but less efficient. Ideally, inject it.
            from ..data_access.AWS.bedrock_service import BedrockService
            from ..data_access.AWS.config import AWS_ACCESS_KEY, AWS_SECRET, AWS_REGION
            
            bedrock = BedrockService(aws_access_key=AWS_ACCESS_KEY, aws_secret_key=AWS_SECRET, region=AWS_REGION)
            
            # We use send_journey_prompt which returns a dict
            response = bedrock.send_journey_prompt(message=prompt, system_prompt="You are a helpful travel assistant.")
            
            return response["text"]
            
        except Exception as e:
            print(f"AI Insight Generation Failed: {e}")
            return "AI Analysis unavailable."
