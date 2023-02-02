import os
import re

from fastapi import APIRouter, Request
from loguru import logger
from quarter_lib.easy_voice_recorder import get_logs_from_recording
from quarter_lib.file_helper import get_config

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
    add_book_finished_task,
    add_book_reminder,
    complete_task,
)

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

router = APIRouter()

proxy_mapping_dict = get_config("tasker_mapping.json")
habit_tracker_mapping_dict = get_config("habit_tracker_mapping.json")

RECORDING_FILE = "temp_recording.mp3"


@logger.catch
@router.post("/proxy/{service}")
async def proxy(service: str):
    logger.info("service: " + service)
    selected_service = proxy_mapping_dict[service]
    await complete_task(selected_service)


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
    await complete_task(proxy_mapping_dict["sport"])


@logger.catch
@router.post("/habit-tracker/meditation")
async def track_meditation(item: meditation_session):
    error_flag = add_meditation_session(item)
    if not error_flag:
        selected_service = proxy_mapping_dict["meditation-evening"]
        await complete_task(selected_service)


@logger.catch
@router.post("/habit-tracker/yoga")
async def track_meditation(item: yoga_session):
    add_yoga_session(item)


@logger.catch
@router.post("/habit-tracker/reading")
async def track_reading(item: reading_session):
    add_reading_session(item)
    if item.finished:
        await add_book_finished_task(item)
        update_reading_page_finished(item)
    selected_service = proxy_mapping_dict["reading"]
    await complete_task(selected_service)


@logger.catch
@router.post("/habit-tracker/new_book")
async def track_reading(item: new_book):
    update_reading_page(item)
    await add_book_reminder(item)


@logger.catch
@router.post("/file/recording/{context}")
async def create_file(request: Request, context: str):
    body = await request.body()
    temp = str(body.decode("ISO-8859-1")).split("Content-Type: application/octet-stream")
    test = temp[0].replace("--joaomgcdTaskerMOTHERFOCKERMUAHAHA\r\n", "")
    file_name = re.search(r"\"file_name\":\"(.*)\"", test).group(1).split("/")[-1]
    logger.info("file_name: " + file_name)
    file_path = os.path.join(os.getcwd(), RECORDING_FILE)
    with open(file_path, "wb") as f:
        f.write(temp[1].encode("ISO-8859-1"))
    get_logs_from_recording(file_path, file_name, context)
