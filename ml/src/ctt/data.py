from __future__ import annotations

import polars as pl

from src.configs import CONTENT_TYPE_TAGS


def data_preprocessor(data: pl.LazyFrame) -> pl.LazyFrame:
    req_cols = {"channelId", "contentType", "title"}
    data_cols = data.columns
    if not all(i in data_cols for i in req_cols):
        msg = f"X must contains columns {list(req_cols - set(data_cols))}"
        raise pl.ColumnNotFoundError(msg)
    return (
        data
        # Data Cleaning
        .with_columns(
            pl.col("contentType").replace(
                CONTENT_TYPE_TAGS,
                range(len(CONTENT_TYPE_TAGS)),
            ),
        )
        # Data Transformation
        .group_by("contentType")
        .agg("title")
        .with_columns(pl.col("title").list.join(" "))
    )
