import math

import pandas as pd


def validate_stress_inputs(
    market_values: pd.Series,
    shocks: pd.Series,
) -> tuple[pd.Series, pd.Series]:
    if market_values.empty:
        raise ValueError("Market values are empty")

    if shocks.empty:
        raise ValueError("Stress shocks are empty")

    market_values = market_values.astype(float)
    shocks = shocks.astype(float)

    if market_values.isnull().any():
        raise ValueError(
            "Market values contain missing values"
        )

    if shocks.isnull().any():
        raise ValueError(
            "Stress shocks contain missing values"
        )

    if (market_values < 0).any():
        raise ValueError(
            "Market values cannot be negative"
        )

    if set(market_values.index) != set(shocks.index):
        raise ValueError(
            "Market values and stress shocks must contain "
            "the same assets"
        )

    shocks = shocks.reindex(market_values.index)

    if (shocks <= -1.0).any():
        raise ValueError(
            "Stress shock cannot be -100% or lower"
        )

    return market_values, shocks


def calculate_stress_test(
    market_values: pd.Series,
    shocks: pd.Series,
) -> pd.DataFrame:
    market_values, shocks = validate_stress_inputs(
        market_values,
        shocks,
    )

    stressed_values = (
        market_values * (1.0 + shocks)
    )

    pnl = stressed_values - market_values

    pnl_percentage = (
        pnl / market_values
    )

    return pd.DataFrame(
        {
            "market_value": market_values,
            "shock": shocks,
            "stressed_value": stressed_values,
            "pnl": pnl,
            "pnl_percentage": pnl_percentage,
        }
    )


def calculate_portfolio_stress(
    market_values: pd.Series,
    shocks: pd.Series,
) -> dict[str, float]:
    stress_results = calculate_stress_test(
        market_values,
        shocks,
    )

    original_value = float(
        market_values.astype(float).sum()
    )

    stressed_value = float(
        stress_results["stressed_value"].sum()
    )

    pnl = stressed_value - original_value

    if original_value <= 0:
        raise ValueError(
            "Original portfolio value must be greater than zero"
        )

    pnl_percentage = pnl / original_value

    return {
        "original_value": original_value,
        "stressed_value": stressed_value,
        "pnl": pnl,
        "pnl_percentage": pnl_percentage,
    }
