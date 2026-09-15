from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    asset_id: UUID
    transaction_type: TransactionType
    quantity: Decimal = Field(gt=0)
    price: Decimal = Field(gt=0)
    fees: Decimal = Field(default=Decimal("0"), ge=0)
    executed_at: datetime


class TransactionResponse(BaseModel):
    id: UUID
    portfolio_id: UUID
    asset_id: UUID
    transaction_type: TransactionType
    quantity: Decimal
    price: Decimal
    fees: Decimal
    realized_pnl: Decimal
    executed_at: datetime
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }