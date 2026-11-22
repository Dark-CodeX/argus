"""
Seed the NIFTY 50 universe into Argus and load its market data.

What it does
------------
1. Inserts NIFTY 50 stocks, the NIFTY 50 index and India VIX into `assets`
   (skips any symbol that already exists).
2. Downloads daily OHLCV from Yahoo Finance (via your existing
   `ingest_historical_data`) from 2013-01-01 to today into `market_prices`.

Run from the `backend/` folder (same place you run insertDataDB.py):

    python seed_nifty.py                  # assets + market data (incremental)
    python seed_nifty.py --assets-only    # only fill the assets table
    python seed_nifty.py --data-only      # only download market data
    python seed_nifty.py --full           # ignore existing data, re-download from start
    python seed_nifty.py --symbol INFY.NS # only one symbol
    python seed_nifty.py --start 2013-01-01

Safe to re-run: assets are inserted only if missing, and prices use an upsert.
"""

import argparse
import time
from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.asset import Asset
from app.models.market_prices import MarketPrice
from app.services.market_data import ingest_historical_data


DEFAULT_START_DATE = date(2013, 1, 1)
PAUSE_BETWEEN_SYMBOLS_SECONDS = 0.5
MAX_ATTEMPTS = 3


@dataclass(frozen=True)
class AssetSpec:
    symbol: str  # Yahoo Finance ticker, stored as-is in assets.symbol
    name: str
    asset_type: str  # "STOCK" or "INDEX"
    exchange: str = "NSE"


# ----------------------------------------------------------------------
# Universe
# NOTE: NIFTY 50 constituents change twice a year. Verify this list
# against NSE's official list and edit it when needed.
# ----------------------------------------------------------------------

INDICES = [
    AssetSpec("^NSEI", "NIFTY 50", "INDEX"),
    AssetSpec("^INDIAVIX", "India VIX", "INDEX"),
]

STOCKS = [
    AssetSpec("ADANIENT.NS", "Adani Enterprises", "STOCK"),
    AssetSpec("ADANIPORTS.NS", "Adani Ports and SEZ", "STOCK"),
    AssetSpec("APOLLOHOSP.NS", "Apollo Hospitals Enterprise", "STOCK"),
    AssetSpec("ASIANPAINT.NS", "Asian Paints", "STOCK"),
    AssetSpec("AXISBANK.NS", "Axis Bank", "STOCK"),
    AssetSpec("BAJAJ-AUTO.NS", "Bajaj Auto", "STOCK"),
    AssetSpec("BAJFINANCE.NS", "Bajaj Finance", "STOCK"),
    AssetSpec("BAJAJFINSV.NS", "Bajaj Finserv", "STOCK"),
    AssetSpec("BEL.NS", "Bharat Electronics", "STOCK"),
    AssetSpec("BHARTIARTL.NS", "Bharti Airtel", "STOCK"),
    AssetSpec("CIPLA.NS", "Cipla", "STOCK"),
    AssetSpec("COALINDIA.NS", "Coal India", "STOCK"),
    AssetSpec("DRREDDY.NS", "Dr. Reddy's Laboratories", "STOCK"),
    AssetSpec("EICHERMOT.NS", "Eicher Motors", "STOCK"),
    AssetSpec("ETERNAL.NS", "Eternal (Zomato)", "STOCK"),
    AssetSpec("GRASIM.NS", "Grasim Industries", "STOCK"),
    AssetSpec("HCLTECH.NS", "HCL Technologies", "STOCK"),
    AssetSpec("HDFCBANK.NS", "HDFC Bank", "STOCK"),
    AssetSpec("HDFCLIFE.NS", "HDFC Life Insurance", "STOCK"),
    AssetSpec("HINDALCO.NS", "Hindalco Industries", "STOCK"),
    AssetSpec("HINDUNILVR.NS", "Hindustan Unilever", "STOCK"),
    AssetSpec("ICICIBANK.NS", "ICICI Bank", "STOCK"),
    AssetSpec("INDIGO.NS", "InterGlobe Aviation (IndiGo)", "STOCK"),
    AssetSpec("INFY.NS", "Infosys", "STOCK"),
    AssetSpec("ITC.NS", "ITC", "STOCK"),
    AssetSpec("JIOFIN.NS", "Jio Financial Services", "STOCK"),
    AssetSpec("JSWSTEEL.NS", "JSW Steel", "STOCK"),
    AssetSpec("KOTAKBANK.NS", "Kotak Mahindra Bank", "STOCK"),
    AssetSpec("LT.NS", "Larsen & Toubro", "STOCK"),
    AssetSpec("M&M.NS", "Mahindra & Mahindra", "STOCK"),
    AssetSpec("MARUTI.NS", "Maruti Suzuki India", "STOCK"),
    AssetSpec("MAXHEALTH.NS", "Max Healthcare Institute", "STOCK"),
    AssetSpec("NESTLEIND.NS", "Nestle India", "STOCK"),
    AssetSpec("NTPC.NS", "NTPC", "STOCK"),
    AssetSpec("ONGC.NS", "Oil & Natural Gas Corporation", "STOCK"),
    AssetSpec("POWERGRID.NS", "Power Grid Corporation of India", "STOCK"),
    AssetSpec("RELIANCE.NS", "Reliance Industries", "STOCK"),
    AssetSpec("SBILIFE.NS", "SBI Life Insurance", "STOCK"),
    AssetSpec("SBIN.NS", "State Bank of India", "STOCK"),
    AssetSpec("SHRIRAMFIN.NS", "Shriram Finance", "STOCK"),
    AssetSpec("SUNPHARMA.NS", "Sun Pharmaceutical Industries", "STOCK"),
    AssetSpec("TCS.NS", "Tata Consultancy Services", "STOCK"),
    AssetSpec("TATACONSUM.NS", "Tata Consumer Products", "STOCK"),
    # Tata Motors demerged; the passenger-vehicle company trades as TMPV.
    # Check the ticker on Yahoo; if it has no data it is skipped and reported.
    AssetSpec("TMPV.NS", "Tata Motors Passenger Vehicles", "STOCK"),
    AssetSpec("TATASTEEL.NS", "Tata Steel", "STOCK"),
    AssetSpec("TECHM.NS", "Tech Mahindra", "STOCK"),
    AssetSpec("TITAN.NS", "Titan Company", "STOCK"),
    AssetSpec("TRENT.NS", "Trent", "STOCK"),
    AssetSpec("ULTRACEMCO.NS", "UltraTech Cement", "STOCK"),
    AssetSpec("WIPRO.NS", "Wipro", "STOCK"),
]

UNIVERSE = INDICES + STOCKS


# ----------------------------------------------------------------------
# Step A: assets
# ----------------------------------------------------------------------

def seed_assets(db: Session, specs: list[AssetSpec]) -> tuple[int, int]:
    """Insert missing assets. Returns (inserted, already_existing)."""
    existing_symbols = set(
        db.scalars(
            select(Asset.symbol).where(
                Asset.symbol.in_([s.symbol.upper() for s in specs])
            )
        ).all()
    )

    inserted = 0

    for spec in specs:
        symbol = spec.symbol.upper()

        if symbol in existing_symbols:
            continue

        db.add(
            Asset(
                symbol=symbol,
                name=spec.name,
                asset_type=spec.asset_type,
                exchange=spec.exchange,
            )
        )
        inserted += 1

    db.commit()

    return inserted, len(specs) - inserted


# ----------------------------------------------------------------------
# Step B: market data
# ----------------------------------------------------------------------

def resolve_start_date(
    db: Session,
    asset_id,
    default_start: date,
    full: bool,
) -> date:
    """Incremental: resume from the last stored date. Full: from default_start."""
    if full:
        return default_start

    last_date = db.scalar(
        select(func.max(MarketPrice.price_date)).where(
            MarketPrice.asset_id == asset_id
        )
    )

    return last_date or default_start


def load_market_data(
    db: Session,
    specs: list[AssetSpec],
    default_start: date,
    full: bool,
) -> tuple[dict[str, int], dict[str, str]]:
    """Download prices per symbol. One bad symbol never stops the rest."""
    # Yahoo's `end` is exclusive, so +1 day to include today's bar.
    end_date = date.today() + timedelta(days=1)

    loaded: dict[str, int] = {}
    failed: dict[str, str] = {}

    for index, spec in enumerate(specs, start=1):
        symbol = spec.symbol.upper()

        asset = db.scalar(select(Asset).where(Asset.symbol == symbol))

        if asset is None:
            failed[symbol] = "not in assets table (run without --data-only first)"
            print(f"[{index}/{len(specs)}] {symbol:15s} SKIPPED (no asset row)")
            continue

        start_date = resolve_start_date(db, asset.id, default_start, full)

        count = None
        last_error = ""

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                count = ingest_historical_data(
                    asset_id=asset.id,
                    start_date=start_date,
                    end_date=end_date,
                    db=db,
                )
                break
            except Exception as exc:  # noqa: BLE001 - report and continue
                db.rollback()
                last_error = f"{type(exc).__name__}: {exc}"

                if attempt < MAX_ATTEMPTS:
                    time.sleep(2 * attempt)

        if count is None:
            failed[symbol] = last_error
            print(f"[{index}/{len(specs)}] {symbol:15s} FAILED  ({last_error})")
        elif count == 0:
            failed[symbol] = "Yahoo returned no data (check the ticker)"
            print(f"[{index}/{len(specs)}] {symbol:15s} NO DATA")
        else:
            loaded[symbol] = count
            print(
                f"[{index}/{len(specs)}] {symbol:15s} "
                f"{count:5d} rows  (from {start_date})"
            )

        time.sleep(PAUSE_BETWEEN_SYMBOLS_SECONDS)

    return loaded, failed


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed NIFTY 50 + NIFTY index + India VIX and load market data."
    )
    parser.add_argument("--assets-only", action="store_true",
                        help="only insert assets, do not download prices")
    parser.add_argument("--data-only", action="store_true",
                        help="only download prices, do not insert assets")
    parser.add_argument("--full", action="store_true",
                        help="re-download from --start even if data already exists")
    parser.add_argument("--start", type=date.fromisoformat,
                        default=DEFAULT_START_DATE,
                        help="first date to download (YYYY-MM-DD), default 2013-01-01")
    parser.add_argument("--symbol", type=str, default=None,
                        help="process just one symbol, e.g. INFY.NS or ^NSEI")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.assets_only and args.data_only:
        raise SystemExit("Use either --assets-only or --data-only, not both.")

    specs = UNIVERSE

    if args.symbol:
        wanted = args.symbol.upper()
        specs = [s for s in UNIVERSE if s.symbol.upper() == wanted]

        if not specs:
            raise SystemExit(f"{wanted} is not in the universe list.")

    db = SessionLocal()

    try:
        if not args.data_only:
            inserted, existing = seed_assets(db, specs)
            print(f"Assets: {inserted} inserted, {existing} already existed.\n")

        if not args.assets_only:
            loaded, failed = load_market_data(
                db=db,
                specs=specs,
                default_start=args.start,
                full=args.full,
            )

            print("\n" + "=" * 60)
            print(f"Loaded: {len(loaded)} symbols, {sum(loaded.values())} rows")

            if failed:
                print(f"Problems: {len(failed)} symbols")
                for symbol, reason in failed.items():
                    print(f"  - {symbol}: {reason}")
    finally:
        db.close()


if __name__ == "__main__":
    main()