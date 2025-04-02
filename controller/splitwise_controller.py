from fastapi import APIRouter
from pydantic import BaseModel
from quarter_lib.logging import setup_logging

from services.splitwise_service import add_placeholder_to_splitwise
from services.telegram_service import send_to_telegram

logger = setup_logging(__name__)

router = APIRouter(prefix="/splitwise", tags=["splitwise"])


class AddExpenseItem(BaseModel):
	description: str


@logger.catch
@router.post("/add")
async def add_splitwise_entry(item: AddExpenseItem):
	result = add_placeholder_to_splitwise(item.description)
	if result.status_code != 200:
		await send_to_telegram("Error adding new splitwise entry: " + item.description)
	else:
		await send_to_telegram("Successfully added new splitwise entry: " + item.description)
	return result.json()
