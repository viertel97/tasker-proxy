import os
from datetime import datetime, time, timedelta

import pandas as pd
import todoist
from dateutil import parser
from loguru import logger
from models.db_models import new_book, reading_session

END_TIME = time(hour=6, minute=0, second=0)

TODOIST_API = todoist.TodoistAPI(os.environ["TODOIST_TOKEN"])

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


def get_list(list_name):
    return [item.data for item in TODOIST_API.state[list_name]]


def add_reading_finished_task(item: reading_session):
    TODOIST_API.sync()
    TODOIST_API.items.add(
        "'{other}' in Zotero & Obsidian einpflegen".format(other=item.title),
        project_id="2244725398",
        due={"string": "Tomorrow"},
    )
    TODOIST_API.items.add(
        "eBook Reader updaten",
        project_id="2244725398",
        due={"string": "Tomorrow"},
    )
    TODOIST_API.items.add(
        "'{other}' Obsidian-Notiz erstellen".format(other=item.title), project_id="2244466879", section_id="97635796"
    )
    TODOIST_API.commit()


def add_book_reminder(item: new_book):
    TODOIST_API.sync()
    TODOIST_API.items.add(
        "'{title}' in [Reading List](https://www.notion.so/e88940d2346e4f66a8cec95faa11dcfb) pflegen".format(
            title=item.title
        ),
        project_id="2244725398",
        due={"string": "Tomorrow"},
    )
    TODOIST_API.commit()


def todoist_proxy(selected_service):
    TODOIST_API.sync()

    df_items = pd.DataFrame(get_list("items"))
    item = df_items[df_items.content == selected_service].sample(1).iloc[0]
    logger.info(item)

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
