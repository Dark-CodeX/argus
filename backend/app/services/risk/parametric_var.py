import math

import pandas as pd
from scipy.stats import norm
from app.services.risk.exceptions import (
    InsufficientDataError,
    InvalidRiskInputError,
    UndefinedMetricError,
)


def calculate_parametric_var(
    returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
    if returns.empty:
        raise InsufficientDataError(
            "Historical returns are required to calculate Parametric VaR"
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

    mean_return = returns.mean()
    volatility = returns.std(ddof=1)

    if volatility <= 0:
        raise UndefinedMetricError(
            "Parametric VaR is undefined when volatility is zero"
        )

    tail_probability = 1.0 - confidence_level

    z_score = norm.ppf(tail_probability)

    return float(
        mean_return + z_score * volatility
    )


def calculate_parametric_var_amount(
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

    var_return = calculate_parametric_var(
        returns,
        confidence_level,
    )

    return float(
        -var_return * portfolio_value
    )
