import os

from fastapi import APIRouter
from loguru import logger

from models.tasks import audiobook_finished, zotero_task
from services.audiobook_service import add_audiobook_finished_task, add_audiobook_task

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

router = APIRouter()


@logger.catch
@router.post("/audiobook_bookmark")
async def create_todoist_zotero_task(item: zotero_task):
    await add_audiobook_task(item)


@logger.catch
@router.post("/audiobook_finished")
async def audiobook_finished(item: audiobook_finished):
    await add_audiobook_finished_task(item)
