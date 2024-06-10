from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import polars as pl
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.configs import CTT_MODEL_PATH, CTT_MODEL_URL, ContentTypeEnum
from src.utils import load_obj_from_path

if TYPE_CHECKING:
    from src.ctt.model import CttPredictorModel

router = APIRouter()


@lru_cache(1)
def load_model_from_path() -> CttPredictorModel:
    model = load_obj_from_path(CTT_MODEL_URL, CTT_MODEL_PATH)
    return model


class CttInputData(BaseModel):
    title: str
    tags: list[str]
    videoId: str


class CttPrediction(BaseModel):
    videoId: str
    contentTypePred: ContentTypeEnum


@router.post(
    "/predict",
    description="Make prediction using list of JSON data.",
    response_model=list[CttPrediction],
)
async def predict(
    data: list[CttInputData],
    model: CttPredictorModel = Depends(load_model_from_path),
):
    df = pl.from_dicts([i.model_dump() for i in data]).lazy()
    prediction = await model.predict(df).collect_async()
    return prediction.to_dicts()
