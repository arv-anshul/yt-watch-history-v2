import polars as pl
import streamlit as st
from plotly import express as px
from src.configs import USER_WATCH_HISTORY_DATA_PATH

st.set_page_config("YouTube Watch History Analysis", ":bar_chart:", "wide")

# Toggle button to dic=splay captions
TOGGLE_CAPTION = st.sidebar.toggle("Toggle Plots Caption", True)

if not USER_WATCH_HISTORY_DATA_PATH.with_suffix(".parquet").exists():
    st.switch_page("pages/Upload_Data.py")


@st.cache_resource
def load_watch_history_data() -> pl.LazyFrame:
    return pl.read_parquet(USER_WATCH_HISTORY_DATA_PATH.with_suffix(".parquet")).lazy()


df = load_watch_history_data()

# Data datetime range
l, r = st.columns(2)
_temp = (
    df.with_columns(
        pl.col("time").str.to_datetime(),
    )
    .select(
        pl.min("time").dt.strftime("%b, %y").alias("min"),
        pl.max("time").dt.strftime("%b, %y").alias("max"),
    )
    .collect()
    .row(0)
)
l.metric(
    "Time Range of Dataset",
    f"{_temp[0]} - {_temp[1]}",
)
r.metric(
    "No. of Days of Data Present",
    df.select(pl.col("time").str.to_datetime().dt.date().n_unique()).collect().item(),
)

# No. Of Channels You Watches Frequently
fig_left = px.pie(
    values=(
        df.with_columns(
            pl.col("subtitles").list.get(0).struct.field("name").alias("channelTitle"),
        )
        .select(
            pl.col("channelTitle").value_counts(),
        )
        .unnest("channelTitle")
        .select(
            pl.col("count").ge(7).sum().alias("ge"),
            pl.col("count").is_between(2, 6).sum().alias("lt"),
        )
        .collect()
        .row(0)
    ),
    names=["Frequently Watched Channel (>=7)", "Non Freq. Channel [2,6]"],
    title="% of channels you watches frequently",
)

# Count Of Video Watched From Different Activity
fig_right = px.pie(
    values=(
        df.with_columns(
            pl.col("activityControls")
            .list.contains("Web & App Activity")
            .alias("fromWebAppActivity"),
            pl.col("activityControls")
            .list.contains("YouTube search history")
            .alias("fromYtSearchHistActivity"),
            pl.col("activityControls")
            .list.contains("YouTube watch history")
            .alias("fromYtWatchHistActivity"),
        )
        .select(
            "fromYtSearchHistActivity",
            "fromYtWatchHistActivity",
            "fromWebAppActivity",
        )
        .sum()
        .collect()
        .row(0)
    ),
    names=("fromYtSearchHistActivity", "fromYtWatchHistActivity", "fromWebAppActivity"),
    title="Count of videos you have watched from different activity",
)

# Plot both pie chart left and right respectively
l.plotly_chart(fig_left, True)
r.plotly_chart(fig_right, True)
if TOGGLE_CAPTION:
    l.caption(
        "Pie chart showing the distribution of frequently watched channels and "
        "less watched channels, categorized by the no. of videos being watched. "
        "Offering an overview of the user's channel engagement pattern.",
    )
    r.caption(
        "Chart visualizes the count of videos watched based on different activities.",
    )

# Top 7 Channel
fig = px.bar(
    df.with_columns(
        pl.col("subtitles").list.get(0).struct.field("name").alias("channelTitle"),
    )
    .select(
        pl.col("channelTitle").value_counts(sort=True).head(7),
    )
    .unnest("channelTitle")
    .collect(),
    "channelTitle",
    "count",
    title="Top 7 channels you have watched",
)
st.plotly_chart(fig, True)
if TOGGLE_CAPTION:
    st.caption(
        "Bar chart displaying the top 7 channels user have watched based on the "
        "count of videos viewed from each channel. Provides a quick overview of "
        "user's most frequently visited channels.",
    )
