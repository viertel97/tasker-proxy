import os

import quarter_lib_old.file_helper as file_helper
from fastapi import APIRouter, Request
from loguru import logger
from models.db_models import drug_session
from services.drug_session_service import add_drug_session

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

router = APIRouter()


@logger.catch
@router.post("/drugs/session")
async def track_drug_session(item: drug_session):
    add_drug_session(item)
