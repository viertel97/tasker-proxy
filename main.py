import os
import platform
from pathlib import Path

import uvicorn
from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from controller import (
    audiobook_controller,
    drug_session_controller,
    ght_controller,
    session_controller,
    shield_controller,
    timer_controller, dynamic_notification_controller, smart_home_controller, leaf_controller
)

controllers = [
    drug_session_controller,
    session_controller,
    ght_controller,
    shield_controller,
    timer_controller,
    audiobook_controller,
    dynamic_notification_controller,
    smart_home_controller,leaf_controller
]

from helper.network_helper import log_request_info

app = FastAPI(debug=True)
router = APIRouter()

[app.include_router(controller.router, dependencies=[Depends(log_request_info)]) for controller in controllers]

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/logs/" + os.path.basename(__file__) + ".log"),
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.info(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


if __name__ == "__main__":
    if platform.system() == "Windows":
        uvicorn.run(f"{Path(__file__).stem}:app", host="0.0.0.0", reload=True, port=9000)
    else:
        uvicorn.run(app, host="0.0.0.0", port=9000)
