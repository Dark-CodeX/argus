from decimal import Decimal

import pandas as pd


def calculate_simple_returns(
    prices: pd.Series,
) -> pd.Series:
    if prices.empty:
        return pd.Series(dtype=float)

    numeric_prices = prices.astype(float)

    returns = (
        numeric_prices
        .div(numeric_prices.shift(1))
        .sub(1.0)
    )

    return returns.dropna()