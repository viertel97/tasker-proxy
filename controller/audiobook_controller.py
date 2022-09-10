import os

from fastapi import APIRouter
from loguru import logger
from models.tasks import zotero_task

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

router = APIRouter()


@logger.catch
@router.post("/audiobook")
async def create_zotero_task(item: zotero_task):
    print(item)
