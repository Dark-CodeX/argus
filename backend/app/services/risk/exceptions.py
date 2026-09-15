class RiskCalculationError(Exception):
    """Base exception for risk-engine calculation errors."""


class InsufficientDataError(RiskCalculationError):
    """Raised when there is not enough data for a calculation."""


class UndefinedMetricError(RiskCalculationError):
    """Raised when a metric is mathematically undefined."""


class InvalidRiskInputError(RiskCalculationError):
    """Raised when risk calculation inputs are invalid."""

class PortfolioRiskDataError(RiskCalculationError):
    """Raised when required portfolio risk data is unavailable."""