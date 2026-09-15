import json
from datetime import date
from decimal import Decimal
from typing import Any, Hashable
from uuid import UUID

import yfinance as yf
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.market_prices import MarketPrice

from app.cache.redis import redis_client


def fetch_historical_data(
    symbol: str,
    start_date: date,
    end_date: date,
) -> list[dict[str, Any]]:
    if start_date >= end_date:
        raise ValueError("start_date must be earlier than end_date")

    ticker = yf.Ticker(symbol)

    dataframe = ticker.history(
        start=start_date,
        end=end_date,
        auto_adjust=False,
    )

    if dataframe.empty:
        return []

    dataframe = dataframe.reset_index()

    records: list[dict[str, Any]] = []

    for _, row in dataframe.iterrows():
        record = {
            "date": row["Date"].date(),
            "open": Decimal(str(row["Open"])),
            "high": Decimal(str(row["High"])),
            "low": Decimal(str(row["Low"])),
            "close": Decimal(str(row["Close"])),
            "volume": Decimal(str(row["Volume"])),
        }

        validate_market_record(record)
        records.append(record)

    return records


def validate_market_record(record: dict[str, Any]) -> None:
    open_price = record["open"]
    high_price = record["high"]
    low_price = record["low"]
    close_price = record["close"]
    volume = record["volume"]

    if (
        open_price < 0
        or high_price < 0
        or low_price < 0
        or close_price < 0
    ):
        raise ValueError("Price values cannot be negative")

    if volume < 0:
        raise ValueError("Volume cannot be negative")

    if high_price < max(open_price, close_price, low_price):
        raise ValueError("High price is inconsistent")

    if low_price > min(open_price, close_price, high_price):
        raise ValueError("Low price is inconsistent")


def get_latest_price(
    db: Session,
    asset_id: UUID,
) -> MarketPrice | None:
    return db.scalar(
        select(MarketPrice)
        .where(
            MarketPrice.asset_id == asset_id
        )
        .order_by(
            MarketPrice.price_date.desc()
        )
        .limit(1)
    )


def ingest_historical_data(
    asset_id: UUID,
    start_date: date,
    end_date: date,
    db: Session,
) -> int:
    asset = db.scalar(
        select(Asset).where(Asset.id == asset_id)
    )

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    records = fetch_historical_data(
        symbol=asset.symbol,
        start_date=start_date,
        end_date=end_date,
    )

    if not records:
        return 0

    values = [
        {
            "asset_id": asset.id,
            "price_date": record["date"],
            "open": record["open"],
            "high": record["high"],
            "low": record["low"],
            "close": record["close"],
            "volume": record["volume"],
        }
        for record in records
    ]

    statement = insert(MarketPrice).values(values)

    statement = statement.on_conflict_do_update(
        constraint="uq_market_price_asset_date",
        set_={
            "open": statement.excluded.open,
            "high": statement.excluded.high,
            "low": statement.excluded.low,
            "close": statement.excluded.close,
            "volume": statement.excluded.volume,
        },
    )

    db.execute(statement)
    db.commit()

    return len(records)


def get_historical_prices(
    asset_id: UUID,
    start_date: date | None,
    end_date: date | None,
    db: Session,
) -> list[MarketPrice]:
    cache_key = (
        f"argus:market_prices:"
        f"{asset_id}:"
        f"{start_date}:"
        f"{end_date}"
    )

    cached = redis_client.get(cache_key)

    if cached:
        cached_data = json.loads(cached)

        return [
            MarketPrice(
                asset_id=item["asset_id"],
                price_date=date.fromisoformat(item["price_date"]),
                open=Decimal(item["open"]),
                high=Decimal(item["high"]),
                low=Decimal(item["low"]),
                close=Decimal(item["close"]),
                volume=Decimal(item["volume"]),
            )
            for item in cached_data
        ]

    query = (
        select(MarketPrice)
        .where(MarketPrice.asset_id == asset_id)
    )

    if start_date is not None:
        query = query.where(
            MarketPrice.price_date >= start_date
        )

    if end_date is not None:
        query = query.where(
            MarketPrice.price_date <= end_date
        )

    query = query.order_by(MarketPrice.price_date)

    prices = list(db.scalars(query).all())

    cache_data = [
        {
            "asset_id": str(price.asset_id),
            "price_date": price.price_date.isoformat(),
            "open": str(price.open),
            "high": str(price.high),
            "low": str(price.low),
            "close": str(price.close),
            "volume": str(price.volume),
        }
        for price in prices
    ]

    redis_client.set(
        cache_key,
        json.dumps(cache_data),
        ex=500,
    )

    return prices


def fetch_company_info(symbol: str) -> dict[str, Any] | None:
    ticker = yf.Ticker(symbol)

    info = ticker.get_info()

    if not info:
        return

    return info
