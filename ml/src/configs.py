import os
from enum import StrEnum, auto
from pathlib import Path
from typing import Final

# CTT Model Configs
CTT_TITLES_DATA_PATH = Path("data/ctt/titles.json")
CTT_CHANNELS_DATA_PATH = Path("data/ctt/channels.json")
CTT_MODEL_PATH = Path("models/ctt/model.pkl")
CTT_MODEL_URL: Final[str] = os.environ["CTT_MODEL_URL"]


class ContentTypeEnum(StrEnum):
    education = auto()
    entertainment = auto()
    moviesandreviews = "movies & reviews"
    music = auto()
    news = auto()
    programming = auto()
    pseudoeducation = "pseudo education"
    reaction = auto()
    shorts = auto()
    tech = auto()
    vlogs = auto()


CONTENT_TYPE_TAGS = [i.value for i in ContentTypeEnum]

# Channel Recommender System Configs
CHR_DATA_PATH = Path("data/chr/titles.json")
CHR_SYS_OBJ_PATH = Path("models/chr/chr_obj.pkl")
CHR_SYS_OBJ_URL: Final[str] = os.environ["CHR_SYS_OBJ_URL"]
