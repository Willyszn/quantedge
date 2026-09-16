"""
Risk engine (spec sections 25-26). Builds the concrete trade plan — entry
zone, stop loss, target, risk/reward — from actual price and volatility
data, plus a 0-100 risk score describing how workable those numbers are.
Every value here is deterministic and traceable back to the ATR and current
price that produced it; nothing is randomly generated.
"""

from dataclasses import dataclass

from app.core.scoring_config import RISK_CONFIG
from app.quant.scoring import bell_score, clamp
from app.quant.volatility import VolatilityResult


@dataclass
class TradePlan:
    entry_low: float
    entry_high: float
    stop_loss: float
    target: float
    risk_reward_ratio: float


@dataclass
class RiskAssessment:
    risk_score: float  # 0-100, higher = safer/more workable
    expected_risk_reward: float
    stop_distance_percent: float
    position_risk_percent: float
    volatility_regime: str
    plan: TradePlan


def build_trade_plan(
    direction: str,
    current_price: float,
    atr: float,
    digits: int,
) -> TradePlan:
    """
    Entry zone is centered on current price, sized as a fraction of ATR
    (tight enough to be actionable, wide enough to absorb noise). Stop
    distance is a multiple of ATR beyond the entry zone. Target is placed
    to hit the configured target risk/reward ratio.
    """
    entry_half_width = atr * RISK_CONFIG.ENTRY_ZONE_ATR_FRACTION
    stop_distance = atr * RISK_CONFIG.ATR_STOP_MULTIPLIER

    entry_low = current_price - entry_half_width
    entry_high = current_price + entry_half_width

    if direction == "long":
        stop_loss = entry_low - stop_distance
        target_distance = stop_distance * RISK_CONFIG.TARGET_RISK_REWARD
        target = entry_high + target_distance
    else:
        stop_loss = entry_high + stop_distance
        target_distance = stop_distance * RISK_CONFIG.TARGET_RISK_REWARD
        target = entry_low - target_distance

    risk_reward_ratio = round(target_distance / stop_distance, 2) if stop_distance else 0.0

    return TradePlan(
        entry_low=round(entry_low, digits),
        entry_high=round(entry_high, digits),
        stop_loss=round(stop_loss, digits),
        target=round(target, digits),
        risk_reward_ratio=risk_reward_ratio,
    )


def assess_risk(
    direction: str,
    current_price: float,
    volatility: VolatilityResult,
    digits: int,
) -> RiskAssessment:
    plan = build_trade_plan(direction, current_price, max(volatility.atr, current_price * 0.0005), digits)

    stop_distance = abs((plan.entry_low if direction == "long" else plan.entry_high) - plan.stop_loss)
    stop_distance_percent = round((stop_distance / current_price) * 100, 3) if current_price else 0.0
    position_risk_percent = round(min(stop_distance_percent * 0.4, RISK_CONFIG.MAX_POSITION_RISK_PERCENT), 2)

    # Risk score rewards: R:R at/above target, stop distance that's neither
    # razor-thin (gets stopped by noise) nor huge (poor capital efficiency),
    # and a volatility regime that isn't "extreme".
    rr_score = (
        clamp(
            (
                (plan.risk_reward_ratio - RISK_CONFIG.MIN_RISK_REWARD)
                / (RISK_CONFIG.TARGET_RISK_REWARD - RISK_CONFIG.MIN_RISK_REWARD)
            )
            * 100
        )
        if RISK_CONFIG.TARGET_RISK_REWARD != RISK_CONFIG.MIN_RISK_REWARD
        else 50.0
    )

    stop_score = bell_score(stop_distance_percent, ideal=0.6, tolerance=1.2)
    regime_score = {"low": 70.0, "normal": 95.0, "elevated": 60.0, "extreme": 25.0}.get(volatility.regime, 50.0)

    risk_score = clamp(0.4 * rr_score + 0.3 * stop_score + 0.3 * regime_score)

    return RiskAssessment(
        risk_score=round(risk_score, 1),
        expected_risk_reward=plan.risk_reward_ratio,
        stop_distance_percent=stop_distance_percent,
        position_risk_percent=position_risk_percent,
        volatility_regime=volatility.regime,
        plan=plan,
    )
