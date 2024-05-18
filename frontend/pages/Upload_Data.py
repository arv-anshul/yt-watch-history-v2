from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl
import streamlit as st
from src.configs import (
    USER_SUBSCRIPTIONS_DATA_PATH,
    USER_WATCH_HISTORY_DATA_PATH,
)
from src.upload_data_validator import (
    validate_subscription_data,
    validate_watch_history_data,
)

if TYPE_CHECKING:
    from collections.abc import Callable

st.set_page_config("Upload Data", ":card_index_dividers:", "wide")

PATHS_DICT: dict[str, tuple[Path, Callable]] = {
    "Watch Histrory Data": (
        USER_WATCH_HISTORY_DATA_PATH,
        validate_watch_history_data,
    ),
    "Channel Subscriptions Data": (
        USER_SUBSCRIPTIONS_DATA_PATH,
        validate_subscription_data,
    ),
}


def store_uploaded_data(path: Path, data: bytes) -> None:
    df: pl.DataFrame = getattr(pl, "read_" + path.suffix[1:])(data)
    df.write_parquet(path.with_suffix(".parquet"))


choose = st.selectbox("Choose to upload", PATHS_DICT.keys())
if not choose:
    st.error("Please select to upload file.")
    st.stop()

chosen_path, validation_func = PATHS_DICT[choose]
chosen_path_pq = chosen_path.with_suffix(".parquet")
if chosen_path_pq.exists():
    l, r = st.columns(2)
    l.button(
        "Delete Data",
        on_click=chosen_path_pq.unlink,
        type="primary",
        use_container_width=True,
    )
    r.download_button(
        "Download Data",
        chosen_path_pq.read_bytes(),
        chosen_path.name,
        type="primary",
        use_container_width=True,
    )
    st.stop()

with st.form("upload_data", clear_on_submit=True):
    file = st.file_uploader(f"Upload {choose!r} file", chosen_path.suffix)
    if st.form_submit_button("Upload", "Upload selected file!"):
        if not file:
            st.toast("Please select file!", icon="❗")
            st.stop()
        chosen_path.parent.mkdir(parents=True, exist_ok=True)
        file_data = file.read()
        if Path(file.name).suffix != chosen_path.suffix:
            st.error(f"Upload file with extension {chosen_path.suffix!r}")
            st.stop()
        if err_msg := validation_func(file_data):
            st.error(err_msg, icon="❌")
            st.stop()
        store_uploaded_data(chosen_path, file_data)
        st.success(f"{choose} uploaded successfully!", icon="😎")
