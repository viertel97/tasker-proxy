from fastapi import APIRouter
from quarter_lib.logging import setup_logging

import services.persistence_service as persistence_service

logger = setup_logging(__name__)
router = APIRouter(prefix="/wol", tags=["wol"])


@logger.catch
@router.post("/status")
async def change_status():
	persistence_service.LEAVE_MONITORS_OFF = True
	logger.info("Received change_status post request")
	return {"status": "ok"}


@logger.catch
@router.get("/status")
async def get_status():
	temp = persistence_service.LEAVE_MONITORS_OFF
	persistence_service.LEAVE_MONITORS_OFF = False
	logger.info("Received change_status get request: result: " + str(temp))
	return temp
