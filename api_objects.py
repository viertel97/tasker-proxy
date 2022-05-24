import os
from typing import List, Optional

from loguru import logger
from pydantic import BaseModel

logger.add(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__))
        + "/logs/"
        + os.path.basename(__file__)
        + ".log"
    ),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


class meditation_session(BaseModel):
    warm_up_seconds: float
    meditation_seconds: float
    yoga_seconds: float
    morning_meditation: bool = False
    meditation_start_ms: int
    meditation_end_ms: int
    yoga_start_ms: int
    yoga_end_ms: int


class reading_session(BaseModel):
    title: str
    reading_seconds: float
    page_old: int
    page_new: int
    page_difference: float
    reading_type: str
    finished: Optional[bool] = False
    reading_start_ms: int
    reading_end_ms: int


class timer(BaseModel):
    context: str
    duration: float
    start_ms: int
    end_ms: int


class list_item(BaseModel):
    objects: List[dict]
