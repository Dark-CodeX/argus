from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class HoldingValuation(BaseModel):
    holding_id: UUID
    asset_id: UUID
    symbol: str

    quantity: Decimal
    average_cost: Decimal
    current_price: Decimal

    cost_basis: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal


class PortfolioValuation(BaseModel):
    portfolio_id: UUID
    portfolio_name: str

    total_cost_basis: Decimal
    total_market_value: Decimal

    total_realized_pnl: Decimal
    total_unrealized_pnl: Decimal
    total_pnl: Decimal

    holdings: list[HoldingValuation]