from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from server.routes import chat
from server.routes.travel import router as travel_router

app = FastAPI(title="Smart Travel Assistant API")

# Register routes
app.include_router(chat.router)
app.include_router(travel_router)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="server/static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("server/static/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
