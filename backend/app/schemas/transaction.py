from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.transaction import TransactionType


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    amount: int
    type: TransactionType
    timestamp: datetime
    reference_id: UUID | None = None
