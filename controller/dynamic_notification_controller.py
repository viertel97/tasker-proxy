import os

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from services.google_service import get_events_for_rework
from services.todoist_service import get_rework_tasks

logger.add(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__))
        + "/logs/"
        + os.path.basename(__file__)
        + ".log"
    ),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

router = APIRouter(tags=["dynamic_notification"])


def generate_html_list(list, title):
    html_list = "<h4>" + title + "</h2><ul>"
    for item in list:
        html_list += "<li>" + item + "</li>"
    html_list += "</ul>"
    return html_list


@logger.catch
@router.get("/tasker/notification")
async def preparations():
    tasks = get_rework_tasks()
    events = get_events_for_rework()
    return_str = "<h1>Nach- oder Vorarbeiten?</h1>"
    if tasks:
        return_str += generate_html_list(tasks, "Tasks")
    if events:
        return_str += generate_html_list(events, "Events")
    if len(tasks) or len(events):
        return return_str
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tasks found")
