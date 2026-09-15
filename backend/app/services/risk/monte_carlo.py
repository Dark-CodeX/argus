import math

import numpy as np

def validate_monte_carlo_inputs(
    initial_value: float,
    expected_return: float,
    volatility: float,
    simulations: int,
) -> None:
    if not math.isfinite(initial_value):
        raise ValueError(
            "Initial portfolio value must be finite"
        )

    if initial_value <= 0:
        raise ValueError(
            "Initial portfolio value must be greater than zero"
        )

    if not math.isfinite(expected_return):
        raise ValueError(
            "Expected return must be finite"
        )

    if not math.isfinite(volatility):
        raise ValueError(
            "Volatility must be finite"
        )

    if volatility < 0:
        raise ValueError(
            "Volatility cannot be negative"
        )

    if simulations <= 0:
        raise ValueError(
            "Number of simulations must be greater than zero"
        )


def simulate_portfolio_values(
    initial_value: float,
    expected_return: float,
    volatility: float,
    simulations: int = 10_000,
    random_seed: int | None = None,
) -> np.ndarray:
    validate_monte_carlo_inputs(
        initial_value,
        expected_return,
        volatility,
        simulations,
    )

    rng = np.random.default_rng(random_seed)

    simulated_returns = rng.normal(
        loc=expected_return,
        scale=volatility,
        size=simulations,
    )

    simulated_values = (
        initial_value
        * (1.0 + simulated_returns)
    )

    return simulated_values

def summarize_simulated_values(
    simulated_values: np.ndarray,
) -> dict[str, float]:
    if simulated_values.size == 0:
        raise ValueError(
            "Simulated values are empty"
        )

    return {
        "mean_value": float(
            simulated_values.mean()
        ),
        "median_value": float(
            np.median(simulated_values)
        ),
        "minimum_value": float(
            simulated_values.min()
        ),
        "maximum_value": float(
            simulated_values.max()
        ),
        "percentile_5": float(
            np.percentile(
                simulated_values,
                5,
            )
        ),
        "percentile_95": float(
            np.percentile(
                simulated_values,
                95,
            )
        ),
    }