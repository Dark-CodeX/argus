import math

import pandas as pd


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
) -> float:
    if returns.empty:
        raise ValueError("Returns are empty")

    if not math.isfinite(risk_free_rate):
        raise ValueError("Risk-free rate must be finite")

    returns = returns.astype(float)

    mean_return = returns.mean()
    volatility = returns.std(ddof=1)

    if volatility <= 0:
        raise ValueError(
            "Sharpe ratio cannot be calculated when volatility is zero"
        )

    return float(
        (mean_return - risk_free_rate) / volatility
    )