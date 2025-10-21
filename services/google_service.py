import os
from datetime import datetime, timedelta

from dateutil import parser
from quarter_lib.logging import setup_logging
from quarter_lib.google_calendar import build_calendar_service, get_dict

logger = setup_logging(__file__)


def get_events_from_calendar(calendar_name, calendar_dict, calendar_service, query_params=None):
	event_list = []
	page_token = None
	while True:
		if query_params is None:
			events = (
				calendar_service.events()
				.list(
					calendarId=calendar_dict[calendar_name]["id"],
					pageToken=page_token,
				)
				.execute()
			)
		else:
			events = (
				calendar_service.events()
				.list(
					calendarId=calendar_dict[calendar_name]["id"],
					pageToken=page_token,
					**query_params,
				)
				.execute()
			)
		for event in events["items"]:
			event_list.append(event)
		page_token = events.get("nextPageToken")
		if not page_token:
			break
	return event_list


def get_events():
	calendar_service = build_calendar_service()

	calendar_dict = get_dict(calendar_service)

	event_list = []

	event_list.extend(get_events_from_calendar("Janik's Kalender", calendar_dict, calendar_service))
	event_list.extend(get_events_from_calendar("Drug-Kalender", calendar_dict, calendar_service))
	event_list.extend(get_events_from_calendar("Reisen", calendar_dict, calendar_service))
	event_list.extend(get_events_from_calendar("Veranstaltungen", calendar_dict, calendar_service))

	return event_list


def get_events_by_timespan(start, end, calendars=None):
	if calendars is None:
		calendars = ["Janik's Kalender", "Drug-Kalender", "Reisen", "Veranstaltungen"]
	calendar_service = build_calendar_service()

	calendar_dict = get_dict(calendar_service)

	event_list = []

	query_params = {
		"singleEvents": True,
		"timeMin": start.isoformat() + "Z",
		"timeMax": end.isoformat() + "Z",
	}
	for calendar in calendars:
		event_list.extend(get_events_from_calendar(calendar, calendar_dict, calendar_service, query_params))
	return event_list


def get_date_or_datetime(event, key):
	date_or_datetime = event[key]
	if "date" in date_or_datetime:
		date_or_datetime = date_or_datetime["date"]
	else:
		date_or_datetime = date_or_datetime["dateTime"]
	return parser.parse(date_or_datetime).replace(tzinfo=None)


def get_rework_events_from_google_calendar(time_threshold=1.5, calendars=None, skip_check=False):
	yesterday = datetime.now() - timedelta(days=time_threshold)
	tomorrow = datetime.now() + timedelta(days=time_threshold)
	events = get_events_by_timespan(yesterday, tomorrow, calendars)
	events = [event for event in events if event["status"] != "cancelled"]
	result = []

	for event in events:
		start = get_date_or_datetime(event, "start")
		if skip_check or (yesterday <= start <= tomorrow):
			result.append("{summary} ({start})".format(summary=event["summary"], start=start.strftime("%d.%m.%Y %H:%M")))
	sorted_list = sorted(result, key=lambda x: x.split("(")[1])
	return sorted_list
