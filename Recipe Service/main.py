from contextlib import asynccontextmanager
from core.database import engine, Base
from core.es import init_es, close_es
from core.config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis.v2.ingredient_api import ingredient_router
from apis.v2.recipe_api import recipe_router
from messaging.manager import kafka_manager
from messaging.consumers.ingredient_consumer import consume_ingredient_events
from messaging.consumers.recipe_consumer import consume_recipe_events
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_es()
    kafka_manager.setup(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

    tasks = [
        asyncio.create_task(consume_ingredient_events()),
        asyncio.create_task(consume_recipe_events())
    ]

    yield

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    await kafka_manager.close()
    await close_es()

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

app.include_router(ingredient_router)
app.include_router(recipe_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False, log_level="debug")