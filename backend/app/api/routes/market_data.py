from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.schemas.market_price import MarketPriceResponse
from app.services.market_data import get_historical_prices


router = APIRouter(
    prefix="/assets",
    tags=["Market Data"],
)


@router.get(
    "/{symbol}/prices",
    response_model=list[MarketPriceResponse],
)
def get_asset_prices(
    symbol: str,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be earlier than or equal to end_date",
        )

    asset = db.scalar(
        select(Asset).where(
            Asset.symbol == symbol.upper()
        )
    )

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    prices = get_historical_prices(
        asset_id=asset.id,
        start_date=start_date,
        end_date=end_date,
        db=db,
    )

    return [
        MarketPriceResponse(
            date=price.price_date,
            open=price.open,
            high=price.high,
            low=price.low,
            close=price.close,
            volume=price.volume,
        )
        for price in prices
    ]
