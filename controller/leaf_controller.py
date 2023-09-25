import os

from fastapi import APIRouter, Request, Body
from quarter_lib.logging import setup_logging
from quarter_lib_old.todoist import complete_task_by_title

from services.sqlite_service import update_koreader_tables
from services.telegram_service import send_to_telegram

logger = setup_logging(__name__)
router = APIRouter(prefix="/leaf", tags=["leaf"])


@logger.catch
@router.post("/test")
async def upload_file(request: Request, file: bytes = Body("binary")):
    file_name = request.headers.get("file_name")
    file_path = os.path.join(os.getcwd(), file_name)
    logger.info("file_name: " + file_name)

    with open(file_name, "wb") as f:
        f.write(file)

    update_result_koreader_book, update_result_koreader_page_stat_data = update_koreader_tables(file_path)
    if update_result_koreader_book > 0 or update_result_koreader_page_stat_data > 0:
        complete_task_by_title("Lesen")
        await send_to_telegram("Reading session added to database with {} books and {} page_stat_data rows".format(
            update_result_koreader_book, update_result_koreader_page_stat_data))
    else:
        await send_to_telegram("No rows for reading session were added to database")
    return {"file_name": file_name}
