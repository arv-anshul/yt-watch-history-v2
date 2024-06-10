from __future__ import annotations

import polars as pl

from src.configs import CONTENT_TYPE_TAGS


def preprocess(data: pl.LazyFrame) -> pl.LazyFrame:
    return (
        data
        # Data Cleaning
        .with_columns(
            pl.col("tags").list.unique(),
        )
        .explode("tags")
        .drop_nulls("tags")
        .with_columns(
            pl.col("contentType")
            .str.to_lowercase()
            .replace(
                CONTENT_TYPE_TAGS,
                range(len(CONTENT_TYPE_TAGS)),
                return_dtype=pl.UInt16(),
            ),
        )
        # Data Transformation
        .group_by("contentType")
        .agg(
            pl.col("title").unique(),
            pl.col("tags").flatten().unique(),
        )
        .with_columns(
            pl.col("title")
            .list.join(" ")
            .add(pl.col("tags").list.join(" "))
            .str.to_lowercase()
            .alias("input"),
        )
        .select("input", "contentType")
    )
