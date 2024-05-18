from __future__ import annotations

import os
from typing import Final

# Database Configs
MONGODB_URL: Final[str] = os.environ["MONGODB_URL"]
DB_YOUTUBE: Final = "YoutubeDB"
COLLECTION_YT_VIDEO: Final = "YtVideosDetails"
COLLECTION_YT_CHANNEL_VIDEO: Final = "YtChannelsVideoIds"
