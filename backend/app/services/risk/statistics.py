import pandas as pd


def calculate_mean_return(
    returns: pd.Series,
) -> float:
    if returns.empty:
        raise ValueError("Returns series is empty")

    return float(returns.mean())


def calculate_variance(
    returns: pd.Series,
) -> float:
    if len(returns) < 2:
        raise ValueError(
            "At least two observations are required "
            "to calculate sample variance"
        )

    return float(returns.var(ddof=1))


def calculate_standard_deviation(
    returns: pd.Series,
) -> float:
    if len(returns) < 2:
        raise ValueError(
            "At least two observations are required "
            "to calculate sample standard deviation"
        )

    return float(returns.std(ddof=1))


def calculate_summary_statistics(
    returns: pd.Series,
) -> dict[str, float]:
    if returns.empty:
        raise ValueError("Returns series is empty")

    if len(returns) < 2:
        raise ValueError(
            "At least two observations are required "
            "for variance-based statistics"
        )

    return {
        "mean": float(returns.mean()),
        "variance": float(returns.var(ddof=1)),
        "standard_deviation": float(returns.std(ddof=1)),
        "minimum": float(returns.min()),
        "maximum": float(returns.max()),
        "median": float(returns.median()),
        "percentile_5": float(returns.quantile(0.05)),
        "percentile_25": float(returns.quantile(0.25)),
        "percentile_75": float(returns.quantile(0.75)),
        "percentile_95": float(returns.quantile(0.95)),
    }