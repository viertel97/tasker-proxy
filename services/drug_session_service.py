import os
from datetime import timedelta

import pymysql.cursors
from loguru import logger
from quarter_lib_old.database import close_server_connection, create_server_connection

from models.db_models import drug_session

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


def generate_insert(keys):
    return "INSERT INTO d_session ({keys}) VALUES ({values})".format(
        keys=", ".join(keys), values=", ".join(["%s"] * len(keys))
    )


def add_drug_session(item: drug_session):
    item_dict = {k: v for k, v in item.dict().items() if v}
    connection = create_server_connection()
    try:
        with connection.cursor() as cursor:
            values = tuple(item_dict.values())
            sql = generate_insert(item_dict.keys())
            cursor.execute(
                sql,
                values,
            )
            connection.commit()
    except pymysql.err.IntegrityError as e:
        logger.error("IntegrityError: {error}".format(error=e))
    close_server_connection(connection)
