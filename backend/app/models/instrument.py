from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class InstrumentModel(Base):
    __tablename__ = "instruments"

    canonical_symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    asset_class: Mapped[str] = mapped_column(String(20))
    digits: Mapped[int]
    base_currency: Mapped[str | None] = mapped_column(String(10))
    quote_currency: Mapped[str] = mapped_column(String(10))
