from __future__ import annotations

from typing import TYPE_CHECKING

from sklearn.naive_bayes import MultinomialNB

from .data import data_preprocessor
from .model import get_model

if TYPE_CHECKING:
    import polars as pl
    from sklearn.pipeline import Pipeline


def train_ctt_model(raw_data: pl.LazyFrame) -> Pipeline:
    data = data_preprocessor(raw_data).collect()
    model = get_model(MultinomialNB(alpha=0.2))
    model.fit(data["title"], data["contentType"])
    return model


if __name__ == "__main__":
    # Demostrate training pipeline working
    import joblib
    import polars as pl

    from src.configs import CTT_CHANNELS_DATA_PATH, CTT_MODEL_PATH, CTT_TITLES_DATA_PATH

    raw_data = (
        pl.read_json(CTT_CHANNELS_DATA_PATH)
        .join(
            pl.read_json(CTT_TITLES_DATA_PATH),
            on="channelId",
        )
        .lazy()
    )

    print(f"Training starts at {__package__}")
    model = train_ctt_model(raw_data)

    CTT_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CTT_MODEL_PATH.open("wb") as f:
        joblib.dump(model, f)
