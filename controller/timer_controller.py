import os

from fastapi import APIRouter
from loguru import logger
from models.db_models import timer
from services.timer_service import add_timer

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

router = APIRouter()


@logger.catch
@router.post("/habit-tracker/timer")
async def track_timer(item: timer):
    add_timer(item)
