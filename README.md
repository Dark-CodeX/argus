# Argus

<p align="center">
  <img src="img/logo.svg" alt="Argus Logo" width="180"/>
</p>

<p align="center"><strong>Financial Risk Intelligence Platform</strong></p>

<p align="center">
  A quantitative risk platform combining deterministic financial analytics,
  machine learning, high-performance computation, and an AI analyst.
</p>

---

## Overview

**Argus** helps users understand the behavior and risk of investment portfolios — going beyond prices to analyze performance, volatility, Sharpe/Sortino ratios, drawdown, VaR/CVaR, risk contribution, stress testing, Monte Carlo simulation, optimization, market regimes, volatility forecasts, and AI-assisted analysis.

> **Financial calculations should be deterministic and auditable, while AI should explain, orchestrate, and interact with those calculations.**

The LLM never performs financial math — that's handled by dedicated Python/C++ services, with the AI layer consuming results through controlled tools.

---

## The Problem

Portfolio risk analysis (risk exposure, loss scenarios, concentration, market regime, optimal allocation, plain-English explanations) is usually scattered across spreadsheets, notebooks, libraries, dashboards, and APIs. Argus brings it into one coherent platform.

---

## Features

- **Auth** — JWT-based auth, Argon2 password hashing, protected endpoints, per-user resource isolation.
- **Portfolios** — CRUD for portfolios containing holdings, transactions, and market-data relationships, with ownership checks.
- **Assets** — Reusable records (symbol, name, type, exchange) referenced by holdings/transactions.
- **Transactions & Holdings** — Transactions (BUY/SELL) are the source of truth; SELL validates quantity, updates holdings, computes realized P&L, and accounts for fees.
- **Market Data** — Historical OHLCV stored in PostgreSQL, cached via Redis/Valkey.

---

## Quantitative Risk Engine

Core, auditable financial calculations, including:

- Returns, volatility (with annualization), covariance/correlation
- Portfolio weights, return, and volatility ($\sigma_p = \sqrt{w^T\Sigma w}$)
- Sharpe and Sortino ratios
- Maximum drawdown
- Historical & parametric VaR, and CVaR (Expected Shortfall)
- Marginal & component risk contribution
- Scenario-based stress testing (e.g., asset-specific shocks)
- Monte Carlo simulation of future outcomes
- Minimum-variance portfolio optimization ($\min_w\ w^T\Sigma w$, s.t. $\sum w_i = 1$)

---

## Machine Learning

Two forward-looking model families, kept separate from the deterministic risk engine:

1. **Market regime classification** — labels conditions as Calm / Normal / Stress using return, volatility, momentum, drawdown, and volume features (baseline: logistic regression). *Note: current labels are derived from rolling volatility thresholds, which also appear as a feature — so this baseline mainly demonstrates the pipeline rather than true regime discovery.*
2. **Future volatility prediction** — targets 5-day forward realized volatility, using chronological splits to avoid look-ahead bias.

---

## AI Analyst (Planned)

A LangChain-based analyst will answer natural-language questions (e.g., *"Why is my portfolio risky?"*, *"What if tech falls 20%?"*) by routing through tool selection to Argus's risk/ML services, then explaining the results — never inventing numbers.

An **MCP server** will expose tools like `get_portfolio`, `calculate_risk`, `run_stress_test`, `run_monte_carlo`, `optimize_portfolio`, `predict_market_regime`, and `predict_volatility`. **Langfuse** will provide observability (traces, latency, errors, evals) for this AI subsystem.

---

## C++ Performance Layer (Planned)

Selected computational bottlenecks (covariance, Monte Carlo, optimization) will move to native C++ via **pybind11**, without rewriting the full application.

---

## Technology Stack

| Area | Technology |
|---|---|
| Backend / API | Python, FastAPI |
| Database / ORM | PostgreSQL, SQLAlchemy, Alembic |
| Auth | JWT, Argon2 |
| Cache | Redis / Valkey |
| Market Data | yfinance |
| Data / Numerics | pandas, NumPy, SciPy |
| ML | scikit-learn |
| AI | LangChain, MCP, Langfuse |
| Native Computation | C++, pybind11 |
| Frontend | React |

---

## Architecture

```text
React Frontend → FastAPI API → {Auth, Portfolio, Risk/ML Services} → Data/Cache Layer → {PostgreSQL, Redis/Valkey}

AI Analyst (LangChain) → MCP Server → Argus Tools/API → Risk + ML Engine   (traced via Langfuse)
```

**Design principles:** deterministic finance / probabilistic AI; strict separation of API → services → data access → computation; no look-ahead bias in ML (chronological splits only); transactions as source of truth; caching kept at the data boundary, isolated from the risk engine.

---

## Project Structure

```text
argus/
├── backend/
│   ├── app/ (api, cache, core, db, ml, models, schemas, services/risk)
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
├── cpp/
├── frontend/
└── docs/
```

---

## Development Status

**Completed:** backend foundation, FastAPI, PostgreSQL/SQLAlchemy/Alembic, JWT + Argon2 auth, portfolio/asset/holding/transaction CRUD, realized P&L, market data + Redis caching, full quantitative risk engine (with tests/profiling), ML architecture, feature engineering, chronological splitting, baseline regime classifier + evaluation.

**Planned:** stronger regime-model evaluation, volatility prediction model, ML persistence/service/API, C++ acceleration, LangChain AI analyst, MCP server, Langfuse, React frontend, full integration, security hardening, Docker/CI/CD, deployment.

---

## Local Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Docs at `http://127.0.0.1:8000/docs` (Swagger) or `/redoc`.

Configuration (`.env`, not committed):

```env
DATABASE_URL=postgresql+psycopg://...
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Testing

- **Unit** — returns, volatility, Sharpe, Sortino, drawdown, VaR, CVaR, risk contribution, stress testing
- **Service** — portfolio behavior, transactions, market-data ingestion, risk-report construction
- **API** — auth, portfolio/transaction/market-data/risk endpoints
- **ML** — chronological evaluation against simple baselines

---

## Security

JWT auth, Argon2 hashing, ownership checks, Pydantic validation, database constraints, env-based secrets — with rate limiting/API hardening planned. Use HTTPS and proper secret management in production.

---

## Disclaimer

Argus is a software engineering and quantitative-finance project for analysis, research, and educational purposes. It is not personalized financial advice, and historical data or model predictions do not guarantee future performance.

---

## Name

Named after **Argus Panoptes**, the many-eyed figure from Greek mythology — the idea being to observe a portfolio's risk from multiple perspectives at once.

<p align="center">
  <strong>Argus — Observe risk. Understand it. Act on it.</strong>
</p>