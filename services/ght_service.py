import os

import pandas as pd
import pymysql
from dateutil import parser
from loguru import logger
from quarter_lib.database import close_server_connection, create_server_connection

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


def get_ght_questions(type_of_question):
    connection = create_server_connection()
    df = pd.read_sql("SELECT * FROM ght_questions_" + type_of_question, connection)
    close_server_connection(connection)
    df.sort_values(by=["question_order"], inplace=True)
    df = df[df["active"] == 1]
    df = df[["code", "message", "notation", "default_type"]]
    return df.to_json(orient="values")


def get_exercises(type):
    connection = create_server_connection()
    df = pd.read_sql("SELECT * FROM exercises where type = '{type}' and active = 1".format(type=type), connection)
    close_server_connection(connection)
    return_list = []
    df.apply(lambda row: [return_list.append(row["exercise"]) for x in range(0, row["quantifier"])], axis=1)
    return return_list


def add_ght_entry(item: dict):
    timestamp = parser.parse(item.pop("timestamp"))
    connection = create_server_connection()
    for code, value in item.items():
        try:
            with connection.cursor() as cursor:
                values = tuple((code, str(value), timestamp, timestamp.tzinfo.utcoffset(timestamp).seconds))
                cursor.execute("INSERT INTO `ght` (`code`, `value`, `ts`, `offset`) VALUES (%s, %s, %s, %s)", values)
                connection.commit()
        except pymysql.err.IntegrityError as e:
            logger.error("IntegrityError: {error}".format(error=e))
            continue

    close_server_connection(connection)
