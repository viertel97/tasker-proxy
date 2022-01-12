import json
import os
import platform
from datetime import datetime, time, timedelta
from urllib.request import urlopen

import pandas as pd
import todoist
import uvicorn
from dateutil import parser
from fastapi import FastAPI
from loguru import logger

TODOIST_JSON_URL = os.environ["TODOIST_JSON_URL"]

END_TIME = time(hour=6, minute=0, second=0)

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


def todoist_proxy(selected_service, api):
    response = urlopen(TODOIST_JSON_URL)
    data_json = json.loads(response.read())
    df_items = pd.DataFrame(data_json["items"])

    item = df_items[df_items.content == selected_service].sample(1).iloc[0]
    logger.info(item)

    api.sync()
    api_item = api.items.get_by_id(int(item["id"]))
    api_item.close()

    if parser.parse(api_item["due"]["date"]).date() >= (datetime.today() + timedelta(days=1)).date():
        logger.info(api.queue)
        api.commit()
        due = {
            "date": (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "is_recurring": True,
            "lang": "en",
            "string": "every day",
            "timezone": None,
        }
        api_item.update(due=due)

    if END_TIME > datetime.now().time():
        due = {
            "date": datetime.today().strftime("%Y-%m-%d"),
            "is_recurring": True,
            "lang": "en",
            "string": "every day",
            "timezone": None,
        }
        api_item.update(due=due)
    logger.info(api.queue)
    api.commit()
