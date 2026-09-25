import math

import pandas as pd

from app.services.risk.volatility import TRADING_DAYS_PER_YEAR


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    if returns.empty:
        raise ValueError("Returns are empty")

    if not math.isfinite(risk_free_rate):
        raise ValueError("Risk-free rate must be finite")

    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be greater than zero")

    returns = returns.astype(float)

    mean_return = returns.mean()
    volatility = returns.std(ddof=1)

    if volatility <= 0:
        raise ValueError(
            "Sharpe ratio cannot be calculated when volatility is zero"
        )

    period_risk_free_rate = risk_free_rate / periods_per_year

    daily_sharpe = (mean_return - period_risk_free_rate) / volatility

    return float(daily_sharpe * math.sqrt(periods_per_year))