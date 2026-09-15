import math

import pandas as pd
from app.services.risk.exceptions import (
    InsufficientDataError,
    InvalidRiskInputError,
)


def calculate_historical_var(
    returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
    if returns.empty:
        raise ValueError("Returns are empty")

    if not 0 < confidence_level < 1:
        raise InvalidRiskInputError(
            "Confidence level must be between 0 and 1"
        )

    returns = returns.astype(float)

    if returns.empty:
        raise InsufficientDataError(
            "Historical returns are required to calculate VaR"
        )

    percentile = 1.0 - confidence_level

    return float(
        returns.quantile(percentile)
    )


def calculate_historical_var_amount(
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

    var_return = calculate_historical_var(
        returns,
        confidence_level,
    )

    return float(
        -var_return * portfolio_value
    )
