import requests
import json
from datetime import datetime, timedelta

URL = "http://localhost:8000/api/v1/connections"

def test_connections():
    # Parameters from the screenshot
    params = {
        "start": "Frankfurt HBF",
        "end": "Hamburg HBF",
        "via": "Köln",
        "min_transfer_time": 180,
        "departure_time": (datetime.now() + timedelta(days=1)).replace(hour=8, minute=0).isoformat()
    }
    
    print(f"Testing connections with params: {params}")
    
    try:
        response = requests.get(URL, params=params)
        # response.raise_for_status() # Don't raise yet, we want to see the error
        
        print("Response Status:", response.status_code)
        try:
            data = response.json()
            print("Response Body:", json.dumps(data, indent=2))
            
            if data.get("journeys"):
                print(f"SUCCESS: Found {len(data['journeys'])} journeys.")
            else:
                print("FAILURE: No journeys found.")
                
        except json.JSONDecodeError:
            print("Response Text:", response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connections()
