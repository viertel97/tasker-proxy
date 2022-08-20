import os
from datetime import datetime
from typing import List, Optional

from loguru import logger
from pydantic import BaseModel

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


class meditation_session(BaseModel):
    meditation_start: datetime
    meditation_end: datetime


class yoga_session(BaseModel):
    start: datetime
    end: datetime


class reading_session(BaseModel):
    title: str
    start: datetime
    end: datetime
    page_old: int
    page_new: int
    reading_type: str
    finished: Optional[bool] = False


class timer(BaseModel):
    context: str
    start: datetime
    end: datetime


class list_item(BaseModel):
    objects: List[dict]
