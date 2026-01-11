from contextlib import asynccontextmanager
from core.database import engine, Base
from core.config import settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from core.head_chef_middleware import HeadChefMiddleware
from core.messaging import kafka_manager
from apis.v1.meal_api import meal_router
from tasks.scheduler import setup_scheduler
from shopping_shared.caching.redis_manager import redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.setup(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD
    )

    kafka_manager.setup(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

    scheduler = setup_scheduler()
    scheduler.start()

    yield

    scheduler.shutdown()
    await kafka_manager.close()
    await redis_manager.close()


app = FastAPI(
    title="Meal Service",
    description="API for managing meals",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    openapi_url = "https://dichotienloi.com/docs/meal-service/openapi.json"
    html = f"""<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <title>{app.title} - Swagger UI</title>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
    SwaggerUIBundle({{
        url: '{openapi_url}',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
        layout: "BaseLayout"
    }})
    </script>
</body>
</html>"""
    return HTMLResponse(content=html)


app.add_middleware(HeadChefMiddleware)
app.include_router(meal_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="debug")