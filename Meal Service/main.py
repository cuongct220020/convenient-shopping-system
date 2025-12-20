from contextlib import asynccontextmanager
from database import engine, Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis.v1.meal_api import meal_router
from messaging.manager import kafka_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Startup
    kafka_manager.setup("localhost:9092")
    tasks = [

    ]

    yield

    #Shutdown
    for task in tasks:
        task.cancel()
    await kafka_manager.close()

app = FastAPI(
    title="Meal Service",
    description="API for managing meals",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meal_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=False, log_level="debug")