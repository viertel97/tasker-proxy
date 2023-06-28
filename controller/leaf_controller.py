import os
import re

from fastapi import APIRouter, Request
from loguru import logger
from quarter_lib_old.easy_voice_recorder import get_logs_from_recording
from quarter_lib_old.file_helper import get_config
import sqlite3
import pandas as pd
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

router = APIRouter(prefix="/leaf")




@logger.catch
@router.post("/test")
async def create_file(request: Request):
    body = await request.body()
    temp = str(body.decode("ISO-8859-1")).split("Content-Type: application/octet-stream")
    test = temp[0].replace("--joaomgcdTaskerMOTHERFOCKERMUAHAHA\r\n", "")
    file_name = re.search(r"\"file_name\":\"(.*)\"", test).group(1).split("/")[-1]
    logger.info("file_name: " + file_name)
    file_path = os.path.join(os.getcwd(), file_name)
    with open(file_path, "wb") as f:
        temp[1] = temp[1].replace("\r\n", "")
        f.write(temp[1].encode("ISO-8859-1"))
    con = sqlite3.connect(file_path)
    df_book = pd.read_sql_query("SELECT * FROM book", con)
    df_book.to_csv("book.csv", index=False)
