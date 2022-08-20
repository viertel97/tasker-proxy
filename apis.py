import os

import todoist
from loguru import logger

from api_objects import reading_session

TODOIST_API = todoist.TodoistAPI(os.environ["TODOIST_TOKEN"])
TODOIST_API.sync()

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
