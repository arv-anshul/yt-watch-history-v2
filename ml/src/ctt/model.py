from __future__ import annotations

import re
import string
from typing import TYPE_CHECKING

import emoji
import httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

from src.configs import CTT_MODEL_PATH, CTT_MODEL_URL

if TYPE_CHECKING:
    from sklearn.base import BaseEstimator


def preprocessor(s: str) -> str:
    """Preprocessor for Vectorizer"""
    s = re.sub(r"\b\w{1,3}\b", " ", s)
    s = s.translate(str.maketrans("", "", string.punctuation + string.digits))
    s = emoji.replace_emoji(s, "")
    s = re.sub(r"\s+", " ", s)
    return s


def get_model(model: BaseEstimator) -> Pipeline:
    vectorizer = TfidfVectorizer(
        preprocessor=preprocessor,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=7000,
    )
    return Pipeline([("vectorizer", vectorizer), ("model", model)])


def download_ctt_ml_model_from_url() -> None:
    """Download CTT model from URL and store it at its defined path."""
    response = httpx.get(CTT_MODEL_URL, timeout=5, follow_redirects=True)
    if not response.is_success:
        msg = f"Wrong status code from response [{response.status_code}]"
        raise httpx.HTTPStatusError(msg, request=response.request, response=response)
    CTT_MODEL_PATH.write_bytes(response.content)
