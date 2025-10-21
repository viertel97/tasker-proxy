import json
from datetime import datetime
from uuid import uuid4

import pymysql
from quarter_lib.logging import setup_logging
from quarter_lib.monica import create_monica_server_connection

from helper.db_helper import close_server_connection
from models.call import call

logger = setup_logging(__file__)


DEFAULT_ACCOUNT_ID = 1
INBOX_CONTACT_ID = 52


def add_call_rework_task(item: call):
	logger.info("Adding call rework task: {item}".format(item=item))
	connection = create_monica_server_connection()
	summary = (
		f"Incoming call by '{item.contact}' at '{item.timestamp}'"
		if item.incoming
		else f"Outgoing call to '{item.contact}' at '{item.timestamp}'"
	)
	timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	temp_dict = {
		"type": "call",
		"contact": item.contact,
		"timestamp": item.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
		"incoming": item.incoming,
	}
	description = "---\n" + json.dumps(temp_dict, indent=4, sort_keys=True) + "\n---\n\n" + item.message if item.message is not None else ""
	try:
		with connection.cursor() as cursor:
			happened_at = item.timestamp.strftime("%Y-%m-%d")
			activities_values = tuple(
				(
					uuid4(),
					DEFAULT_ACCOUNT_ID,
					summary,
					description,
					happened_at,
					timestamp,
					timestamp,
				)
			)
			cursor.execute(
				"INSERT INTO activities (uuid, account_id, summary, description, happened_at, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
				activities_values,
			)
			connection.commit()
			last_row_id = cursor.lastrowid

			activity_contact_values = tuple((last_row_id, INBOX_CONTACT_ID, DEFAULT_ACCOUNT_ID))
			cursor.execute(
				"INSERT INTO activity_contact (activity_id, contact_id, account_id) VALUES (%s, %s, %s)",
				activity_contact_values,
			)
			connection.commit()
	except pymysql.err.IntegrityError as e:
		logger.error("IntegrityError: {error}".format(error=e))
	close_server_connection(connection)
