import os

from fastapi import APIRouter
from quarter_lib.logging import setup_logging

from models.db_models import drug_session
from services.drug_session_service import add_drug_session

logger = setup_logging(__file__)

router = APIRouter(tags=["drug_session"])


@logger.catch
@router.post("/drugs/session")
async def track_drug_session(item: drug_session):
    add_drug_session(item)
