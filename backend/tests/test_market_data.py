from datetime import UTC, datetime, timedelta

import pytest

from app.market_data.registry import get_instrument, instrument_exists, list_instruments
from app.market_data.validation import CandleValidationError, RawCandle, filter_valid_candles, validate_series


def make_candle(**overrides) -> RawCandle:
    defaults = dict(
        time=datetime(2026, 1, 1, tzinfo=UTC), open=100.0, high=101.0, low=99.0, close=100.5, volume=1000
    )
    defaults.update(overrides)
    return RawCandle(**defaults)


class TestCandleValidation:
    def test_valid_candle_passes(self):
        validate_series([make_candle()])  # should not raise

    def test_rejects_high_below_open_close(self):
        with pytest.raises(CandleValidationError, match="high_below_open_close"):
            validate_series([make_candle(high=99.5, open=100.0, close=100.5)])

    def test_rejects_low_above_open_close(self):
        with pytest.raises(CandleValidationError, match="low_above_open_close"):
            validate_series([make_candle(low=100.2, open=100.0, close=100.5)])

    def test_rejects_high_below_low(self):
        with pytest.raises(CandleValidationError, match="high_below_low"):
            validate_series([make_candle(high=98.0, low=99.0, open=98.2, close=98.5)])

    def test_rejects_non_positive_price(self):
        with pytest.raises(CandleValidationError, match="non_positive_price"):
            validate_series([make_candle(open=-1.0)])

    def test_rejects_negative_volume(self):
        with pytest.raises(CandleValidationError, match="negative_volume"):
            validate_series([make_candle(volume=-5)])

    def test_rejects_duplicate_timestamps(self):
        t = datetime(2026, 1, 1, tzinfo=UTC)
        with pytest.raises(CandleValidationError, match="duplicate_timestamp"):
            validate_series([make_candle(time=t), make_candle(time=t)])

    def test_rejects_non_monotonic_ordering(self):
        t = datetime(2026, 1, 1, tzinfo=UTC)
        with pytest.raises(CandleValidationError, match="non_monotonic_ordering"):
            validate_series([make_candle(time=t), make_candle(time=t - timedelta(minutes=5))])

    def test_empty_series_is_valid(self):
        assert validate_series([]) == []


class TestFilterValidCandles:
    def test_keeps_good_candles_and_reports_bad_ones(self):
        t0 = datetime(2026, 1, 1, tzinfo=UTC)
        good = make_candle(time=t0)
        bad = make_candle(
            time=t0 + timedelta(minutes=1), high=99.5
        )  # below max(open, close)=100.5, but still >= low
        good2 = make_candle(time=t0 + timedelta(minutes=2))

        valid, rejected = filter_valid_candles([good, bad, good2])

        assert len(valid) == 2
        assert len(rejected) == 1
        assert rejected[0][1] == "high_below_open_close"

    def test_duplicate_timestamp_is_reported_not_raised(self):
        t0 = datetime(2026, 1, 1, tzinfo=UTC)
        valid, rejected = filter_valid_candles([make_candle(time=t0), make_candle(time=t0)])
        assert len(valid) == 1
        assert rejected[0][1] == "duplicate_timestamp"


class TestInstrumentRegistry:
    def test_all_frontend_symbols_present(self):
        expected = {
            "GBPUSD",
            "USDJPY",
            "EURUSD",
            "GBPJPY",
            "XAUUSD",
            "XAGUSD",
            "US500",
            "US100",
            "BTCUSD",
            "ETHUSD",
        }
        actual = {inst.canonical_symbol for inst in list_instruments()}
        assert actual == expected

    def test_unknown_symbol_returns_none(self):
        assert get_instrument("NOTASYMBOL") is None
        assert instrument_exists("NOTASYMBOL") is False

    def test_known_symbol_lookup_is_case_insensitive(self):
        assert get_instrument("xauusd") is not None
        assert instrument_exists("xauusd") is True

    def test_minimum_price_increment_matches_digits(self):
        gbpusd = get_instrument("GBPUSD")
        assert gbpusd.digits == 4
        assert gbpusd.minimum_price_increment == pytest.approx(0.0001)

    def test_provider_symbol_mapping_falls_back_to_canonical(self):
        eurusd = get_instrument("EURUSD")
        assert eurusd.provider_symbol("mt5") == "EURUSD"  # no override defined

    def test_provider_symbol_mapping_uses_override_when_present(self):
        us500 = get_instrument("US500")
        assert us500.provider_symbol("mt5") == "SPX500"
        assert us500.provider_symbol("mock") == "US500"  # no mock override -> falls back to canonical
