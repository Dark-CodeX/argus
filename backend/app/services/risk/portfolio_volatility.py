import math

import pandas as pd


def calculate_portfolio_volatility(
    returns: pd.DataFrame,
    weights: pd.Series,
) -> float:
    if returns.empty:
        raise ValueError("Returns dataframe is empty")

    if weights.empty:
        raise ValueError("Weights are empty")

    returns = returns.astype(float)
    weights = weights.astype(float)

    if set(returns.columns) != set(weights.index):
        raise ValueError(
            "Returns columns and weight indices must contain the same assets"
        )

    weights = weights.reindex(returns.columns)

    covariance_matrix = returns.cov()

    weight_vector = weights.to_numpy()
    covariance_array = covariance_matrix.to_numpy()

    portfolio_variance = (
        weight_vector.T
        @ covariance_array
        @ weight_vector
    )

    if portfolio_variance < 0:
        raise ValueError(
            "Portfolio variance cannot be negative"
        )

    return math.sqrt(portfolio_variance)