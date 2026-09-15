import pandas as pd


def calculate_drawdowns(
    portfolio_values: pd.Series,
) -> pd.Series:
    if portfolio_values.empty:
        raise ValueError("Portfolio values are empty")

    portfolio_values = portfolio_values.astype(float)

    if portfolio_values.isnull().any():
        raise ValueError(
            "Portfolio values contain missing values"
        )

    if (portfolio_values <= 0).any():
        raise ValueError(
            "Portfolio values must be greater than zero"
        )

    running_peak = portfolio_values.cummax()

    drawdowns = (
        portfolio_values - running_peak
    ) / running_peak

    return drawdowns


def calculate_maximum_drawdown(
    portfolio_values: pd.Series,
) -> float:
    drawdowns = calculate_drawdowns(
        portfolio_values
    )

    return float(drawdowns.min())