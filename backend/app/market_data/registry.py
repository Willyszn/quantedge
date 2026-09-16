"""
The canonical symbol system (spec section 6).

The frontend and every QUANTEDGE API always speak canonical symbols
(GBPUSD, XAUUSD, ...). Individual market-data providers may use different
symbol spellings (a broker might list the S&P 500 as "SPX500" or
"US500.cash"); `provider_symbols` is the configuration-driven translation
layer so adding or swapping a provider never touches calculation code.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

Timeframe = Literal["1m", "5m", "15m", "1H", "4H", "1D"]


class AssetClass(StrEnum):
    FOREX = "forex"
    METALS = "metals"
    INDEX = "index"
    CRYPTO = "crypto"


ALL_TIMEFRAMES: list[Timeframe] = ["1m", "5m", "15m", "1H", "4H", "1D"]


@dataclass(frozen=True)
class InstrumentDef:
    canonical_symbol: str
    name: str
    asset_class: AssetClass
    digits: int
    base_currency: str | None
    quote_currency: str
    supported_timeframes: list[Timeframe]
    # provider name -> provider-specific symbol. Falls back to canonical_symbol
    # when a provider isn't listed here.
    provider_symbols: dict[str, str] = field(default_factory=dict)

    @property
    def minimum_price_increment(self) -> float:
        return 10 ** (-self.digits)

    def provider_symbol(self, provider: str) -> str:
        return self.provider_symbols.get(provider, self.canonical_symbol)


INSTRUMENT_REGISTRY: dict[str, InstrumentDef] = {
    inst.canonical_symbol: inst
    for inst in [
        InstrumentDef(
            canonical_symbol="GBPUSD",
            name="British Pound / US Dollar",
            asset_class=AssetClass.FOREX,
            digits=4,
            base_currency="GBP",
            quote_currency="USD",
            supported_timeframes=["5m", "15m", "1H", "4H", "1D"],
        ),
        InstrumentDef(
            canonical_symbol="USDJPY",
            name="US Dollar / Japanese Yen",
            asset_class=AssetClass.FOREX,
            digits=2,
            base_currency="USD",
            quote_currency="JPY",
            supported_timeframes=["5m", "15m", "1H", "4H", "1D"],
        ),
        InstrumentDef(
            canonical_symbol="EURUSD",
            name="Euro / US Dollar",
            asset_class=AssetClass.FOREX,
            digits=4,
            base_currency="EUR",
            quote_currency="USD",
            supported_timeframes=["1m", "5m", "15m", "1H", "4H", "1D"],
        ),
        InstrumentDef(
            canonical_symbol="GBPJPY",
            name="British Pound / Japanese Yen",
            asset_class=AssetClass.FOREX,
            digits=2,
            base_currency="GBP",
            quote_currency="JPY",
            supported_timeframes=["5m", "15m", "1H", "4H", "1D"],
        ),
        InstrumentDef(
            canonical_symbol="XAUUSD",
            name="Gold Spot / US Dollar",
            asset_class=AssetClass.METALS,
            digits=2,
            base_currency="XAU",
            quote_currency="USD",
            supported_timeframes=["1m", "5m", "15m", "1H", "4H", "1D"],
        ),
        InstrumentDef(
            canonical_symbol="XAGUSD",
            name="Silver Spot / US Dollar",
            asset_class=AssetClass.METALS,
            digits=2,
            base_currency="XAG",
            quote_currency="USD",
            supported_timeframes=["15m", "1H", "4H", "1D"],
        ),
        InstrumentDef(
            canonical_symbol="US500",
            name="S&P 500 Index",
            asset_class=AssetClass.INDEX,
            digits=1,
            base_currency=None,
            quote_currency="USD",
            supported_timeframes=["5m", "15m", "1H", "4H", "1D"],
            provider_symbols={"mt5": "SPX500"},
        ),
        InstrumentDef(
            canonical_symbol="US100",
            name="Nasdaq 100 Index",
            asset_class=AssetClass.INDEX,
            digits=1,
            base_currency=None,
            quote_currency="USD",
            supported_timeframes=["5m", "15m", "1H", "4H", "1D"],
            provider_symbols={"mt5": "NAS100"},
        ),
        InstrumentDef(
            canonical_symbol="BTCUSD",
            name="Bitcoin / US Dollar",
            asset_class=AssetClass.CRYPTO,
            digits=1,
            base_currency="BTC",
            quote_currency="USD",
            supported_timeframes=["1m", "5m", "15m", "1H", "4H", "1D"],
        ),
        InstrumentDef(
            canonical_symbol="ETHUSD",
            name="Ethereum / US Dollar",
            asset_class=AssetClass.CRYPTO,
            digits=1,
            base_currency="ETH",
            quote_currency="USD",
            supported_timeframes=["5m", "15m", "1H", "4H", "1D"],
        ),
    ]
}


def get_instrument(symbol: str) -> InstrumentDef | None:
    return INSTRUMENT_REGISTRY.get(symbol.upper())


def list_instruments() -> list[InstrumentDef]:
    return list(INSTRUMENT_REGISTRY.values())


def instrument_exists(symbol: str) -> bool:
    return symbol.upper() in INSTRUMENT_REGISTRY
