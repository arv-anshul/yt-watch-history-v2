"""
Whichever files/data were accepted by `pages/upload_data.py` page they must undergo
a basic validation. And those validation functions are written here.
"""

from __future__ import annotations

import polars as pl


def validate_watch_history_data(data: bytes) -> str | None:
    msg = None
    df = pl.read_json(
        data,
        schema={
            "title": pl.String,
            "titleUrl": pl.String,
            "subtitles": pl.List(pl.Struct({"name": pl.String, "url": pl.String})),
            "time": pl.Datetime,
            "activityControls": pl.List(pl.String),
        },
        infer_schema_length=1000,
    )
    if df.select(pl.all().is_null().sum().eq(df.height)).sum_horizontal().sum() > 0:
        msg = "Required columns are not in Watch History Data."
    return msg


def validate_subscription_data(data: bytes) -> str | None:
    msg = None
    req_cols = ("Channel Id", "Channel Url", "Channel Title")
    df = pl.read_csv(data)
    if not all(i in df.columns for i in req_cols):
        msg = f"Subscrition data doesn't have all required columns {req_cols}"
    return msg
