import os
from pathlib import Path
from typing import Final

# User data configs
USER_WATCH_HISTORY_DATA_PATH = Path("data/user/watch-history.json")
USER_SUBSCRIPTIONS_DATA_PATH = Path("data/user/subscriptions.csv")
VIDEO_DETAILS_DATA_PATH = Path("data/user/video_details.parquet")

# APIs configs
BACKEND_API_URL: Final[str] = os.environ["BACKEND_API_URL"]
ML_API_URL: Final[str] = os.environ["ML_API_URL"]
