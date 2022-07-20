import os

import pymysql.cursors
from loguru import logger

import api_objects

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


def add_timer(item: api_objects.timer):
    connection = create_server_connection()
    try:
        with connection.cursor() as cursor:
            values = tuple((item.context, item.start_ms, item.end_ms))
            cursor.execute(
                "INSERT INTO timer (context, start_ms, end_ms) VALUES (%s, %s, %s)",
                values,
            )
            connection.commit()
    except pymysql.err.IntegrityError as e:
        logger.error("IntegrityError: {error}".format(error=e))
    close_server_connection(connection)


def add_reading_session(item: api_objects.reading_session):
    connection = create_server_connection()
    try:
        with connection.cursor() as cursor:
            values = tuple(
                (
                    item.title,
                    item.reading_seconds,
                    item.page_old,
                    item.page_new,
                    item.reading_type,
                    item.finished,
                    item.reading_start_ms,
                    item.reading_end_ms,
                )
            )
            cursor.execute(
                "INSERT INTO reading (title, reading_seconds, page_old, page_new, reading_type, finished, reading_start_ms, reading_end_ms) VALUES (%s, %s, %s, %s, %s,%s, %s, %s)",
                values,
            )
            connection.commit()
    except pymysql.err.IntegrityError as e:
        logger.error("IntegrityError: {error}".format(error=e))
    close_server_connection(connection)


def add_meditation_session(item: api_objects.meditation_session):
    connection = create_server_connection()
    try:
        with connection.cursor() as cursor:
            values = tuple(
                (
                    item.warm_up_seconds,
                    item.meditation_seconds,
                    item.yoga_seconds,
                    item.morning_meditation,
                    item.meditation_start_ms,
                    item.meditation_end_ms,
                    item.yoga_start_ms,
                    item.yoga_end_ms,
                )
            )
            cursor.execute(
                "INSERT INTO meditation (warm_up_seconds, meditation_seconds, yoga_seconds, morning_meditation, meditation_start_ms, meditation_end_ms, yoga_start_ms, yoga_end_ms) VALUES (%s, %s, %s, %s, %s,%s, %s, %s)",
                values,
            )
            connection.commit()
    except pymysql.err.IntegrityError as e:
        logger.error("IntegrityError: {error}".format(error=e))
    close_server_connection(connection)
