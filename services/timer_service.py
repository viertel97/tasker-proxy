import pymysql.cursors
from quarter_lib.logging import setup_logging

from helper.db_helper import create_server_connection, close_server_connection
from models.db_models import timer

logger = setup_logging(__file__)


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
    except Exception as e:
        logger.error("Exception: {error}".format(error=e))
    close_server_connection(connection)
