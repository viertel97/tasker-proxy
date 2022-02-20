import os
from datetime import datetime, time, timedelta

import pandas as pd
from dateutil import parser
from fastapi import FastAPI
from loguru import logger

END_TIME = time(hour=6, minute=0, second=0)

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

from apis import TODOIST_API, get_list


def todoist_proxy(selected_service):
    df_items = pd.DataFrame(get_list("items"))
    item = df_items[df_items.content == selected_service].sample(1).iloc[0]
    logger.info(item)

    TODOIST_API.sync()
    api_item = TODOIST_API.items.get_by_id(int(item["id"]))
    api_item.close()

    if parser.parse(api_item["due"]["date"]).date() >= (datetime.today() + timedelta(days=1)).date():
        logger.info(TODOIST_API.queue)
        TODOIST_API.commit()
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
    logger.info("Todoist Queue:")
    logger.info(TODOIST_API.queue)
    TODOIST_API.commit()
