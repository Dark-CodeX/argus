from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.asset import AssetResponse


class HoldingResponse(BaseModel):
    id: UUID
    portfolio_id: UUID
    asset_id: UUID
    quantity: Decimal
    average_cost: Decimal
    created_at: datetime
    updated_at: datetime
    asset: AssetResponse

    model_config = ConfigDict(from_attributes=True)