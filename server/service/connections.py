from server.service.journey_service import JourneyService
from server.models.connection_schema import ConnectionsRequest, ConnectionsResponse
from datetime import datetime

journey_service = JourneyService()

def get_connections(request: ConnectionsRequest) -> ConnectionsResponse:
    origin = request.origin
    destination = request.destination
    # Extract time from date or use current time
    # request.date is ISO format (YYYY-MM-DDTHH:MM:SS)
    if request.date:
        dt = datetime.fromisoformat(request.date)
        time_str = dt.strftime("%H:%M:%S")
    else:
        time_str = datetime.now().strftime("%H:%M:%S")
    
    journeys = journey_service.find_routes(origin, destination, time_str)
    
    return ConnectionsResponse(journeys=journeys)