import os

from loguru import logger
from pydantic import BaseModel

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


class meditation_session(BaseModel):
    warm_up_seconds: int
    meditation_seconds: int
    yoga_seconds: int


class reading_session(BaseModel):
    title: str
    reading_length: float
    page_difference: float
    reading_type: str


class standup(BaseModel):
    duration: float
