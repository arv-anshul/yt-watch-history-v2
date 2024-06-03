from fastapi import FastAPI

from src import channel_reco, ctt

app = FastAPI()

app.include_router(
    ctt.api.router,
    prefix="/ml/ctt",
    tags=["MLModel"],
)
app.include_router(
    channel_reco.api.router,
    prefix="/ml/channel_reco",
    tags=["RecommenderSystem"],
)
