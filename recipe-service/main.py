from contextlib import asynccontextmanager
from core.database import engine, Base
from core.config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.admin_middleware import AdminMiddleware
from apis.v2.ingredient_api import ingredient_router
from apis.v2.recipe_api import recipe_router
from messaging.manager import kafka_manager
from messaging.consumers.component_existence_consumer import consume_component_existence_events
from messaging.consumers.group_tags_consumer import consume_group_tags_events
from shopping_shared.caching.redis_manager import redis_manager
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Redis connection
    await redis_manager.setup(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD
    )

    kafka_manager.setup(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

    tasks = [
        asyncio.create_task(consume_component_existence_events()),
        asyncio.create_task(consume_group_tags_events())
    ]

    yield

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    await kafka_manager.close()
    await redis_manager.close()

app = FastAPI(
    title="Recipe Service",
    description="API for managing recipes and ingredients",
    version="0.2.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AdminMiddleware)

app.include_router(ingredient_router)
app.include_router(recipe_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="debug")