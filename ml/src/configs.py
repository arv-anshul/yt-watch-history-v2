from enum import StrEnum, auto
from pathlib import Path

# CTT Model Configs
CTT_TITLES_DATA_PATH = Path("data/ctt/titles.json")
CTT_CHANNELS_DATA_PATH = Path("data/ctt/channels.json")
CTT_MODEL_PATH = Path("models/ctt/model.pkl")


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