"""
Plan Service - Planned Timetable

Endpoint: GET /plan/{evaNo}/{date}/{hour}
Returns planned timetable data for a station within an hourly time slice.
"""

import httpx
import xmltodict
import json
from datetime import datetime
from .config import BASE_URL, get_headers, save_response, print_separator


def get_plan(eva_no: str, date: str, hour: str) -> dict:
    """
    Get planned timetable for a station at a specific date and hour.

    Planned data is static and generated hours in advance. It contains
    planned times (pt), platforms (pp), status (ps), and paths (ppth).
    It does NOT contain messages or change data.

    Args:
        eva_no: Station EVA number (e.g., "8000105" for Frankfurt Hbf)
        date: Date in YYMMDD format (e.g., "251205" for Dec 5, 2025)
        hour: Hour in HH format (e.g., "14" for 2 PM, must be 00-23)

    Examples:
        get_plan("8000105", "251205", "14")  # Frankfurt Hbf, Dec 5 2025, 2 PM

    Common EVA numbers:
        8000105 - Frankfurt (Main) Hbf
        8000191 - Koeln Hbf
        8011160 - Berlin Hbf
        8000261 - Muenchen Hbf
        8000152 - Hamburg Hbf

    Returns:
        dict: Parsed timetable data with arrivals and departures

    Saves:
        Raw XML response to data/plan_{eva_no}_{date}_{hour}.xml
    """
    url = f"{BASE_URL}/plan/{eva_no}/{date}/{hour}"

    print_separator(f"Planned Timetable: Station {eva_no}")
    print(f"Date: {date} (YYMMDD), Hour: {hour}")
    print(f"URL: {url}")

    try:
        response = httpx.get(url, headers=get_headers(), timeout=30.0)
        response.raise_for_status()

        # Save raw XML response
        filename = f"plan_{eva_no}_{date}_{hour}.xml"
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


def get_plan_now(eva_no: str) -> dict:
    """
    Convenience function to get the plan for the current hour.

    Args:
        eva_no: Station EVA number

    Returns:
        dict: Parsed timetable data for current hour
    """
    now = datetime.now()
    date = now.strftime("%y%m%d")  # YYMMDD
    hour = now.strftime("%H")  # HH

    print(f"Getting plan for current time: {now.strftime('%Y-%m-%d %H:00')}")
    return get_plan(eva_no, date, hour)


if __name__ == "__main__":
    # Test the function when run directly
    # Example: python -m service.plan_service
    result = get_plan_now("8000105")  # Frankfurt Hbf, current hour
