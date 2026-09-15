import pandas as pd


def validate_returns_dataframe(
    returns: pd.DataFrame,
) -> pd.DataFrame:
    if returns.empty:
        raise ValueError("Returns dataframe is empty")

    if returns.shape[1] < 2:
        raise ValueError(
            "At least two assets are required"
        )

    if returns.isnull().values.any():
        raise ValueError(
            "Returns dataframe contains missing values"
        )

    return returns.astype(float)


def calculate_covariance_matrix(
    returns: pd.DataFrame,
) -> pd.DataFrame:
    returns = validate_returns_dataframe(returns)

    return returns.cov()


def calculate_correlation_matrix(
    returns: pd.DataFrame,
) -> pd.DataFrame:
    returns = validate_returns_dataframe(returns)

    return returns.corr()