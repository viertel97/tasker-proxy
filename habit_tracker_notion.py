import json
import os

import pandas as pd
import requests
from loguru import logger

import api_objects

api_key = os.environ["NOTION_TOKEN"]

base_url = "https://api.notion.com/v1/"
headers = {
    "Authorization": "Bearer " + api_key,
    "Content-Type": "application/json",
    "Notion-Version": "2021-08-16",
}


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
        content = page[property][0]["plain_text"] + " / "
    return content


def ebook_reading_update_notion_habit_tracker_page(page, item):
    url = base_url + "pages/" + page.id
    content = get_previous_rich_text_content(page, "properties~Reading~rich_text")
    content += "{reading_length}s | {page_difference} pages | {title} ".format(
        page_difference=item.page_difference,
        title=item.title,
        reading_length=item.reading_length,
    )

    data = {"properties": {"Reading": {"rich_text": [{"type": "text", "text": {"content": content}}]}}}
    r = requests.patch(url, data=json.dumps(data), headers=headers).json()
    logger.info("'ebook read' filled on page '" + page.id + "'")


def book_reading_update_notion_habit_tracker_page(page, item):
    url = base_url + "pages/" + page.id
    data = get_rich_text_data(page, item)
    r = requests.patch(url, data=json.dumps(data), headers=headers).json()
    logger.info("'book read' filled on page '" + page.id + "'")


def meditation_update_notion_habit_tracker_page(page, item):
    url = base_url + "pages/" + page.id
    data = get_rich_text_data(page, item)
    r = requests.patch(url, data=json.dumps(data), headers=headers).json()
    logger.info("'meditation' filled on page '" + page.id + "'")


def get_rich_text_data(page, item):
    if type(item) == api_objects.book_reading_session:
        content = get_previous_rich_text_content(page, "properties~Reading~rich_text")
        content += "{reading_length}s | {page_difference} pages | {title} ".format(
            page_difference=item.page_difference,
            title=item.title,
            reading_length=item.reading_length,
        )
        return {"properties": {"Reading": {"rich_text": [{"type": "text", "text": {"content": content}}]}}}
    else:
        content = get_previous_rich_text_content(page, "properties~Meditation~rich_text")
        content += "{warm_up_seconds} | {meditation_seconds} | {yoga_seconds}".format(
            warm_up_seconds=item.warm_up_seconds,
            meditation_seconds=item.meditation_seconds,
            yoga_seconds=item.yoga_seconds,
        )
        return {"properties": {"Meditation": {"rich_text": [{"type": "text", "text": {"content": content}}]}}}


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
    logger.info("'" + completed_habit + "' checked on page '" + page.id + "'")
