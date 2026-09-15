import math

import numpy as np
import pandas as pd
from scipy.optimize import minimize


def optimize_minimum_variance(
    returns: pd.DataFrame,
) -> pd.Series:
    if returns.empty:
        raise ValueError("Returns dataframe is empty")

    if returns.shape[1] < 2:
        raise ValueError(
            "At least two assets are required"
        )

    returns = returns.astype(float)

    if returns.isnull().values.any():
        raise ValueError(
            "Returns dataframe contains missing values"
        )

    covariance_matrix = returns.cov().to_numpy()
    assets = list(returns.columns)
    number_of_assets = len(assets)

    def portfolio_variance(
        weights: np.ndarray,
    ) -> float:
        return float(
            weights.T
            @ covariance_matrix
            @ weights
        )

    initial_weights = np.full(
        number_of_assets,
        1.0 / number_of_assets,
    )

    constraints = {
        "type": "eq",
        "fun": lambda weights: np.sum(weights) - 1.0,
    }

    bounds = [
        (0.0, 1.0)
        for _ in range(number_of_assets)
    ]

    result = minimize(
        portfolio_variance,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )

    if not result.success:
        raise ValueError(
            f"Portfolio optimization failed: {result.message}"
        )

    optimized_weights = pd.Series(
        result.x,
        index=assets,
    )

    if not math.isclose(
        optimized_weights.sum(),
        1.0,
        rel_tol=1e-7,
        abs_tol=1e-7,
    ):
        raise ValueError(
            "Optimized weights do not sum to 1"
        )

    return optimized_weights