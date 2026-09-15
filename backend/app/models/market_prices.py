from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MarketPrice(Base):
    __tablename__ = "market_prices"

    __table_args__ = (
        UniqueConstraint(
            "asset_id",
            "price_date",
            name="uq_market_price_asset_date",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "assets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    price_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    open: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    high: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    low: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    close: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
    )

    volume: Mapped[Decimal] = mapped_column(
        Numeric(30, 8),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )