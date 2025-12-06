import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

# Configuration
BASE_URL = "https://apis.deutschebahn.com/db-api-marketplace/apis/ris-journeys-transporteure/v2"
CLIENT_ID = os.environ.get("DB_CLIENT_ID")
API_KEY = os.environ.get("DB_API_KEY")

def make_request(endpoint, method="GET", data=None, params=None):
    if not CLIENT_ID or not API_KEY:
        print("Error: DB_CLIENT_ID and DB_API_KEY environment variables are required.")
        print("Please export them in your terminal:")
        print("export DB_CLIENT_ID='your_client_id'")
        print("export DB_API_KEY='your_api_key'")
        exit(1)

    url = f"{BASE_URL}{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    headers = {
        "DB-Client-ID": CLIENT_ID,
        "DB-Api-Key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/vnd.de.db.ris+json"
    }

    body = None
    if data:
        body = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        print(e.read().decode("utf-8"))
        exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

def main():
    print("--- RIS::Journeys API Test (Machine-to-Machine) ---")
    
    # 1. Match a Journey (ICE 219 from Lindau-Reutin)
    # Note: Using specific details found in local GTFS for testing
    today = datetime.now().strftime("%Y-%m-%d")
    start_time = f"{today}T15:58:00+01:00" # Scheduled time for ICE 219
    
    print(f"\n1. Matching ICE 219 from Lindau-Reutin (EVA 8003693) at {start_time}...")
    
    match_body = {
        "requests": [
            {
                "requestID": "test-req-1",
                "transportTypes": ["HIGH_SPEED_TRAIN"],
                "matchStartEnd": {
                    "startJourneyNumber": 219,
                    "startStopPlace": {
                        "evaNumber": "8003693"
                    },
                    "startTime": start_time
                }
            }
        ]
    }
    
    match_result = make_request("/match/by-start-end", method="POST", data=match_body)
    
    journeys = match_result.get("journeys", [])
    if not journeys:
        print("No journeys matched.")
        print("Response:", json.dumps(match_result, indent=2))
        return

    print(f"Found {len(journeys)} journeys.")
    first_journey = journeys[0].get("journey")
    if not first_journey:
        print("Journey object missing in result.")
        print(json.dumps(journeys[0], indent=2))
        return

    journey_id = first_journey["journeyID"]
    print(f"Matched Journey ID: {journey_id}")
    print(f"Relation: {first_journey['journeyRelation']['startStopPlace']['name']} -> {first_journey['journeyRelation']['endStopPlace']['name']}")

    # 2. Get Full Details (Batch Request)
    print(f"\n2. Fetching details for Journey ID: {journey_id}...")
    
    batch_body = {
        "journeyIDs": [journey_id],
        "includeReferences": True
    }
    
    batch_result = make_request("/batch", method="POST", data=batch_body)
    
    print("\n--- Result ---")
    print(json.dumps(batch_result, indent=2))

if __name__ == "__main__":
    main()
