import logging
import os
import platform

import uvicorn
from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from controller import controllers
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
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


if __name__ == "__main__":
    if platform.system() == "Windows":
        uvicorn.run(app, host="0.0.0.0", port=9000)
    else:
        uvicorn.run(app, host="192.168.178.100", port=9000)
