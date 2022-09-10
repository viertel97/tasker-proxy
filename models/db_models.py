import os
from datetime import datetime
from sqlite3 import Timestamp
from typing import List, Optional

from loguru import logger
from pydantic import BaseModel

from models.default_model import DefaultModel

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


class Exercise(DefaultModel):
    type: str


class meditation_session(Exercise):
    pass


class yoga_session(Exercise):
    pass


class reading_session(DefaultModel):
    title: str
    page_old: int
    page_new: int
    reading_type: str
    finished: Optional[bool] = False


class new_book(BaseModel):
    title: str
    type: str


class timer(DefaultModel):
    context: str


class app_usage(DefaultModel):
    app: str


class power(BaseModel):
    type: str