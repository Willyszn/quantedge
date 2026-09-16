"""
MT5MarketDataProvider (spec section 5).

Real integration with MetaTrader 5 via the official `MetaTrader5` Python
package. Two important constraints to be upfront about, since pretending
otherwise would violate the "no fake intelligence" principle:

1. The `MetaTrader5` package only talks to a *running MT5 terminal*, and
   that terminal only ships for Windows. In practice this provider runs
   either on a Windows host next to a logged-in terminal, or behind a small
   Windows-side bridge service that this backend calls over HTTP — the
   `MetaTrader5` package itself cannot be installed/used on Linux.
2. Because of (1), this class is not exercised by the Linux CI/test
   environment this backend was developed in. It's structurally complete
   and follows the same MarketDataProvider interface as the mock provider,
   but treat it as needing a real MT5-connected environment to validate
   before relying on it in production.

Until MT5_ENABLED=true and a terminal is reachable, QUANTEDGE runs on
MockMarketDataProvider instead of silently failing.
"""

from datetime import UTC, datetime

from app.core.config import get_settings
from app.core.logging import get_logger
from app.market_data.provider_base import (
    DataFreshness,
    MarketDataProvider,
    MarketStatus,
    ProviderQuote,
)
from app.market_data.registry import Timeframe, get_instrument
from app.market_data.validation import RawCandle

logger = get_logger(__name__)

try:
    import MetaTrader5 as mt5

    MT5_PACKAGE_AVAILABLE = True
except ImportError:  # pragma: no cover - expected on non-Windows dev machines
    mt5 = None
    MT5_PACKAGE_AVAILABLE = False

TIMEFRAME_MAP = {
    "1m": "TIMEFRAME_M1",
    "5m": "TIMEFRAME_M5",
    "15m": "TIMEFRAME_M15",
    "1H": "TIMEFRAME_H1",
    "4H": "TIMEFRAME_H4",
    "1D": "TIMEFRAME_D1",
}


class MT5ConnectionError(RuntimeError):
    pass


class MT5MarketDataProvider(MarketDataProvider):
    name = "mt5"

    def __init__(self) -> None:
        self.settings = get_settings()
        self._connected = False

    def _ensure_connected(self) -> None:
        if not MT5_PACKAGE_AVAILABLE:
            raise MT5ConnectionError(
                "MetaTrader5 package is not installed. It only runs on Windows "
                "alongside a live MT5 terminal — see module docstring."
            )
        if self._connected:
            return

        initialized = mt5.initialize(
            server=self.settings.MT5_SERVER,
            login=int(self.settings.MT5_LOGIN) if self.settings.MT5_LOGIN else None,
            password=self.settings.MT5_PASSWORD,
        )
        if not initialized:
            raise MT5ConnectionError(f"MT5 initialize() failed: {mt5.last_error()}")
        self._connected = True
        logger.info("mt5_connected", extra={"event": "mt5_connected", "server": self.settings.MT5_SERVER})

    async def is_healthy(self) -> bool:
        try:
            self._ensure_connected()
            return mt5.terminal_info() is not None
        except Exception:
            return False

    async def get_instrument_info(self, symbol: str) -> dict | None:
        inst = get_instrument(symbol)
        if inst is None:
            return None
        try:
            self._ensure_connected()
            info = mt5.symbol_info(inst.provider_symbol(self.name))
            if info is None:
                return None
            return {
                "canonicalSymbol": inst.canonical_symbol,
                "providerSymbol": inst.provider_symbol(self.name),
                "name": inst.name,
                "assetClass": inst.asset_class.value,
                "digits": info.digits,
                "minimumPriceIncrement": info.point,
            }
        except MT5ConnectionError:
            return None

    async def get_supported_timeframes(self, symbol: str) -> list[Timeframe]:
        # MT5 itself supports all standard timeframes; the registry still
        # governs what QUANTEDGE *claims* to support per-instrument, since a
        # given broker/symbol may not have history at every resolution.
        inst = get_instrument(symbol)
        return inst.supported_timeframes if inst else []

    async def get_quote(self, symbol: str) -> ProviderQuote | None:
        inst = get_instrument(symbol)
        if inst is None:
            return None
        try:
            self._ensure_connected()
        except MT5ConnectionError as exc:
            logger.warning("mt5_unavailable", extra={"event": "mt5_unavailable", "reason": str(exc)})
            return None

        provider_symbol = inst.provider_symbol(self.name)
        tick = mt5.symbol_info_tick(provider_symbol)
        if tick is None:
            return None

        rates = mt5.copy_rates_from_pos(provider_symbol, mt5.TIMEFRAME_M5, 0, 24)
        spark = [round(float(r["close"]), inst.digits) for r in rates] if rates is not None else []

        # change%/change-absolute are derived downstream from spark[0] (see
        # MarketDataService._reference_price), consistent with how
        # MockMarketDataProvider is handled — the provider only needs to
        # supply price + spark.
        price = float(tick.bid)

        info = mt5.symbol_info(provider_symbol)
        is_market_open = bool(info.trade_mode) if info else True

        return ProviderQuote(
            symbol=inst.canonical_symbol,
            price=round(price, inst.digits),
            status=MarketStatus.OPEN if is_market_open else MarketStatus.CLOSED,
            timestamp=datetime.fromtimestamp(tick.time, tz=UTC),
            freshness=DataFreshness.LIVE,
            spark=spark,
        )

    async def get_quotes(self, symbols: list[str]) -> list[ProviderQuote]:
        results = []
        for symbol in symbols:
            quote = await self.get_quote(symbol)
            if quote is not None:
                results.append(quote)
        return results

    async def get_historical_candles(
        self, symbol: str, timeframe: str, start: datetime, end: datetime
    ) -> list[RawCandle]:
        inst = get_instrument(symbol)
        if inst is None or timeframe not in TIMEFRAME_MAP:
            return []
        try:
            self._ensure_connected()
        except MT5ConnectionError as exc:
            logger.warning("mt5_unavailable", extra={"event": "mt5_unavailable", "reason": str(exc)})
            return []

        mt5_timeframe = getattr(mt5, TIMEFRAME_MAP[timeframe])
        provider_symbol = inst.provider_symbol(self.name)
        rates = mt5.copy_rates_range(provider_symbol, mt5_timeframe, start, end)
        if rates is None:
            return []

        return [
            RawCandle(
                time=datetime.fromtimestamp(r["time"], tz=UTC),
                open=float(r["open"]),
                high=float(r["high"]),
                low=float(r["low"]),
                close=float(r["close"]),
                volume=float(r["tick_volume"]),
            )
            for r in rates
        ]

    async def get_candles(self, symbol: str, timeframe: str, count: int = 200) -> list[RawCandle]:
        inst = get_instrument(symbol)
        if inst is None or timeframe not in TIMEFRAME_MAP:
            return []
        try:
            self._ensure_connected()
        except MT5ConnectionError as exc:
            logger.warning("mt5_unavailable", extra={"event": "mt5_unavailable", "reason": str(exc)})
            return []

        mt5_timeframe = getattr(mt5, TIMEFRAME_MAP[timeframe])
        provider_symbol = inst.provider_symbol(self.name)
        rates = mt5.copy_rates_from_pos(provider_symbol, mt5_timeframe, 0, count)
        if rates is None:
            return []

        return [
            RawCandle(
                time=datetime.fromtimestamp(r["time"], tz=UTC),
                open=float(r["open"]),
                high=float(r["high"]),
                low=float(r["low"]),
                close=float(r["close"]),
                volume=float(r["tick_volume"]),
            )
            for r in rates
        ]
