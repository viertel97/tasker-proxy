import json
import os
from datetime import datetime, time

import helper.file_helper as file_helper
import pandas as pd
import requests
from loguru import logger
from models.db_models import meditation_session, new_book, reading_session, timer

api_key = os.environ["NOTION_TOKEN"]

base_url = "https://api.notion.com/v1/"
headers = {
    "Authorization": "Bearer " + api_key,
    "Content-Type": "application/json",
    "Notion-Version": "2021-08-16",
}

END_TIME = time(hour=6, minute=0, second=0)
DATABASES = file_helper.get_config("databases_config.json")

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


def get_page_for_date(date, database_id):
    url = base_url + "databases/" + database_id + "/query"
    result_list = []
    body = None
    while True:
        r = (
            requests.post(url, headers=headers).json()
            if body is None
            else requests.post(url, data=json.dumps(body), headers=headers).json()
        )
        for results in r["results"]:
            result_list.append(results)
        body = {"start_cursor": r.get("next_cursor")}
        if not r["has_more"]:
            break
    df = pd.json_normalize(result_list, sep="~")
    return df.loc[df["properties~Date~date~start"] == date.strftime("%Y-%m-%d")].iloc[0]


def get_previous_rich_text_content(page, property):
    content = ""
    if len(page[property]) > 0:
        content = page[property][0]["plain_text"]
    return content


def book_reading_update_notion_habit_tracker_page(page, item: reading_session):
    url = base_url + "pages/" + page.id
    data = get_rich_text_data(page, item)
    r = requests.patch(url, data=json.dumps(data), headers=headers).json()
    logger.info("'book read' filled on page '" + page.id + "'")


def meditation_update_notion_habit_tracker_page(page, item: meditation_session):
    url = base_url + "pages/" + page.id
    data = get_rich_text_data(page, item)
    r = requests.patch(url, data=json.dumps(data), headers=headers).json()
    logger.info("'meditation' filled on page '" + page.id + "'")


def get_meditation_data(page, item: meditation_session):
    previous_data = get_previous_rich_text_content(page, "properties~Meditation~rich_text")
    content_list = json.loads(previous_data) if previous_data else []
    content_list.append(item.__dict__)
    content_json = json.dumps(content_list, indent=4)
    return {"properties": {"Meditation": {"rich_text": [{"type": "text", "text": {"content": content_json}}]}}}


def get_reading_data(page, item: reading_session):
    previous_data = get_previous_rich_text_content(page, "properties~Reading~rich_text")
    content_list = json.loads(previous_data) if previous_data else []
    content_list.append(item.__dict__)
    content_json = json.dumps(content_list, indent=4, ensure_ascii=False)
    return {"properties": {"Reading": {"rich_text": [{"type": "text", "text": {"content": content_json}}]}}}


def get_rich_text_data(page, item):
    if type(item) == meditation_session:
        return get_meditation_data(page, item)
    elif type(item) == reading_session:
        return get_reading_data(page, item)
    elif type(item) == timer:
        return get_timer_data(page, item)
    else:
        logger.info("Wrong object")


def get_previous_multi_select_content(page, property):
    content = []
    print(page[property])
    if len(page[property]) > 0:
        for select in page[property]:
            content.append(select["name"])
    return content


def get_multi_select_data(page, habit):
    content_list = get_previous_multi_select_content(page, "properties~Sport~multi_select")
    content_list.append(habit)
    content_list = list(dict.fromkeys(content_list))
    data = {"properties": {"Sport": {"multi_select": []}}}
    for content in content_list:
        data["properties"]["Sport"]["multi_select"].append({"name": content})
    return data


def update_notion_habit_tracker_page(page, completed_habit):
    url = base_url + "pages/" + page.id
    data = get_multi_select_data(page, completed_habit)
    r = requests.patch(url, data=json.dumps(data), headers=headers).json()
    logger.info(
        "'timer' ({completed_habit}) checked on page {page_id}'".format(
            completed_habit=completed_habit, page_id=page.id
        )
    )


def timer_update_notion_habit_tracker_page(page, item: timer):
    url = base_url + "pages/" + page.id
    data = get_rich_text_data(page, item)
    r = requests.patch(url, data=json.dumps(data), headers=headers).json()
    logger.info("'timer' ({item}) checked on page {page_id}'".format(item=item.context, page_id=page.id))


def get_timer_data(page, item: timer):
    previous_data = get_previous_rich_text_content(page, "properties~Timer~rich_text")
    content_list = json.loads(previous_data) if previous_data else []

    content_list.append(item.__dict__)
    content_json = json.dumps(content_list, indent=4, ensure_ascii=False)

    return {"properties": {"Timer": {"rich_text": [{"type": "text", "text": {"content": content_json}}]}}}


def update_reading_page(item: new_book):
    url = base_url + "pages"
    data = {
        "parent": {"type": "database_id", "database_id": "e88940d2346e4f66a8cec95faa11dcfb"},
        "properties": {
            "Title": {"type": "title", "title": [{"type": "text", "text": {"content": item.title}}]},
            "Format": {"multi_select": {"name": item.type}},
            "Dates Read": {"date": {"start": datetime.today().strftime("%Y-%m-%d")}},
        },
    }

    r = requests.post(
        url,
        data=json.dumps(data),
        headers=headers,
    ).json()
    logger.info("added book '{title}' (type: {type}) to Reading List".format(title=item.title, type=item.type))


def update_reading_page_finished(item: reading_session):
    url = base_url + "databases/e88940d2346e4f66a8cec95faa11dcfb" + "/query"
    data = {
        "filter": {
            "or": [
                {"property": "Title", "title": {"equals": item.title}},
            ]
        }
    }

    r = requests.post(
        url,
        data=json.dumps(data),
        headers=headers,
    ).json()
    if len(r["results"]) > 0:
        end = datetime.today().strftime("%Y-%m-%d")
        url = base_url + "pages/" + r["results"][0]["id"]
        data = {
            "properties": {
                "Dates Read": {
                    "date": {"start": r["results"][0]["properties"]["Dates Read"]["date"]["start"], "end": end}
                },
            },
        }
        r = requests.patch(url, data=json.dumps(data), headers=headers).json()
        logger.info("book with '{title}' was updated with 'Dates Read'-end at {end}".format(title=item.title, end=end))
    else:
        logger.error("book with '{title}' was not found on Reading List".format(title=item.title))


def track_habit(selected_service):
    database = file_helper.get_value("habit_tracker", "name", DATABASES)
    page = get_page_for_date(
        datetime.today(),
        database["id"],
    )
    update_notion_habit_tracker_page(page, selected_service)
