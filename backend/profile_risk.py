import time

import numpy as np
import pandas as pd

from app.services.risk.covariance import (
    calculate_covariance_matrix,
    calculate_correlation_matrix,
)

from app.services.risk.monte_carlo import (
    simulate_portfolio_values,
)

from app.services.risk.optimization import (
    optimize_minimum_variance,
)

from app.services.risk.portfolio import (
    calculate_portfolio_return,
)

from app.services.risk.portfolio_volatility import (
    calculate_portfolio_volatility,
)

from app.services.risk.risk_contribution import (
    calculate_risk_contribution,
)


def time_function(
    name: str,
    function,
    *args,
    **kwargs,
):
    start = time.perf_counter()

    result = function(
        *args,
        **kwargs,
    )

    elapsed = time.perf_counter() - start

    print(
        f"{name:35s}: "
        f"{elapsed * 1000:.3f} ms"
    )

    return result


def main():
    print("\n" + "=" * 70)
    print("ARGUS RISK ENGINE PERFORMANCE PROFILE")
    print("=" * 70)

    # ------------------------------------------------------------
    # Generate synthetic multi-asset returns
    # ------------------------------------------------------------

    rng = np.random.default_rng(42)

    number_of_observations = 252
    number_of_assets = 100

    asset_names = [
        f"ASSET_{i + 1}"
        for i in range(number_of_assets)
    ]

    returns = pd.DataFrame(
        rng.normal(
            loc=0.0005,
            scale=0.02,
            size=(
                number_of_observations,
                number_of_assets,
            ),
        ),
        columns=asset_names,
    )

    weights = pd.Series(
        np.full(
            number_of_assets,
            1.0 / number_of_assets,
        ),
        index=asset_names,
    )

    print("\nInput:")
    print(
        f"Observations: {number_of_observations}"
    )
    print(
        f"Assets:       {number_of_assets}"
    )

    # ------------------------------------------------------------
    # Covariance
    # ------------------------------------------------------------

    print("\nRisk calculations:\n")

    covariance = time_function(
        "Covariance matrix",
        calculate_covariance_matrix,
        returns,
    )

    # ------------------------------------------------------------
    # Correlation
    # ------------------------------------------------------------

    correlation = time_function(
        "Correlation matrix",
        calculate_correlation_matrix,
        returns,
    )

    # ------------------------------------------------------------
    # Portfolio return
    # ------------------------------------------------------------

    portfolio_returns = time_function(
        "Portfolio return",
        calculate_portfolio_return,
        returns,
        weights,
    )

    # ------------------------------------------------------------
    # Portfolio volatility
    # ------------------------------------------------------------

    portfolio_volatility = time_function(
        "Portfolio volatility",
        calculate_portfolio_volatility,
        returns,
        weights,
    )

    # ------------------------------------------------------------
    # Risk contribution
    # ------------------------------------------------------------

    risk_contribution = time_function(
        "Risk contribution",
        calculate_risk_contribution,
        returns,
        weights,
    )

    # ------------------------------------------------------------
    # Monte Carlo
    # ------------------------------------------------------------

    simulated_values = time_function(
        "Monte Carlo (10,000,000 simulations)",
        simulate_portfolio_values,
        1_000_000,
        portfolio_returns.mean(),
        portfolio_returns.std(ddof=1),
        10_000_000,
        42,
    )

    # ------------------------------------------------------------
    # Optimization
    # ------------------------------------------------------------

    optimized_weights = time_function(
        "Minimum variance optimization",
        optimize_minimum_variance,
        returns,
    )

    # ------------------------------------------------------------
    # Results
    # ------------------------------------------------------------

    print("\n" + "-" * 70)
    print("RESULT SUMMARY")
    print("-" * 70)

    print(
        f"Portfolio volatility: "
        f"{portfolio_volatility:.6f}"
    )

    print(
        f"Monte Carlo outcomes: "
        f"{len(simulated_values)}"
    )

    print(
        f"Optimized weight sum: "
        f"{optimized_weights.sum():.6f}"
    )


if __name__ == "__main__":
    main()