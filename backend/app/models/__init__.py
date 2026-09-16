"""
Importing this package registers every ORM model on Base.metadata, which is
what Alembic's autogenerate (see alembic/env.py) and create_all() (used in
tests) rely on.
"""

from app.models.alert import AlertModel
from app.models.backtest import BacktestModel, BacktestTradeModel
from app.models.instrument import InstrumentModel
from app.models.market import MarketCandleModel, MarketQuoteModel
from app.models.performance import PerformanceSnapshotModel
from app.models.quant import QuantSnapshotModel
from app.models.sentiment import SentimentObservationModel
from app.models.signal import SignalFactorModel, SignalModel, TradePlanModel

__all__ = [
    "AlertModel",
    "BacktestModel",
    "BacktestTradeModel",
    "InstrumentModel",
    "MarketCandleModel",
    "MarketQuoteModel",
    "PerformanceSnapshotModel",
    "QuantSnapshotModel",
    "SentimentObservationModel",
    "SignalFactorModel",
    "SignalModel",
    "TradePlanModel",
]
