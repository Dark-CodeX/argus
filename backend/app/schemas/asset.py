from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AssetResponse(BaseModel):
    id: UUID
    symbol: str
    name: str
    asset_type: str
    exchange: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)