from __future__ import annotations

from datetime import timedelta
from typing import Any

import httpx
import polars as pl
import streamlit as st
from src.configs import (
    BACKEND_API_URL,
    USER_WATCH_HISTORY_DATA_PATH,
    VIDEO_DETAILS_DATA_PATH,
)

st.set_page_config("Fetch More Details", ":nerd_face:", "wide")


def _handel_api_respose_for_streamlit(
    res: httpx.Response,
    msg: str | None = None,
    stop: bool = True,
) -> None:
    if res.status_code not in (200, 204):
        st.error(msg or f"Error while API request [{res.status_code}]")
        st.stop() if stop else ...


def filter_available_ids(
    client: httpx.Client,
    data: list[dict[str, str | list[str]]],
) -> list[str] | None:
    res = client.post("/db/yt/channel/video/excludeExistingIds", json=data)
    _handel_api_respose_for_streamlit(res)
    return res.json() or None


def fetch_details_from_yt_api(
    client: httpx.Client,
    video_ids: list[str],
) -> list[dict[str, Any]] | None:
    res = client.post(
        "/yt/video/?n=400",
        headers={"x-yt-api-key": api_key},
        json=video_ids,
    )
    _handel_api_respose_for_streamlit(res)
    details = res.json()
    return details or None


def store_video_details_in_db(
    client: httpx.Client,
    video_details: list[dict[str, Any]],
) -> None:
    res = client.put("/db/yt/video/", json=video_details)
    _handel_api_respose_for_streamlit(
        res,
        "Error while storing video details into database.",
    )

    res = client.put("/db/yt/channel/video/usingVideosDetails", json=video_details)
    _handel_api_respose_for_streamlit(
        res,
        "Error while storing video details in Channels database.",
    )


def finally_request_videos_details_from_db(
    client: httpx.Client,
    video_ids: list[str],
) -> list[dict[str, Any]]:
    res = client.post("/db/yt/video/", json=video_ids)
    _handel_api_respose_for_streamlit(res)
    details = res.json()
    if not details:
        st.error("No video details found in database (in the end).", icon=":no_good:")
        st.stop()
    return details


def store_video_details_in_file(video_details: list[dict[str, Any]]) -> pl.LazyFrame:
    df = pl.from_dicts(video_details)
    df.write_parquet(VIDEO_DETAILS_DATA_PATH)
    return df.lazy()


@st.cache_resource
def load_watch_history_data() -> pl.LazyFrame:
    df = (
        pl.read_parquet(USER_WATCH_HISTORY_DATA_PATH.with_suffix(".parquet"))
        .lazy()
        .with_columns(
            pl.col("time").str.to_datetime(),
            pl.col("titleUrl").str.extract(r"v=(.?*)").alias("videoId"),
            pl.col("subtitles").list.get(0).struct.field("name").alias("channelTitle"),
        )
    )
    return df


if not USER_WATCH_HISTORY_DATA_PATH.with_suffix(".parquet").exists():
    st.switch_page("pages/Upload_Data.py")

if not VIDEO_DETAILS_DATA_PATH.exists():
    frequent_ids: list[str] | None = None
    with st.form("store-api-key"):
        api_key = st.text_input(
            "Enter YouTube API Key",
            type="password",
            placeholder="YouTube Data API Key",
        )
        last_n_days = st.number_input(
            "Fetch details of last (n) days",
            min_value=300,
            max_value=500,
            value="min",
            step=20,
            format="%d",
        )
        if not st.form_submit_button(use_container_width=True):
            st.stop()

    watch_history = load_watch_history_data()

    frequent_channels = (
        watch_history.drop_nulls("channelTitle")
        .group_by("channelTitle")
        .len()
        .filter(pl.col("len").gt(10))
        .collect()
        .get_column("channelTitle")
    )
    frequent_ids = (
        watch_history.filter(
            pl.col("time").gt(pl.max("time").sub(timedelta(days=last_n_days))),
        )
        .filter(pl.col("channelTitle").is_in(frequent_channels))
        .select(pl.col("videoId").unique())
        .collect()
        .get_column("videoId")
        .to_list()
    )

    if not frequent_ids:
        st.info("Not enough data to show analysis.", icon="🥹")
        st.stop()

    client = httpx.Client(base_url=BACKEND_API_URL)
    with st.spinner("Fetching and storing data..."):
        filtered_ids = filter_available_ids(
            client,
            watch_history.filter(
                pl.col("videoId").is_in(frequent_ids),
            )
            .drop_nulls("channelTitle")
            .group_by(
                pl.col("subtitles")
                .list.get(0)
                .struct.field("url")
                .str.strip_prefix("https://www.youtube.com/channel/")
                .alias("channelId"),
            )
            .agg(
                pl.col("channelTitle").first(),
                pl.col("videoId").unique().alias("videoIds"),
            )
            .collect()
            .to_dicts(),
        )

        if filtered_ids:
            details_from_yt_api = fetch_details_from_yt_api(client, filtered_ids)
            if details_from_yt_api:
                st.toast("Storing video details into database.", icon="🗂️")
                store_video_details_in_db(client, details_from_yt_api)
            else:
                st.toast("No video details to store.", icon="🗂️")
        else:
            st.toast("Nothing to fetched from YouTube API.", icon="🙅")

    st.toast("Requesting video details from database.", icon="🎥")
    video_details = finally_request_videos_details_from_db(client, frequent_ids)
    store_video_details_in_file(video_details)
    st.dataframe(video_details)
    st.balloons()

video_details = pl.read_parquet(VIDEO_DETAILS_DATA_PATH)
st.dataframe(video_details)
