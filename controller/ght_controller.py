from fastapi import APIRouter, Request
from quarter_lib.logging import setup_logging

from proxies.telegram_proxy import log_to_telegram
from services.ght_service import add_ght_entry, add_wellbeing_entry, create_obsidian_file_from_ght_data, get_ght_questions

logger = setup_logging(__file__)


router = APIRouter(tags=["ght"])


@logger.catch
@router.post("/ght")
async def get_body(request: Request):
	ght_data = await request.json()
	logger.info("service: " + str(ght_data))
	error_count, success_count, task_count, result_df, timestamp, ght_type = add_ght_entry(ght_data)
	log_to_telegram(
		f"Added {success_count} entries to GHT and created {task_count} tasks. {error_count} errors occurred.",
		logger,
	)

	create_obsidian_file_from_ght_data(result_df, ght_type, timestamp)

	log_to_telegram(
		f"Created Obsidian file from GHT data for {ght_type} at {timestamp}.",
		logger,
	)

	return {"error_count": error_count, "success_count": success_count}


@logger.catch
@router.get("/ght/{service}")
async def ght_question_single(service: str):
	result = get_ght_questions(service)
	return result


@logger.catch
@router.get("/ght/{service}/{type_of_question}")
async def ght_question_both(service: str, type_of_question: str):
	result = get_ght_questions(service + "/" + type_of_question)
	return result


@logger.catch
@router.post("/wellbeing")
async def add_wellbeing(request: Request):
	wellbeing_data = await request.json()
	logger.info("service: " + str("wellbeing"))
	add_wellbeing_entry(wellbeing_data)
