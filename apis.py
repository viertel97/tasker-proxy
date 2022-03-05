import os

import todoist

TODOIST_API = todoist.TodoistAPI(os.environ["TODOIST_TOKEN"])
TODOIST_API.sync()


def get_list(list_name):
    return [item.data for item in TODOIST_API.state[list_name]]


def add_reading_other_task(name):
    TODOIST_API.sync()
    item = TODOIST_API.items.add(
        "Reading-Habit-Tracker pflegen mit : {other}".format(other=name),
        project_id="2244725398",
        due={"string": "Tomorrow"},
    )
    TODOIST_API.commit()
