import traceback
from pathlib import Path

import uvicorn
from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from quarter_lib.logging import setup_logging

from config.api_documentation import description, tags_metadata, title
from controller import (
	audiobook_controller,
	call_controller,
	drug_session_controller,
	dynamic_notification_controller,
	ght_controller,
	leaf_controller,
	obsidian_controller,
	session_controller,
	shield_controller,
	smart_home_controller,
	splitwise_controller,
	timer_controller,
	wol_controller,
)
from helper.network_helper import DEBUG, log_request_info
from services.telegram_service import send_to_telegram

controllers = [
	drug_session_controller,
	session_controller,
	ght_controller,
	shield_controller,
	timer_controller,
	audiobook_controller,
	splitwise_controller,
	dynamic_notification_controller,
	smart_home_controller,
	leaf_controller,
	obsidian_controller,
	call_controller,
	wol_controller,
]

logger = setup_logging(__name__)

logger.info(f"DEBUG: {DEBUG}")

app = FastAPI(debug=DEBUG, openapi_tags=tags_metadata, title=title, description=description)
router = APIRouter()

[app.include_router(controller.router, dependencies=[Depends(log_request_info)]) for controller in controllers]


@app.get("/")
def health():
	return {"status": "ok"}


@app.post("/blabla")
async def test():
	raise HTTPException("test")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
	logger.info(f"{request}: {exc_str}")
	content = {"status_code": 10422, "message": exc_str, "data": None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
	items = request.path_params.items()
	headers = request.headers.items()

	request_logging_string = f"{request.method} {request.url}\n\n Headers:\n{headers}\n\nItems:\n{items}"
	exception_logging_string = f"{exc.__class__.__name__}: {exc}\n\n{''.join(traceback.TracebackException.from_exception(exc).format())}"
	logging_string = f"Exception:\n{exception_logging_string}\n---------\nRequest:\n{request_logging_string}\n\n"
	await send_to_telegram(logging_string)
	logger.error(logging_string)
	return JSONResponse(
		content={
			"status_code": 500,
			"message": "Internal Server Error",
			"data": None,
		},
		status_code=500,
	)


if __name__ == "__main__":
	if DEBUG:
		uvicorn.run(f"{Path(__file__).stem}:app", host="0.0.0.0", reload=True, port=9000)
	else:
		uvicorn.run(f"{Path(__file__).stem}:app", host="0.0.0.0", port=9000, workers=1)
