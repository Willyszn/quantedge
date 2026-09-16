from app.schemas.market import CamelModel


class StrategySchema(CamelModel):
    """
    Backing GET /strategies — same single-source-of-truth intent as
    GET /instruments. The Backtesting page currently imports its strategy
    list from src/mocks/backtests.ts (STRATEGIES); wiring that to this
    endpoint is a frontend follow-up, not required for this backend to work.
    """

    name: str
    description: str
