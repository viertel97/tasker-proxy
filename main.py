import os
import platform

import uvicorn
from fastapi import FastAPI
from loguru import logger

import api_objects
import helper
from apis import TODOIST_API
from habit_tracker import (
    track_habit,
    track_mediation_habit,
    track_reading_habit,
    track_time,
)
from proxy import todoist_proxy

app = FastAPI()

proxy_mapping_dict = helper.get_config("tasker_mapping.json")
habit_tracker_mapping_dict = helper.get_config("habit_tracker_mapping.json")


logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


@logger.catch
@app.post("/proxy/{service}")
def proxy(service: str):
    logger.info("service: " + service)
    selected_service = proxy_mapping_dict[service]
    todoist_proxy(selected_service)


@logger.catch
@app.post("/habit-tracker/sport/{service}")
def habit_tracker(service: str):
    logger.info("habit-tracker: " + service)
    selected_service = habit_tracker_mapping_dict[service]
    track_habit(selected_service)
    selected_service = proxy_mapping_dict["sport"]
    todoist_proxy(selected_service)


@logger.catch
@app.post("/habit-tracker/meditation")
def test(item: api_objects.meditation_session):
    track_mediation_habit(item)


@logger.catch
@app.post("/habit-tracker/reading")
def test(item: api_objects.reading_session):
    track_reading_habit(item)


@logger.catch
@app.post("/habit-tracker/timer")
def test(item: api_objects.timer):
    track_time(item)


@app.get("/proxy")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    if platform.system() == "Windows":
        uvicorn.run(app, host="0.0.0.0", port=9000)
    else:
        uvicorn.run(app, host="192.168.178.100", port=9000)
