import os
import re

from fastapi import APIRouter, Request
from quarter_lib.logging import setup_logging
from quarter_lib.voice_recorder import get_logs_from_recording

from helper.web_helper import (
	get_habit_tracker_mapping_from_web,
	get_tasker_mapping_from_web,
)
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
from services.telegram_service import send_to_telegram
from services.todoist_service import (
	add_book_finished_task,
	add_book_reminder,
	add_guided_meditation_task,
	complete_task,
)

logger = setup_logging(__name__)

router = APIRouter(tags=["session"])

proxy_mapping_dict = get_tasker_mapping_from_web()
habit_tracker_mapping_dict = get_habit_tracker_mapping_from_web()

RECORDING_FILE = "temp_recording.mp3"


@logger.catch
@router.post("/proxy/{service}")
async def proxy(service: str):
	logger.info("service: " + service)
	selected_service = proxy_mapping_dict[service]
	await complete_task(selected_service)
	return {"message": "Task completed in background"}


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
	await track_habit(service)
	await complete_task(proxy_mapping_dict["sport"])

	return {"message": "Task added in background"}


@logger.catch
@router.post("/habit-tracker/meditation")
async def track_meditation(item: meditation_session):
	error_flag = await add_meditation_session(item)
	logger.info("error during DB insert: " + str(error_flag))
	if not error_flag:
		selected_service = proxy_mapping_dict["meditation-evening"]
		await complete_task(selected_service)
		if item.type == "Guided" and (item.guided_name is not None or item.guided_name != ""):
			await add_guided_meditation_task(item.guided_name)
		return {"message": "Task completed in background"}
	else:
		return {"message": "Error"}


@logger.catch
@router.post("/habit-tracker/yoga")
async def track_yoga(item: yoga_session):
	await add_yoga_session(item)
	return {"message": "Yoga session added in the background"}


@logger.catch
@router.post("/habit-tracker/reading")
async def track_reading(item: reading_session):
	add_reading_session(item)
	if item.finished:
		await add_book_finished_task(item)
		update_reading_page_finished(item)
	selected_service = proxy_mapping_dict["reading"]
	await complete_task(selected_service)
	return {"message": "Reading session added in the background"}


@logger.catch
@router.post("/habit-tracker/new_book")
async def add_new_book(item: new_book):
	update_reading_page(item)
	await add_book_reminder(item)
	return {"message": "New book added in the background"}


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
	await send_to_telegram("New recording with the context: " + context + " was added")
	return {"file_name": file_name}
