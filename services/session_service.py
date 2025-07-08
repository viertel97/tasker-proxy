from datetime import timedelta

import pymysql.cursors
from quarter_lib.logging import setup_logging

from helper.db_helper import close_server_connection, create_server_connection
from models.db_models import meditation_session, reading_session, yoga_session
from services.telegram_service import send_to_telegram

logger = setup_logging(__file__)


def add_reading_session(item: reading_session):
	connection = create_server_connection()
	raw_connection = connection.raw_connection()
	try:
		with raw_connection.cursor() as cursor:
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
			raw_connection.commit()
	except pymysql.err.IntegrityError as e:
		logger.error("IntegrityError: {error}".format(error=e))
	close_server_connection(connection)


async def add_meditation_session(item: meditation_session):
	item.start = item.start + timedelta(seconds=30)  # Warm Up
	error_flag = False
	connection = create_server_connection()
	raw_connection = connection.raw_connection()
	try:
		with raw_connection.cursor() as cursor:
			values = tuple(
				(
					item.start,
					item.start.tzinfo.utcoffset(item.start).seconds,
					item.end,
					item.end.tzinfo.utcoffset(item.end).seconds,
					item.type,
					item.selected_duration,
				)
			)
			cursor.execute(
				"INSERT INTO meditation (start, start_offset, end, end_offset, type, selected_duration) VALUES (%s, %s, %s, %s, %s, %s)",
				values,
			)
			raw_connection.commit()
	except pymysql.err.IntegrityError as e:
		logger.error("IntegrityError: {error}".format(error=e))
		error_flag = True
	close_server_connection(connection)
	await send_to_telegram("Meditation session added to database")
	return error_flag


async def add_yoga_session(item: yoga_session):
	connection = create_server_connection()
	raw_connection = connection.raw_connection()
	try:
		with raw_connection.cursor() as cursor:
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
			raw_connection.commit()
	except pymysql.err.IntegrityError as e:
		logger.error("IntegrityError: {error}".format(error=e))
	close_server_connection(connection)
	await send_to_telegram("Yoga session added to database")
