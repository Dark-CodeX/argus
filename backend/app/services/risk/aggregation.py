from dataclasses import dataclass

import pandas as pd


@dataclass
class RiskReport:
    portfolio_value: float

    mean_return: float

    daily_volatility: float
    annualized_volatility: float

    sharpe_ratio: float
    sortino_ratio: float

    maximum_drawdown: float

    historical_var: float
    historical_var_amount: float

    parametric_var: float
    parametric_var_amount: float

    historical_cvar: float
    historical_cvar_amount: float

    portfolio_volatility: float

    risk_contribution: pd.DataFrame

    stress_result: dict[str, float]


def build_risk_report(
    portfolio_value: float,
    returns: pd.Series,
    daily_volatility: float,
    annualized_volatility: float,
    sharpe_ratio: float,
    sortino_ratio: float,
    maximum_drawdown: float,
    historical_var: float,
    historical_var_amount: float,
    parametric_var: float,
    parametric_var_amount: float,
    historical_cvar: float,
    historical_cvar_amount: float,
    portfolio_volatility: float,
    risk_contribution: pd.DataFrame,
    stress_result: dict[str, float],
) -> RiskReport:
    if portfolio_value <= 0:
        raise ValueError(
            "Portfolio value must be greater than zero"
        )

    if returns.empty:
        raise ValueError(
            "Returns are empty"
        )

    return RiskReport(
        portfolio_value=portfolio_value,
        mean_return=float(returns.mean()),
        daily_volatility=float(daily_volatility),
        annualized_volatility=float(
            annualized_volatility
        ),
        sharpe_ratio=float(sharpe_ratio),
        sortino_ratio=float(sortino_ratio),
        maximum_drawdown=float(maximum_drawdown),
        historical_var=float(historical_var),
        historical_var_amount=float(
            historical_var_amount
        ),
        parametric_var=float(parametric_var),
        parametric_var_amount=float(
            parametric_var_amount
        ),
        historical_cvar=float(
            historical_cvar
        ),
        historical_cvar_amount=float(
            historical_cvar_amount
        ),
        portfolio_volatility=float(
            portfolio_volatility
        ),
        risk_contribution=risk_contribution,
        stress_result=stress_result,
    )
