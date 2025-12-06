from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict

from server.models.train import Train
from server.models.journey import Journey
from server.models.station import Station
from server.models.station_change import StationChange


# Minimum transfer time between trains (in minutes)
MIN_TRANSFER_TIME = 5

# Maximum transfer time - if longer, it's not a reasonable connection
MAX_TRANSFER_TIME = 120

# Maximum number of changes allowed in a journey
MAX_CHANGES = 3


def find_possible_journeys(
    all_trains: List[Train],
    start_station: Station,
    end_station: Station,
    departure_time: Optional[datetime] = None,
) -> List[Journey]:
    """
    Find all possible journeys from start to end using the given trains.

    This algorithm:
    1. Groups trains by their train number (e.g., "ICE 920")
    2. Finds direct trains that go from start to end
    3. Finds connecting journeys where you change trains at intermediate stations
    4. Filters for valid connections (arrival time + transfer time < departure time)

    Args:
        all_trains: List of all trains from all relevant stations
        start_station: The origin station
        end_station: The destination station
        departure_time: Minimum departure time (defaults to now)

    Returns:
        List of Journey objects sorted by total travel time
    """
    if departure_time is None:
        departure_time = datetime.now()

    # Group trains by train number for easier lookup
    trains_by_number = _group_trains_by_number(all_trains)

    # Index trains by departure station for connection finding
    trains_by_departure_station = _index_trains_by_departure_station(all_trains)

    journeys: List[Journey] = []

    # Find direct journeys first
    direct_journeys = _find_direct_journeys(
        all_trains, start_station, end_station, departure_time
    )
    journeys.extend(direct_journeys)

    # Find journeys with one change
    one_change_journeys = _find_journeys_with_changes(
        all_trains,
        trains_by_departure_station,
        start_station,
        end_station,
        departure_time,
        max_changes=1,
    )
    journeys.extend(one_change_journeys)

    # Find journeys with two changes (if needed)
    if len(journeys) < 5:
        two_change_journeys = _find_journeys_with_changes(
            all_trains,
            trains_by_departure_station,
            start_station,
            end_station,
            departure_time,
            max_changes=2,
        )
        journeys.extend(two_change_journeys)

    # Remove duplicates and sort by total time
    journeys = _deduplicate_journeys(journeys)
    journeys.sort(key=lambda j: j.totalTime)

    return journeys


def _group_trains_by_number(trains: List[Train]) -> Dict[str, List[Train]]:
    """Group trains by their train number."""
    grouped: Dict[str, List[Train]] = defaultdict(list)
    for train in trains:
        grouped[train.trainNumber].append(train)
    return grouped


def _index_trains_by_departure_station(trains: List[Train]) -> Dict[str, List[Train]]:
    """Index trains by their departure station name (lowercased for matching)."""
    indexed: Dict[str, List[Train]] = defaultdict(list)
    for train in trains:
        key = train.startLocation.name.lower()
        indexed[key].append(train)

        # Also index by stations in the path where this train could be boarded
        # (but this would require knowing arrival times at each station)
    return indexed


def _station_matches(station1: Station, station2: Station) -> bool:
    """Check if two stations refer to the same location."""
    # If EVA numbers are available and non-zero, compare them
    if station1.eva > 0 and station2.eva > 0:
        return station1.eva == station2.eva

    # Otherwise compare names (case-insensitive, partial match)
    name1 = station1.name.lower()
    name2 = station2.name.lower()

    return name1 == name2 or name1 in name2 or name2 in name1


def _station_in_path(station: Station, path: List[Station]) -> bool:
    """Check if a station is in a train's path."""
    for path_station in path:
        if _station_matches(station, path_station):
            return True
    return False


def _find_direct_journeys(
    trains: List[Train],
    start_station: Station,
    end_station: Station,
    min_departure_time: datetime,
) -> List[Journey]:
    """Find direct trains that go from start to end without changes."""
    journeys = []

    for train in trains:
        # Check if this train departs from or passes through start station
        departs_from_start = _station_matches(train.startLocation, start_station)
        passes_through_start = _station_in_path(start_station, train.path)

        if not (departs_from_start or passes_through_start):
            continue

        # Check if this train goes to or passes through end station
        arrives_at_end = _station_matches(train.endLocation, end_station)
        passes_through_end = _station_in_path(end_station, train.path)

        if not (arrives_at_end or passes_through_end):
            continue

        # Check departure time
        if train.departureTime and train.departureTime < min_departure_time:
            continue

        # Verify the order: start must come before end in the path
        if not _verify_station_order(train.path, start_station, end_station):
            continue

        # Calculate journey time (estimate if arrival time not available)
        total_time = _estimate_journey_time(train, start_station, end_station)

        journey = Journey(
            startStation=start_station,
            endStation=end_station,
            trains=[train],
            changes=None,
            totalTime=total_time,
            description=f"Direct {train.trainNumber} from {start_station.name} to {end_station.name}",
        )
        journeys.append(journey)

    return journeys


def _verify_station_order(path: List[Station], start: Station, end: Station) -> bool:
    """Verify that start station comes before end station in the path."""
    start_idx = -1
    end_idx = -1

    for i, station in enumerate(path):
        if start_idx < 0 and _station_matches(station, start):
            start_idx = i
        if _station_matches(station, end):
            end_idx = i

    return start_idx >= 0 and end_idx >= 0 and start_idx < end_idx


def _estimate_journey_time(train: Train, start: Station, end: Station) -> int:
    """Estimate journey time in minutes based on path length."""
    # If we have actual times, use them
    if train.departureTime and train.arrivalTime:
        return int((train.arrivalTime - train.departureTime).total_seconds() / 60)

    # Estimate based on number of stops (roughly 15-20 minutes per stop for long-distance)
    start_idx = 0
    end_idx = len(train.path) - 1

    for i, station in enumerate(train.path):
        if _station_matches(station, start):
            start_idx = i
        if _station_matches(station, end):
            end_idx = i
            break

    num_stops = end_idx - start_idx

    # Estimate based on train category
    if train.trainCategory in ["ICE"]:
        minutes_per_stop = 15
    elif train.trainCategory in ["IC", "EC"]:
        minutes_per_stop = 18
    elif train.trainCategory in ["RE"]:
        minutes_per_stop = 12
    else:
        minutes_per_stop = 8  # S-Bahn, RB

    return max(num_stops * minutes_per_stop, 10)


def _find_journeys_with_changes(
    all_trains: List[Train],
    trains_by_departure: Dict[str, List[Train]],
    start_station: Station,
    end_station: Station,
    min_departure_time: datetime,
    max_changes: int = 1,
) -> List[Journey]:
    """Find journeys that require changing trains."""
    journeys = []

    # Find all trains departing from start station
    first_leg_trains = [
        t
        for t in all_trains
        if (
            _station_matches(t.startLocation, start_station)
            or _station_in_path(start_station, t.path[:1])
        )  # Check if it's the first stop
        and t.departureTime
        and t.departureTime >= min_departure_time
    ]

    for first_train in first_leg_trains:
        # For each potential change station in the first train's path
        for change_station in first_train.path[1:]:  # Skip the first station (start)
            # Skip if this is the end station (would be a direct journey)
            if _station_matches(change_station, end_station):
                continue

            # Estimate arrival time at change station
            arrival_at_change = _estimate_arrival_time(first_train, change_station)
            if not arrival_at_change:
                continue

            # Find connecting trains from this station
            min_connection_time = arrival_at_change + timedelta(
                minutes=MIN_TRANSFER_TIME
            )
            max_connection_time = arrival_at_change + timedelta(
                minutes=MAX_TRANSFER_TIME
            )

            # Look for trains departing from the change station
            connecting_trains = _find_connecting_trains(
                all_trains,
                change_station,
                end_station,
                min_connection_time,
                max_connection_time,
            )

            for second_train in connecting_trains:
                # Calculate total journey time
                total_time = _calculate_total_journey_time(
                    [first_train, second_train],
                    [change_station],
                    start_station,
                    end_station,
                )

                # Create the journey
                change = StationChange(
                    station=change_station,
                    timeMinutes=int(
                        (second_train.departureTime - arrival_at_change).total_seconds()
                        / 60
                    )
                    if second_train.departureTime
                    else MIN_TRANSFER_TIME,
                )

                journey = Journey(
                    startStation=start_station,
                    endStation=end_station,
                    trains=[first_train, second_train],
                    changes=[change],
                    totalTime=total_time,
                    description=f"{first_train.trainNumber} to {change_station.name}, then {second_train.trainNumber} to {end_station.name}",
                )
                journeys.append(journey)

    return journeys


def _estimate_arrival_time(train: Train, station: Station) -> Optional[datetime]:
    """Estimate arrival time at a station along the train's route."""
    if not train.departureTime:
        return None

    # Find the station in the path
    station_idx = -1
    for i, path_station in enumerate(train.path):
        if _station_matches(path_station, station):
            station_idx = i
            break

    if station_idx < 0:
        return None

    # Estimate time based on position in path
    minutes_per_stop = 15 if train.trainCategory in ["ICE", "IC"] else 10
    estimated_minutes = station_idx * minutes_per_stop

    return train.departureTime + timedelta(minutes=estimated_minutes)


def _find_connecting_trains(
    all_trains: List[Train],
    change_station: Station,
    end_station: Station,
    min_departure: datetime,
    max_departure: datetime,
) -> List[Train]:
    """Find trains that depart from change_station and go to end_station."""
    connecting = []

    for train in all_trains:
        # Check if this train departs from or passes through the change station
        departs_from_change = _station_matches(train.startLocation, change_station)
        passes_through_change = _station_in_path(
            change_station, train.path[:3]
        )  # Early in path

        if not (departs_from_change or passes_through_change):
            continue

        # Check if this train goes to the end station
        arrives_at_end = _station_matches(train.endLocation, end_station)
        passes_through_end = _station_in_path(end_station, train.path)

        if not (arrives_at_end or passes_through_end):
            continue

        # Check departure time is within the connection window
        if not train.departureTime:
            continue

        if train.departureTime < min_departure or train.departureTime > max_departure:
            continue

        # Verify station order
        if not _verify_station_order(train.path, change_station, end_station):
            continue

        connecting.append(train)

    return connecting


def _calculate_total_journey_time(
    trains: List[Train], change_stations: List[Station], start: Station, end: Station
) -> int:
    """Calculate total journey time including travel and transfer times."""
    total_minutes = 0

    for i, train in enumerate(trains):
        if i == 0:
            # First leg: from start to first change
            if change_stations:
                leg_time = _estimate_journey_time(train, start, change_stations[0])
            else:
                leg_time = _estimate_journey_time(train, start, end)
        elif i == len(trains) - 1:
            # Last leg: from last change to end
            leg_time = _estimate_journey_time(train, change_stations[-1], end)
        else:
            # Middle leg: between changes
            leg_time = _estimate_journey_time(
                train, change_stations[i - 1], change_stations[i]
            )

        total_minutes += leg_time

    # Add transfer times
    for station in change_stations:
        total_minutes += MIN_TRANSFER_TIME

    return total_minutes


def _deduplicate_journeys(journeys: List[Journey]) -> List[Journey]:
    """Remove duplicate journeys based on train combinations."""
    seen: Set[str] = set()
    unique = []

    for journey in journeys:
        # Create a key from train numbers
        key = "-".join(t.trainNumber for t in journey.trains)
        if key not in seen:
            seen.add(key)
            unique.append(journey)

    return unique
