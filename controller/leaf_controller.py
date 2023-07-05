import os

from fastapi import APIRouter, Request, Body
from fastapi import BackgroundTasks
from quarter_lib.logging import setup_logging

from services.sqlite_service import update_koreader_tables

logger = setup_logging(__name__)
router = APIRouter(prefix="/leaf")


@logger.catch
@router.post("/test")
async def upload_file(background_tasks: BackgroundTasks, request: Request, file: bytes = Body("binary")):
    file_name = request.headers.get("file_name")
    file_path = os.path.join(os.getcwd(), file_name)
    logger.info("file_name: " + file_name)

    with open(file_name, "wb") as f:
        f.write(file)

    background_tasks.add_task(update_koreader_tables, file_path)
    return {"file_name": file_name}
