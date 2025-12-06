"""
Full Changes Service

Endpoint: GET /fchg/{evaNo}
Returns all known changes for a station (delays, platform changes, cancellations, etc.)
"""

import httpx
import xmltodict
import json
from .config import BASE_URL, get_headers, save_response, print_separator


def get_full_changes(eva_no: str) -> dict:
    """
    Get all known changes for a station.

    Full changes include all known modifications from now until indefinitely
    into the future. Changes become obsolete when their trip departs and are
    then removed from this resource.

    Changes may include:
    - Delay information (ct - changed time)
    - Platform changes (cp - changed platform)
    - Status changes (cs - changed status, e.g., cancellations)
    - Path changes (cpth - changed path/route)
    - Messages about disruptions, delays, etc.

    Note: Full changes are updated every 30 seconds and should be cached
    for that period.

    Args:
        eva_no: Station EVA number (e.g., "8000105" for Frankfurt Hbf)

    Examples:
        get_full_changes("8000105")  # Frankfurt Hbf
        get_full_changes("8011160")  # Berlin Hbf

    Common EVA numbers:
        8000105 - Frankfurt (Main) Hbf
        8000191 - Koeln Hbf
        8011160 - Berlin Hbf
        8000261 - Muenchen Hbf
        8000152 - Hamburg Hbf

    Returns:
        dict: Parsed change data including delays, cancellations, etc.

    Saves:
        Raw XML response to data/fchg_{eva_no}.xml
    """
    url = f"{BASE_URL}/fchg/{eva_no}"

    print_separator(f"Full Changes: Station {eva_no}")
    print(f"URL: {url}")

    try:
        response = httpx.get(url, headers=get_headers(), timeout=30.0)
        response.raise_for_status()

        # Save raw XML response
        filename = f"fchg_{eva_no}.xml"
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
    # Example: python -m service.full_changes_service
    result = get_full_changes("8000105")  # Frankfurt Hbf
