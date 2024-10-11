import json
import time

import pandas as pd
from dateutil.parser import parse
from fastapi import APIRouter
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from quarter_lib.logging import setup_logging
from quarter_lib_old.database import create_monica_server_connection

from config.queries import activity_query
from helper.web_helper import get_onenote_default_ids
from services.microsoft_service import duplicate_page, get_new_page_id, get_access_token, add_formatted_text_to_page

DEFAULT_ACCOUNT_ID = 1
INBOX_CONTACT_ID = 52
TO_DELETE_LIST = ["Inbox", "Blocker", "No-GitHub"]

logger = setup_logging(__name__)
router = APIRouter(prefix="/obsidian", tags=["obsidian"])


class api_model(BaseModel):
    happened_at: str = None


def get_activities(happened_at):
    connection = create_monica_server_connection()
    query = activity_query.format(happened_at=happened_at.strftime("%Y-%m-%d"))
    activities = pd.read_sql(query, connection)
    activities = activities[["summary", "people", "description", "uuid"]]
    connection.close()
    return activities


def prepare_result(result: pd.DataFrame):
    final_result = []
    for index, row in result.iterrows():
        people_list = row["people"].split("~")
        people_list.sort()
        people_list = [i for i in people_list if i not in TO_DELETE_LIST]
        if len(people_list) == 0:
            logger.info(f"Skipping row: {str(row['summary'])}")
            continue
        # check if "description" contains two times "---" and if yes, use only the part after the second "---"
        if row["description"].count("---") == 2:
            row["description"] = row["description"].split("---")[2]
        final_result.append(
            {
                "summary": row["summary"],
                "people_frontmatter": [f"[[{p}]]" for p in people_list],
                "people_content": [f"- [[{p}]]" for p in people_list],
                "description": row["description"],
                "uuid": row["uuid"],
            }
        )
    logger.info(final_result)
    return final_result


@router.post("/activities")
async def get_activities_post(request: Request):
    raw_body = await request.body()
    body_data = json.loads(raw_body.decode("utf-8"))
    happened_at = parse(body_data["happened_at"])
    logger.info(f"Received request for activities on {str(happened_at)}")
    result = get_activities(happened_at)
    prepared_result = prepare_result(result)
    return JSONResponse(content=prepared_result, status_code=status.HTTP_200_OK)


def retry_get_new_page_id(duplicate_response, access_token, max_retries=10, backoff_factor=1, initial_delay=5):
    retries = 0
    delay = initial_delay
    new_page_id = None

    while new_page_id is None and retries < max_retries:
        try:
            new_page_id = get_new_page_id(duplicate_response, access_token)
            if new_page_id is not None:
                return new_page_id
        except Exception as e:
            logger.error(f"Error getting new page id: {e}")
            pass

        retries += 1
        time.sleep(delay)
        delay *= backoff_factor  # Exponential backoff

    return JSONResponse(content={"error": "Could not get new page id"},
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/to_onenote")
async def send_to_onenote(request: Request):
    raw_body = await request.body()
    body_data = json.loads(raw_body.decode("utf-8"))
    happened_at = parse(body_data["happened_at"])

    onenote_ids = get_onenote_default_ids()
    access_token = get_access_token()
    duplicate_response = duplicate_page(onenote_ids['default_template_page_id'],
                                        onenote_ids['default_template_section_id'], access_token)
    if duplicate_response is None:
        return JSONResponse(content={"error": "Could not duplicate page"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    logger.info("Duplicate response: " + str(duplicate_response))

    new_page_id = retry_get_new_page_id(duplicate_response, access_token)

    logger.info(f"New page id: {new_page_id}")
    title = f"{happened_at.strftime('%Y-%m-%d')} - {body_data['summary']}"
    logger.info(f"Adding to page {new_page_id} with title {title} - waiting 10 seconds first")
    time.sleep(10)
    add_text_response = add_formatted_text_to_page(new_page_id, body_data["content"], title, access_token)
    if add_text_response is not None:
        return JSONResponse(content={"page_id": new_page_id}, status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(content={"error": "Could not add text to page"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
