import logging
import os
import platform
from json import JSONDecodeError, loads

import uvicorn
from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

import api_objects
import helper
from habit_tracker import (
    track_ght_db,
    track_habit,
    track_list,
    track_meditation_habit_db,
    track_reading_habit_db,
    track_time_db,
    track_yoga_habit_db,
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


async def log_request_info(request: Request):
    logger.debug(f"{request.method} {request.url}")
    if request.path_params.items():
        logger.debug("Params:")
        for name, value in request.path_params.items():
            logger.debug(f"\t{name}: {value}")
    if request.headers.items():
        logger.debug("Headers:")
        for name, value in request.headers.items():
            logger.debug(f"\t{name}: {value}")
    logger.debug("Body:")
    try:
        request_body = await request.json()
        try:
            request_body = loads(request_body)
        except Exception:
            pass
        if isinstance(request_body, list):
            for item in request_body:
                for key in item.keys():
                    logger.debug(f"\t{key}: {item[key]}")
        else:
            for key in request_body.keys():
                logger.debug(f"\t{key}: {request_body[key]}")

    except JSONDecodeError:
        logger.debug("Wrong Empty body")


@logger.catch
@router.post("/proxy/{service}")
async def proxy(service: str):
    logger.info("service: " + service)
    selected_service = proxy_mapping_dict[service]
    todoist_proxy(selected_service)


@logger.catch
@router.post("/habit-tracker/drink")
async def get_drink(request: Request):
    ght_data = await request.json()
    logger.info("service: " + str(ght_data))


@logger.catch
@router.post("/habit-tracker/ght")
async def get_body(request: Request):
    ght_data = await request.json()
    logger.info("service: " + str(ght_data))
    track_ght_db(ght_data)


@logger.catch
@router.post("/habit-tracker/sport/{service}")
async def habit_tracker(service: str):
    logger.info("habit-tracker: " + service)
    service = habit_tracker_mapping_dict[service]
    track_habit(service)
    todoist_proxy(proxy_mapping_dict["sport"])


@logger.catch
@router.post("/habit-tracker/list")
async def track_list(request: Request):
    try:
        item = await request.json()
        track_list(item)
    except Exception as e:
        logger.error(e)


@logger.catch
@router.post("/habit-tracker/meditation")
async def track_meditation(item: api_objects.meditation_session):
    error_flag = track_meditation_habit_db(item)
    if not error_flag:
        selected_service = proxy_mapping_dict["meditation-evening"]
        # todoist_proxy(selected_service)


@logger.catch
@router.post("/habit-tracker/yoga")
async def track_meditation(item: api_objects.yoga_session):
    track_yoga_habit_db(item)


@logger.catch
@router.post("/habit-tracker/reading")
async def track_reading(item: api_objects.reading_session):
    track_reading_habit_db(item)
    selected_service = proxy_mapping_dict["reading"]
    todoist_proxy(selected_service)


@logger.catch
@router.post("/habit-tracker/timer")
async def track_timer(item: api_objects.timer):
    track_time_db(item)


@app.get("/proxy")
async def read_root():
    return {"Hello": "World"}


app.include_router(router, dependencies=[Depends(log_request_info)])


if __name__ == "__main__":
    if platform.system() == "Windows":
        uvicorn.run(app, host="0.0.0.0", port=9000)
    else:
        uvicorn.run(app, host="192.168.178.100", port=9000)
