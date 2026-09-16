# QUANTEDGE Backend

The production backend for QUANTEDGE — a manual, decision-support quantitative
and sentiment trading-analysis platform. It ingests market data, computes real
quantitative and risk metrics, aggregates sentiment, generates explainable
trade signals, runs historical backtests, and serves all of it through a REST
API that matches the existing React frontend's TypeScript contracts exactly.

**QUANTEDGE never places, modifies, or closes trades.** There is no
`place_order` / `execute_trade` endpoint anywhere in this codebase, by design.

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

This starts Postgres, Redis, and the API (migrations run automatically on
container start). The API is then live at `http://localhost:8000`, with
interactive docs at `http://localhost:8000/docs`.

## Quick start (local, no Docker)

Requires Python 3.11+, PostgreSQL, and Redis running locally.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env   # adjust DATABASE_URL/REDIS_URL if needed

# create the database (adjust user/db name to match your .env)
createuser quantedge --superuser
createdb quantedge --owner quantedge

.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

## Connecting the existing frontend

In the frontend project, set:

```
VITE_DEMO_MODE=false
VITE_API_BASE_URL=http://localhost:8000
```

Every hook in the frontend's `src/api/*.ts` already branches on demo mode —
no frontend code changes are required. CORS is controlled by `CORS_ORIGINS`
in `.env` (defaults to `http://localhost:5173`, Vite's default dev port).

### Two endpoints beyond the original frontend contract

`GET /instruments` and `GET /strategies` were added as the intended eventual
single source of truth for the instrument list and strategy list — the
frontend currently still sources both from `src/mocks/instruments.ts` and
`src/mocks/backtests.ts` (`STRATEGIES`) even with demo mode off. Wiring the
frontend over to these two endpoints is a small follow-up, not a blocker:
everything else already works against the real backend.

## Running tests

```bash
createdb quantedge_test --owner quantedge   # one-time
.venv/bin/pytest                             # 127 tests
.venv/bin/pytest --cov=app --cov-report=term-missing
```

Tests use a real Postgres database (`quantedge_test`, dropped/recreated per
test function) and a real Redis instance (flushed per test) — not mocks of
the persistence layer — so they exercise the actual query and caching code.

## Code quality

```bash
.venv/bin/ruff check app/ tests/
.venv/bin/ruff format app/ tests/
.venv/bin/mypy app/
```

## Architecture

```
MARKET DATA (provider abstraction: Mock | MT5)
        │
  DATA VALIDATION (app/market_data/validation.py — OHLC sanity, dedup, ordering)
        │
   ┌────┴────┐
   ▼         ▼
QUANT     SENTIMENT ENGINE
ENGINE    (relevance × recency × confidence weighted aggregation)
(trend/momentum/volatility/structure → composite Quant Score)
   └────┬────┘
        ▼
  SIGNAL ENGINE (app/services/signal_engine.py)
        │
   RISK ENGINE (ATR-based trade plan, R:R, risk score)
        │
  EXPLAINABLE TradeSignal (factors + confidence + narrative, all traceable)
        │
     REST API  ← this is what the frontend talks to
```

Each of `MarketDataService`, `QuantAnalysisService` (the `app/quant/*`
modules), `SentimentService`, `SignalEngine`, `RiskEngine`, `BacktestEngine`,
`PerformanceService`, and `AlertService` is independently importable and
tested without the others — see `tests/`.

### Directory layout

```
app/
  api/routes/      One file per resource; routes call services, never engines directly
  core/            Config, database, Redis, logging, error envelope, scoring weights
  models/          SQLAlchemy ORM (12 tables, Alembic-migrated)
  schemas/         Pydantic response models — the frontend TypeScript contract, in code
  services/        Orchestration layer: caching, persistence, wiring engines together
  market_data/     Provider abstraction, instrument registry, candle validation
  quant/           Trend, momentum, volatility, structure, composite scoring
  sentiment/       Provider abstraction, relevance mapping, aggregation
  signals/         Factor generation, confidence, rating, narrative, ranking
  risk/            Trade plan construction, risk scoring
  backtesting/     Strategies, execution simulator, metrics — usable outside FastAPI
  performance/     (reserved for future standalone aggregation jobs)
  alerts/          (reserved for future standalone alert-generation jobs)
  realtime/        (reserved for WebSocket event types — not yet implemented)
```

## Data honesty — what's real vs. what's mock

- **The intelligence layer is always real.** Every quant score, risk
  calculation, confidence value, and signal factor is computed from actual
  OHLC math (pandas/numpy) against whatever candles the configured provider
  returns — mock or live. Nothing in `app/quant`, `app/risk`, or `app/signals`
  branches on demo vs. production; it's the same code either way.
- **`MARKET_DATA_PROVIDER=mock` (default) uses deterministic, seeded
  synthetic price data**, clearly not a real feed. Backtests against it will
  typically show flat-to-negative returns once realistic slippage/commission
  are applied — synthetic random-walk data has no genuine exploitable edge,
  and the engine doesn't pretend otherwise. Connect `MT5MarketDataProvider`
  (see below) for economically meaningful results.
- **`/trades/history` and `/performance/*` are empty until a backtest has
  run.** `SEED_ON_STARTUP=true` (development only) runs three example
  backtests on first startup so these endpoints aren't empty on first
  integration — every seeded row went through the exact same `BacktestEngine`
  a manual `POST /backtests` call would use.
- **Alerts are only ever raised from a real detected state change** — see
  `app/services/alert_service.py`'s docstring. One category
  (`entry-zone`, price crossing into a signal's zone) is intentionally not
  implemented yet: detecting a *crossing* honestly needs two consecutive
  price observations over time, which is a background-job concern (see
  Known limitations below), not something a single request can produce
  without faking it.

## Swapping in real providers

### Market data: MetaTrader 5

Set `MARKET_DATA_PROVIDER=mt5`, `MT5_ENABLED=true`, and the `MT5_SERVER` /
`MT5_LOGIN` / `MT5_PASSWORD` variables. Read the docstring at the top of
`app/market_data/mt5_provider.py` first — the `MetaTrader5` Python package
only works alongside a running MT5 terminal, which only ships for Windows.
This backend was developed and tested on Linux against `MockMarketDataProvider`;
the MT5 adapter is structurally complete (implements the same
`MarketDataProvider` interface, is exercised by the same instrument
registry) but wasn't exercised end-to-end in this environment. Validate it
against a real terminal before depending on it in production.

### Sentiment: a real news API

Set `SENTIMENT_PROVIDER=news`, `NEWS_PROVIDER` (an API host), and
`NEWS_API_KEY`. `app/sentiment/news_provider.py`'s docstring explains the
one deliberate placeholder: headline-to-sentiment-score classification
(`_score_headline`) is a minimal keyword scorer, not a real financial
sentiment model. Swap it for a proper classifier (e.g. a FinBERT-style
model) before relying on this in production — the provider's job (fetching,
normalizing, rate-limiting) is complete; the scoring model is a product
decision left open intentionally rather than papered over.

## Known limitations / honest gaps

- **Signals and quotes are generated synchronously on read** (with Redis
  caching: ~12s for quotes, ~45s for signals, ~60s for sentiment), not by a
  continuously-running background scheduler. The architecture is ready for
  one — `arq` is in `requirements.txt`, and every engine is a plain callable
  with no FastAPI dependency — but no worker process ships yet (spec Phase 8).
  Practically: `generated_at`-based primary-signal ranking has limited effect
  today since signals for a given request batch are generated in the same
  instant; it will matter once a scheduler staggers real generation times.
- **`entry-zone` alerts aren't implemented** — see Data honesty above.
- **`Sentiment Confluence` strategy is a documented proxy.** Bar-by-bar
  historical sentiment isn't stored yet (only `published_at`, not a
  backfilled time series), so this strategy approximates "confluence" via
  multiple agreeing price-derived signals instead. See the docstring in
  `app/backtesting/strategies/sentiment_confluence.py`.
- **`/performance/by/signal-type` groups by trade direction (Long/Short)**,
  not a rating tier — research/backtest trades aren't yet linked back to the
  live `TradeSignal` rating that might have inspired them. See the docstring
  in `app/services/performance_service.py`.
- **WebSocket real-time updates aren't implemented.** `app/realtime/` is
  reserved for this; the frontend currently polls, which still works.
- **No authentication.** Explicitly deferred per the spec ("do not build
  unnecessary authentication complexity before the core engine works") —
  `SECRET_KEY` is present in config for when it's needed.
