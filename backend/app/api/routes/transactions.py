from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.models.portfolio import Portfolio
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
)
from app.services.transactions import create_transaction


router = APIRouter(
    prefix="/portfolios/{portfolio_id}/transactions",
    tags=["Transactions"],
)


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_portfolio_transaction(
    portfolio_id: UUID,
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_transaction(
        portfolio_id=portfolio_id,
        transaction_data=transaction_data,
        current_user=current_user,
        db=db,
    )


@router.get(
    "",
    response_model=list[TransactionResponse],
)
def get_portfolio_transactions(
    portfolio_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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

    transactions = db.scalars(
        select(Transaction)
        .where(Transaction.portfolio_id == portfolio.id)
        .order_by(Transaction.executed_at.desc())
    ).all()

    return transactions
