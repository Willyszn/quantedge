from datetime import datetime
from typing import Literal

from app.schemas.market import CamelModel

AlertType = Literal[
    "new-signal",
    "confidence-up",
    "confidence-down",
    "entry-zone",
    "risk-change",
    "sentiment-change",
    "backtest-complete",
]


class AlertItemSchema(CamelModel):
    id: str
    type: AlertType
    title: str
    description: str
    symbol: str | None = None
    created_at: datetime
    read: bool
