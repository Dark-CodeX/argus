import math

import pandas as pd

from app.services.risk.exceptions import UndefinedMetricError
from app.services.risk.volatility import TRADING_DAYS_PER_YEAR


def calculate_downside_deviation(
    returns: pd.Series,
    target_return: float = 0.0,
) -> float:
    if returns.empty:
        raise ValueError("Returns are empty")

    if not math.isfinite(target_return):
        raise ValueError("Target return must be finite")

    returns = returns.astype(float)

    downside_returns = returns - target_return
    downside_returns = downside_returns.clip(upper=0)

    downside_deviation = math.sqrt(
        (downside_returns ** 2).mean()
    )

    return float(downside_deviation)


def calculate_sortino_ratio(
    returns: pd.Series,
    target_return: float = 0.0,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    if returns.empty:
        raise ValueError("Returns are empty")

    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be greater than zero")

    period_target_return = target_return / periods_per_year

    mean_return = returns.astype(float).mean()

    downside_deviation = calculate_downside_deviation(
        returns,
        period_target_return,
    )

    if downside_deviation <= 0:
        raise UndefinedMetricError(
            "Sortino ratio is undefined because "
            "downside deviation is zero"
        )

    daily_sortino = (mean_return - period_target_return) / downside_deviation

    return float(daily_sortino * math.sqrt(periods_per_year))