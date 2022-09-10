import os

import pymysql.cursors
from helper.db_helper import close_server_connection, create_server_connection
from loguru import logger
from models.db_models import timer

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


def add_timer(item: timer):
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
