import json

import pandas as pd
from dateutil.parser import parse
from fastapi import APIRouter
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from quarter_lib.logging import setup_logging
from quarter_lib_old.database import create_monica_server_connection

from config.queries import activity_query

DEFAULT_ACCOUNT_ID = 1
INBOX_CONTACT_ID = 52

connection = create_monica_server_connection()

logger = setup_logging(__name__)
router = APIRouter(prefix="/obsidian", tags=["obsidian"])


class api_model(BaseModel):
    happened_at: str = None


def get_activities(happened_at):
    connection = create_monica_server_connection()
    query = activity_query.format(happened_at=happened_at.strftime("%Y-%m-%d"))
    activities = pd.read_sql(query, connection)
    activities = activities[["summary", "people"]]
    connection.close()
    return activities


def prepare_result(result: pd.DataFrame):
    result = result.to_dict(orient="records")
    if len(result) == 0:
        return "No activities found for the given date."
    final_result = ""
    for r in result:
        final_result += f"{r['summary']}\n"
        people = r["people"].split("~")
        final_result += "# People:\n"
        for p in people:
            final_result += f" - [[{p}]]\n"
        final_result += "---\n"
        final_result += "people: [\n"
        for p in people:
            if p == people[-1]:
                final_result += f'"[[{p}]]"\n'
            else:
                final_result += f'"[[{p}]]",\n'
        final_result += "]\n"

        final_result += "---\n"
    return final_result


@router.post("/activities")
async def get_activities_post(request: Request):
    raw_body = await request.body()
    body_data = json.loads(raw_body.decode("utf-8"))
    happened_at = parse(body_data["happened_at"])
    result = get_activities(happened_at)

    return JSONResponse(content=prepare_result(result), status_code=status.HTTP_200_OK)
