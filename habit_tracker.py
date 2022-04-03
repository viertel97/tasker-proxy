import os
from datetime import datetime, time, timedelta

from loguru import logger

import api_objects
import habit_tracker_notion
import helper
from apis import add_reading_other_task

END_TIME = time(hour=6, minute=0, second=0)


DATABASES = helper.get_config("databases_config.json")

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

# If the habit is performed between 0:00 and 6:00 it should count for the day before
def get_date():
    now = datetime.now().time()
    if now < END_TIME:
        return datetime.today() - timedelta(days=1)
    else:
        return datetime.today()


def track_habit(selected_service):
    database = helper.get_value("habit_tracker", "name", DATABASES)
    page = habit_tracker_notion.get_page_for_date(
        datetime.today(),
        database["id"],
    )
    habit_tracker_notion.update_notion_habit_tracker_page(page, selected_service)


def track_reading_habit(item: api_objects.reading_session):
    database = helper.get_value("habit_tracker", "name", DATABASES)
    page = habit_tracker_notion.get_page_for_date(
        get_date(),
        database["id"],
    )
    if item.reading_type != "Book" and item.reading_type != "eBook":
        add_reading_other_task(item.title)
    habit_tracker_notion.book_reading_update_notion_habit_tracker_page(page, item)


def track_mediation_habit(item):
    database = helper.get_value("habit_tracker", "name", DATABASES)
    page = habit_tracker_notion.get_page_for_date(
        get_date(),
        database["id"],
    )
    habit_tracker_notion.meditation_update_notion_habit_tracker_page(page, item)


def track_standup(item):
    database = helper.get_value("habit_tracker", "name", DATABASES)
    page = habit_tracker_notion.get_page_for_date(
        get_date(),
        database["id"],
    )
    habit_tracker_notion.standup_update_notion_habit_tracker_page(page, item)
