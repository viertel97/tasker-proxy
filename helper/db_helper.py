import os
from datetime import timedelta

import pymysql.cursors
from dateutil import parser
from loguru import logger
from models.db_models import (
    app_usage,
    meditation_session,
    power,
    reading_session,
    timer,
    yoga_session,
)

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)
DB_HOST = os.environ["DB_HOST"]

DB_NAME = os.environ["DB_NAME"]
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]


def create_server_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=3306,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
    )


def close_server_connection(connection):
    connection.close()
