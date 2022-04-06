import os
import platform

import uvicorn
from fastapi import APIRouter, Depends, FastAPI, Request
from loguru import logger

import api_objects
import helper
from habit_tracker import (
    track_habit,
    track_mediation_habit,
    track_reading_habit,
    track_time,
)
from proxy import todoist_proxy

app = FastAPI(debug=True)
router = APIRouter()

proxy_mapping_dict = helper.get_config("tasker_mapping.json")
habit_tracker_mapping_dict = helper.get_config("habit_tracker_mapping.json")

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


async def log_request_info(request: Request):
    logger.debug(f"{request.method} {request.url}")
    logger.debug("Params:")
    for name, value in request.path_params.items():
        logger.debug(f"\t{name}: {value}")
    logger.debug("Headers:")
    for name, value in request.headers.items():
        logger.debug(f"\t{name}: {value}")
    logger.debug("Body:")
    request_body = await request.json()
    for key in request_body.keys():
        logger.debug(f"\t{key}: {request_body[key]}")


@logger.catch
@router.post("/proxy/{service}")
async def proxy(service: str):
    logger.info("service: " + service)
    selected_service = proxy_mapping_dict[service]
    todoist_proxy(selected_service)


@logger.catch
@router.post("/habit-tracker/sport/{service}")
async def habit_tracker(service: str):
    logger.info("habit-tracker: " + service)
    selected_service = habit_tracker_mapping_dict[service]
    track_habit(selected_service)
    selected_service = proxy_mapping_dict["sport"]
    todoist_proxy(selected_service)


@logger.catch
@router.post("/habit-tracker/meditation")
async def test(item: api_objects.meditation_session):
    track_mediation_habit(item)


@logger.catch
@router.post("/habit-tracker/reading")
async def test(item: api_objects.reading_session):
    track_reading_habit(item)


@logger.catch
@router.post("/habit-tracker/timer")
async def test(item: api_objects.timer):
    track_time(item)


@app.get("/proxy")
async def read_root():
    return {"Hello": "World"}


app.include_router(router, dependencies=[Depends(log_request_info)])


if __name__ == "__main__":
    if platform.system() == "Windows":
        uvicorn.run(app, host="0.0.0.0", port=9000)
    else:
        uvicorn.run(app, host="192.168.178.100", port=9000)
