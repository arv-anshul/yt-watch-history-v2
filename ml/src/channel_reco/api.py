from functools import lru_cache
from typing import Self

import polars as pl
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.channel_reco.model import ChannelRecommenderSystem
from src.configs import CHR_SYS_OBJ_PATH, CHR_SYS_OBJ_URL
from src.utils import load_obj_from_path

router = APIRouter()


@lru_cache(1)
def load_ch_reco_obj_from_path() -> ChannelRecommenderSystem:
    model = load_obj_from_path(CHR_SYS_OBJ_URL, CHR_SYS_OBJ_PATH)
    return model


class ChRecoInput(BaseModel):
    channelId: str
    channelTitle: str
    title: str
    tags: list[str]

    @classmethod
    def to_polars(cls, data: list[Self]) -> pl.LazyFrame:
        return pl.from_dicts([i.model_dump() for i in data]).lazy()


class ChRecoOutput(BaseModel):
    channelId: str
    channelTitle: str
    similarity: float


@router.post(
    "/recommend",
    response_model=list[ChRecoOutput],
)
async def recommend(
    data: list[ChRecoInput],
    sort: bool = False,
    ch_reco: ChannelRecommenderSystem = Depends(load_ch_reco_obj_from_path),
):
    ldf = ChRecoInput.to_polars(data)
    recommendation = ch_reco.recommend(ldf)
    if sort:
        recommendation = recommendation.sort("similarity", descending=True)
    return (await recommendation.collect_async()).to_dicts()
