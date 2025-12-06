import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

# Configuration
BASE_URL = "https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1"
CLIENT_ID = os.environ.get("TROY_API_CLIENT")
API_KEY = os.environ.get("TROY_API_KEY")

def make_request(endpoint, method="GET", data=None, headers_extra=None):
    if not CLIENT_ID or not API_KEY:
        print("Error: TROY_API_CLIENT and TROY_API_KEY environment variables are required.")
        exit(1)

    url = f"{BASE_URL}{endpoint}"
    
    headers = {
        "DB-Client-ID": CLIENT_ID,
        "DB-Api-Key": API_KEY,
        "Accept": "application/xml" # Timetables API returns XML by default, let's see
    }
    if headers_extra:
        headers.update(headers_extra)

    req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        print(e.read().decode("utf-8"))
        exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

def main():
    print("--- DB Timetables API Test ---")
    
    # Test with Lindau-Reutin (EVA 8003693)
    eva_no = "8003693"
    now = datetime.now()
    date_str = now.strftime("%y%m%d") # YYMMDD
    hour_str = now.strftime("%H")     # HH
    
    endpoint = f"/plan/{eva_no}/{date_str}/{hour_str}"
    print(f"\nFetching Plan for EVA {eva_no} at {date_str} {hour_str}:00...")
    print(f"URL: {BASE_URL}{endpoint}")
    
    result = make_request(endpoint)
    
    print("\n--- Result (First 500 chars) ---")
    print(result[:500])
    
    # Test /fchg (Real-time changes)
    print(f"\nFetching Full Changes (fchg) for EVA {eva_no}...")
    fchg_endpoint = f"/fchg/{eva_no}"
    fchg_result = make_request(fchg_endpoint)
    print("\n--- Result (First 500 chars) ---")
    print(fchg_result[:500])
    print("...")

if __name__ == "__main__":
    main()
