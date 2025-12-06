# Feature Verification Report
Date: 2025-12-06 23:35:07

## 3. Complex Routing (JourneyService)
Testing `JourneyService.find_routes` for Frankfurt -> München

**Route:** Frankfurt (Main) Hbf -> München Hbf at 08:00:00

**Result:** Found 10 journey options:

- **191 min** | Direct | 41 (Frankfurt (Main) Hauptbahnhof) -> München Hbf
- **192 min** | Direct | 41 (Frankfurt (Main) Hauptbahnhof) -> München Hbf
- **192 min** | Direct | 41 (Frankfurt (Main) Hauptbahnhof) -> München Hbf
- **194 min** | Direct | 41 (Frankfurt (Main) Hauptbahnhof) -> München Hbf
- **200 min** | Direct | 39 (Frankfurt (Main) Hauptbahnhof) -> München Hbf
- **201 min** | Direct | 39 (Frankfurt (Main) Hauptbahnhof) -> München Hbf
- **201 min** | Direct | 39 (Frankfurt (Main) Hauptbahnhof) -> München Hbf
- **201 min** | Direct | 39 (Frankfurt (Main) Hauptbahnhof) -> München Hbf
- **201 min** | Direct | 39 (Frankfurt (Main) Hauptbahnhof) -> München Hbf
- **222 min** | 1 Transfer(s) | 11 (Frankfurt (Main) Hauptbahnhof) -> 11 (Hauptbahnhof (oben)) -> München Hbf

---

## 1. Discover Intermediate Stations
Testing `GraphService.find_intermediate_stations`

**Route:** Frankfurt (Main) Hbf -> München Hbf

**Result:** Found 10 intermediate stations:

- Hauptbahnhof (oben)
- Mannheim, Hauptbahnhof
- Frankfurt (Main) Südbahnhof
- Frankfurt (Main) Flughafen Fernbahnhof
- Augsburg Hbf
- Ulm Hauptbahnhof
- Frankfurt (Main) Niederrad Bahnhof
- Ulm Hauptbahnhof
- Frankfurt (Main) Stadion
- Augsburg Hbf

---

## 2. Get All Planned Trains
Testing `plan_service.get_plan_now` for Frankfurt (Main) Hbf (EvaNo: 8000105)

**Result:** Successfully retrieved timetable data.
**Station:** Frankfurt(Main)Hbf
**Total Planned Stops in this hour:** 43

### Sample Trains (First 5):
- **Train:** ICE 775 | **Arr:** 2512062300 | **Dep:** 2512062305
- **Train:** RE 4634 | **Arr:** 2512062344 | **Dep:** N/A
- **Train:** RE 19940 | **Arr:** 2512062325 | **Dep:** N/A
- **Train:** RE 4586 | **Arr:** 2512062345 | **Dep:** N/A
- **Train:** STN 21525 | **Arr:** N/A | **Dep:** 2512062347