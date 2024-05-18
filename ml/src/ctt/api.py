from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import joblib
import polars as pl
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.configs import CTT_MODEL_PATH, ContentTypeEnum

if TYPE_CHECKING:
    from sklearn.pipeline import Pipeline

router = APIRouter()


@lru_cache(1)
def load_model_from_path() -> Pipeline:
    if not CTT_MODEL_PATH.exists():
        raise HTTPException(404, {"error": "Ctt Model not found."})
    with CTT_MODEL_PATH.open("rb") as f:
        return joblib.load(f)


class CttInputData(BaseModel):
    title: str
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
    model: Pipeline = Depends(load_model_from_path),
):
    df = pl.from_dicts([i.model_dump() for i in data])
    prediction = model.predict(df["title"].to_list())
    return df.with_columns(
        pl.lit(prediction).str.to_lowercase().alias("contentTypePred"),
    ).to_dicts()
