import os

import pymysql
from loguru import logger
from quarter_lib_old.google import add_event_to_calendar

from helper.db_helper import close_server_connection, create_server_connection
from models.db_models import app_usage, power

logger.add(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__))
        + "/logs/"
        + os.path.basename(__file__)
        + ".log"
    ),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


def add_start_stop(item: power):
    connection = create_server_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO `startup-shutdown-shield` (type) values (%s)",
                item.type,
            )
            connection.commit()
            logger.info("Inserted shield " + item.type)
    except pymysql.err.IntegrityError as e:
        logger.error("IntegrityError: {error}".format(error=e))
    except Exception as e:
        logger.error("Exception: {error}".format(error=e))
    finally:
        close_server_connection(connection)


def add_app_usage(item: app_usage):
    connection = create_server_connection()
    try:
        with connection.cursor() as cursor:
            values = tuple(
                (
                    item.app,
                    item.start,
                    item.start.tzinfo.utcoffset(item.start).seconds,
                    item.end,
                    item.end.tzinfo.utcoffset(item.end).seconds,
                )
            )
            cursor.execute(
                "INSERT INTO shield_app_usage (app, start, start_offset, end, end_offset) VALUES (%s, %s, %s, %s, %s)",
                values,
            )
            connection.commit()
    except pymysql.err.IntegrityError as e:
        logger.error("IntegrityError: {error}".format(error=e))
    add_event_to_calendar(item.app, item.start, item.end)
    close_server_connection(connection)
