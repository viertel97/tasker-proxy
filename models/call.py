from datetime import datetime

from pydantic import BaseModel


class call(BaseModel):
	timestamp: datetime
	message: str
	contact: str
	incoming: bool
