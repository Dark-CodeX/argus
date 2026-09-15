import math

import pandas as pd


def calculate_risk_contribution(
    returns: pd.DataFrame,
    weights: pd.Series,
) -> pd.DataFrame:
    if returns.empty:
        raise ValueError("Returns dataframe is empty")

    if weights.empty:
        raise ValueError("Weights are empty")

    returns = returns.astype(float)
    weights = weights.astype(float)

    if set(returns.columns) != set(weights.index):
        raise ValueError(
            "Returns columns and weight indices must contain "
            "the same assets"
        )

    weights = weights.reindex(returns.columns)

    if weights.isnull().any():
        raise ValueError("Weights contain missing values")

    if not math.isclose(
        weights.sum(),
        1.0,
        rel_tol=1e-9,
        abs_tol=1e-9,
    ):
        raise ValueError(
            "Portfolio weights must sum to 1"
        )

    covariance_matrix = returns.cov()

    weight_vector = weights.to_numpy()
    covariance_array = covariance_matrix.to_numpy()

    portfolio_variance = (
        weight_vector.T
        @ covariance_array
        @ weight_vector
    )

    if portfolio_variance <= 0:
        raise ValueError(
            "Portfolio variance must be greater than zero"
        )

    portfolio_volatility = math.sqrt(
        portfolio_variance
    )

    covariance_times_weights = (
        covariance_array @ weight_vector
    )

    marginal_contribution = (
        covariance_times_weights
        / portfolio_volatility
    )

    component_contribution = (
        weight_vector
        * marginal_contribution
    )

    contribution_percentage = (
        component_contribution
        / portfolio_volatility
    )

    return pd.DataFrame(
        {
            "weight": weight_vector,
            "marginal_contribution": marginal_contribution,
            "risk_contribution": component_contribution,
            "risk_contribution_pct": contribution_percentage,
        },
        index=returns.columns,
    )