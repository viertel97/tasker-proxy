import urllib.parse

from quarter_lib.akeyless import get_target
from quarter_lib.logging import setup_logging
from sqlalchemy import create_engine

logger = setup_logging(__file__)


DB_USER_NAME, DB_HOST_NAME, DB_PASSWORD, DB_PORT, DB_NAME = get_target("private")
(
	MONICA_DB_USER_NAME,
	MONICA_DB_HOST_NAME,
	MONICA_DB_PASSWORD,
	MONICA_DB_PORT,
	MONICA_DB_NAME,
) = get_target("monica")


def create_server_connection():
	return create_engine(
		"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4".format(
			user=DB_USER_NAME,
			password=urllib.parse.quote_plus(DB_PASSWORD),
			host=DB_HOST_NAME,
			port=DB_PORT,
			db=DB_NAME,
		),
		echo=True,
	)


def create_monica_server_connection():
	return create_engine(
		"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4".format(
			user=MONICA_DB_USER_NAME,
			password=urllib.parse.quote_plus(MONICA_DB_PASSWORD),
			host=MONICA_DB_HOST_NAME,
			port=MONICA_DB_PORT,
			db=MONICA_DB_NAME,
		),
		echo=True,
	)


def close_server_connection(connection):
	connection.dispose()


def create_sqlalchemy_engine():
	return create_engine(
		"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4".format(
			user=DB_USER_NAME,
			password=urllib.parse.quote_plus(DB_PASSWORD),
			host=DB_HOST_NAME,
			port=DB_PORT,
			db=DB_NAME,
		),
		echo=True,
	)
