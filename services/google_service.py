import os
from datetime import datetime, timedelta

from dateutil import parser
from loguru import logger
from quarter_lib_old.google import build_calendar_service, get_dict, get_events_from_calendar

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
]
if os.name == "nt":
    pickle_path = r"D:\OneDrive\Code\todoist-refresher\config\token.pickle"
    creds_path = r"D:\OneDrive\Code\todoist-refresher\config\cred7.json"
else:
    pickle_path = "/home/pi/code/todoist-refresher/config/token.pickle"
    creds_path = "/home/pi/code/todoist-refresher/config/cred7.json"

creds = None

DEBUG = os.name == "nt"


def get_events():
    calendar_service = build_calendar_service()

    calendar_dict = get_dict(calendar_service)

    event_list = []

    event_list.extend(get_events_from_calendar("Janik's Kalender", calendar_dict, calendar_service))
    event_list.extend(get_events_from_calendar("Drug-Kalender", calendar_dict, calendar_service))
    event_list.extend(get_events_from_calendar("Reisen", calendar_dict, calendar_service))
    event_list.extend(get_events_from_calendar("Veranstaltungen", calendar_dict, calendar_service))

    return event_list


def get_date_or_datetime(event, key):
    date_or_datetime = event[key]
    if "date" in date_or_datetime:
        date_or_datetime = date_or_datetime["date"]
    else:
        date_or_datetime = date_or_datetime["dateTime"]
    return parser.parse(date_or_datetime).replace(tzinfo=None)


def get_events_for_rework():
    events = get_events()
    events = [event for event in events if event["status"] != "cancelled"]
    result = []
    yesterday = (datetime.now() - timedelta(days=1.5))
    tomorrow = (datetime.now() + timedelta(days=1.5))
    for event in events:
        start = get_date_or_datetime(event, "start")
        if yesterday <= start <= tomorrow:
            result.append("{summary}({start})".format(summary=event['summary'], start=start.strftime("%d.%m.%Y %H:%M")))
    sorted_list = sorted(result, key=lambda x: x.split("(")[1])
    return sorted_list
