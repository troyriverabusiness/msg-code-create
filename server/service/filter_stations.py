from typing import List, Dict, Set, Optional, Tuple
from collections import deque
import csv
import os
from server.models.station import Station


# German long-distance rail network graph
# Based on major ICE/IC routes connecting main cities
# Each node is an EVA number, edges represent direct train connections
RAIL_NETWORK: Dict[int, List[int]] = {
    # Frankfurt(Main)Hbf - major hub
    8000105: [
        8000244,
        8000068,
        8002041,
        8000115,
        8000150,
        8000240,
        8070003,
        8000250,
        8000124,
    ],
    # Mannheim Hbf
    8000244: [8000105, 8000156, 8000191, 8000096, 8000236],
    # Heidelberg Hbf
    8000156: [8000244, 8000191],
    # Karlsruhe Hbf
    8000191: [8000244, 8000156, 8000107, 8000774, 8000096, 8000055],
    # Freiburg(Breisgau) Hbf
    8000107: [8000191, 8000290, 8000026],
    # Basel Bad Bf
    8000026: [8000107],
    # Offenburg
    8000290: [8000191, 8000107],
    # Stuttgart Hbf
    8000096: [8000244, 8000191, 8000170, 8000284],
    # Ulm Hbf
    8000170: [8000096, 8000013, 8000261],
    # Augsburg Hbf
    8000013: [8000170, 8000261],
    # München Hbf
    8000261: [8000013, 8000170, 8000284, 8000320, 8000298, 8000262],
    # München Ost
    8000262: [8000261, 8000320],
    # Rosenheim
    8000320: [8000261, 8000262, 8000108],
    # Freilassing
    8000108: [8000320],
    # Passau Hbf
    8000298: [8000261, 8000309],
    # Nürnberg Hbf
    8000284: [8000096, 8000261, 8000260, 8000309, 8001844],
    # Erlangen
    8001844: [8000284],
    # Würzburg Hbf
    8000260: [8000284, 8000105, 8000115, 8000150],
    # Fulda
    8000115: [8000105, 8000260, 8003200, 8000029],
    # Kassel-Wilhelmshöhe
    8003200: [8000115, 8000128, 8000337, 8010224],
    # Göttingen
    8000128: [8003200, 8000152, 8000169],
    # Hannover Hbf
    8000152: [8000128, 8000050, 8002549, 8006552, 8000169, 8000263, 8000064],
    # Celle
    8000064: [8000152, 8000168],
    # Uelzen
    8000168: [8000064, 8000238, 8002549],
    # Lüneburg
    8000238: [8000168, 8002549],
    # Hildesheim Hbf
    8000169: [8000152, 8000128],
    # Braunschweig Hbf
    8000049: [8000152, 8006552, 8010224],
    # Wolfsburg Hbf
    8006552: [8000152, 8000049, 8011160],
    # Bremen Hbf
    8000050: [8000152, 8002549, 8000294, 8000291],
    # Oldenburg(Oldb)
    8000291: [8000050],
    # Osnabrück Hbf
    8000294: [8000050, 8000263, 8000149],
    # Hamburg Hbf
    8002549: [
        8000152,
        8000050,
        8000168,
        8000238,
        8002553,
        8002548,
        8000147,
        8000237,
        8000199,
        8010304,
    ],
    # Hamburg-Altona
    8002553: [8002549, 8002548],
    # Hamburg Dammtor
    8002548: [8002549, 8002553],
    # Hamburg-Harburg
    8000147: [8002549, 8000050],
    # Lübeck Hbf
    8000237: [8002549],
    # Kiel Hbf
    8000199: [8002549, 8000271],
    # Neumünster
    8000271: [8000199, 8002549],
    # Münster(Westf)Hbf
    8000263: [8000152, 8000294, 8000149, 8000080],
    # Hamm(Westf)
    8000149: [8000263, 8000294, 8000080],
    # Dortmund Hbf
    8000080: [8000149, 8000263, 8000041, 8000142, 8000098],
    # Bochum Hbf
    8000041: [8000080, 8000098],
    # Essen Hbf
    8000098: [8000041, 8000080, 8000086],
    # Duisburg Hbf
    8000086: [8000098, 8000085, 8000207],
    # Düsseldorf Hbf
    8000085: [8000086, 8000207, 8000211],
    # Köln Hbf
    8000207: [8000086, 8000085, 8000044, 8000001, 8003330, 8000206, 8005556],
    # Köln/Bonn Flughafen
    8003330: [8000207, 8005556],
    # Siegburg/Bonn
    8005556: [8000207, 8003330, 8000044],
    # Bonn Hbf
    8000044: [8000207, 8005556, 8000206],
    # Koblenz Hbf
    8000206: [8000044, 8000240, 8000667],
    # Montabaur
    8000667: [8000206, 8003680],
    # Limburg Süd
    8003680: [8000667, 8000105],
    # Mainz Hbf
    8000240: [8000105, 8000206, 8000250],
    # Wiesbaden Hbf
    8000250: [8000105, 8000240],
    # Aachen Hbf
    8000001: [8000207],
    # Krefeld Hbf
    8000211: [8000085, 8000253],
    # Mönchengladbach Hbf
    8000253: [8000211, 8000001],
    # Darmstadt Hbf
    8000068: [8000105, 8002041, 8000244],
    # Frankfurt(Main)Süd
    8002041: [8000105, 8000068, 8000150, 8000349],
    # Frankfurt(M) Flughafen Fernbf
    8070003: [8000105, 8000244],
    # Offenbach(Main)Hbf
    8000349: [8002041, 8000150],
    # Hanau Hbf
    8000150: [8000105, 8002041, 8000349, 8000260, 8000115],
    # Gießen
    8000124: [8000105, 8000337, 8000111],
    # Marburg(Lahn)
    8000337: [8000124, 8003200],
    # Friedberg(Hess)
    8000111: [8000124, 8000105],
    # Hagen Hbf
    8000142: [8000080, 8000266],
    # Wuppertal Hbf
    8000266: [8000142, 8000207, 8000085],
    # Berlin Hbf
    8011160: [
        8006552,
        8010404,
        8010405,
        8010406,
        8010255,
        8011113,
        8011102,
        8010085,
        8010205,
        8010224,
    ],
    # Berlin-Spandau
    8010404: [8011160, 8006552],
    # Berlin Wannsee
    8010405: [8011160],
    # Berlin Zoologischer Garten
    8010406: [8011160],
    # Berlin Ostbahnhof
    8010255: [8011160, 8010089],
    # Berlin Südkreuz
    8011113: [8011160, 8010205],
    # Berlin Gesundbrunnen
    8011102: [8011160],
    # Leipzig Hbf
    8010205: [8011160, 8011113, 8010085, 8010159, 8010101, 8012183],
    # Leipzig/Halle Flughafen
    8012183: [8010205, 8010159],
    # Dresden Hbf
    8010085: [8011160, 8010205, 8010089],
    # Dresden-Neustadt
    8010089: [8010085, 8010255],
    # Halle(Saale)Hbf
    8010159: [8010205, 8010224, 8012183],
    # Magdeburg Hbf
    8010224: [8011160, 8003200, 8000049, 8010159, 8010334],
    # Stendal
    8010334: [8010224, 8006552],
    # Erfurt Hbf
    8010101: [8010205, 8010366, 8000115, 8010309],
    # Weimar
    8010366: [8010101, 8010205],
    # Saalfeld(Saale)
    8010309: [8010101, 8000284],
    # Regensburg Hbf
    8000309: [8000284, 8000298, 8000261],
    # Rostock Hbf
    8010304: [8002549, 8010324, 8013236, 8010338],
    # Warnemünde
    8013236: [8010304],
    # Schwerin Hbf
    8010324: [8010304, 8010216],
    # Ludwigslust
    8010216: [8010324, 8011160],
    # Stralsund Hbf
    8010338: [8010304, 8011191],
    # Ostseebad Binz
    8011191: [8010338],
    # Bebra
    8000029: [8000115, 8010097],
    # Eisenach
    8010097: [8000029, 8010101],
    # Baden-Baden
    8000774: [8000191],
    # Bruchsal
    8000055: [8000191, 8000096],
}


def load_stations_from_csv() -> Dict[int, str]:
    """Load station EVA numbers and names from the CSV file."""
    stations = {}
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "db_fv_stations.csv"
    )

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                eva = int(row["EVA_NR"])
                name = row["NAME"]
                stations[eva] = name
    except Exception as e:
        print(f"Error loading stations CSV: {e}")

    return stations


# Cache for station data
_STATIONS_CACHE: Optional[Dict[int, str]] = None


def get_stations_cache() -> Dict[int, str]:
    """Get cached station data, loading from CSV if needed."""
    global _STATIONS_CACHE
    if _STATIONS_CACHE is None:
        _STATIONS_CACHE = load_stations_from_csv()
    return _STATIONS_CACHE


def find_station_by_name(name: str) -> Optional[Station]:
    """
    Find a station by name using fuzzy matching.
    Handles common variations like 'Frankfurt' -> 'Frankfurt(Main)Hbf'
    Prioritizes main stations (Hbf) over secondary stations.
    """
    stations = get_stations_cache()
    name_lower = name.lower().strip()

    # First try exact match
    for eva, station_name in stations.items():
        if station_name.lower() == name_lower:
            return Station(name=station_name, eva=eva)

    # Try exact match with "Hbf" suffix
    for eva, station_name in stations.items():
        station_lower = station_name.lower()
        if station_lower == f"{name_lower} hbf" or station_lower == f"{name_lower}hbf":
            return Station(name=station_name, eva=eva)

    # Try to find main station (Hbf) that starts with the search term
    # Prioritize "Hbf" stations over other matches
    hbf_matches = []
    other_matches = []

    for eva, station_name in stations.items():
        station_lower = station_name.lower()

        # Check if station name starts with the search term
        if station_lower.startswith(name_lower):
            if "hbf" in station_lower or "hauptbahnhof" in station_lower:
                hbf_matches.append((eva, station_name))
            else:
                other_matches.append((eva, station_name))
        # Check for pattern like "Berlin Hbf" matching "Berlin"
        elif name_lower in station_lower:
            if "hbf" in station_lower:
                hbf_matches.append((eva, station_name))
            else:
                other_matches.append((eva, station_name))

    # Prefer Hbf matches
    if hbf_matches:
        # Sort by length to get the most specific match
        hbf_matches.sort(key=lambda x: len(x[1]))
        eva, station_name = hbf_matches[0]
        return Station(name=station_name, eva=eva)

    if other_matches:
        other_matches.sort(key=lambda x: len(x[1]))
        eva, station_name = other_matches[0]
        return Station(name=station_name, eva=eva)

    # Try matching with common abbreviations
    common_suffixes = ["hbf", "hauptbahnhof", "hb", "bf"]
    for suffix in common_suffixes:
        search_with_suffix = f"{name_lower} {suffix}"
        for eva, station_name in stations.items():
            if station_name.lower().startswith(search_with_suffix):
                return Station(name=station_name, eva=eva)

    return None


def get_station_by_eva(eva: int) -> Optional[Station]:
    """Get a station by its EVA number."""
    stations = get_stations_cache()
    if eva in stations:
        return Station(name=stations[eva], eva=eva)
    return None


def find_stations_between(start_eva: int, end_eva: int, max_hops: int = 3) -> List[int]:
    """
    Find all stations that lie on possible routes between start and end.
    Uses BFS to find all paths within max_hops extra stops.

    Args:
        start_eva: EVA number of start station
        end_eva: EVA number of end station
        max_hops: Maximum additional stops beyond direct path

    Returns:
        List of EVA numbers for all relevant stations
    """
    if start_eva not in RAIL_NETWORK or end_eva not in RAIL_NETWORK:
        return []

    # First find the shortest path length
    shortest_path = _find_shortest_path(start_eva, end_eva)
    if not shortest_path:
        return []

    shortest_length = len(shortest_path)
    max_path_length = shortest_length + max_hops

    # Find all stations on any valid path
    relevant_stations: Set[int] = set()

    # Use DFS to find all paths within the length limit
    def dfs(current: int, target: int, path: List[int], visited: Set[int]):
        if len(path) > max_path_length:
            return

        if current == target:
            relevant_stations.update(path)
            return

        for neighbor in RAIL_NETWORK.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                dfs(neighbor, target, path, visited)
                path.pop()
                visited.remove(neighbor)

    visited = {start_eva}
    dfs(start_eva, end_eva, [start_eva], visited)

    return list(relevant_stations)


def _find_shortest_path(start_eva: int, end_eva: int) -> Optional[List[int]]:
    """Find the shortest path between two stations using BFS."""
    if start_eva == end_eva:
        return [start_eva]

    queue = deque([(start_eva, [start_eva])])
    visited = {start_eva}

    while queue:
        current, path = queue.popleft()

        for neighbor in RAIL_NETWORK.get(current, []):
            if neighbor == end_eva:
                return path + [neighbor]

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None


def filter_stations(start: str, end: str) -> List[Station]:
    """
    Find all stations that should be queried to find connections between start and end.

    This includes:
    - The start and end stations themselves
    - All intermediate stations on possible routes
    - Stations up to 3 hops beyond the direct path (for alternative routes)

    Args:
        start: Name or partial name of start station
        end: Name or partial name of end station

    Returns:
        List of Station objects representing relevant stations
    """
    # Find start and end stations
    start_station = find_station_by_name(start)
    end_station = find_station_by_name(end)

    if not start_station:
        print(f"Warning: Could not find start station '{start}'")
        return []

    if not end_station:
        print(f"Warning: Could not find end station '{end}'")
        return []

    # Find all relevant stations between start and end
    relevant_evas = find_stations_between(start_station.eva, end_station.eva)

    if not relevant_evas:
        # If no path found in network, return just start and end
        return [start_station, end_station]

    # Convert EVA numbers to Station objects
    stations = []
    for eva in relevant_evas:
        station = get_station_by_eva(eva)
        if station:
            stations.append(station)

    return stations


def get_direct_connections(eva: int) -> List[Station]:
    """Get all stations directly connected to the given station."""
    connections = RAIL_NETWORK.get(eva, [])
    stations = []
    for conn_eva in connections:
        station = get_station_by_eva(conn_eva)
        if station:
            stations.append(station)
    return stations
