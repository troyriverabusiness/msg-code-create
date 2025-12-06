"""
Example Journey objects using the models from server/models/
"""
from server.models.journey import Journey
from server.models.train import Train
from server.models.station import Station
from server.models.station_change import StationChange

# Example 1: Direct journey from Frankfurt to Berlin (no changes)
journey1 = Journey(
    startStation=Station(name="Frankfurt Hauptbahnhof", eva="8000105"),
    endStation=Station(name="Berlin Hauptbahnhof", eva="8011160"),
    trains=[
        Train(
            trainNumber="ICE 1234",
            startLocation=Station(name="Frankfurt Hauptbahnhof", eva="8000105"),
            endLocation=Station(name="Berlin Hauptbahnhof", eva="8011160"),
            path=[
                Station(name="Frankfurt Hauptbahnhof", eva="8000105"),
                Station(name="Fulda", eva="8010060"),
                Station(name="Kassel-Wilhelmshöhe", eva="8010205"),
                Station(name="Göttingen", eva="8010159"),
                Station(name="Hannover Hauptbahnhof", eva="8010152"),
                Station(name="Wolfsburg", eva="8010340"),
                Station(name="Berlin Hauptbahnhof", eva="8011160")
            ],
            platform=8,
            wagons=[45, 52, 38, 61, 55, 48, 50, 43]
        )
    ],
    changes=None,
    totalTime=240,  # 4 hours in minutes
    description="Direct ICE connection from Frankfurt to Berlin"
)

# Example 2: Journey with one change (Frankfurt to Munich via Mannheim)
journey2 = Journey(
    startStation=Station(name="Frankfurt Hauptbahnhof", eva="8000105"),
    endStation=Station(name="München Hauptbahnhof", eva="8000261"),
    trains=[
        Train(
            trainNumber="ICE 5678",
            startLocation=Station(name="Frankfurt Hauptbahnhof", eva="8000105"),
            endLocation=Station(name="Mannheim Hauptbahnhof", eva="8000244"),
            path=[
                Station(name="Frankfurt Hauptbahnhof", eva="8000105"),
                Station(name="Darmstadt Hauptbahnhof", eva="8000080"),
                Station(name="Mannheim Hauptbahnhof", eva="8000244")
            ],
            platform=5,
            wagons=[30, 35, 28, 32, 40]
        ),
        Train(
            trainNumber="ICE 9012",
            startLocation=Station(name="Mannheim Hauptbahnhof", eva="8000244"),
            endLocation=Station(name="München Hauptbahnhof", eva="8000261"),
            path=[
                Station(name="Mannheim Hauptbahnhof", eva="8000244"),
                Station(name="Stuttgart Hauptbahnhof", eva="8000096"),
                Station(name="Ulm Hauptbahnhof", eva="8000170"),
                Station(name="Augsburg Hauptbahnhof", eva="8000001"),
                Station(name="München Hauptbahnhof", eva="8000261")
            ],
            platform=12,
            wagons=[50, 48, 55, 52, 60, 45, 58]
        )
    ],
    changes=[
        StationChange(
            station=Station(name="Mannheim Hauptbahnhof", eva="8000244"),
            timeMinutes=15
        )
    ],
    totalTime=285,  # 4 hours 45 minutes (including 15 min change time)
    description="Journey from Frankfurt to Munich with one change in Mannheim"
)

# Example 3: Journey with multiple changes (Frankfurt to Hamburg via Köln and Hannover)
journey3 = Journey(
    startStation=Station(name="Frankfurt Hauptbahnhof", eva="8000105"),
    endStation=Station(name="Hamburg Hauptbahnhof", eva="8002549"),
    trains=[
        Train(
            trainNumber="ICE 3456",
            startLocation=Station(name="Frankfurt Hauptbahnhof", eva="8000105"),
            endLocation=Station(name="Köln Hauptbahnhof", eva="8000207"),
            path=[
                Station(name="Frankfurt Hauptbahnhof", eva="8000105"),
                Station(name="Mainz Hauptbahnhof", eva="8000240"),
                Station(name="Koblenz Hauptbahnhof", eva="8000206"),
                Station(name="Bonn Hauptbahnhof", eva="8000044"),
                Station(name="Köln Hauptbahnhof", eva="8000207")
            ],
            platform=3,
            wagons=[42, 38, 45, 40, 35]
        ),
        Train(
            trainNumber="ICE 7890",
            startLocation=Station(name="Köln Hauptbahnhof", eva="8000207"),
            endLocation=Station(name="Hannover Hauptbahnhof", eva="8010152"),
            path=[
                Station(name="Köln Hauptbahnhof", eva="8000207"),
                Station(name="Dortmund Hauptbahnhof", eva="8000085"),
                Station(name="Bielefeld Hauptbahnhof", eva="8000036"),
                Station(name="Hannover Hauptbahnhof", eva="8010152")
            ],
            platform=7,
            wagons=[48, 52, 45, 50, 55, 42]
        ),
        Train(
            trainNumber="ICE 2468",
            startLocation=Station(name="Hannover Hauptbahnhof", eva="8010152"),
            endLocation=Station(name="Hamburg Hauptbahnhof", eva="8002549"),
            path=[
                Station(name="Hannover Hauptbahnhof", eva="8010152"),
                Station(name="Hamburg Hauptbahnhof", eva="8002549")
            ],
            platform=4,
            wagons=[60, 58, 55, 62, 65, 60, 58]
        )
    ],
    changes=[
        StationChange(
            station=Station(name="Köln Hauptbahnhof", eva="8000207"),
            timeMinutes=20
        ),
        StationChange(
            station=Station(name="Hannover Hauptbahnhof", eva="8010152"),
            timeMinutes=10
        )
    ],
    totalTime=360,  # 6 hours (including 30 min total change time)
    description="Journey from Frankfurt to Hamburg with changes in Köln and Hannover"
)

# Print examples
if __name__ == "__main__":
    print("Example Journey 1 (Direct):")
    print(journey1.model_dump_json(indent=2))
    print("\n" + "="*50 + "\n")
    
    print("Example Journey 2 (One change):")
    print(journey2.model_dump_json(indent=2))
    print("\n" + "="*50 + "\n")
    
    print("Example Journey 3 (Multiple changes):")
    print(journey3.model_dump_json(indent=2))