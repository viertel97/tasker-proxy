import os

from fastapi import APIRouter
from loguru import logger
from quarter_lib_old.todoist import complete_task_by_title

from services.home_assistant_service import add_washer_finished_task

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

router = APIRouter(tags=["smart_home"])


@logger.catch
@router.post("/smart_home/washer_finished")
async def washer_finished():
    logger.info("washer_finished")
    complete_task_by_title("Wäsche waschen")
    await add_washer_finished_task()
