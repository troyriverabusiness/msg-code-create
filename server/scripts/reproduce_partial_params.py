import requests
import json

URL = "http://localhost:8000/api/v1/chat"

def test_chat():
    # Only partial info, no origin/destination
    payload = {
        "message": "via Cologne with 180min changeover"
    }
    
    try:
        response = requests.post(URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        print("Response Status:", response.status_code)
        print("Response Body:", json.dumps(data, indent=2))
        
        if data.get("search_params"):
            print("SUCCESS: search_params found!")
            print(data["search_params"])
            
            # Check if via and min_transfer_time are present
            params = data["search_params"]
            if "via" in params and "min_transfer_time" in params:
                print("SUCCESS: Partial params present.")
            else:
                print("FAILURE: Partial params missing.")
        else:
            print("FAILURE: search_params missing or empty.")
            
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print("Error Response:", e.response.text)

if __name__ == "__main__":
    test_chat()
