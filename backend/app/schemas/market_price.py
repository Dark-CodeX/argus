from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class MarketPriceResponse(BaseModel):
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal