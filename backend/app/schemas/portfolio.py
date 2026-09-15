from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(
        default=None,
        max_length=500,
    )


class PortfolioUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )


class PortfolioResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_at: datetime
