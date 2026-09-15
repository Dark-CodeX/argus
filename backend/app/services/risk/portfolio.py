import pandas as pd


def calculate_portfolio_return(
    returns: pd.DataFrame,
    weights: pd.Series,
) -> pd.Series:
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

    return returns.mul(weights, axis=1).sum(axis=1)