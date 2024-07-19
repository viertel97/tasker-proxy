import os
import re

import pandas as pd
import pandas.errors
import pymysql
from dateutil import parser
from loguru import logger
import json

from helper.caching import ttl_cache
from helper.db_helper import create_server_connection, close_server_connection
from helper.web_helper import get_rework_events_from_web
from services.google_service import get_events_for_rework
from services.todoist_service import add_task

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


def parse_json(json_str):
    try:
        json_dict = json.loads(json_str)
        return json_dict
    except (json.JSONDecodeError, TypeError):
        return {}


def schema_matches(row, event):
    return (
        row["schema"] == "regex"
        and re.match(row["pattern"], event)
        or (row["schema"] == "match" and event in row["pattern"])
        or (row["schema"] == "contains" and row["pattern"] in event)
        or (row["schema"] == "not_contains" and row["pattern"] not in event)
        or (row["schema"] == "startswith" and event.startswith(row["pattern"]))
        or (row["schema"] == "endswith" and event.endswith(row["pattern"]))
    )


@ttl_cache(ttl=60 * 5)
def get_ght_questions_from_database(type_of_question, connection=None):
    if connection is None:
        connection = create_server_connection()
    df = pd.read_sql("SELECT * FROM ght_questions_" + type_of_question, connection)
    return df


def get_ght_questions(type_of_question):
    df = get_ght_questions_from_database(type_of_question)
    df.sort_values(by=["question_order"], inplace=True)

    rework_events = pd.DataFrame(get_rework_events_from_web())
    exploded_rework_events = rework_events.explode("questions")
    df = df.merge(
        exploded_rework_events, how="left", left_on="code", right_on="questions"
    )
    events = get_events_for_rework()
    events.append("TS")
    for index, row in df.query("questions.notnull()").iterrows():
        if row["pattern"] and row["schema"]:  # filter here the event based questions
            for event in events:
                if schema_matches(row, event):
                    df.at[index, "active"] = 1
    try:
        selected_mindmap_index = df.query("rotating_mindmap == True").sample(1).index[0]
        df.at[selected_mindmap_index, "active"] = 1
    except IndexError:
        logger.error("No rotating mindmap question found")
    except pandas.errors.UndefinedVariableError:
        logger.error("No column 'rotating_mindmap' found")
    # add/filter the questions based on the rotating mindmap question
    df = df[df["active"] == 1]
    df = df[["code", "message", "notation", "default_type"]]

    result = df.to_dict(orient="records")
    return result


def get_exercises(type):
    connection = create_server_connection()
    df = pd.read_sql(
        "SELECT * FROM exercises where type = '{type}' and active = 1".format(
            type=type
        ),
        connection,
    )
    close_server_connection(connection)
    return_list = []
    df.apply(
        lambda row: [
            return_list.append(row["exercise"]) for x in range(0, row["quantifier"])
        ],
        axis=1,
    )
    return return_list


def add_ght_entry(result_dict: dict):
    connection = create_server_connection()
    df = get_ght_questions_from_database(result_dict.pop("type"), connection)
    df = df.set_index("code")
    timestamp = parser.parse(result_dict.pop("timestamp"))
    error_count = 0
    result_df = pd.DataFrame(result_dict.items(), columns=["code", "value"])
    result_df = result_df.merge(df, how="left", on="code")
    raw_connection = connection.raw_connection()
    for index, row in result_df.iterrows():
        if any(temp in row["value"] for temp in ["?", "!"]):
            add_task(f"{timestamp}: {row['message']} (code: {row['code']}) -> value: {row['value']}")
        try:
            with raw_connection.cursor() as cursor:
                values = tuple(
                    (
                        row["code"],
                        row["value"],
                        timestamp,
                        timestamp.tzinfo.utcoffset(timestamp).seconds,
                        row["multiplier"],
                    )
                )
                cursor.execute(
                    "INSERT INTO `ght` (`code`, `value`, `ts`, `offset`, `multiplier`) VALUES (%s, %s, %s, %s, %s)",
                    values,
                )
                raw_connection.commit()
        except pymysql.err.IntegrityError as e:
            logger.error("IntegrityError: {error}".format(error=e))
            error_count += 1
            continue

    close_server_connection(connection)
    return error_count


def add_wellbeing_entry(item: dict):
    connection = create_server_connection()
    timestamp = parser.parse(item.pop("ts"))
    try:
        with connection.cursor() as cursor:
            values = tuple(
                (
                    "daily_wellbeing",
                    item["value"],
                    timestamp,
                    timestamp.tzinfo.utcoffset(timestamp).seconds,
                )
            )
            cursor.execute(
                "INSERT INTO `ght` (`code`, `value`, `ts`, `offset`) VALUES (%s, %s, %s, %s)",
                values,
            )
            connection.commit()
    except pymysql.err.IntegrityError as e:
        logger.error("IntegrityError: {error}".format(error=e))

    close_server_connection(connection)
