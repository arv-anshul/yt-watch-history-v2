from pathlib import Path
from typing import Any

import httpx
import joblib
from fastapi import HTTPException


def download_obj_from_url(url: str, path: Path) -> None:
    """Download objects from URL and store it at given path."""
    response = httpx.get(url, timeout=5, follow_redirects=True)
    if not response.is_success:
        msg = f"Wrong status code from response [{response.status_code}]"
        raise httpx.HTTPStatusError(msg, request=response.request, response=response)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)


def load_obj_from_path(url: str, path: Path) -> Any:
    """
    Provide URL to download the object from internet if it doesn't present on path.
    """
    if not path.exists():
        download_obj_from_url(url, path)
    if not path.exists():
        raise HTTPException(422, "Model doesn't download properly.")
    return joblib.load(path)
