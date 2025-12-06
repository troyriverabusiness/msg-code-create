import sys
import os

# Add server to path so we can import service
sys.path.append(os.getcwd())

from server.service.timetable_service import TimetableService
from datetime import datetime

def test_fallback():
    print("🧪 Testing API Key Fallback...")
    service = TimetableService()
    
    # Use a known station (Berlin Hbf = 8011160)
    print("Requesting timetable for Berlin Hbf...")
    try:
        data = service.get_timetable("8011160", datetime.now())
        
        if data:
            print(f"✅ Success! Retrieved {len(data)} items.")
            print("Check logs above for 'Switching to fallback' message.")
        else:
            print("❌ Failed to retrieve data.")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_fallback()
