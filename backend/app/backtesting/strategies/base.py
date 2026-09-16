"""
Strategy interface (spec section 29). Every strategy precomputes its
indicators once (vectorized, using only backward-looking rolling windows —
pandas .rolling()/.ewm() never reference future rows), then `entry_signal`
is asked, bar by bar, whether to enter. `entry_signal(df, i)` must only ever
read df.iloc[i] or earlier; this is how the engine avoids look-ahead bias
(spec section 30).
"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseStrategy(ABC):
    name: str
    description: str

    @abstractmethod
    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        """Returns a copy of df with any indicator columns this strategy needs added."""

    @abstractmethod
    def entry_signal(self, df: pd.DataFrame, i: int) -> str | None:
        """
        Returns "long", "short", or None for bar index i. Must only use
        df.iloc[j] for j <= i.
        """
