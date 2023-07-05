import os

import pymysql.cursors
from loguru import logger
from quarter_lib.akeyless import get_target
from sqlalchemy import create_engine
import urllib.parse

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


def create_sqlalchemy_engine():
    return create_engine(
        "mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4".format(
            user=DB_USER_NAME,
            password=urllib.parse.quote_plus(DB_PASSWORD),
            host=DB_HOST_NAME,
            port=DB_PORT,
            db=DB_NAME,
        ),
        echo=True,
    )
