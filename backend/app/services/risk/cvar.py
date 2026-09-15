import math

import pandas as pd

from app.services.risk.var import calculate_historical_var
from app.services.risk.exceptions import (
    InsufficientDataError,
    InvalidRiskInputError,
)


def calculate_historical_cvar(
    returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
    if returns.empty:
        raise InsufficientDataError(
            "Historical returns are required to calculate CVaR"
        )

    if not 0 < confidence_level < 1:
        raise InvalidRiskInputError(
            "Confidence level must be between 0 and 1"
        )

    returns = returns.astype(float)

    if returns.isnull().any():
        raise InvalidRiskInputError(
            "Returns contain missing values"
        )

    var_return = calculate_historical_var(
        returns,
        confidence_level,
    )

    tail_returns = returns[
        returns <= var_return
    ]

    if tail_returns.empty:
        raise InsufficientDataError(
            "No observations are available in the VaR tail"
        )

    return float(tail_returns.mean())


def calculate_historical_cvar_amount(
    returns: pd.Series,
    portfolio_value: float,
    confidence_level: float = 0.95,
) -> float:
    if not math.isfinite(portfolio_value):
        raise ValueError(
            "Portfolio value must be finite"
        )

    if portfolio_value <= 0:
        raise ValueError(
            "Portfolio value must be greater than zero"
        )

    cvar_return = calculate_historical_cvar(
        returns,
        confidence_level,
    )

    return float(
        -cvar_return * portfolio_value
    )
