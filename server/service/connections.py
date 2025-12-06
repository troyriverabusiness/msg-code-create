from server.examples import journey_examples
from server.routes.connections import ConnectionsRequest, ConnectionsResponse


def get_connections_example(request: ConnectionsRequest) -> ConnectionsResponse:
    # TODO: Implement actual connection logic
    return ConnectionsResponse(journeys=[journey_examples.journey1, journey_examples.journey2])


def get_connections(request: ConnectionsRequest) -> ConnectionsResponse:
    # TODO: Implement actual connection logic
    return ConnectionsResponse(journeys=[])