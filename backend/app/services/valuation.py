from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.holding import Holding
from app.models.market_prices import MarketPrice
from app.models.portfolio import Portfolio
from app.models.user import User
from app.schemas.valuation import (
    HoldingValuation,
    PortfolioValuation,
)
from app.models.transaction import Transaction, TransactionType


def calculate_portfolio_valuation(
    portfolio_id: UUID,
    current_user: User,
    db: Session,
) -> PortfolioValuation:
    portfolio = db.scalar(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
        )
    )

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    holdings = db.scalars(
        select(Holding)
        .options(selectinload(Holding.asset))
        .where(Holding.portfolio_id == portfolio.id)
    ).all()

    total_cost_basis = Decimal("0")
    total_market_value = Decimal("0")
    valuation_items: list[HoldingValuation] = []

    realized_pnl = db.scalar(
        select(
            func.coalesce(
                func.sum(Transaction.realized_pnl),
                0,
            )
        )
        .where(
            Transaction.portfolio_id == portfolio.id,
            Transaction.transaction_type == TransactionType.SELL,
        )
    )

    realized_pnl = Decimal(str(realized_pnl))

    for holding in holdings:
        latest_price = db.scalar(
            select(MarketPrice)
            .where(
                MarketPrice.asset_id == holding.asset_id
            )
            .order_by(
                MarketPrice.price_date.desc()
            )
            .limit(1)
        )

        if not latest_price:
            continue

        cost_basis = (
            holding.quantity
            * holding.average_cost
        )

        market_value = (
            holding.quantity
            * latest_price.close
        )

        unrealized_pnl = (
            market_value - cost_basis
        )

        total_cost_basis += cost_basis
        total_market_value += market_value

        valuation_items.append(
            HoldingValuation(
                holding_id=holding.id,
                asset_id=holding.asset_id,
                symbol=holding.asset.symbol,
                quantity=holding.quantity,
                average_cost=holding.average_cost,
                current_price=latest_price.close,
                cost_basis=cost_basis,
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
            )
        )

    return PortfolioValuation(
        portfolio_id=portfolio.id,
        portfolio_name=portfolio.name,
        total_cost_basis=total_cost_basis,
        total_market_value=total_market_value,
        total_realized_pnl=Decimal(realized_pnl),
        total_unrealized_pnl=(
            total_market_value - total_cost_basis
        ),
        total_pnl=(
            realized_pnl
            + (total_market_value - total_cost_basis)
        ),
        holdings=valuation_items,
    )
