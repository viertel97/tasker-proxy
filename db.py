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
            values = tuple(
                (
                    item.context,
                    item.start,
                    item.start.tzinfo.utcoffset(item.start).seconds,
                    item.end,
                    item.end.tzinfo.utcoffset(item.end).seconds,
                )
            )
            cursor.execute(
                "INSERT INTO timer (context, start, start_offset, end, end_offset) VALUES (%s, %s, %s, %s, %s)",
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
                    item.start,
                    item.start.tzinfo.utcoffset(item.start).seconds,
                    item.end,
                    item.end.tzinfo.utcoffset(item.end).seconds,
                    item.page_old,
                    item.page_new,
                    item.reading_type,
                    item.finished,
                )
            )
            cursor.execute(
                "INSERT INTO reading (title, start, start_offset, end, end_offset, page_old, page_new, reading_type, finished) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s)",
                values,
            )
            connection.commit()
    except pymysql.err.IntegrityError as e:
        logger.error("IntegrityError: {error}".format(error=e))
    close_server_connection(connection)


def add_meditation_session(item: api_objects.meditation_session):
    error_flag = False
    connection = create_server_connection()
    try:
        with connection.cursor() as cursor:
            values = tuple(
                (
                    item.meditation_start,
                    item.meditation_start.tzinfo.utcoffset(item.meditation_start).seconds,
                    item.meditation_end,
                    item.meditation_end.tzinfo.utcoffset(item.meditation_end).seconds,
                )
            )
            cursor.execute(
                "INSERT INTO meditation (meditation_start, start_offset, meditation_end, end_offset) VALUES (%s, %s, %s, %s)",
                values,
            )
            connection.commit()
    except pymysql.err.IntegrityError as e:
        logger.error("IntegrityError: {error}".format(error=e))
        error_flag = True
    close_server_connection(connection)
    return error_flag


def add_yoga_session(item: api_objects.yoga_session):
    connection = create_server_connection()
    try:
        with connection.cursor() as cursor:
            values = tuple(
                (
                    item.start,
                    item.start.tzinfo.utcoffset(item.start).seconds,
                    item.end,
                    item.end.tzinfo.utcoffset(item.end).seconds,
                )
            )
            cursor.execute(
                "INSERT INTO yoga (start, start_offset, end, end_offset) VALUES (%s, %s, %s, %s)",
                values,
            )
            connection.commit()
    except pymysql.err.IntegrityError as e:
        logger.error("IntegrityError: {error}".format(error=e))
    close_server_connection(connection)


def add_ght_entry(item: dict):
    timestamp = item.pop("timestamp")
    offset = item.pop("offset")
    connection = create_server_connection()
    for code, value in item.items():
        try:
            with connection.cursor() as cursor:
                values = tuple((code, value, timestamp, offset))
                cursor.execute("INSERT INTO `ght` (`code`, `value`, `ts`, `offset`) VALUES (%s, %s, %s, %s)", values)
                connection.commit()
        except pymysql.err.IntegrityError as e:
            logger.error("IntegrityError: {error}".format(error=e))
            continue
    close_server_connection(connection)
