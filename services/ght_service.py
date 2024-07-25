import json
import re
from datetime import datetime
import ast
import pandas as pd
from pandas import concat
import pandas.errors
import pymysql
from croniter import croniter
from dateutil import parser
from quarter_lib.logging import setup_logging

from sqlalchemy import text

from config.queries import ght_get_old_answers_query
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


def schema_matches_event(row, event):
    match row["schema"]:
        case "regex":
            return re.match(row["pattern"], event)
        case "match":
            return event == row["pattern"]
        case "contains":
            return row["pattern"] in event
        case "not_contains":
            return row["pattern"] not in event
        case "startswith":
            return event.startswith(row["pattern"])
        case "endswith":
            return event.endswith(row["pattern"])
        case _:
            return False


def schema_matches_without_event(row):
    match row["schema"]:
        case "crontab":
            return is_cron_matching_today(row["pattern"])
        case _:
            return False


def get_ght_questions_from_database(type_of_question, connection=None):
    if connection is None:
        connection = create_server_connection()
    logger.info("Getting questions from database: " + type_of_question)
    type_of_question = type_of_question.replace("/", "_")
    query = f"SELECT * FROM ght_questions_{type_of_question}"
    df = pd.DataFrame(connection.connect().execute(text(query)))
    return df, connection


def get_unique_ght_answers():
    connection = create_server_connection()
    logger.info("Getting unique last answers from database")
    df = pd.DataFrame(connection.connect().execute(text(ght_get_old_answers_query)))
    close_server_connection(connection)
    return df


def get_ght_questions(type_of_question):
    df, connection = get_ght_questions_from_database(type_of_question)
    close_server_connection(connection)

    df = handle_rework_events(df)
    df = add_mindmap_question(df)
    df = add_previous_answers_to_ght(df)

    df.sort_values(by=["question_order"], inplace=True)
    df = df[df["active"] == 1]
    df = df[["code", "message", "notation", "default_type"]]

    result = df.to_dict(orient="records")
    return result


def add_previous_answers_to_ght(df):
    if "last_answers_to_show" in df.columns:
        unique_ght_answers = get_unique_ght_answers()
        for index, row in df.query("last_answers_to_show.notnull()").iterrows():
            answer_list = ast.literal_eval(row["last_answers_to_show"])
            for answer in answer_list:
                latest_answer = unique_ght_answers.query(
                    f'ght_code == "{answer}"'
                ).iloc[0]
                message = f'Answer at "{latest_answer["ts"]}+{latest_answer["offset"]}s" for question\n"{latest_answer["message"]}" (code: {answer}):\n\n"{latest_answer["value"]}"'
                line = pd.DataFrame(
                    {
                        "code": "h4-" + answer,
                        "default_type": "h4",
                        "message": message,
                        "value": latest_answer["value"],
                        "ts": latest_answer["ts"],
                        "offset": latest_answer["offset"],
                        "active": 1,
                        "question_order": row["question_order"] - 1,
                        "notation": None,
                    },
                    index=[index],
                )
                df = concat([df.iloc[:index], line, df.iloc[index:]]).reset_index(
                    drop=True
                )
    return df


def handle_rework_events(df):
    rework_events = pd.DataFrame(get_rework_events_from_web())
    exploded_rework_events = rework_events.explode("questions")
    df = df.merge(
        exploded_rework_events, how="left", left_on="code", right_on="questions"
    )
    events = get_rework_events_from_google_calendar(
        time_threshold=1,
        calendars=[
            "Janik's Kalender",
            "Drug-Kalender",
            "Reisen",
            "Veranstaltungen",
            "Arbeit",
        ],
        skip_check= True,
    )
    for index, row in df.query("questions.notnull()").iterrows():
        if row["pattern"] and row["schema"]:
            if schema_matches_without_event(row):
                df.at[index, "active"] = 1
                continue
            for event in events:
                if schema_matches_event(row, event):
                    df.at[index, "active"] = 1
                    continue
    return df


def add_mindmap_question(df):
    if "rotating_mindmap" in df.columns:
        try:
            selected_mindmap_index = (
                df.query("rotating_mindmap == True").sample(1).index[0]
            )
            df.at[selected_mindmap_index, "active"] = 1
        except IndexError:
            logger.error("No rotating mindmap question found")
        except pandas.errors.UndefinedVariableError:
            logger.error("No column 'rotating_mindmap' found")
        except Exception as e:
            logger.error("Error: {error}".format(error=e))
    return df


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
    ght_type = result_dict.pop("type")
    df, connection = get_ght_questions_from_database(ght_type, connection)
    df = df.set_index("code")
    timestamp = parser.parse(result_dict.pop("timestamp"))
    error_count = 0
    result_df = pd.DataFrame(result_dict.items(), columns=["code", "value"])
    result_df = result_df.merge(df, how="left", on="code")
    raw_connection = connection.raw_connection()
    for index, row in result_df.iterrows():
        if row["value"] is str and any(temp in row["value"] for temp in ["?", "!"]):
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
