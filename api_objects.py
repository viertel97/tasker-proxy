import os
from typing import Optional

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
    morning_meditation: bool = False
    meditation_start_ms: int
    meditation_end_ms: int
    yoga_start_ms: int
    yoga_end_ms: int


class reading_session(BaseModel):
    title: str
    reading_length: float
    page_difference: float
    reading_type: str
    finished: Optional[bool] = False
    reading_start_ms: int
    reading_end_ms: int


class timer(BaseModel):
    context: str
    duration: float
