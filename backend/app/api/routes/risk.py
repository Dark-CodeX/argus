from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.risk import RiskReportResponse
from app.services.risk_service import (
    get_portfolio_risk_report,
)
from app.services.risk.exceptions import (
    InsufficientDataError,
    InvalidRiskInputError,
    UndefinedMetricError,
    PortfolioRiskDataError,
)


router = APIRouter(
    prefix="/portfolios",
    tags=["Risk"],
)


@router.get(
    "/{portfolio_id}/risk",
    response_model=RiskReportResponse,
)
def get_portfolio_risk(
    portfolio_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_portfolio_risk_report(
            portfolio_id=portfolio_id,
            current_user=current_user,
            db=db,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InsufficientDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    except InvalidRiskInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    except UndefinedMetricError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except PortfolioRiskDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
