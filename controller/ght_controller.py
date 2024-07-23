from fastapi import APIRouter, Request
from quarter_lib.logging import setup_logging

from services.ght_service import add_ght_entry, add_wellbeing_entry, get_ght_questions

logger = setup_logging(__file__)


router = APIRouter()


@logger.catch
@router.post("/ght")
async def get_body(request: Request):
    ght_data = await request.json()
    logger.info("service: " + str(ght_data))
    add_ght_entry(ght_data)


@logger.catch
@router.get("/ght/{service}")
async def ght_questions(service: str):
    result = get_ght_questions(service)
    return result


@logger.catch
@router.get("/ght/{service}/{type}")
async def ght_questions(service: str, type: str):
    result = get_ght_questions(service + "/" + type)
    return result


@logger.catch
@router.post("/wellbeing")
async def add_wellbeing(request: Request):
    wellbeing_data = await request.json()
    logger.info("service: " + str("wellbeing"))
    add_wellbeing_entry(wellbeing_data)
