import os
import sys
from datetime import datetime, time, timedelta

import pandas as pd
from dateutil import parser
from loguru import logger
from quarter_lib.todoist import move_item_to_project, move_item_to_section, update_due
from todoist_api_python.api import TodoistAPI

from models.db_models import new_book, reading_session
from models.tasks import zotero_task

END_TIME = time(hour=6, minute=0, second=0)

TODOIST_API = TodoistAPI(os.environ["TODOIST_TOKEN"])

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


async def add_book_finished_task(item: reading_session):
    task = TODOIST_API.add_task(
        "'{other}' in Zotero & Obsidian einpflegen".format(other=item.title),
    )
    move_item_to_project(task.id, "2244725398")
    update_due(task.id, due={"string": "Tomorrow"})
    if type(item) == reading_session:
        task = TODOIST_API.add_task(
            "eBook Reader updaten",
        )
    else:
        task = TODOIST_API.add_task(
            "Hörbücher updaten",
        )
    update_due(task.id, due={"string": "Tomorrow"})
    move_item_to_project(task.id, "2244725398")
    task = TODOIST_API.add_task(
        "Aus Obsidian-Datei für '{other}' Tasks generieren".format(other=item.title),
    )
    move_item_to_section(task.id, "97635796")


async def add_book_reminder(item: new_book):
    item = TODOIST_API.add_task(
        "'{title}' in [Reading List](https://www.notion.so/e88940d2346e4f66a8cec95faa11dcfb) pflegen".format(
            title=item.title
        ),
    )
    move_item_to_project(item.id, "2244725398")
    update_due(item.id, due={"string": "Tomorrow"})


async def todoist_proxy(selected_service):
    df_items = pd.DataFrame([item.__dict__ for item in TODOIST_API.get_tasks()])
    item = df_items[df_items.content == selected_service].sample(1).iloc[0]
    logger.info(item)

    TODOIST_API.close_task(str(item["id"]))
    api_item = TODOIST_API.get_task(str(item["id"]))
    if parser.parse(api_item.due.date).date() >= (datetime.today() + timedelta(days=1)).date():
        due = {
            "date": (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "is_recurring": True,
            "lang": "en",
            "string": "every day",
            "timezone": None,
        }
        update_due(item["id"], due=due)

    if END_TIME > datetime.now().time():
        due = {
            "date": datetime.today().strftime("%Y-%m-%d"),
            "is_recurring": True,
            "lang": "en",
            "string": "every day",
            "timezone": None,
        }
        update_due(item["id"], due=due)


async def add_zotero_task(item: zotero_task):
    bookmark_timestamp = timedelta(seconds=(int(item.ms_of_bookmark_timestamp / 1000)))
    chapter_length = timedelta(seconds=int(item.ms_of_bookmark_chapter / 1000))

    message = '{bookmark_timestamp}/{chapter_length} in "{title}" by {author} on {date} at {time} - add highlight to Zotero'.format(
        bookmark_timestamp=str(bookmark_timestamp),
        chapter_length=str(chapter_length),
        title=item.title,
        author=item.author,
        date=item.timestamp.strftime("%d.%m.%Y"),
        time=item.timestamp.strftime("%H:%M"),
    )

    due = {
        "date": (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "is_recurring": False,
        "lang": "en",
        "string": "tomorrow",
        "timezone": None,
    }
    item = TODOIST_API.add_task(message)
    move_item_to_project(item.id, "2281154095")
    update_due(item.id, due=due, add_reminder=True)


async def update_due_date(task_id, due):
    return update_due(task_id, due)
