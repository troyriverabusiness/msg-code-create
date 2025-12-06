from langchain_core.tools import tool
from server.services.timetable_service import TimetableService
from server.services.linker_service import LinkerService
from datetime import datetime

timetable_service = TimetableService()
linker_service = LinkerService()

# Hardcoded EVA map (same as main.py for now, ideally shared)
STATION_EVA_MAP = {
    "München Hbf": "8000261",
    "Berlin Hbf": "8011160",
    "Hamburg Hbf": "8002549",
    "Frankfurt (Main) Hbf": "8000105",
    "Lindau-Reutin": "8003693",
    "Köln Hbf": "8000207",
    "Stuttgart Hbf": "8000096",
    "Leipzig Hbf": "8010205",
    "Dresden Hbf": "8010085",
    "Hannover Hbf": "8000152",
    "Nürnberg Hbf": "8000284"
}

@tool
def get_live_departures(station_name: str) -> str:
    """
    Get live departure board for a specific station.
    Returns a list of trains with their planned time, delay, and platform.
    """
    eva = STATION_EVA_MAP.get(station_name)
    if not eva:
        # Fuzzy search
        for name, e in STATION_EVA_MAP.items():
            if station_name.lower() in name.lower():
                eva = e
                break
    
    if not eva:
        return f"Station '{station_name}' not found. Available: {', '.join(STATION_EVA_MAP.keys())}"

    board = timetable_service.get_station_board(eva, datetime.now())
    if not board:
        return f"No departures found for {station_name}."

    # Format as string for LLM
    output = [f"Departures for {station_name}:"]
    for dep in board[:10]: # Limit to 10
        delay_str = ""
        if dep['real_time'].get('delay'):
            delay_str = f"(DELAYED +{dep['real_time']['delay']} min)"
        
        plat_str = f"Plat {dep['platform']}"
        if dep['real_time'].get('platform'):
            plat_str = f"Plat {dep['real_time']['platform']} (CHANGED)"

        output.append(f"- {dep['time'][8:10]}:{dep['time'][10:12]} {dep['train']} to {dep['direction']} {plat_str} {delay_str}")
    
    return "\n".join(output)

@tool
def get_train_details(train_category: str, train_number: str) -> str:
    """
    Get full details for a specific train (e.g. 'ICE', '690').
    Returns the full list of stops and accessibility info.
    """
    trip_id = linker_service.find_trip_id(train_category, train_number)
    if not trip_id:
        return f"Could not find details for {train_category} {train_number} in the database."

    details = linker_service.get_trip_details(trip_id)
    if not details:
        return "Found trip ID but failed to load details."

    output = [f"Details for {details['train']} (Headsign: {details['headsign']}):"]
    for stop in details['stops']:
        wheelchair = "♿" if stop['wheelchair'] else ""
        time = stop['departure'] or stop['arrival']
        output.append(f"- {time} {stop['station']} {wheelchair}")

    return "\n".join(output)
