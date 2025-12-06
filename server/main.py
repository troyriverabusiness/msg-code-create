from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from server.routes import chat
from server.routes.travel import router as travel_router
from server.routes.example import router as example_router

app = FastAPI(title="Smart Travel Assistant API")

# Register routes
app.include_router(chat.router)
app.include_router(travel_router)
app.include_router(example_router)

# Mount static files for frontend
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def read_root():
    return FileResponse(str(static_dir / "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
