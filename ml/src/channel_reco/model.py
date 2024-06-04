from __future__ import annotations

import re
import string
from typing import TYPE_CHECKING, Self

import polars as pl
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .data import preprocess

if TYPE_CHECKING:
    import scipy.sparse as sp


def text_preprocessor(s: str) -> str:
    s = re.sub(r"\b\w{1,3}\b", " ", s)
    s = s.translate(str.maketrans("", "", string.punctuation + string.digits))
    s = re.sub(r"\s+", " ", s)
    return s


class ChannelRecommenderSystem:
    _req_cols = ("channelId", "channelTitle", "input")

    def __init__(self, data: pl.LazyFrame) -> None:
        if not all(col in data.columns for col in self._req_cols):
            msg = f"data must have required cols {self._req_cols}"
            raise pl.ColumnNotFoundError(msg)
        self.data = data
        self.data_height = self.data.collect().height

        self._transformer = TfidfVectorizer(
            preprocessor=text_preprocessor,
            stop_words="english",
            ngram_range=(1, 1),
            strip_accents="ascii",
        )
        self.transformed_data: sp.spmatrix
        self.channel_ids_order: pl.Series

    def fit(self) -> Self:
        _data = self.data.select("channelId", "input").collect()
        self.channel_ids_order = _data.get_column("channelId")
        self.transformed_data = self._transformer.fit_transform(
            _data.get_column("input"),
        )
        return self

    def recommend(self, data: pl.LazyFrame) -> pl.LazyFrame:
        if data.select(pl.n_unique("channelId")).collect().item() > 1:
            raise ValueError("data must contains only one channel")
        preprocessed_data = preprocess(data).collect()
        similarity = pl.LazyFrame(
            {
                "channelId": self.channel_ids_order,
                "similarity": cosine_similarity(
                    self.transformed_data,
                    self._transformer.transform(preprocessed_data.get_column("input")),
                ).ravel(),
            },
        )
        return self.data.drop("input").join(similarity, on="channelId")


if __name__ == "__main__":
    import joblib

    from src.configs import CHR_DATA_PATH, CHR_SYS_OBJ_PATH

    df = pl.read_json(CHR_DATA_PATH)
    data = preprocess(df.lazy())

    ch_reco = ChannelRecommenderSystem(data)
    ch_reco.fit()

    joblib.dump(ch_reco, CHR_SYS_OBJ_PATH)
