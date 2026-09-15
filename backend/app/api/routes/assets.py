from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.asset import Asset
from app.schemas.asset import AssetResponse


router = APIRouter(
    prefix="/assets",
    tags=["Assets"],
)


@router.get(
    "",
    response_model=list[AssetResponse],
)
def get_assets(
    db: Session = Depends(get_db),
):
    assets = db.scalars(
        select(Asset).order_by(Asset.symbol)
    ).all()

    return assets


@router.get(
    "/{symbol}",
    response_model=AssetResponse,
)
def get_asset(
    symbol: str,
    db: Session = Depends(get_db),
):
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

    return asset