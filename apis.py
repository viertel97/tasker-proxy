import os

import todoist

TODOIST_API = todoist.TodoistAPI(os.environ["TODOIST_TOKEN"])
TODOIST_API.sync()


def get_list(list_name):
    return [item.data for item in TODOIST_API.state[list_name]]
