from datetime import datetime, timedelta
from typing import List, Optional

from server.examples import journey_examples
from server.models.API import ConnectionsRequest, ConnectionsResponse
from server.models.train import Train
from server.models.station import Station
from server.data_access.DB.timetable_service import TimetableService
from server.service.filter_stations import filter_stations, find_station_by_name
from server.service.filter_journeys import find_possible_journeys


# Initialize the timetable service
timetable_service = TimetableService()


def get_connections_example(request: ConnectionsRequest) -> ConnectionsResponse:
    """Get connections example - returns mock data."""
    return ConnectionsResponse(
        journeys=[journey_examples.journey1, journey_examples.journey2]
    )


def get_connections(
    request: ConnectionsRequest, departure_time: Optional[datetime] = None
) -> ConnectionsResponse:
    """
    Get real connections between start and end stations.

    This function:
    1. Finds relevant stations between start and end using the rail network graph
    2. Queries the Deutsche Bahn API for train data at each station
    3. Finds possible journeys (direct or with changes) between the stations
    4. Returns a list of journey options sorted by travel time

    Args:
        request: The connection request containing start and end station names
        departure_time: Optional departure time (defaults to now)

    Returns:
        ConnectionsResponse containing a list of possible journeys
    """
    if departure_time is None:
        departure_time = datetime.now()

    # Step 1: Find the start and end stations
    start_station = find_station_by_name(request.start)
    end_station = find_station_by_name(request.end)

    if not start_station:
        print(f"Could not find start station: {request.start}")
        return ConnectionsResponse(journeys=[])

    if not end_station:
        print(f"Could not find end station: {request.end}")
        return ConnectionsResponse(journeys=[])

    print(f"Finding connections from {start_station.name} to {end_station.name}")

    # Step 2: Get list of possible stations between start and end
    stations = filter_stations(request.start, request.end)

    if not stations:
        print("No stations found on route")
        return ConnectionsResponse(journeys=[])

    print(f"Found {len(stations)} relevant stations on possible routes")

    # Step 3: Get list of all trains at these stations
    all_trains: List[Train] = []

    for station in stations:
        print(f"Fetching trains for {station.name} (EVA: {station.eva})")

        # Get trains for the current hour and next hour
        trains_current = timetable_service.get_trains_for_station(
            station, departure_time, include_arrivals=True, include_departures=True
        )

        # Also get trains for the next hour
        next_hour = departure_time.replace(minute=0, second=0) + timedelta(hours=1)
        trains_next = timetable_service.get_trains_for_station(
            station, next_hour, include_arrivals=True, include_departures=True
        )

        all_trains.extend(trains_current)
        all_trains.extend(trains_next)

        print(f"  Found {len(trains_current) + len(trains_next)} trains")

    # Remove duplicate trains (same train ID)
    seen_ids = set()
    unique_trains = []
    for train in all_trains:
        if train.trainId and train.trainId not in seen_ids:
            seen_ids.add(train.trainId)
            unique_trains.append(train)
        elif not train.trainId:
            unique_trains.append(train)

    all_trains = unique_trains
    print(f"Total unique trains collected: {len(all_trains)}")

    # Step 4: Filter out trains and build possible journeys
    journeys = find_possible_journeys(
        all_trains, start_station, end_station, departure_time
    )

    print(f"Found {len(journeys)} possible journeys")

    # Limit to top 10 journeys
    journeys = journeys[:10]

    return ConnectionsResponse(journeys=journeys)


def get_connections_for_time_range(
    request: ConnectionsRequest, start_time: datetime, end_time: datetime
) -> ConnectionsResponse:
    """
    Get connections within a specific time range.

    Useful for finding all possible journeys within a time window.
    """
    all_journeys = []
    current_time = start_time

    while current_time < end_time:
        response = get_connections(request, current_time)
        all_journeys.extend(response.journeys)
        current_time += timedelta(hours=1)

    # Deduplicate by train combination
    seen = set()
    unique_journeys = []
    for journey in all_journeys:
        key = "-".join(t.trainNumber for t in journey.trains)
        if key not in seen:
            seen.add(key)
            unique_journeys.append(journey)

    unique_journeys.sort(key=lambda j: j.totalTime)

    return ConnectionsResponse(journeys=unique_journeys[:20])
