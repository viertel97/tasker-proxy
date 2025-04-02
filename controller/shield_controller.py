from fastapi import APIRouter
from quarter_lib.logging import setup_logging

from models.db_models import app_usage, power
from services.shield_service import add_app_usage, add_start_stop

logger = setup_logging(__name__)


router = APIRouter(tags=["shield"])


@logger.catch
@router.post("/shield/apps")
async def track_timer(item: app_usage):
	add_app_usage(item)


@logger.catch
@router.post("/shield/power")
async def track_start_stop(item: power):
	add_start_stop(item)
