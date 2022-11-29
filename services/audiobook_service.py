import os

from loguru import logger

from models.tasks import zotero_task
from services.notion_service import update_reading_page_finished
from services.todoist_service import add_book_finished_task, add_zotero_task

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


async def add_audiobook_task(item: zotero_task):
    await add_zotero_task(item)


async def add_audiobook_finished_task(item: zotero_task):
    await add_book_finished_task(item)
    update_reading_page_finished(item)
