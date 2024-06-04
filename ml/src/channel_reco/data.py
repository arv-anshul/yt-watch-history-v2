from __future__ import annotations

import polars as pl


def preprocess(raw_data: pl.LazyFrame) -> pl.LazyFrame:
    return (
        raw_data.with_columns(
            pl.col("tags").list.unique(),
        )
        .explode("tags")
        .drop_nulls("tags")
        .group_by("channelId", "channelTitle")
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
        .select("channelId", "channelTitle", "input")
    )
