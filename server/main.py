from fastapi import FastAPI
from routes.example import router as example_router
from routes import chat

app = FastAPI()

# Register routes
app.include_router(example_router)
app.include_router(chat.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
