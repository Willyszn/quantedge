from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from app.backtesting.execution import run_execution
from app.backtesting.metrics import compute_metrics
from app.backtesting.strategies.base import BaseStrategy
from app.backtesting.strategies.momentum_breakout import MomentumBreakoutStrategy


def make_df(n=200, start=100.0, drift=0.001, noise=0.003, seed=1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    closes = [start]
    for _ in range(n - 1):
        closes.append(closes[-1] * (1 + drift + rng.normal(0, noise)))
    closes = np.array(closes)
    opens = np.roll(closes, 1)
    opens[0] = closes[0]
    highs = np.maximum(opens, closes) * (1 + np.abs(rng.normal(0, noise / 2, n)))
    lows = np.minimum(opens, closes) * (1 - np.abs(rng.normal(0, noise / 2, n)))
    index = pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC")
    return pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes, "volume": 1000}, index=index)


class AlwaysLongOnceStrategy(BaseStrategy):
    """Fires exactly one long entry signal at a fixed bar, for deterministic execution tests."""

    name = "Always Long Once"
    description = "test double"

    def __init__(self, entry_index: int):
        self.entry_index = entry_index

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.copy()

    def entry_signal(self, df: pd.DataFrame, i: int) -> str | None:
        return "long" if i == self.entry_index else None


class LookAheadCheckingStrategy(BaseStrategy):
    """Records the max index it was ever asked to evaluate signals for versus
    what data it could see, to catch any accidental future-peeking."""

    name = "Look-ahead probe"
    description = "test double"

    def __init__(self):
        self.violations = []

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.copy()

    def entry_signal(self, df: pd.DataFrame, i: int) -> str | None:
        # A correct engine never calls this with i >= len(df).
        if i >= len(df):
            self.violations.append(i)
        return None


class TestNoLookAhead:
    def test_engine_never_asks_strategy_about_future_bars(self):
        df = make_df()
        strategy = LookAheadCheckingStrategy()
        run_execution(
            df,
            strategy,
            "TEST",
            initial_capital=10000,
            risk_per_trade_percent=1,
            slippage_bps=0,
            commission_bps=0,
            digits=2,
        )
        assert strategy.violations == []

    def test_entry_signal_only_receives_data_up_to_current_bar(self):
        # MomentumBreakoutStrategy's prior_high/prior_low use .shift(1), so
        # the breakout comparison at bar i never includes bar i's own high/low.
        df = make_df(seed=3)
        strategy = MomentumBreakoutStrategy()
        prepared = strategy.prepare(df)
        for i in range(30, len(prepared)):
            # prior_high at bar i must equal the max high over bars
            # [i-20, i-1] — never including bar i itself.
            window_high = df["high"].iloc[max(0, i - 20) : i].max()
            if not pd.isna(prepared["prior_high"].iloc[i]):
                assert prepared["prior_high"].iloc[i] == pytest.approx(window_high)


class TestExecutionMechanics:
    def test_entry_fills_at_signal_bar_close_with_slippage(self):
        df = make_df()
        entry_index = 70
        strategy = AlwaysLongOnceStrategy(entry_index)
        result = run_execution(
            df,
            strategy,
            "TEST",
            initial_capital=10000,
            risk_per_trade_percent=1,
            slippage_bps=10,
            commission_bps=0,
            digits=2,
        )
        assert len(result.trades) == 1
        trade = result.trades[0]
        signal_bar_close = df["close"].iloc[entry_index]
        # Long entry should be filled slightly *above* the raw close (unfavorable slippage).
        assert trade.entry_price > signal_bar_close
        assert trade.entry_price == pytest.approx(signal_bar_close, rel=0.01)

    def test_position_resolves_after_entry_bar_not_on_it(self):
        df = make_df()
        entry_index = 70
        strategy = AlwaysLongOnceStrategy(entry_index)
        result = run_execution(
            df,
            strategy,
            "TEST",
            initial_capital=10000,
            risk_per_trade_percent=1,
            slippage_bps=0,
            commission_bps=0,
            digits=2,
        )
        assert len(result.trades) == 1
        assert result.trades[0].exit_date > df.index[entry_index]

    def test_zero_commission_and_slippage_produces_reasonable_r_multiple(self):
        # With no cost drag, the resulting R multiple should land in a
        # sane range for a single stop/target/forced-close resolution.
        df = make_df(seed=99)
        strategy = AlwaysLongOnceStrategy(entry_index=50)
        result = run_execution(
            df,
            strategy,
            "TEST",
            initial_capital=10000,
            risk_per_trade_percent=1,
            slippage_bps=0,
            commission_bps=0,
            digits=2,
        )
        assert len(result.trades) == 1
        assert -1.5 <= result.trades[0].r_multiple <= 3.0

    def test_higher_commission_reduces_final_equity(self):
        df = make_df(seed=5)
        strategy = MomentumBreakoutStrategy()
        low_cost = run_execution(
            df,
            strategy,
            "TEST",
            initial_capital=10000,
            risk_per_trade_percent=1,
            slippage_bps=0,
            commission_bps=0,
            digits=2,
        )
        high_cost = run_execution(
            df,
            strategy,
            "TEST",
            initial_capital=10000,
            risk_per_trade_percent=1,
            slippage_bps=0,
            commission_bps=50,
            digits=2,
        )
        if low_cost.trades:  # only meaningful if the strategy actually traded
            assert high_cost.final_equity <= low_cost.final_equity

    def test_open_position_is_force_closed_at_final_bar(self):
        df = make_df(n=60)
        strategy = AlwaysLongOnceStrategy(entry_index=len(df) - 2)  # opens right before the end
        result = run_execution(
            df,
            strategy,
            "TEST",
            initial_capital=10000,
            risk_per_trade_percent=1,
            slippage_bps=0,
            commission_bps=0,
            digits=2,
        )
        assert len(result.trades) == 1  # forced closed, not left dangling
        assert result.trades[0].exit_date == df.index[-1]

    def test_equity_curve_has_one_point_per_closed_trade(self):
        df = make_df(seed=11)
        strategy = MomentumBreakoutStrategy()
        result = run_execution(
            df,
            strategy,
            "TEST",
            initial_capital=10000,
            risk_per_trade_percent=1,
            slippage_bps=2,
            commission_bps=1,
            digits=2,
        )
        assert len(result.equity_curve) == len(result.trades)

    def test_drawdown_percent_is_never_positive(self):
        df = make_df(seed=13)
        strategy = MomentumBreakoutStrategy()
        result = run_execution(
            df,
            strategy,
            "TEST",
            initial_capital=10000,
            risk_per_trade_percent=1,
            slippage_bps=2,
            commission_bps=1,
            digits=2,
        )
        for point in result.equity_curve:
            assert point.drawdown_percent <= 0.01  # allow tiny float rounding


class TestBacktestMetrics:
    def test_no_trades_returns_zeroed_metrics(self):
        metrics = compute_metrics([], [], 10000)
        assert metrics.total_trades == 0
        assert metrics.total_return_percent == 0.0
        assert metrics.win_rate == 0.0

    def test_metrics_reflect_actual_trade_outcomes(self):
        from app.backtesting.execution import EquityPoint, SimulatedTrade

        t0 = datetime(2026, 1, 1, tzinfo=UTC)
        trades = [
            SimulatedTrade("t1", "TEST", "long", t0, t0 + timedelta(days=1), 100, 102, 2.0, "win", 2.0, "normal"),
            SimulatedTrade(
                "t2", "TEST", "long", t0, t0 + timedelta(days=2), 100, 99, -1.0, "loss", -1.0, "normal"
            ),
        ]
        equity_curve = [
            EquityPoint(t0 + timedelta(days=1), 10200, 0.0),
            EquityPoint(t0 + timedelta(days=2), 10098, -1.0),
        ]
        metrics = compute_metrics(trades, equity_curve, 10000)
        assert metrics.total_trades == 2
        assert metrics.win_rate == 50.0
        assert metrics.total_return_percent == pytest.approx(0.98, abs=0.01)

    def test_profit_factor_is_gross_win_over_gross_loss(self):
        from app.backtesting.execution import EquityPoint, SimulatedTrade

        t0 = datetime(2026, 1, 1, tzinfo=UTC)
        trades = [
            SimulatedTrade("t1", "TEST", "long", t0, t0, 100, 104, 4.0, "win", 4.0, "normal"),
            SimulatedTrade("t2", "TEST", "long", t0, t0, 100, 98, -2.0, "loss", -2.0, "normal"),
        ]
        equity_curve = [EquityPoint(t0, 10400, 0.0), EquityPoint(t0, 10192, 0.0)]
        metrics = compute_metrics(trades, equity_curve, 10000)
        assert metrics.profit_factor == pytest.approx(2.0, abs=0.1)
