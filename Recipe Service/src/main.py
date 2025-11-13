from core.database import engine, Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router
from models.recipe import Recipe, RecipeCountableIngredient, RecipeUncountableIngredient

app = FastAPI(
    title="Recipe Service",
    description="API for managing recipes and meals",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)