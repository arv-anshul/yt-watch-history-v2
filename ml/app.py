from fastapi import FastAPI

from src import ctt

app = FastAPI()

app.include_router(
    ctt.api.router,
    prefix="/ml/ctt",
    tags=["MLModel"],
)
