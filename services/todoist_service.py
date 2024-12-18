from datetime import datetime, time, timedelta

import pandas as pd
from dateutil import parser
from quarter_lib.akeyless import get_secrets
from quarter_lib.logging import setup_logging
from quarter_lib_old.todoist import (
    complete_task_by_title,
    move_item_to_project,
    update_due,
)
from todoist_api_python.api import TodoistAPI

from models.db_models import new_book, reading_session
from models.tasks import zotero_task
from services.telegram_service import send_to_telegram

END_TIME = time(hour=6, minute=0, second=0)

TODOIST_TOKEN = get_secrets(["todoist/token"])
TODOIST_API = TodoistAPI(TODOIST_TOKEN)

logger = setup_logging(__name__)


async def add_book_finished_task(item: reading_session):
    task = TODOIST_API.add_task(
        "'{other}' in Zotero & Obsidian einpflegen".format(other=item.title), labels=["Digital"]
    )
    move_item_to_project(task.id, "2244725398")
    update_due(task.id, due={"string": "Tomorrow"})

    if type(item) is reading_session:
        task = TODOIST_API.add_task(
            "eBook Reader updaten", labels=["Digital"]
        )
    else:
        task = TODOIST_API.add_task(
            "Hörbücher updaten + in einzelne Kapitel aufteilen + PDF runterladen", labels=["Digital"]
        )
    update_due(task.id, due={"string": "Tomorrow"})
    move_item_to_project(task.id, "2244725398")

    task = TODOIST_API.add_task(
        "Aus Obsidian-Datei für '{other}' Tasks generieren".format(other=item.title), labels=["Digital"]
    )
    update_due(task.id, due={"string": "Tomorrow"})
    move_item_to_project(task.id, "2244725398")

    task = TODOIST_API.add_task(
        "Vorherige Obsidian-Notizen aus dem Buch '{other}' in 10 Takeaways überführen + Impressionen, Zitate und Bonus einpflegen".format(
            other=item.title
        ),
        labels=["Digital"],
    )
    update_due(task.id, due={"string": "Tomorrow"})
    move_item_to_project(task.id, "2244725398")


async def add_task_with_check(title, due=None, project_id=None, labels=None):
    tasks = TODOIST_API.get_tasks(project_id=project_id)
    if len(tasks) > 0:
        found_tasks = [task for task in tasks if task.content == title]
        if len(found_tasks) > 0:
            for task in found_tasks:
                TODOIST_API.delete_task(task.id)
    if labels:
        task = TODOIST_API.add_task(title, labels=labels)
    else:
        task = TODOIST_API.add_task(title)
    if project_id:
        move_item_to_project(task.id, project_id)
    if due:
        update_due(task.id, due={"string": due})
    return task


def add_task(title: str, due=None, project_id=None, labels=None):
    if labels:
        task = TODOIST_API.add_task(title, labels=labels)
    else:
        task = TODOIST_API.add_task(title)
    if project_id:
        move_item_to_project(task.id, project_id)
    if due:
        update_due(task.id, due={"string": due})
    return task


async def add_book_reminder(item: new_book):
    item = TODOIST_API.add_task(
        "'{title}' in [Reading List](https://www.notion.so/e88940d2346e4f66a8cec95faa11dcfb) pflegen".format(
            title=item.title
        ),
    )
    move_item_to_project(item.id, "2244725398")
    update_due(item.id, due={"string": "Tomorrow"})


async def complete_task(selected_service):
    complete_task_by_title(selected_service)
    await send_to_telegram("Task completed: " + selected_service)


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
    item = TODOIST_API.add_task(message, labels=["Digital"])
    move_item_to_project(item.id, "2281154095")
    update_due(item.id, due=due, add_reminder=True)


async def update_due_date(task_id, due):
    return update_due(task_id, due)


def get_rework_tasks():
    df_items = pd.DataFrame(
        [item.__dict__ for item in TODOIST_API.get_tasks(project_id="2244725398")]
    )
    df_items = df_items[df_items.content.str.contains("nacharbeiten")]
    df_items.content = df_items.content.str.replace(
        " - nacharbeiten & Tracker pflegen", ""
    )
    df_items.content = df_items.content.str.replace(" nacharbeiten", "")
    df_items.sort_values(by="due", inplace=True)
    item_list = df_items.to_dict(orient="records")
    result_list = []
    for item in item_list:
        result_str = str(item["content"])
        if item["due"] is not None:
            if item["due"].datetime is not None:
                result_str += (
                    " (Due: "
                    + parser.parse(item["due"].datetime).strftime("%d.%m.%Y %H:%M")
                    + ")"
                )
            else:
                result_str += (
                    " (Due: "
                    + parser.parse(item["due"].date).strftime("%d.%m.%Y")
                    + ")"
                )
            if item["priority"] != 1:
                result_str += " (Prio: " + str(item["priority"]) + ")"
            result_list.append(result_str)
    return result_list
