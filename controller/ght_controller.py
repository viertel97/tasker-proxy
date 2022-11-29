import os

from fastapi import APIRouter, Request
from loguru import logger

from services.ght_service import add_ght_entry, get_ght_questions

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

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
    return get_ght_questions(service)
