import httpx
import polars as pl
import streamlit as st
from src.configs import ML_API_URL, VIDEO_DETAILS_DATA_PATH

st.set_page_config("CTT Analysis", ":robot:", "wide")


def predict_ctt_of_video_title(data: list[dict[str, str]]) -> list[dict[str, str]]:
    try:
        res = httpx.post(ML_API_URL + "/ml/ctt/predict", json=data)
    except httpx.ConnectError:
        st.error("API is not running. Check, it is running or not.", icon="🧑‍💻")
        st.stop()
    if res.status_code != 200:
        st.error(f"Response status code [{res.status_code}] from ML API", icon="❌")
        st.stop()
    return res.json()


@st.cache_resource
def load_watch_history_data() -> pl.LazyFrame:
    df = pl.scan_parquet(VIDEO_DETAILS_DATA_PATH)
    ctt_df = pl.from_dicts(
        predict_ctt_of_video_title(
            df.select(
                pl.col("title"),
                pl.col("id").alias("videoId"),
                pl.col("tags").fill_null([""]),
            )
            .collect()
            .to_dicts(),
        ),
    ).lazy()
    return df.join(ctt_df, left_on="id", right_on="videoId")


if not VIDEO_DETAILS_DATA_PATH.exists():
    st.switch_page("pages/Upload_Data.py")

watch_history = load_watch_history_data()
st.dataframe(watch_history.head(20).collect(), use_container_width=True)
