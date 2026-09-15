import pandas as pd


def validate_market_values(
    market_values: pd.Series,
) -> pd.Series:
    if market_values.empty:
        raise ValueError("Market values are empty")

    if market_values.isnull().any():
        raise ValueError("Market values contain missing values")

    market_values = market_values.astype(float)

    if (market_values < 0).any():
        raise ValueError("Market values cannot be negative")

    if market_values.sum() <= 0:
        raise ValueError("Total market value must be greater than zero")

    return market_values


def calculate_portfolio_weights(
    market_values: pd.Series,
) -> pd.Series:
    market_values = validate_market_values(market_values)

    total_market_value = market_values.sum()

    return market_values / total_market_value