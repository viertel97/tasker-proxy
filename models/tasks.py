import os
from datetime import datetime

from loguru import logger
from pydantic import BaseModel

logger.add(
	os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
	format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
	backtrace=True,
	diagnose=True,
)


class zotero_task(BaseModel):
	title: str
	author: str
	ms_of_bookmark_timestamp: int
	ms_of_bookmark_chapter: int
	timestamp: datetime


class audiobook_finished(BaseModel):
	title: str
