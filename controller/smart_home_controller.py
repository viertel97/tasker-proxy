import os

from fastapi import APIRouter
from loguru import logger

from services.home_assistant_service import add_washer_finished_task, add_dishwasher_finished_task

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

router = APIRouter()


@logger.catch
@router.post("/smart_home/washer_finished")
async def washer_finished():
    logger.info("washer_finished")
    await add_washer_finished_task()

@logger.catch
@router.post("/smart_home/dishwasher_finished")
async def washer_finished():
    logger.info("dishwasher_finished")
    await add_dishwasher_finished_task()
