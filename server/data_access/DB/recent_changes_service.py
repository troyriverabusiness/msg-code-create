"""
Recent Changes Service

Endpoint: GET /rchg/{evaNo}
Returns recent changes for a station (last 2 minutes only).
"""

import httpx
import xmltodict
import json
from .config import BASE_URL, get_headers, save_response, print_separator


def get_recent_changes(eva_no: str) -> dict:
    """
    Get recent changes for a station (last 2 minutes).

    Recent changes are a subset of full changes (/fchg). They contain only
    changes that became known within the last 2 minutes.

    Use this for efficient polling:
    1. Load full changes initially with get_full_changes()
    2. Then periodically call get_recent_changes() to get updates

    This saves bandwidth compared to repeatedly fetching full changes.

    Note: Recent changes are updated every 30 seconds and should be cached
    for that period.

    Args:
        eva_no: Station EVA number (e.g., "8000105" for Frankfurt Hbf)

    Examples:
        get_recent_changes("8000105")  # Frankfurt Hbf
        get_recent_changes("8011160")  # Berlin Hbf

    Common EVA numbers:
        8000105 - Frankfurt (Main) Hbf
        8000191 - Koeln Hbf
        8011160 - Berlin Hbf
        8000261 - Muenchen Hbf
        8000152 - Hamburg Hbf

    Returns:
        dict: Parsed recent change data (subset of full changes)

    Saves:
        Raw XML response to data/rchg_{eva_no}.xml
    """
    url = f"{BASE_URL}/rchg/{eva_no}"

    print_separator(f"Recent Changes: Station {eva_no}")
    print(f"URL: {url}")

    try:
        response = httpx.get(url, headers=get_headers(), timeout=30.0)
        response.raise_for_status()

        # Save raw XML response
        filename = f"rchg_{eva_no}.xml"
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
    # Example: python -m service.recent_changes_service
    result = get_recent_changes("8000105")  # Frankfurt Hbf
