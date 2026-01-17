from contextlib import asynccontextmanager
from core.database import engine, Base
from core.config import settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from core.admin_middleware import AdminMiddleware
from apis.v2.ingredient_api import ingredient_router
from apis.v2.recipe_api import recipe_router
from core.messaging import kafka_manager
from messaging.consumers.component_existence_consumer import consume_component_existence_events
from messaging.consumers.group_tags_consumer import consume_group_tags_events
from core.caching import redis_manager
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await redis_manager.setup(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD
        )
        kafka_manager.setup(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    except Exception as e:
        raise

    tasks = [
        asyncio.create_task(consume_component_existence_events()),
        asyncio.create_task(consume_group_tags_events())
    ]

    yield

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    
    try:
        await kafka_manager.close()
        await redis_manager.close()
    except Exception as e:
        pass


app = FastAPI(
    title="Recipe Service",
    description="API for managing recipes and ingredients",
    version="0.2.0",
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
    openapi_url = "https://dichotienloi.com/docs/recipe-service/openapi.json"
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


app.add_middleware(AdminMiddleware)
app.include_router(ingredient_router)
app.include_router(recipe_router)


if __name__ == "__main__":
    import uvicorn, os
    workers = int(os.getenv('WORKERS', 1))
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=workers, reload=False, log_level="debug")