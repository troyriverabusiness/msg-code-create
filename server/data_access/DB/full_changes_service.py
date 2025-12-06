import httpx
import xmltodict
import json
from .config import BASE_URL, get_headers, save_response, print_separator


def get_full_changes(eva_no: str) -> dict:
    url = f"{BASE_URL}/fchg/{eva_no}"

    print_separator(f"Full Changes: Station {eva_no}")
    print(f"URL: {url}")

    try:
        response = httpx.get(url, headers=get_headers(), timeout=30.0)
        response.raise_for_status()

        filename = f"fchg_{eva_no}.xml"
        filepath = save_response(filename, response.text)
        print(f"Saved response to: {filepath}")

        data = xmltodict.parse(response.text)
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
