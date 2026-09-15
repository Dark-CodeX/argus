from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.holding import Holding
from app.models.portfolio import Portfolio
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.schemas.transaction import TransactionCreate


def create_transaction(
    portfolio_id: UUID,
    transaction_data: TransactionCreate,
    current_user: User,
    db: Session,
) -> Transaction:
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

    asset = db.scalar(
        select(Asset).where(
            Asset.id == transaction_data.asset_id
        )
    )

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    holding = db.scalar(
        select(Holding)
        .where(
            Holding.portfolio_id == portfolio_id,
            Holding.asset_id == transaction_data.asset_id,
        )
        .with_for_update()
    )

    realized_pnl = Decimal("0")

    if transaction_data.transaction_type == TransactionType.BUY:
        if holding:
            old_quantity = holding.quantity
            old_average_cost = holding.average_cost

            new_quantity = (
                old_quantity + transaction_data.quantity
            )

            old_total_cost = (
                old_quantity * old_average_cost
            )

            new_total_cost = (
                old_total_cost
                + (
                    transaction_data.quantity
                    * transaction_data.price
                )
                + transaction_data.fees
            )

            new_average_cost = (
                new_total_cost / new_quantity
            )

            holding.quantity = new_quantity
            holding.average_cost = new_average_cost

        else:
            holding = Holding(
                portfolio_id=portfolio_id,
                asset_id=transaction_data.asset_id,
                quantity=transaction_data.quantity,
                average_cost=(
                    transaction_data.price
                    + (
                        transaction_data.fees
                        / transaction_data.quantity
                    )
                ),
            )

            db.add(holding)

    elif transaction_data.transaction_type == TransactionType.SELL:
        if not holding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot sell an asset that is not held",
            )

        if transaction_data.quantity > holding.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient quantity to sell",
            )

        realized_pnl = (
            transaction_data.quantity
            * (
                transaction_data.price
                - holding.average_cost
            )
            - transaction_data.fees
        )

        holding.quantity -= transaction_data.quantity

        if holding.quantity == Decimal("0"):
            db.delete(holding)

    transaction = Transaction(
        portfolio_id=portfolio_id,
        asset_id=transaction_data.asset_id,
        transaction_type=transaction_data.transaction_type,
        quantity=transaction_data.quantity,
        price=transaction_data.price,
        fees=transaction_data.fees,
        realized_pnl=realized_pnl,
        executed_at=transaction_data.executed_at,
    )

    db.add(transaction)

    db.commit()
    db.refresh(transaction)

    return transaction
