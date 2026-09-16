import pytest

from app.quant.volatility import VolatilityResult
from app.risk.engine import assess_risk, build_trade_plan


def make_volatility(atr=1.0, atr_percent=0.6, regime="normal") -> VolatilityResult:
    return VolatilityResult(score=90.0, atr=atr, atr_percent_of_price=atr_percent, regime=regime, expanding=False)


class TestTradePlan:
    def test_long_plan_has_stop_below_and_target_above_entry(self):
        plan = build_trade_plan("long", current_price=100.0, atr=1.0, digits=2)
        assert plan.stop_loss < plan.entry_low
        assert plan.target > plan.entry_high

    def test_short_plan_has_stop_above_and_target_below_entry(self):
        plan = build_trade_plan("short", current_price=100.0, atr=1.0, digits=2)
        assert plan.stop_loss > plan.entry_high
        assert plan.target < plan.entry_low

    def test_entry_zone_is_centered_on_current_price(self):
        plan = build_trade_plan("long", current_price=100.0, atr=1.0, digits=2)
        midpoint = (plan.entry_low + plan.entry_high) / 2
        assert midpoint == pytest.approx(100.0, abs=0.5)

    def test_risk_reward_ratio_matches_configured_target(self):
        from app.core.scoring_config import RISK_CONFIG

        plan = build_trade_plan("long", current_price=100.0, atr=1.0, digits=2)
        assert plan.risk_reward_ratio == pytest.approx(RISK_CONFIG.TARGET_RISK_REWARD, abs=0.05)

    def test_wider_atr_produces_wider_stop_distance(self):
        tight = build_trade_plan("long", current_price=100.0, atr=0.5, digits=2)
        wide = build_trade_plan("long", current_price=100.0, atr=2.0, digits=2)
        tight_stop_distance = tight.entry_low - tight.stop_loss
        wide_stop_distance = wide.entry_low - wide.stop_loss
        assert wide_stop_distance > tight_stop_distance


class TestRiskAssessment:
    def test_risk_score_is_bounded(self):
        result = assess_risk("long", 100.0, make_volatility(), digits=2)
        assert 0 <= result.risk_score <= 100

    def test_normal_regime_scores_higher_than_extreme(self):
        normal = assess_risk("long", 100.0, make_volatility(regime="normal"), digits=2)
        extreme = assess_risk("long", 100.0, make_volatility(atr=5.0, atr_percent=5.0, regime="extreme"), digits=2)
        assert normal.risk_score > extreme.risk_score

    def test_volatility_regime_is_passed_through(self):
        result = assess_risk("long", 100.0, make_volatility(regime="elevated"), digits=2)
        assert result.volatility_regime == "elevated"

    def test_position_risk_percent_is_capped(self):
        from app.core.scoring_config import RISK_CONFIG

        result = assess_risk(
            "long", 100.0, make_volatility(atr=20.0, atr_percent=20.0, regime="extreme"), digits=2
        )
        assert result.position_risk_percent <= RISK_CONFIG.MAX_POSITION_RISK_PERCENT

    def test_zero_atr_does_not_produce_zero_stop_distance(self):
        # A degenerate all-flat series could report ATR == 0; the engine
        # must still produce a workable (non-zero) stop, not a division
        # error or a stop equal to the entry price.
        result = assess_risk("long", 100.0, make_volatility(atr=0.0, atr_percent=0.0, regime="low"), digits=2)
        assert result.plan.stop_loss != result.plan.entry_low
