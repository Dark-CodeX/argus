from app.services.market_data import ingest_historical_data
from app.db.session import get_db
import datetime
from datetime import date
from sqlalchemy import select, func
from app.models.asset import Asset
from app.models.market_prices import MarketPrice

if __name__ == "__main__":
    db = next(get_db())
    A = db.scalars(select(Asset.symbol)).all()
    for a in A:
        asset = db.scalar(select(Asset).where(Asset.symbol == a))
        if not asset:
            raise ValueError(f"{a} is not available in asset table")
        start_date = db.scalar(select(func.max(MarketPrice.price_date)).where(
            MarketPrice.asset_id == asset.id))
        if not start_date:
            start_date = date(2014, 1, 1)
        if start_date >= date.today() - datetime.timedelta(days=1):
            print(f"Skipping {a} as data is already up to date")
            continue
        count = ingest_historical_data(asset.id, start_date, date.today(), db)
        print(f"Inserted {count} rows for {a}")