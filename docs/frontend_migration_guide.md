# Frontend Migration Guide: Multi-Leg Routing

We have updated the backend to support multi-leg journeys (transfers). This introduces breaking changes to the `Journey` data model.

## 1. Data Model Changes

The `Journey` object no longer has a flat list of `trains`. Instead, it has a list of `legs`.

### Old Structure
```json
{
  "id": "...",
  "trains": [
    { "name": "ICE 123", ... },
    { "name": "RE 456", ... }
  ],
  "changes": [
    { "station": "...", "timeMinutes": 10 }
  ]
}
```

### New Structure
```json
{
  "journeys": [
    {
      "id": "j_12345",
      "startStation": {
        "name": "Frankfurt (Main) Hbf",
        "eva": "8000105"
      },
      "endStation": {
        "name": "München Hbf",
        "eva": "8000261"
      },
      "transfers": 1,
      "totalTime": 240,
      "description": "1 Transfer",
      "legs": [
        {
          "origin": {
            "name": "Frankfurt (Main) Hbf",
            "eva": "8000105"
          },
          "destination": {
            "name": "Mannheim Hbf",
            "eva": "8000244"
          },
          "departureTime": "10:00:00",
          "arrivalTime": "10:45:00",
          "train": {
            "name": "ICE 123",
            "trainNumber": "123",
            "startLocation": { "name": "Frankfurt (Main) Hbf", "eva": "8000105" },
            "endLocation": { "name": "Mannheim Hbf", "eva": "8000244" },
            "departureTime": "10:00:00",
            "arrivalTime": "10:45:00",
            "path": [],
            "platform": 5,
            "wagons": []
          }
        },
        {
          "origin": {
            "name": "Mannheim Hbf",
            "eva": "8000244"
          },
          "destination": {
            "name": "München Hbf",
            "eva": "8000261"
          },
          "departureTime": "11:00:00",
          "arrivalTime": "14:00:00",
          "train": {
            "name": "ICE 555",
            "trainNumber": "555",
            "startLocation": { "name": "Mannheim Hbf", "eva": "8000244" },
            "endLocation": { "name": "München Hbf", "eva": "8000261" },
            "departureTime": "11:00:00",
            "arrivalTime": "14:00:00",
            "path": [],
            "platform": 3,
            "wagons": []
          }
        }
      ]
    }
  ]
}
```

## 2. Rendering Logic

### Displaying a Journey
Iterate through `journey.legs`.
- **Leg 1**: Show Train Name, Origin, Departure Time.
- **Transfer**: If there is a next leg, calculate transfer time (`nextLeg.departureTime - currentLeg.arrivalTime`) and display it.
- **Leg N**: Show Train Name, Destination, Arrival Time.

### Example React Component (Pseudo-code)
```jsx
{journey.legs.map((leg, index) => (
  <div key={index}>
    <div className="leg">
      <span className="time">{leg.departureTime}</span>
      <span className="station">{leg.origin.name}</span>
      <span className="train">{leg.train.name}</span>
    </div>
    
    {/* Show Transfer if not last leg */}
    {index < journey.legs.length - 1 && (
      <div className="transfer">
        Transfer at {leg.destination.name}
      </div>
    )}
    
    {/* Show Final Arrival for last leg */}
    {index === journey.legs.length - 1 && (
      <div className="leg">
        <span className="time">{leg.arrivalTime}</span>
        <span className="station">{leg.destination.name}</span>
      </div>
    )}
  </div>
))}
```

## 3. API Endpoints
The endpoint `/connections` (or wherever you fetch journeys) now returns this new structure. No URL changes.
