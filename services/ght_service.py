import json
import re
from datetime import datetime

import pandas as pd
import pandas.errors
import pymysql
from croniter import croniter
from dateutil import parser
from loguru import logger
from quarter_lib.logging import setup_logging

from sqlalchemy import text
from helper.db_helper import close_server_connection, create_server_connection
from helper.web_helper import get_rework_events_from_web
from services.google_service import get_rework_events_from_google_calendar
from services.todoist_service import add_task

logger = setup_logging(__file__)


def parse_json(json_str):
    try:
        json_dict = json.loads(json_str)
        return json_dict
    except (json.JSONDecodeError, TypeError):
        return {}


def is_cron_matching_today(cron_expression):
    now = datetime.now()

    # Create a croniter object with the current time as the base time
    cron = croniter(cron_expression, now)

    # Get the next and previous scheduled times
    next_time = cron.get_next(datetime)
    prev_time = cron.get_prev(datetime)

    # Check if either the next or previous scheduled time is today
    if now.date() == next_time.date() or now.date() == prev_time.date():
        return True

    return False


def schema_matches(row, event):
    return (
        row["schema"] == "regex"
        and re.match(row["pattern"], event)
        or (row["schema"] == "match" and event in row["pattern"])
        or (row["schema"] == "contains" and row["pattern"] in event)
        or (row["schema"] == "not_contains" and row["pattern"] not in event)
        or (row["schema"] == "startswith" and event.startswith(row["pattern"]))
        or (row["schema"] == "endswith" and event.endswith(row["pattern"]))
        # TODO: fix / add crontab
        or (row["schema"] == "crontab" and is_cron_matching_today(row["pattern"]))
    )


def get_ght_questions_from_database(type_of_question, connection=None):
    if connection is None:
        connection = create_server_connection()
    logger.info("Getting questions from database: " + type_of_question)
    if "/" in type_of_question:
        type_of_question = type_of_question.split("/")
        query = f'SELECT * FROM ght_questions_{type_of_question[0]} WHERE time_of_day = "{type_of_question[1]}"'
    else:
        query = f"SELECT * FROM ght_questions_{type_of_question}"
    df = pd.DataFrame(connection.connect().execute(text(query)))
    return df, connection


def get_ght_questions(type_of_question):
    df, connection = get_ght_questions_from_database(type_of_question)
    close_server_connection(connection)

    df.sort_values(by=["question_order"], inplace=True)

    rework_events = pd.DataFrame(get_rework_events_from_web())
    exploded_rework_events = rework_events.explode("questions")
    df = df.merge(
        exploded_rework_events, how="left", left_on="code", right_on="questions"
    )
    events = get_rework_events_from_google_calendar()
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
    except Exception as e:
        logger.error("Error: {error}".format(error=e))
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
    df, connection = get_ght_questions_from_database(result_dict.pop("type"), connection)
    df = df.set_index("code")
    timestamp = parser.parse(result_dict.pop("timestamp"))
    error_count = 0
    result_df = pd.DataFrame(result_dict.items(), columns=["code", "value"])
    result_df = result_df.merge(df, how="left", on="code")
    raw_connection = connection.raw_connection()
    for index, row in result_df.iterrows():
        if any(temp in row["value"] for temp in ["?", "!"]):
            add_task(
                f"{timestamp}: {row['message']} (code: {row['code']}) -> value: {row['value']}"
            )
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
