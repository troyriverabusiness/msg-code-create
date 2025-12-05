from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import RouteRequest, RouteOption, StationInfo, RealTimeStatus
from .services.travel_service import TravelService

app = FastAPI(title="Smart Travel Assistant API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service Injection (Simple singleton for now)
travel_service = TravelService()

@app.get("/api/v1/status")
def get_status():
    return {"status": "ok", "service": "Travel Assistant Backend"}

@app.get("/api/v1/status/ticker", response_model=RealTimeStatus)
def get_real_time_status():
    messages = travel_service.simulation.get_messages()
    return RealTimeStatus(
        messages=messages,
        alternatives=[]
    )

@app.post("/api/v1/route", response_model=list[RouteOption])
def find_route(request: RouteRequest):
    routes = travel_service.find_routes(request.start, request.end, request.time)
    if not routes:
        return []
    return routes

@app.get("/api/v1/station/{name}", response_model=StationInfo)
def get_station_info(name: str):
    info = travel_service.get_station_info(name)
    if not info:
        raise HTTPException(status_code=404, detail="Station not found")
    return info
