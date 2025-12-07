from server.service.journey_service import JourneyService
from server.models.API import ConnectionsRequest, ConnectionsResponse
from datetime import datetime

journey_service = JourneyService()

def get_connections(request: ConnectionsRequest) -> ConnectionsResponse:
    origin = request.start
    destination = request.end
    
    # Extract time from date or use current time
    if request.departure_time:
        time_str = request.departure_time.strftime("%H:%M:%S")
    else:
        time_str = datetime.now().strftime("%H:%M:%S")
    
    journeys = journey_service.find_routes(origin, destination, time_str, request.via, request.min_transfer_time)
    
    return ConnectionsResponse(journeys=journeys)
