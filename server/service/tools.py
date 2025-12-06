from typing import List, Dict, Any
from .graph_service import GraphService
from .travel_service import TravelService

# Initialize services
graph_service = GraphService()
travel_service = TravelService()

# Tool Definitions (Bedrock Format)
FIND_INTERMEDIATE_STATIONS_TOOL = {
    "toolSpec": {
        "name": "find_intermediate_stations",
        "description": "Finds major stations (Hbf) located between an origin and a destination. Use this to suggest stopovers or discover routes.",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Name of the start station (e.g. 'Frankfurt')"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Name of the destination station (e.g. 'Munich')"
                    }
                },
                "required": ["origin", "destination"]
            }
        }
    }
}

GET_TRIPS_TOOL = {
    "toolSpec": {
        "name": "get_trips",
        "description": "Finds concrete train connections between two stations at a specific time.",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                    "time": {"type": "string", "description": "Departure time (HH:MM)"}
                },
                "required": ["origin", "destination"]
            }
        }
    }
}

TOOLS = [FIND_INTERMEDIATE_STATIONS_TOOL, GET_TRIPS_TOOL]

def execute_tool(name: str, args: Dict[str, Any]) -> Any:
    """Executes a tool by name with given arguments."""
    if name == "find_intermediate_stations":
        return graph_service.find_intermediate_stations(
            args.get("origin"), 
            args.get("destination")
        )
    elif name == "get_trips":
        routes = travel_service.find_routes(
            args.get("origin"),
            args.get("destination"),
            args.get("time")
        )
        # Convert RouteOption objects to dicts
        return [r.model_dump() for r in routes]
    
    raise ValueError(f"Unknown tool: {name}")
