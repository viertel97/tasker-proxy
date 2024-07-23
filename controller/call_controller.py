from fastapi import APIRouter
from quarter_lib.logging import setup_logging

from models.call import call
from services.monica_service import add_call_rework_task

logger = setup_logging(__name__)

router = APIRouter(prefix="/call", tags=["call"])


@logger.catch
@router.post("/add-rework")
async def create_monica_entry(item: call):
    add_call_rework_task(item)
    return {"status_code": 200, "message": "success", "data": None}
