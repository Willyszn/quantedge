"""
Execution simulator (spec section 30). Explicit assumptions, stated here
rather than buried in code:

- A strategy's entry_signal(df, i) is evaluated using bar i's *closing*
  data (indicators computed from bar i and earlier only). The resulting
  position is filled at bar i's close, adjusted unfavorably by slippage.
- Stop/target are then checked starting from bar i+1's high/low onward —
  never bar i's own high/low, since that would let the same bar that
  produced the signal also resolve it (look-ahead).
- If both the stop and target would be hit within the same bar, the stop
  is assumed to hit first (the conservative assumption).
- Commission is a round-trip cost (entry + exit) deducted from equity as a
  percentage of the equity risked on that trade, per COMMISSION_BPS.
- Any position still open at the final bar is force-closed at that bar's
  close (mark-to-market), so every backtest ends flat.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

import pandas as pd

from app.core.scoring_config import RISK_CONFIG, VOLATILITY_CONFIG
from app.quant.volatility import compute_atr

ATR_PERIOD = 14

TradeDirection = Literal["long", "short"]
TradeOutcome = Literal["win", "loss", "breakeven"]
VolatilityRegime = Literal["low", "normal", "elevated", "extreme"]


def _classify_regime(atr_percent: float) -> VolatilityRegime:
    cfg = VOLATILITY_CONFIG
    if atr_percent <= cfg.LOW_REGIME_MAX:
        return "low"
    if atr_percent <= cfg.NORMAL_REGIME_MAX:
        return "normal"
    if atr_percent <= cfg.ELEVATED_REGIME_MAX:
        return "elevated"
    return "extreme"


@dataclass
class SimulatedTrade:
    id: str
    symbol: str
    direction: TradeDirection
    entry_date: datetime
    exit_date: datetime
    entry_price: float
    exit_price: float
    r_multiple: float
    outcome: TradeOutcome
    pnl_percent: float
    regime: VolatilityRegime  # volatility regime at entry


@dataclass
class EquityPoint:
    date: datetime
    equity: float
    drawdown_percent: float


@dataclass
class ExecutionResult:
    trades: list[SimulatedTrade]
    equity_curve: list[EquityPoint]
    final_equity: float


@dataclass
class _OpenPosition:
    direction: TradeDirection
    entry_price: float
    stop: float
    target: float
    stop_distance: float
    entry_date: datetime
    equity_at_entry: float
    regime: VolatilityRegime


def run_execution(
    df: pd.DataFrame,
    strategy,
    symbol: str,
    initial_capital: float,
    risk_per_trade_percent: float,
    slippage_bps: float,
    commission_bps: float,
    digits: int,
) -> ExecutionResult:
    prepared = strategy.prepare(df)
    atr_series = compute_atr(df, ATR_PERIOD)

    equity = initial_capital
    peak_equity = initial_capital
    position: _OpenPosition | None = None

    trades: list[SimulatedTrade] = []
    equity_curve: list[EquityPoint] = []

    slippage_fraction = slippage_bps / 10000
    commission_fraction = commission_bps / 10000

    def record_equity_point(date: datetime) -> None:
        nonlocal peak_equity
        peak_equity = max(peak_equity, equity)
        drawdown_percent = ((equity - peak_equity) / peak_equity) * 100 if peak_equity else 0.0
        equity_curve.append(
            EquityPoint(date=date, equity=round(equity, 2), drawdown_percent=round(drawdown_percent, 2))
        )

    for i in range(len(prepared)):
        row = prepared.iloc[i]
        time = prepared.index[i]

        if position is None:
            signal = strategy.entry_signal(prepared, i)
            if signal is None:
                continue

            atr_value = (
                float(atr_series.iloc[i]) if not pd.isna(atr_series.iloc[i]) else float(row["close"]) * 0.005
            )
            stop_distance = max(atr_value * RISK_CONFIG.ATR_STOP_MULTIPLIER, float(row["close"]) * 0.0005)
            atr_percent = (atr_value / float(row["close"])) * 100 if row["close"] else 0.0
            regime = _classify_regime(atr_percent)
            slip = float(row["close"]) * slippage_fraction

            if signal == "long":
                entry_price = float(row["close"]) + slip
                stop = entry_price - stop_distance
                target = entry_price + stop_distance * RISK_CONFIG.TARGET_RISK_REWARD
            else:
                entry_price = float(row["close"]) - slip
                stop = entry_price + stop_distance
                target = entry_price - stop_distance * RISK_CONFIG.TARGET_RISK_REWARD

            position = _OpenPosition(
                direction=signal,
                entry_price=entry_price,
                stop=stop,
                target=target,
                stop_distance=stop_distance,
                entry_date=time,
                equity_at_entry=equity,
                regime=regime,
            )
            continue

        # Resolve the open position using this bar's range.
        hit_stop = row["low"] <= position.stop if position.direction == "long" else row["high"] >= position.stop
        hit_target = (
            row["high"] >= position.target if position.direction == "long" else row["low"] <= position.target
        )
        is_last_bar = i == len(prepared) - 1

        if hit_stop or hit_target or is_last_bar:
            if hit_stop:
                raw_exit = position.stop
            elif hit_target:
                raw_exit = position.target
            else:
                raw_exit = float(row["close"])  # forced close, mark-to-market

            slip = raw_exit * slippage_fraction
            exit_price = raw_exit - slip if position.direction == "long" else raw_exit + slip

            sign = 1 if position.direction == "long" else -1
            r_multiple = ((exit_price - position.entry_price) / position.stop_distance) * sign

            gross_pnl = position.equity_at_entry * (risk_per_trade_percent / 100) * r_multiple
            commission_cost = position.equity_at_entry * commission_fraction * 2  # round trip
            net_pnl = gross_pnl - commission_cost

            equity += net_pnl
            pnl_percent = (net_pnl / position.equity_at_entry) * 100 if position.equity_at_entry else 0.0

            outcome: TradeOutcome = "win" if net_pnl > 0.01 else "loss" if net_pnl < -0.01 else "breakeven"

            trades.append(
                SimulatedTrade(
                    id=f"bt-trade-{len(trades)}",
                    symbol=symbol,
                    direction=position.direction,
                    entry_date=position.entry_date,
                    exit_date=time,
                    entry_price=round(position.entry_price, digits),
                    exit_price=round(exit_price, digits),
                    r_multiple=round(r_multiple, 2),
                    outcome=outcome,
                    pnl_percent=round(pnl_percent, 2),
                    regime=position.regime,
                )
            )
            record_equity_point(time)
            position = None

    return ExecutionResult(trades=trades, equity_curve=equity_curve, final_equity=equity)
