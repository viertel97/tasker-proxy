from fastapi import APIRouter
from quarter_lib.logging import setup_logging

from models.db_models import timer
from services.timer_service import add_timer

logger = setup_logging(__name__)
router = APIRouter(tags=["timer"])


@logger.catch
@router.post("/habit-tracker/timer")
async def track_timer(item: timer):
    add_timer(item)
