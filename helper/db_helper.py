import os

import pymysql.cursors
from loguru import logger
from quarter_lib.akeyless import get_target

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)
DB_USER_NAME, DB_HOST_NAME, DB_PASSWORD, DB_PORT, DB_NAME = get_target("private")


def create_server_connection():
    return pymysql.connect(
        host=DB_HOST_NAME,
        port=3306,
        user=DB_USER_NAME,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
    )


def close_server_connection(connection):
    connection.close()
