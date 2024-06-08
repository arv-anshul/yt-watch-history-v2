from __future__ import annotations

import re
import string
from typing import TYPE_CHECKING, Self

import joblib
import polars as pl
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

from src.configs import CTT_MODEL_PATH

from .data import preprocess

if TYPE_CHECKING:
    from pathlib import Path


def text_preprocessor(s: str) -> str:
    """Preprocessor for Vectorizer"""
    s = re.sub(r"\b\w{1,3}\b", " ", s)
    s = s.translate(str.maketrans("", "", string.punctuation + string.digits))
    s = re.sub(r"\s+", " ", s)
    return s


class CttPredictorModel:
    _req_cols = (
        "channelId",
        "channelTitle",
        "title",
        "tags",
        "contentType",
    )

    def __init__(self, data: pl.LazyFrame) -> None:
        if not all(col in data.columns for col in self._req_cols):
            msg = f"data must have required cols {self._req_cols}"
            raise pl.ColumnNotFoundError(msg)
        self.data = data.select(self._req_cols).pipe(preprocess)

    def fit(self) -> Self:
        self.transformer = TfidfVectorizer(
            preprocessor=text_preprocessor,
            stop_words="english",
            ngram_range=(1, 1),
            strip_accents="ascii",
            lowercase=False,
        )
        self.pipeline = make_pipeline(
            self.transformer,
            MultinomialNB(alpha=0.2),
        )

        _data = self.data.collect()
        self.pipeline.fit(
            _data.get_column("input"),
            _data.get_column("contentType"),
        )
        return self

    def predict(self, data: pl.LazyFrame) -> pl.LazyFrame:
        """
        data must have `'videoId', 'title', 'tags'` columns for prediction.
        """
        _data = data.with_columns(
            pl.col("title")
            .add(pl.col("tags").list.join(" "))
            .str.to_lowercase()
            .alias("input"),
        ).collect()
        return _data.with_columns(
            pl.Series(
                "contentType",
                self.pipeline.predict(_data.get_column("input")),
                pl.UInt16(),
            ),
        ).lazy()

    def dump(self, path: Path | None = None) -> None:
        path = path or CTT_MODEL_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)


if __name__ == "__main__":
    from src.configs import CTT_CHANNELS_DATA_PATH, CTT_TITLES_DATA_PATH

    raw_data = (
        pl.read_json(CTT_CHANNELS_DATA_PATH)
        .join(
            pl.read_json(CTT_TITLES_DATA_PATH),
            on=["channelId", "channelTitle"],
        )
        .lazy()
    )
    ctt_model = CttPredictorModel(raw_data)
    ctt_model.fit()
    ctt_model.dump()
