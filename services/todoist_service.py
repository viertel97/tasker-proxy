from datetime import datetime, time, timedelta
from itertools import chain

import pandas as pd
from dateutil import parser
from quarter_lib.akeyless import get_secrets
from quarter_lib.logging import setup_logging
from quarter_lib.todoist import move_item_to_project, update_due, complete_task_by_title

from todoist_api_python.api import TodoistAPI

from models.db_models import new_book, reading_session
from models.tasks import zotero_task
from services.telegram_service import send_to_telegram

END_TIME = time(hour=6, minute=0, second=0)

TODOIST_TOKEN = get_secrets(["todoist/token"])
TODOIST_API = TodoistAPI(TODOIST_TOKEN)

THIS_WEEK_PROJECT_ID = "6Crcr3mXxVh6f97J"

logger = setup_logging(__name__)


def get_from_iterable(iterable):
	return list(chain.from_iterable(iterable))


async def add_book_finished_task(item: reading_session):
	task = TODOIST_API.add_task(
		"'{other}' in Zotero & Obsidian einpflegen".format(other=item.title),
		labels=["Digital", "filtered"],
		project_id=THIS_WEEK_PROJECT_ID,
		due_string="Tomorrow",
	)

	if type(item) is reading_session:
		task = TODOIST_API.add_task("eBook Reader updaten", labels=["Digital", "filtered"])
	else:
		task = TODOIST_API.add_task(
			"Hörbücher updaten + in einzelne Kapitel aufteilen + PDF runterladen",
			labels=["Digital", "filtered"],
			project_id=THIS_WEEK_PROJECT_ID,
			due_string="Tomorrow",
		)

	task = TODOIST_API.add_task(
		"Aus Obsidian-Datei für '{other}' Tasks generieren".format(other=item.title),
		labels=["Digital", "filtered"],
		project_id=THIS_WEEK_PROJECT_ID,
		due_string="Tomorrow",
	)

	task = TODOIST_API.add_task(
		f"Analyse über '{item.title}' zu Cubox hinzufügen und geg. lesen",
		labels=["Digital", "filtered"],
		project_id=THIS_WEEK_PROJECT_ID,
		due_string="Tomorrow",
	)


async def add_task_with_check(title, due=None, project_id=None, labels=None):
	tasks = get_from_iterable(TODOIST_API.get_tasks(project_id=project_id))
	if len(tasks) > 0:
		found_tasks = [task for task in tasks if task.content == title]
		if len(found_tasks) > 0:
			for task in found_tasks:
				TODOIST_API.delete_task(task.id)
	task = TODOIST_API.add_task(title, labels=labels, due_string=due, project_id=project_id)
	return task


async def add_book_reminder(item: new_book):
	item = TODOIST_API.add_task(
		"'{title}' in [Reading List](https://www.notion.so/e88940d2346e4f66a8cec95faa11dcfb) pflegen".format(title=item.title),
		project_id=THIS_WEEK_PROJECT_ID,
		due_string="Tomorrow",
	)


async def complete_task(selected_service):
	await complete_task_by_title(selected_service)
	await send_to_telegram("Task completed: " + selected_service)


async def close_task_by_title(selected_service):
	TODOIST_API.complete_task(selected_service)


async def add_guided_meditation_task(guided_meditation_name):
	item = TODOIST_API.add_task(
		"Guided Meditation '{name}' nacharbeiten".format(name=guided_meditation_name),
		labels=["Digital", "filtered"],
		project_id=THIS_WEEK_PROJECT_ID,
		due_string="Tomorrow",
	)


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

	item = TODOIST_API.add_task(message, labels=["Digital", "filtered"], project_id=THIS_WEEK_PROJECT_ID, due_string="Tomorrow")
	return item


def get_rework_tasks():
	df_items = pd.DataFrame([item.__dict__ for item in get_from_iterable(TODOIST_API.get_tasks(project_id=THIS_WEEK_PROJECT_ID))])
	df_items = df_items[df_items.content.str.contains("nacharbeiten")]
	df_items.content = df_items.content.str.replace(" - nacharbeiten & Tracker pflegen", "")
	df_items.content = df_items.content.str.replace(" nacharbeiten", "")
	df_items.sort_values(by="due", inplace=True)
	item_list = df_items.to_dict(orient="records")
	result_list = []
	for item in item_list:
		result_str = str(item["content"])
		if item["due"] is not None:
			if item["due"].datetime is not None:
				result_str += " (Due: " + parser.parse(item["due"].datetime).strftime("%d.%m.%Y %H:%M") + ")"
			else:
				result_str += " (Due: " + parser.parse(item["due"].date).strftime("%d.%m.%Y") + ")"
			if item["priority"] != 1:
				result_str += " (Prio: " + str(item["priority"]) + ")"
			result_list.append(result_str)
	return result_list
