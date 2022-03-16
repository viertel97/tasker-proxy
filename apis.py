import os

import todoist

TODOIST_API = todoist.TodoistAPI(os.environ["TODOIST_TOKEN"])
TODOIST_API.sync()


def get_list(list_name):
    return [item.data for item in TODOIST_API.state[list_name]]


def add_reading_other_task(name, finished):
    TODOIST_API.sync()
    if finished:
        content = "Reading-Habit-Tracker pflegen mit: {other} + in Zotero & Obsidian einpflegen".format(other=name)
    else:
        content = "Reading-Habit-Tracker pflegen mit: {other}".format(other=name)
    item = TODOIST_API.items.add(
        content,
        project_id="2244725398",
        due={"string": "Tomorrow"},
    )
    TODOIST_API.commit()
