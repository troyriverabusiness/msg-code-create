import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

try:
    from server.service.graph_service import GraphService
    from server.service.plan_service import get_plan_now
    from server.service.journey_service import JourneyService
except ImportError as e:
    import traceback
    traceback.print_exc()
    print(f"\nsys.path is: {sys.path}")
    print(f"project_root is: {project_root}")
    print(f"Error importing services: {e}")
    print("Ensure you are running this script from the project root or scripts directory.")
    sys.exit(1)

def run_tests():
    report_lines = []
    report_lines.append("# Feature Verification Report")
    report_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # ---------------------------------------------------------
    # Test 3: Complex Routing (Multi-Leg)
    # ---------------------------------------------------------
    report_lines.append("## 3. Complex Routing (JourneyService)")
    report_lines.append("Testing `JourneyService.find_routes` for Frankfurt -> München\n")

    try:
        print("Initializing JourneyService...")
        journey_service = JourneyService()
        
        origin = "Frankfurt (Main) Hbf"
        destination = "München Hbf"
        time_str = "08:00:00" # Use a morning time to ensure connections exist
        
        report_lines.append(f"**Route:** {origin} -> {destination} at {time_str}\n")
        
        print(f"Finding journeys for {origin} -> {destination}...")
        journeys = journey_service.find_routes(origin, destination, time_str)
        
        if journeys:
            report_lines.append(f"**Result:** Found {len(journeys)} journey options:\n")
            for j in journeys:
                transfers = "Direct" if j.transfers == 0 else f"{j.transfers} Transfer(s)"
                legs_desc = " -> ".join([f"{l.train.name} ({l.origin.name})" for l in j.legs])
                report_lines.append(f"- **{j.totalTime} min** | {transfers} | {legs_desc} -> {j.endStation.name}")
        else:
            report_lines.append("**Result:** No journeys found.")
            
    except Exception as e:
        import traceback
        report_lines.append(f"**Error:** {str(e)}")
        report_lines.append(f"```\n{traceback.format_exc()}\n```")
        print(f"Error in Test 3: {e}")
        traceback.print_exc()

    report_lines.append("\n---\n")

    # ---------------------------------------------------------
    # Test 1: Discover Intermediate Stations
    # ---------------------------------------------------------
    report_lines.append("## 1. Discover Intermediate Stations")
    report_lines.append("Testing `GraphService.find_intermediate_stations`\n")

    try:
        print("Initializing GraphService...")
        graph_service = GraphService()
        
        origin = "Frankfurt (Main) Hbf"
        destination = "München Hbf"
        
        report_lines.append(f"**Route:** {origin} -> {destination}\n")
        
        print(f"Finding intermediate stations for {origin} -> {destination}...")
        stations = graph_service.find_intermediate_stations(origin, destination)
        
        if stations:
            report_lines.append(f"**Result:** Found {len(stations)} intermediate stations:\n")
            for station in stations:
                report_lines.append(f"- {station}")
        else:
            report_lines.append("**Result:** No intermediate stations found (or pathfinding failed).")
            
    except Exception as e:
        report_lines.append(f"**Error:** {str(e)}")
        print(f"Error in Test 1: {e}")

    report_lines.append("\n---\n")

    # ---------------------------------------------------------
    # Test 2: Get All Planned Trains
    # ---------------------------------------------------------
    report_lines.append("## 2. Get All Planned Trains")
    report_lines.append("Testing `plan_service.get_plan_now` for Frankfurt (Main) Hbf (EvaNo: 8000105)\n")

    try:
        eva_no = "8000105"
        print(f"Fetching planned trains for {eva_no}...")
        
        # This calls the external API
        plan_data = get_plan_now(eva_no)
        
        if plan_data and 'timetable' in plan_data:
            timetable = plan_data['timetable']
            stops = timetable.get('s', [])
            if not isinstance(stops, list):
                stops = [stops]
            
            report_lines.append("**Result:** Successfully retrieved timetable data.")
            report_lines.append(f"**Station:** {timetable.get('@station', 'Unknown')}")
            report_lines.append(f"**Total Planned Stops in this hour:** {len(stops)}\n")
            
            report_lines.append("### Sample Trains (First 5):")
            for i, stop in enumerate(stops[:5]):
                tl = stop.get('tl', {})
                # Arriving
                ar = stop.get('ar', {})
                ar_time = ar.get('@pt', 'N/A')
                # Departing
                dp = stop.get('dp', {})
                dp_time = dp.get('@pt', 'N/A')
                
                train_info = f"{tl.get('@c', '')} {tl.get('@n', '')}"
                report_lines.append(f"- **Train:** {train_info} | **Arr:** {ar_time} | **Dep:** {dp_time}")
                
        else:
             report_lines.append("**Result:** API returned data, but structure was unexpected.")
             report_lines.append("```json")
             report_lines.append(json.dumps(plan_data, indent=2)[:500] + "...")
             report_lines.append("```")

    except Exception as e:
        report_lines.append(f"**Error:** {str(e)}")
        print(f"Error in Test 2: {e}")

    # ---------------------------------------------------------
    # Write Report
    # ---------------------------------------------------------
    report_path = project_root / "Testing" / "FEATURE_VERIFICATION_REPORT.md"
    
    # Ensure directory exists
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    
    print(f"\nVerification complete. Report written to {report_path.absolute()}")

if __name__ == "__main__":
    run_tests()
