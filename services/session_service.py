import os
from datetime import timedelta

import pymysql.cursors
from helper.db_helper import close_server_connection, create_server_connection
from loguru import logger
from models.db_models import meditation_session, reading_session, yoga_session

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


def add_reading_session(item: reading_session):
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


def add_meditation_session(item: meditation_session):
    item.start = item.start + timedelta(seconds=30)  # Warm Up
    error_flag = False
    connection = create_server_connection()
    try:
        with connection.cursor() as cursor:
            values = tuple(
                (
                    item.start,
                    item.start.tzinfo.utcoffset(item.start).seconds,
                    item.end,
                    item.end.tzinfo.utcoffset(item.end).seconds,
                    item.type,
                )
            )
            cursor.execute(
                "INSERT INTO meditation (start, start_offset, end, end_offset, type) VALUES (%s, %s, %s, %s, %s)",
                values,
            )
            connection.commit()
    except pymysql.err.IntegrityError as e:
        logger.error("IntegrityError: {error}".format(error=e))
        error_flag = True
    close_server_connection(connection)
    return error_flag


def add_yoga_session(item: yoga_session):
    connection = create_server_connection()
    try:
        with connection.cursor() as cursor:
            values = tuple(
                (
                    item.start,
                    item.start.tzinfo.utcoffset(item.start).seconds,
                    item.end,
                    item.end.tzinfo.utcoffset(item.end).seconds,
                    item.type,
                )
            )
            cursor.execute(
                "INSERT INTO yoga (start, start_offset, end, end_offset, type) VALUES (%s, %s, %s, %s, %s)",
                values,
            )
            connection.commit()
    except pymysql.err.IntegrityError as e:
        logger.error("IntegrityError: {error}".format(error=e))
    close_server_connection(connection)
