import os

from fastapi import APIRouter
from loguru import logger

from models.db_models import app_usage, power
from services.shield_service import add_app_usage, add_start_stop

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

router = APIRouter(tags=["shield"])


@logger.catch
@router.post("/shield/apps")
async def track_timer(item: app_usage):
    add_app_usage(item)


@logger.catch
@router.post("/shield/power")
async def track_timer(item: power):
    add_start_stop(item)
