import math

import pandas as pd


TRADING_DAYS_PER_YEAR = 252


def calculate_daily_volatility(
    returns: pd.Series,
) -> float:
    if len(returns) < 2:
        raise ValueError(
            "At least two observations are required "
            "to calculate volatility"
        )

    return float(returns.std(ddof=1))


def annualize_volatility(
    volatility: float,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    if volatility < 0:
        raise ValueError("Volatility cannot be negative")

    if periods_per_year <= 0:
        raise ValueError(
            "periods_per_year must be greater than zero"
        )

    return volatility * math.sqrt(periods_per_year)


def calculate_annualized_volatility(
    returns: pd.Series,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    daily_volatility = calculate_daily_volatility(returns)

    return annualize_volatility(
        daily_volatility,
        periods_per_year,
    )