from contextlib import asynccontextmanager
from database import engine, Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis.v1.plan_api import plan_router
from apis.v1.storage_api import storage_router
from apis.v1.storable_unit_api import storable_unit_router
from tasks.scheduler import setup_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = setup_scheduler()
    scheduler.start()

    yield

    scheduler.shutdown()

app = FastAPI(
    title="Shopping & Storage Service",
    description="API for managing food storages and shopping plans",
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

app.include_router(plan_router)
app.include_router(storage_router)
app.include_router(storable_unit_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False, log_level="debug")