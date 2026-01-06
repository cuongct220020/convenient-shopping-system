from contextlib import asynccontextmanager
from core.database import engine, Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.head_chef_middleware import HeadChefMiddleware
from apis.v1.meal_api import meal_router
from tasks.scheduler import setup_scheduler
from shopping_shared.caching.redis_manager import redis_manager
from core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Redis connection
    await redis_manager.setup(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD
    )

    scheduler = setup_scheduler()
    scheduler.start()

    yield

    scheduler.shutdown()
    await redis_manager.close()

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

# Add head chef middleware to enforce head chef role for meal command and transition operations
app.add_middleware(HeadChefMiddleware)

app.include_router(meal_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="debug")