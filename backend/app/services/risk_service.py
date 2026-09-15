from datetime import date, timedelta
from uuid import UUID

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.services.market_data import get_latest_price, get_historical_prices
from app.models.portfolio import Portfolio
from app.models.user import User
from app.services.risk.drawdown import (
    calculate_maximum_drawdown,
)
from app.services.risk.portfolio import (
    calculate_portfolio_return,
)
from app.services.risk.portfolio_volatility import (
    calculate_portfolio_volatility,
)
from app.services.risk.sharpe import (
    calculate_sharpe_ratio,
)
from app.services.risk.sortino import (
    calculate_sortino_ratio,
)
from app.services.risk.statistics import (
    calculate_mean_return,
)
from app.services.risk.volatility import (
    calculate_annualized_volatility,
    calculate_daily_volatility,
)
from app.services.risk.weights import (
    calculate_portfolio_weights,
)
from app.services.risk.cvar import (
    calculate_historical_cvar,
    calculate_historical_cvar_amount,
)

from app.services.risk.parametric_var import (
    calculate_parametric_var,
    calculate_parametric_var_amount,
)

from app.services.risk.risk_contribution import (
    calculate_risk_contribution,
)

from app.services.risk.stress import (
    calculate_portfolio_stress,
)

from app.services.risk.var import (
    calculate_historical_var,
    calculate_historical_var_amount,
)
from app.services.risk.monte_carlo import (
    simulate_portfolio_values,
    summarize_simulated_values,
)
from app.services.risk.exceptions import (
    PortfolioRiskDataError,
    InsufficientDataError,
)
from app.models.holding import Holding


def get_portfolio_risk_report(
    portfolio_id: UUID,
    current_user: User,
    db: Session,
) -> dict:
    # ------------------------------------------------------------
    # 1. Load portfolio and verify ownership
    # ------------------------------------------------------------

    portfolio = db.scalar(
        select(Portfolio)
        .where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
        )
        .options(
            selectinload(Portfolio.holdings)
            .selectinload(Holding.asset)
        )
    )

    if not portfolio:
        raise ValueError("Portfolio not found")

    if not portfolio.holdings:
        raise PortfolioRiskDataError(
            "Portfolio does not contain any holdings"
        )

    # ------------------------------------------------------------
    # 2. Determine historical date range
    # ------------------------------------------------------------

    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    # ------------------------------------------------------------
    # 3. Load latest prices and historical prices
    # ------------------------------------------------------------

    market_values: dict[str, float] = {}
    price_data: dict[str, pd.Series] = {}

    for holding in portfolio.holdings:

        asset = holding.asset

        latest_price = get_latest_price(
            db=db,
            asset_id=asset.id,
        )

        if not latest_price:
            continue

        market_value = (
            float(holding.quantity)
            * float(latest_price.close)
        )

        market_values[asset.symbol] = market_value

        historical_prices = get_historical_prices(
            db=db,
            asset_id=asset.id,
            start_date=start_date,
            end_date=end_date,
        )

        if historical_prices:
            price_data[asset.symbol] = pd.Series(
                {
                    price.price_date: float(price.close)
                    for price in historical_prices
                }
            )

    if not market_values:
        raise PortfolioRiskDataError(
            "No current market prices are available "
            "for this portfolio"
        )

    if len(price_data) < 2:
        raise InsufficientDataError(
            "At least two assets with historical prices "
            "are required for portfolio risk analysis"
        )

    # ------------------------------------------------------------
    # 4. Build aligned price dataframe
    # ------------------------------------------------------------

    prices = pd.DataFrame(price_data).dropna()

    if len(prices) < 2:
        raise ValueError(
            "Not enough aligned historical price data"
        )

    # ------------------------------------------------------------
    # 5. Calculate historical returns
    # ------------------------------------------------------------

    returns = prices.pct_change().dropna()

    if returns.empty:
        raise ValueError(
            "Unable to calculate portfolio returns"
        )

    # ------------------------------------------------------------
    # 6. Scope market value to the assets actually being analyzed
    # ------------------------------------------------------------

    analyzed_assets = list(returns.columns)
    excluded_assets = sorted(set(market_values) - set(analyzed_assets))

    total_value = float(sum(market_values.values()))

    analyzed_market_values = pd.Series(
        {
            asset: market_values[asset]
            for asset in analyzed_assets
        }
    )
    analyzed_value = float(analyzed_market_values.sum())
    if analyzed_value <= 0:
        raise PortfolioRiskDataError(
            "Assets with historical price data have no positive market value"
        )
    # ------------------------------------------------------------
    # 7. Portfolio weights, over analyzed assets only (sums to 1)
    # ------------------------------------------------------------

    weights = calculate_portfolio_weights(analyzed_market_values)
    weights = weights.reindex(analyzed_assets)

    # ------------------------------------------------------------
    # 8. Portfolio return series
    # ------------------------------------------------------------

    portfolio_returns = calculate_portfolio_return(returns, weights)

    # ------------------------------------------------------------
    # 9. Basic statistics
    # ------------------------------------------------------------

    mean_return = calculate_mean_return(portfolio_returns)
    daily_volatility = calculate_daily_volatility(portfolio_returns)
    annualized_volatility = calculate_annualized_volatility(portfolio_returns)

    # ------------------------------------------------------------
    # 10. Risk-adjusted metrics
    # ------------------------------------------------------------

    sharpe_ratio = calculate_sharpe_ratio(
        portfolio_returns, risk_free_rate=0.0)
    sortino_ratio = calculate_sortino_ratio(
        portfolio_returns, target_return=0.0)

    # ------------------------------------------------------------
    # 11. Portfolio value series & max drawdown
    # ------------------------------------------------------------

    portfolio_value_series = analyzed_value * \
        (1.0 + portfolio_returns).cumprod()
    maximum_drawdown = calculate_maximum_drawdown(portfolio_value_series)

    # ------------------------------------------------------------
    # 12. Portfolio volatility
    # ------------------------------------------------------------

    portfolio_volatility = calculate_portfolio_volatility(returns, weights)

    # ------------------------------------------------------------
    # 13. Historical VaR
    # ------------------------------------------------------------
    confidence_level = 0.95

    historical_var = calculate_historical_var(
        portfolio_returns, confidence_level=confidence_level)
    historical_var_amount = calculate_historical_var_amount(
        portfolio_returns, analyzed_value, confidence_level=confidence_level
    )

    # ------------------------------------------------------------
    # 14. Parametric VaR
    # ------------------------------------------------------------
    parametric_var = calculate_parametric_var(
        portfolio_returns, confidence_level=confidence_level)
    parametric_var_amount = calculate_parametric_var_amount(
        portfolio_returns, analyzed_value, confidence_level=confidence_level
    )

    # ------------------------------------------------------------
    # 15. Historical CVaR
    # ------------------------------------------------------------
    historical_cvar = calculate_historical_cvar(
        portfolio_returns, confidence_level)
    historical_cvar_amount = calculate_historical_cvar_amount(
        portfolio_returns, analyzed_value, confidence_level
    )

    # ------------------------------------------------------------
    # 16. Risk contribution
    # ------------------------------------------------------------
    risk_contribution = calculate_risk_contribution(returns, weights)

    # ------------------------------------------------------------
    # 17. Stress testing (same asset scope + value as everything else)
    # ------------------------------------------------------------
    stress_shocks = pd.Series({asset: -0.10 for asset in weights.index})
    stress_result = calculate_portfolio_stress(
        analyzed_market_values.reindex(weights.index),
        stress_shocks,
    )

    # ------------------------------------------------------------
    # 18. Monte Carlo simulation
    # ------------------------------------------------------------
    monte_carlo_simulations = 10_000
    monte_carlo_seed = 42

    simulated_values = simulate_portfolio_values(
        initial_value=analyzed_value,
        expected_return=mean_return,
        volatility=daily_volatility,
        simulations=monte_carlo_simulations,
        random_seed=monte_carlo_seed,
    )

    monte_carlo_summary = summarize_simulated_values(simulated_values)

    # ------------------------------------------------------------
    # 19. Return complete structured result
    # ------------------------------------------------------------
    return {
        "portfolio": {
            "id": str(portfolio.id),
            "name": portfolio.name,
            "value": total_value,
            "analyzed_value": analyzed_value,
            "excluded_assets": excluded_assets,
        },
        "performance": {
            "mean_return": mean_return,
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
        },
        "volatility": {
            "daily": daily_volatility,
            "annualized": annualized_volatility,
            "portfolio": portfolio_volatility,
        },
        "drawdown": {
            "maximum": maximum_drawdown,
        },
        "tail_risk": {
            "confidence_level": confidence_level,
            "historical_var": historical_var,
            "historical_var_amount": historical_var_amount,
            "parametric_var": parametric_var,
            "parametric_var_amount": parametric_var_amount,
            "historical_cvar": historical_cvar,
            "historical_cvar_amount": historical_cvar_amount,
        },
        "risk_contribution": risk_contribution.to_dict(orient="index"),
        "stress_testing": stress_result,
        "portfolio_weights": {
            asset: float(weight) for asset, weight in weights.items()
        },
        "monte_carlo": {
            "simulations": monte_carlo_simulations,
            "expected_return": mean_return,
            "volatility": daily_volatility,
            **monte_carlo_summary,
        },
    }
