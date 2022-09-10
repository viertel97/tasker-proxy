import os

from fastapi import APIRouter, Request
from loguru import logger
from services.ght_service import add_ght_entry, track_ght_db, track_ght_entry
from services.notion_service import update_reading_page
from services.todoist_service import add_book_reminder

from controller.shield_controller import track_app_usage_db, track_start_stop_db

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
@router.get("/ght/daily")
async def get_ght_questions():
    return get_ght_questions("daily")


@logger.catch
@router.get("/ght/weekly")
async def get_ght_questions():
    return get_ght_questions("weekly")


@logger.catch
@router.get("/ght/monthly")
async def get_ght_questions():
    return get_ght_questions("monthly")


@logger.catch
@router.get("/ght/quarterly")
async def get_ght_questions():
    return get_ght_questions("quarterly")


@logger.catch
@router.get("/ght/yearly")
async def get_ght_questions():
    return get_ght_questions("yearly")
