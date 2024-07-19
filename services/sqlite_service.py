import sqlite3

import pandas as pd
from quarter_lib.logging import setup_logging
from sqlalchemy import text

from helper.db_helper import create_sqlalchemy_engine

logger = setup_logging(__name__)


def update_koreader_tables(file_path):
    sqlite_connection = sqlite3.connect(file_path)
    df_book = pd.read_sql_query("SELECT * FROM book", sqlite_connection)
    df_page_stat_data = pd.read_sql_query(
        "SELECT * FROM page_stat_data", sqlite_connection
    )
    sqlite_connection.close()

    engine = create_sqlalchemy_engine()
    update_result_koreader_book = update_table_with_dataframe(
        "koreader_book", df_book, ["id"], engine
    )
    update_result_koreader_page_stat_data = update_table_with_dataframe(
        "koreader_page_stat_data",
        df_page_stat_data,
        ["id_book", "page", "start_time"],
        engine,
    )

    engine.dispose()
    logger.info("update_koreader_tables finished")
    return update_result_koreader_book, update_result_koreader_page_stat_data


def update_table_with_dataframe(table_name, new_data, unique_columns, engine):
    existing_query = f"SELECT {', '.join(unique_columns)} FROM {table_name}"

    existing_data = pd.DataFrame(engine.connect().execute(text(existing_query)))

    merged_data = new_data.merge(
        existing_data, on=unique_columns, how="left", indicator=True
    )
    new_records = merged_data[merged_data["_merge"] == "left_only"]

    if not new_records.empty:
        new_records.drop("_merge", axis=1, inplace=True)
        logger.info(f"Inserting {len(new_records)} new records into {table_name}")
        result = new_records.to_sql(table_name, engine, if_exists="append", index=False)
        if not result:
            return 0
        return result
    else:
        logger.info(f"No new records to insert into {table_name}")
        return 0
