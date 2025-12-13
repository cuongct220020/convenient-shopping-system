from shared.shopping_shared.databases.fastapi_database import engine, Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis.v2.ingredient_api import ingredient_router
from apis.v2.recipe_api import recipe_router

app = FastAPI(
    title="Recipe Service",
    description="API for managing recipes and ingredients",
    version="0.2.0"
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