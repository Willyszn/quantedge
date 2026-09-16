import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestHealthAndCatalog:
    async def test_health_endpoint(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] in {"ok", "degraded"}
        assert "database" in body and "redis" in body

    async def test_instruments_endpoint_returns_all_ten(self, client: AsyncClient):
        response = await client.get("/instruments")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 10
        assert {"symbol", "name", "assetClass", "digits", "supportedTimeframes"} <= body[0].keys()

    async def test_strategies_endpoint_returns_four(self, client: AsyncClient):
        response = await client.get("/strategies")
        assert response.status_code == 200
        names = {s["name"] for s in response.json()}
        assert names == {"Momentum Breakout", "Trend Continuation", "Mean Reversion", "Sentiment Confluence"}


class TestMarketsEndpoints:
    async def test_get_quotes_returns_camel_case_contract(self, client: AsyncClient):
        response = await client.get("/markets/quotes")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 10
        quote = body[0]
        assert {
            "symbol",
            "name",
            "assetClass",
            "price",
            "changePercent",
            "changeAbsolute",
            "status",
            "spark",
            "updatedAt",
        } <= quote.keys()

    async def test_get_single_quote(self, client: AsyncClient):
        response = await client.get("/markets/quotes/XAUUSD")
        assert response.status_code == 200
        assert response.json()["symbol"] == "XAUUSD"

    async def test_unknown_symbol_returns_404_with_error_envelope(self, client: AsyncClient):
        response = await client.get("/markets/quotes/NOTASYMBOL")
        assert response.status_code == 404
        body = response.json()
        assert body["error"]["code"] == "SYMBOL_NOT_FOUND"

    async def test_series_returns_candles(self, client: AsyncClient):
        response = await client.get("/markets/XAUUSD/series", params={"timeframe": "1H"})
        assert response.status_code == 200
        body = response.json()
        assert body["symbol"] == "XAUUSD"
        assert len(body["candles"]) > 0
        assert {"time", "open", "high", "low", "close", "volume"} <= body["candles"][0].keys()

    async def test_unsupported_timeframe_returns_422(self, client: AsyncClient):
        response = await client.get("/markets/XAUUSD/series", params={"timeframe": "7Q"})
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "UNSUPPORTED_TIMEFRAME"

    async def test_capabilities_only_reports_registry_timeframes(self, client: AsyncClient):
        response = await client.get("/markets/XAGUSD/capabilities")
        assert response.status_code == 200
        # XAGUSD deliberately excludes 1m/5m in the registry.
        assert "1m" not in response.json()["supportedTimeframes"]


class TestSignalsEndpoints:
    async def test_get_signal_for_symbol_has_full_explainable_contract(self, client: AsyncClient):
        response = await client.get("/signals/XAUUSD")
        assert response.status_code == 200
        body = response.json()
        assert body["direction"] in {"long", "short"}
        assert body["rating"] in {"strong-buy", "buy", "neutral", "sell", "strong-sell"}
        assert 0 <= body["confidence"] <= 100
        assert len(body["factors"]) == 5
        factor_ids = {f["id"] for f in body["factors"]}
        assert factor_ids == {"momentum", "trend", "volatility", "sentiment-factor", "risk-conditions"}
        assert body["narrative"]

    async def test_get_all_signals_sorted_by_confidence_desc(self, client: AsyncClient):
        response = await client.get("/signals")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 10
        confidences = [s["confidence"] for s in body]
        assert confidences == sorted(confidences, reverse=True)

    async def test_primary_signal_is_one_of_the_listed_signals(self, client: AsyncClient):
        all_signals = (await client.get("/signals")).json()
        primary = (await client.get("/signals/primary")).json()
        assert primary["symbol"] in {s["symbol"] for s in all_signals}

    async def test_unknown_symbol_signal_returns_404(self, client: AsyncClient):
        response = await client.get("/signals/NOTASYMBOL")
        assert response.status_code == 404


class TestSentimentEndpoints:
    async def test_symbol_sentiment_contract(self, client: AsyncClient):
        response = await client.get("/sentiment/XAUUSD")
        assert response.status_code == 200
        body = response.json()
        assert body["split"]["bullish"] + body["split"]["neutral"] + body["split"]["bearish"] == pytest.approx(
            100, abs=1
        )

    async def test_market_sentiment_contract(self, client: AsyncClient):
        response = await client.get("/sentiment/market")
        assert response.status_code == 200
        assert "split" in response.json()


class TestBacktestEndpoint:
    async def test_run_backtest_returns_full_result_contract(self, client: AsyncClient):
        payload = {
            "symbol": "EURUSD",
            "strategy": "Mean Reversion",
            "startDate": "2025-06-01T00:00:00Z",
            "endDate": "2025-12-01T00:00:00Z",
            "initialCapital": 50000,
            "riskPerTradePercent": 1.0,
            "slippageBps": 2,
            "commissionBps": 1,
        }
        response = await client.post("/backtests", json=payload)
        assert response.status_code == 200
        body = response.json()
        for key in [
            "totalReturnPercent",
            "winRate",
            "profitFactor",
            "maxDrawdownPercent",
            "sharpeLike",
            "equityCurve",
            "trades",
        ]:
            assert key in body

    async def test_end_before_start_returns_422(self, client: AsyncClient):
        payload = {
            "symbol": "EURUSD",
            "strategy": "Mean Reversion",
            "startDate": "2025-12-01T00:00:00Z",
            "endDate": "2025-06-01T00:00:00Z",
            "initialCapital": 50000,
            "riskPerTradePercent": 1.0,
            "slippageBps": 2,
            "commissionBps": 1,
        }
        response = await client.post("/backtests", json=payload)
        assert response.status_code == 422

    async def test_unsupported_strategy_returns_422(self, client: AsyncClient):
        payload = {
            "symbol": "EURUSD",
            "strategy": "Not A Real Strategy",
            "startDate": "2025-06-01T00:00:00Z",
            "endDate": "2025-12-01T00:00:00Z",
            "initialCapital": 50000,
            "riskPerTradePercent": 1.0,
            "slippageBps": 2,
            "commissionBps": 1,
        }
        response = await client.post("/backtests", json=payload)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "UNSUPPORTED_STRATEGY"

    async def test_backtest_completion_raises_a_real_alert(self, client: AsyncClient):
        payload = {
            "symbol": "BTCUSD",
            "strategy": "Momentum Breakout",
            "startDate": "2025-06-01T00:00:00Z",
            "endDate": "2025-12-01T00:00:00Z",
            "initialCapital": 50000,
            "riskPerTradePercent": 1.0,
            "slippageBps": 2,
            "commissionBps": 1,
        }
        await client.post("/backtests", json=payload)
        alerts = (await client.get("/alerts")).json()
        assert any(a["type"] == "backtest-complete" for a in alerts)


class TestPerformanceAndHistoryEndpoints:
    async def test_metrics_are_zeroed_before_any_backtest(self, client: AsyncClient):
        response = await client.get("/performance/metrics")
        assert response.status_code == 200
        body = response.json()
        assert body["totalReturnPercent"] == 0.0

    async def test_metrics_shape_is_complete(self, client: AsyncClient):
        response = await client.get("/performance/metrics")
        body = response.json()
        expected_keys = {
            "totalReturnPercent",
            "winRate",
            "profitFactor",
            "maxDrawdownPercent",
            "averageR",
            "expectancy",
            "bestTradePercent",
            "worstTradePercent",
        }
        assert expected_keys <= body.keys()

    async def test_performance_reflects_a_completed_backtest(self, client: AsyncClient):
        payload = {
            "symbol": "GBPUSD",
            "strategy": "Trend Continuation",
            "startDate": "2025-06-01T00:00:00Z",
            "endDate": "2025-12-01T00:00:00Z",
            "initialCapital": 50000,
            "riskPerTradePercent": 1.0,
            "slippageBps": 2,
            "commissionBps": 1,
        }
        await client.post("/backtests", json=payload)

        metrics = (await client.get("/performance/metrics")).json()
        assert "totalReturnPercent" in metrics

        history = (await client.get("/trades/history")).json()
        assert len(history) > 0

        by_instrument = (await client.get("/performance/by/instrument")).json()
        assert any(s["label"] == "GBPUSD" for s in by_instrument)

    async def test_invalid_slice_dimension_returns_422(self, client: AsyncClient):
        response = await client.get("/performance/by/not-a-real-dimension")
        assert response.status_code == 422

    async def test_trade_history_empty_before_any_backtest(self, client: AsyncClient):
        response = await client.get("/trades/history")
        assert response.status_code == 200
        assert response.json() == []


class TestAlertsEndpoint:
    async def test_alerts_endpoint_returns_list(self, client: AsyncClient):
        response = await client.get("/alerts")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_generating_a_signal_raises_a_new_signal_alert(self, client: AsyncClient):
        await client.get("/signals/ETHUSD")
        alerts = (await client.get("/alerts")).json()
        assert any(a["type"] == "new-signal" and a["symbol"] == "ETHUSD" for a in alerts)
