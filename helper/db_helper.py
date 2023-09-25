import os

import pymysql.cursors
from loguru import logger
from quarter_lib.akeyless import get_target
from sqlalchemy import create_engine
import urllib.parse
from quarter_lib.logging import setup_logging

logger = setup_logging(__file__)


DB_USER_NAME, DB_HOST_NAME, DB_PASSWORD, DB_PORT, DB_NAME = get_target("private")
MONICA_DB_USER_NAME, MONICA_DB_HOST_NAME, MONICA_DB_PASSWORD, MONICA_DB_PORT, MONICA_DB_NAME = get_target("monica")

def create_server_connection():
    return pymysql.connect(
        host=DB_HOST_NAME,
        port=3306,
        user=DB_USER_NAME,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
    )

def create_monica_server_connection():
    return pymysql.connect(
        host=MONICA_DB_HOST_NAME,
        port=3306,
        user=MONICA_DB_USER_NAME,
        password=MONICA_DB_PASSWORD,
        database=MONICA_DB_NAME,
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
