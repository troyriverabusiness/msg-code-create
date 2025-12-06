"""
Station Search Service

Endpoint: GET /station/{pattern}
Searches for stations by name prefix, EVA number, DS100 code, or wildcard (*).
"""

import httpx
import xmltodict
import json
from .config import BASE_URL, get_headers, save_response, print_separator


def search_stations(pattern: str) -> dict:
    """
    Search for stations matching the given pattern.

    Args:
        pattern: Can be a station name (prefix), EVA number, DS100/RL100 code,
                 or wildcard (*). Note: umlauts in station names may not work.

    Examples:
        search_stations("Frankfurt")  # Search by name prefix
        search_stations("8000105")    # Search by EVA number
        search_stations("FF")         # Search by DS100 code
        search_stations("BLS")        # Search by DS100 code (Berlin)

    Returns:
        dict: Parsed station data

    Saves:
        Raw XML response to data/station_{pattern}.xml
    """
    url = f"{BASE_URL}/station/{pattern}"

    print_separator(f"Station Search: {pattern}")
    print(f"URL: {url}")

    try:
        response = httpx.get(url, headers=get_headers(), timeout=30.0)
        response.raise_for_status()

        # Save raw XML response
        filename = f"station_{pattern}.xml"
        filepath = save_response(filename, response.text)
        print(f"Saved response to: {filepath}")

        # Parse XML to dict
        data = xmltodict.parse(response.text)

        # Pretty print the parsed data
        print("\nParsed Response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        return data

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    # Test the function when run directly
    # Example: python -m service.station_service
    result = search_stations("Frankfurt")
