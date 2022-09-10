import os

import helper.file_helper as file_helper
from fastapi import APIRouter, Request
from loguru import logger
from models.db_models import meditation_session, new_book, reading_session, yoga_session
from services.notion_service import (
    track_habit,
    update_reading_page,
    update_reading_page_finished,
)
from services.session_service import (
    add_meditation_session,
    add_reading_session,
    add_yoga_session,
)
from services.todoist_service import (
    add_book_reminder,
    add_reading_finished_task,
    todoist_proxy,
)

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

router = APIRouter()


proxy_mapping_dict = file_helper.get_config("tasker_mapping.json")
habit_tracker_mapping_dict = file_helper.get_config("habit_tracker_mapping.json")


@logger.catch
@router.post("/proxy/{service}")
async def proxy(service: str):
    logger.info("service: " + service)
    selected_service = proxy_mapping_dict[service]
    todoist_proxy(selected_service)


@logger.catch
@router.post("/habit-tracker/drink")
async def get_drink(request: Request):
    ght_data = await request.json()
    logger.info("service: " + str(ght_data))


@logger.catch
@router.post("/habit-tracker/sport/{service}")
async def habit_tracker(service: str):
    logger.info("habit-tracker: " + service)
    service = habit_tracker_mapping_dict[service]
    track_habit(service)
    todoist_proxy(proxy_mapping_dict["sport"])


@logger.catch
@router.post("/habit-tracker/meditation")
async def track_meditation(item: meditation_session):
    error_flag = add_meditation_session(item)
    if not error_flag:
        selected_service = proxy_mapping_dict["meditation-evening"]
        todoist_proxy(selected_service)


@logger.catch
@router.post("/habit-tracker/yoga")
async def track_meditation(item: yoga_session):
    add_yoga_session(item)


@logger.catch
@router.post("/habit-tracker/reading")
async def track_reading(item: reading_session):
    add_reading_session(item)
    if item.finished:
        add_reading_finished_task(item)
        update_reading_page_finished(item)
    selected_service = proxy_mapping_dict["reading"]
    todoist_proxy(selected_service)


@logger.catch
@router.post("/habit-tracker/new_book")
async def track_reading(item: new_book):
    update_reading_page(item)
    add_book_reminder(item)
