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

**Argus** is a financial risk intelligence platform designed to help users understand the behavior and risk of investment portfolios.

Instead of treating a portfolio as only a collection of prices, Argus analyzes it across multiple dimensions:

- Portfolio performance
- Volatility
- Sharpe and Sortino ratios
- Maximum drawdown
- Value at Risk (VaR)
- Conditional Value at Risk (CVaR)
- Risk contribution
- Stress testing
- Monte Carlo simulation
- Portfolio optimization
- Market regime classification
- Future volatility prediction
- AI-assisted risk analysis

The core architectural principle is:

> **Financial calculations should be deterministic and auditable, while AI should explain, orchestrate, and interact with those calculations.**

The LLM is therefore not responsible for performing financial mathematics. Quantitative calculations are handled by dedicated Python/C++ services, while the AI layer consumes those results through controlled tools.

---

# The Problem

Portfolio risk analysis often requires many separate calculations and tools.

An investor or analyst may need to answer questions such as:

- How risky is my portfolio?
- Which asset contributes the most risk?
- How much could I lose under an adverse scenario?
- What happens if the market falls sharply?
- Is my portfolio too concentrated?
- What market regime are we experiencing?
- How volatile could the portfolio become?
- Which allocation minimizes risk?
- Can the results be explained in plain English?

These capabilities are often scattered across spreadsheets, notebooks, financial libraries, dashboards, and separate APIs.

**Argus aims to bring them together into one coherent platform.**

---

# Goal

The goal of Argus is to build a complete **financial risk intelligence system** combining:

1. Reliable financial calculations
2. Machine-learning based market intelligence
3. High-performance numerical computation
4. AI-assisted analysis
5. Secure APIs
6. A modern web interface
7. AI observability and evaluation

The project also serves as a practical implementation of modern backend engineering, quantitative finance, machine learning, C++, and LLM application architecture.

---

# Features

## Authentication and Authorization

Argus provides JWT-based authentication and user-level resource isolation.

Capabilities include:

- User registration
- Login
- JWT access tokens
- Protected endpoints
- Current-user identification
- Inactive-user protection
- Portfolio ownership checks
- Secure password hashing with Argon2

---

## Portfolio Management

Users can create and manage investment portfolios.

A portfolio contains:

- Name
- Description
- Holdings
- Transaction history
- Market-data relationships

CRUD operations are exposed through the backend API.

Resource ownership is checked at the service/API layer so users cannot access another user's portfolios.

---

## Assets

Argus maintains reusable financial asset records containing information such as:

```text
Symbol
Name
Asset Type
Exchange
```

Example assets:

```text
AAPL
MSFT
NVDA
```

Assets are referenced by holdings, transactions, and market data.

---

## Transactions and Holdings

Transactions are the **source of truth** for portfolio activity.

Supported transaction types:

```text
BUY
SELL
```

A BUY transaction updates the position and weighted average cost.

A SELL transaction:

- validates the available quantity
- updates the holding
- calculates realized P&L
- accounts for fees
- records the transaction

This provides a more realistic portfolio model than treating holdings as manually entered static data.

---

## Historical Market Data

Argus stores historical OHLCV data:

```text
Open
High
Low
Close
Volume
```

Historical market data can be fetched, validated, and stored in PostgreSQL.

Redis/Valkey is used as a cache for repeated historical-data queries.

---

# Quantitative Risk Engine

The quantitative risk engine is one of the central components of Argus.

It is intentionally separated from the AI layer so financial calculations remain reproducible, testable, and auditable.

## Returns

Simple return:

\[
R_t = \frac{P_t}{P_{t-1}} - 1
\]

---

## Volatility

Daily volatility is calculated from returns and can be annualized using the common 252-trading-day convention:

\[
\sigma_{annual} = \sigma_{daily}\sqrt{252}
\]

---

## Covariance and Correlation

Argus calculates covariance and correlation between assets to understand how portfolio components move together.

Correlation satisfies:

\[
-1 \leq \rho \leq 1
\]

---

## Portfolio Weights

Portfolio weights are based on the value of each position:

\[
w_i = \frac{V_i}{V_p}
\]

where:

- $V_i$ is the value of asset $i$
- $V_p$ is total portfolio value

---

## Portfolio Return

\[
R_p = \sum_i w_i R_i
\]

---

## Portfolio Volatility

\[
\sigma_p = \sqrt{w^T\Sigma w}
\]

where $w$ is the portfolio weight vector and $\Sigma$ is the covariance matrix.

---

## Sharpe Ratio

\[
Sharpe = \frac{R_p - R_f}{\sigma_p}
\]

The Sharpe ratio measures return relative to total volatility.

---

## Sortino Ratio

\[
Sortino = \frac{R_p - T}{DD}
\]

Sortino uses downside deviation instead of total volatility, emphasizing harmful variation below the chosen target.

---

## Maximum Drawdown

Drawdown measures the decline from the running portfolio peak:

\[
Drawdown_t = \frac{V_t - Peak_t}{Peak_t}
\]

Maximum drawdown is the worst observed drawdown over the selected period.

---

## Value at Risk (VaR)

Argus supports:

- Historical VaR
- Parametric VaR

VaR estimates a loss threshold at a selected confidence level such as 95% or 99%.

---

## Conditional Value at Risk (CVaR)

CVaR, or Expected Shortfall, measures the average loss in the tail beyond the VaR threshold.

This helps quantify the severity of extreme losses rather than only identifying a cutoff.

---

## Risk Contribution

Marginal risk contribution:

\[
MRC_i = \frac{(\Sigma w)_i}{\sigma_p}
\]

Component risk contribution:

\[
CRC_i = w_i MRC_i
\]

This allows Argus to identify which assets contribute most to total portfolio risk.

---

## Stress Testing

Argus supports scenario-based stress testing.

For example:

```text
AAPL  -15%
MSFT  -10%
NVDA  -25%
```

The engine calculates the resulting portfolio impact.

This can be used to study hypothetical:

- market crashes
- sector shocks
- asset-specific events
- severe downside scenarios

---

## Monte Carlo Simulation

Argus includes Monte Carlo simulation for exploring possible future portfolio outcomes.

The current baseline implementation models returns statistically and generates simulated future values.

The simulation layer is designed to become more sophisticated as the ML and C++ components mature.

---

## Portfolio Optimization

Argus includes minimum-variance portfolio optimization.

The basic objective is:

\[
\min_w \quad w^T\Sigma w
\]

subject to:

\[
\sum_i w_i = 1
\]

and allocation constraints such as:

\[
0 \leq w_i \leq 1
\]

---

# Machine Learning

Argus includes a separate ML subsystem for forward-looking market intelligence.

The initial ML direction contains two model families:

1. Market regime classification
2. Future volatility prediction

ML outputs provide forecasts and context; deterministic financial calculations remain in the risk engine.

---

## Market Regime Classification

The baseline classifier labels market conditions as:

```text
0 → Calm
1 → Normal
2 → Stress
```

Initial features:

```text
return_1d
volatility_20d
momentum_20d
drawdown
volume_change_20d
```

The baseline model uses logistic regression.

Evaluation includes:

- Accuracy
- Precision
- Recall
- F1 score
- Confusion matrix
- Majority-class baseline comparison

### Baseline limitation

The current labels are initially derived from rolling volatility thresholds. Because `volatility_20d` also appears as a feature, this baseline should be viewed primarily as a demonstration of the ML pipeline, not as a sophisticated economic regime-discovery model.

---

## Future Volatility Prediction

Argus is designed to predict future realized volatility.

The intended target is future 5-day realized volatility:

\[
Target_t = Std(R_{t+1}, ..., R_{t+5})
\]

Chronological datasets are used to avoid look-ahead bias.

---

# AI Analyst

Argus will include an AI-powered financial analyst built with **LangChain**.

The analyst is intended to answer natural-language questions such as:

```text
Why is my portfolio risky?

Which asset contributes the most risk?

What happens if the technology sector falls 20%?

Why did my portfolio risk increase?

What market regime are we currently in?

Why is my Sharpe ratio low?
```

The intended workflow is:

```text
User Question
      ↓
AI Analyst
      ↓
Tool Selection
      ↓
Argus Services
      ↓
Risk / ML Calculations
      ↓
AI Explanation
```

The LLM explains and orchestrates results rather than inventing financial numbers.

---

# MCP Server

Argus will expose selected platform capabilities through an **MCP server**.

Potential tools include:

```text
get_portfolio
get_holdings
get_market_data
calculate_risk
run_stress_test
run_monte_carlo
optimize_portfolio
predict_market_regime
predict_volatility
```

This creates a standardized tool interface for AI systems.

---

# Langfuse

**Langfuse** will provide observability for the AI subsystem.

It can be used to inspect:

- LLM calls
- prompts
- outputs
- tool calls
- latency
- errors
- traces
- evaluation signals

This is important for debugging, monitoring, and improving AI workflows.

---

# C++ Performance Layer

Argus is designed to use **C++ with pybind11** for computational workloads where native performance is useful.

Architecture:

```text
Python Service
      ↓
   pybind11
      ↓
 C++ Engine
      ↓
Numerical Computation
```

Potential candidates include:

- covariance calculations
- Monte Carlo simulation
- large numerical workloads
- optimization-related computation

The objective is not to rewrite the entire application in C++, but to move selected computational bottlenecks into optimized native code.

---

# Technology Stack

| Area | Technology |
|---|---|
| Backend API | Python |
| Web Framework | FastAPI |
| API Documentation | OpenAPI / Swagger UI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT |
| Password Hashing | Argon2 |
| Cache | Redis / Valkey |
| Market Data | yfinance + PostgreSQL |
| Data Processing | pandas |
| Numerical Computing | NumPy / SciPy |
| Machine Learning | scikit-learn |
| LLM Framework | LangChain |
| AI Observability | Langfuse |
| AI Tool Protocol | MCP |
| Native Computation | C++ |
| Python/C++ Binding | pybind11 |
| Frontend | React |
| API Style | REST |

---

# Architecture

## High-Level System

```text
                         ┌───────────────────┐
                         │   React Frontend  │
                         └─────────┬─────────┘
                                   │
                              HTTP / JSON
                                   │
                         ┌─────────▼─────────┐
                         │     FastAPI       │
                         │      API          │
                         └─────────┬─────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
      ┌───────▼───────┐    ┌──────▼──────┐    ┌────────▼────────┐
      │ Authentication│    │ Portfolio   │    │ Risk / ML       │
      │ & Users       │    │ Services    │    │ Services        │
      └───────────────┘    └──────┬──────┘    └────────┬────────┘
                                  │                    │
                                  └─────────┬──────────┘
                                            │
                                  ┌─────────▼─────────┐
                                  │ Data / Cache Layer │
                                  └─────────┬──────────┘
                                            │
                              ┌─────────────┴─────────────┐
                              │                           │
                       ┌──────▼──────┐             ┌──────▼──────┐
                       │ PostgreSQL  │             │ Redis/Valkey│
                       └─────────────┘             └─────────────┘
```

## AI Extension

```text
                ┌─────────────────┐
                │    AI Analyst   │
                │    LangChain    │
                └────────┬────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ MCP Server  │
                  └──────┬──────┘
                         │
                         ▼
                 Argus Tools / API
                         │
                ┌────────▼────────┐
                │ Risk + ML Engine│
                └─────────────────┘

                  ↑
             Langfuse traces
```

---

# Project Structure

```text
argus/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   └── dependencies.py
│   │   ├── cache/
│   │   ├── core/
│   │   ├── db/
│   │   ├── ml/
│   │   │   ├── datasets/
│   │   │   ├── evaluation/
│   │   │   ├── features/
│   │   │   ├── inference/
│   │   │   ├── models/
│   │   │   └── training/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   │       └── risk/
│   ├── alembic/
│   ├── tests/
│   ├── driver.py
│   ├── ml_driver.py
│   ├── profile_risk.py
│   ├── requirements.txt
│   └── .env
│
├── cpp/
│   └── ...
│
├── frontend/
│   └── ...
│
├── docs/
│   └── logo.png
│
├── .gitignore
└── README.md
```

---

# Data Flow

A typical portfolio-risk workflow is:

```text
User
 ↓
Register / Login
 ↓
JWT Access Token
 ↓
Create Portfolio
 ↓
Record BUY / SELL Transactions
 ↓
Holdings Updated
 ↓
Historical Market Data
 ↓
Quantitative Risk Engine
 ↓
Risk Report
 ↓
ML Market Context
 ↓
AI Analyst
 ↓
Natural-Language Explanation
```

---

# Design Principles

## 1. Deterministic Finance, Probabilistic AI

Financial calculations should be:

- deterministic
- reproducible
- testable
- inspectable

AI should primarily provide:

- natural-language interaction
- explanation
- orchestration
- tool selection
- summarization

---

## 2. Separation of Responsibilities

Argus separates API handling, business logic, data access, financial calculations, and ML.

```text
API
 ↓
Services
 ↓
Data Access
 ↓
Risk / ML Computation
```

This makes the system easier to test, maintain, optimize, and extend.

---

## 3. No Look-Ahead Bias

Financial ML models must respect time.

Training data must contain only information that would have been available at the time of prediction.

Therefore Argus uses chronological train/validation/test splits rather than randomly shuffling time-series observations.

---

## 4. Transactions as Source of Truth

Transactions represent portfolio activity.

Holdings represent the current position.

This preserves a meaningful historical record of how the portfolio evolved.

---

## 5. Cache at the Data Boundary

Redis is used by data-access functionality where repeated queries benefit from caching.

The risk engine itself should not depend directly on Redis:

```text
Risk Service
     ↓
Market Data Service
     ↓
Redis → PostgreSQL
```

This keeps financial calculations independent from infrastructure concerns.

---

# API Documentation

FastAPI provides interactive Swagger/OpenAPI documentation.

During local development, it is typically available at:

```text
http://127.0.0.1:8000/docs
```

Alternative documentation:

```text
http://127.0.0.1:8000/redoc
```

---

# Development Status

## Completed

- Project foundation
- FastAPI backend
- Backend architecture
- Configuration management
- PostgreSQL integration
- SQLAlchemy ORM
- Alembic migrations
- JWT authentication
- Argon2 password hashing
- User management
- Portfolio CRUD
- Assets
- Holdings
- Transactions
- Realized P&L
- Historical market data
- Redis/Valkey caching
- Quantitative risk engine
- Risk API
- Risk validation and testing
- Risk profiling
- ML architecture
- ML dataset preparation
- Feature engineering
- Chronological train/validation/test splitting
- Baseline market regime classifier
- Baseline regime evaluation

## Planned / In Progress

- More robust regime-model evaluation
- Future volatility target and model
- ML model persistence
- ML service layer
- ML API
- ML/risk integration
- C++ numerical acceleration
- LangChain AI analyst
- MCP server
- Langfuse observability
- React frontend
- End-to-end integration
- Security hardening
- Performance optimization
- Docker
- CI/CD
- Deployment

---

# Roadmap

```text
[1]  Project Foundation                ✅
[2]  FastAPI                            ✅
[3]  Backend Architecture              ✅
[4]  Configuration                     ✅
[5]  PostgreSQL / SQLAlchemy / Alembic ✅
[6]  Authentication / JWT              ✅
[7]  Assets / Holdings                 ✅
[8]  Transactions / Market Data / Redis✅
[9]  Quantitative Risk Engine          ✅
[10] Machine Learning                  🔄
[11] C++ / pybind11                    ⏳
[12] Background Processing             ⏳
[13] LangChain AI Analyst              ⏳
[14] MCP Server                        ⏳
[15] Langfuse                          ⏳
[16] React Frontend                    ⏳
[17] Full Integration                  ⏳
[18] Testing / Security / Performance  ⏳
[19] Docker / CI/CD / Deployment       ⏳
```

---

# Local Development

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Start the development API:

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

# Environment Variables

Sensitive configuration belongs in `.env` and should not be committed to Git.

Example:

```env
DATABASE_URL=postgresql+psycopg://...
REDIS_URL=redis://localhost:6379/0

JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

A sanitized `.env.example` should be maintained for contributors.

---

# Testing

Argus is designed to use multiple levels of validation.

### Unit Tests

Validate individual financial functions:

```text
returns
volatility
Sharpe
Sortino
drawdown
VaR
CVaR
risk contribution
stress testing
```

### Service Tests

Validate:

```text
portfolio behavior
transactions
market-data ingestion
risk-report construction
```

### API Tests

Validate:

```text
authentication
authorization
portfolio endpoints
transaction endpoints
market-data endpoints
risk endpoints
```

### ML Evaluation

ML models are evaluated with chronological datasets and compared with simple baseline models.

---

# Why Argus?

Argus is intentionally more than a CRUD application and more than a stock-prediction model.

It combines:

```text
Financial Mathematics
        +
Backend Engineering
        +
Machine Learning
        +
C++
        +
Caching and Data Systems
        +
LLM Applications
        +
Observability
        +
Web Development
```

The project demonstrates how these technologies can form one coherent financial software system.

---

# Learning Objectives

Building Argus provides practical experience with:

- Python backend engineering
- FastAPI
- REST API design
- SQLAlchemy
- PostgreSQL
- Alembic
- JWT authentication
- authorization
- Redis caching
- quantitative finance
- financial risk management
- time-series machine learning
- model evaluation
- Monte Carlo methods
- numerical optimization
- C++/Python interoperability
- pybind11
- LangChain
- MCP
- Langfuse
- React integration
- testing
- profiling
- security
- deployment

---

# Example Questions

Argus is being designed to answer questions such as:

```text
What is the current risk of my portfolio?

Which asset contributes the most risk?

What is my 99% historical VaR?

What is my maximum drawdown?

How would the portfolio behave if NVDA dropped 25%?

Is the current market regime Calm, Normal, or Stress?

What is the expected volatility over the next five trading days?

Which allocation minimizes portfolio volatility?

Why did my portfolio risk increase?
```

Answers should be grounded in actual Argus calculations and stored data.

---

# Security

Security considerations include:

- JWT authentication
- Argon2 password hashing
- Protected endpoints
- Ownership checks
- Pydantic input validation
- Database constraints
- Environment-based secrets
- Avoiding committed credentials
- Future rate limiting and API hardening

Production deployments should use HTTPS and proper secret management.

---

# Disclaimer

Argus is a software engineering and quantitative-finance project intended for **analysis, research, and educational purposes**.

Its outputs should not be considered personalized financial advice.

Financial markets are uncertain, and historical data or model predictions do not guarantee future performance.

---

# Name

**Argus** is inspired by **Argus Panoptes**, the many-eyed figure from Greek mythology.

The idea behind the name is simple:

> **Observe the portfolio from multiple perspectives.**

Performance, volatility, correlations, drawdown, tail risk, stress scenarios, market regimes, and forecasts are different views of the same financial system.

Argus brings those views together.

---

<p align="center">
  <strong>Argus — Observe risk. Understand it. Act on it.</strong>
</p>
