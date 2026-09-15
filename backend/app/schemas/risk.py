from typing import Any

from pydantic import BaseModel, ConfigDict


class RiskReportResponse(BaseModel):
    portfolio: dict[str, Any]
    performance: dict[str, Any]
    volatility: dict[str, Any]
    drawdown: dict[str, Any]
    tail_risk: dict[str, Any]
    risk_contribution: dict[str, Any]
    stress_testing: dict[str, Any]
    portfolio_weights: dict[str, Any]
    monte_carlo: dict[str, Any]

    model_config = ConfigDict(
        from_attributes=True,
    )