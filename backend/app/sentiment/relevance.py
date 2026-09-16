"""
Symbol relevance layer (spec section 16). A news item about US inflation
should move USDJPY and XAUUSD more than it moves ETHUSD. This module is a
documented, explicit topic -> instrument relevance table — a reasonable
first version per the spec ("eventually this can use named-entity
recognition"). Swapping in a real NER/entity-linking model later only means
replacing `relevance_for_symbol`'s lookup with a smarter one; the
aggregation layer that consumes it doesn't change.
"""

from app.market_data.registry import AssetClass, get_instrument

# entity/topic keyword -> {canonical_symbol: relevance weight (0-1)}
# Keywords are matched case-insensitively against SentimentObservation.entities.
ENTITY_RELEVANCE: dict[str, dict[str, float]] = {
    "usd": {
        "GBPUSD": 0.9,
        "USDJPY": 0.9,
        "EURUSD": 0.9,
        "XAUUSD": 0.8,
        "XAGUSD": 0.7,
        "US500": 0.7,
        "US100": 0.7,
        "BTCUSD": 0.5,
        "ETHUSD": 0.5,
    },
    "fed": {
        "GBPUSD": 0.85,
        "USDJPY": 0.9,
        "EURUSD": 0.85,
        "XAUUSD": 0.85,
        "US500": 0.8,
        "US100": 0.8,
        "BTCUSD": 0.55,
        "ETHUSD": 0.55,
    },
    "inflation": {
        "USDJPY": 0.9,
        "XAUUSD": 0.9,
        "GBPUSD": 0.6,
        "EURUSD": 0.6,
        "US500": 0.65,
        "US100": 0.65,
        "ETHUSD": 0.3,
        "BTCUSD": 0.35,
    },
    "interest-rates": {
        "USDJPY": 0.85,
        "GBPUSD": 0.8,
        "EURUSD": 0.8,
        "XAUUSD": 0.7,
        "US500": 0.75,
        "US100": 0.75,
    },
    "gbp": {"GBPUSD": 0.95, "GBPJPY": 0.9},
    "boe": {"GBPUSD": 0.9, "GBPJPY": 0.75},
    "eur": {"EURUSD": 0.95},
    "ecb": {"EURUSD": 0.9},
    "jpy": {"USDJPY": 0.95, "GBPJPY": 0.85},
    "boj": {"USDJPY": 0.9, "GBPJPY": 0.7},
    "gold": {"XAUUSD": 0.98, "XAGUSD": 0.4},
    "silver": {"XAGUSD": 0.98, "XAUUSD": 0.3},
    "safe-haven": {"XAUUSD": 0.85, "XAGUSD": 0.6, "USDJPY": 0.4},
    "equities": {"US500": 0.95, "US100": 0.95},
    "tech-earnings": {"US100": 0.9, "US500": 0.6},
    "crypto": {"BTCUSD": 0.95, "ETHUSD": 0.9},
    "bitcoin": {"BTCUSD": 0.98, "ETHUSD": 0.4},
    "ethereum": {"ETHUSD": 0.98, "BTCUSD": 0.35},
    "risk-sentiment": {"US500": 0.6, "US100": 0.6, "BTCUSD": 0.55, "ETHUSD": 0.55, "XAUUSD": 0.4},
    "geopolitical": {"XAUUSD": 0.7, "USDJPY": 0.5, "US500": 0.4, "US100": 0.4},
}

# Fallback relevance by asset class when no entity in the observation maps
# to the symbol directly — keeps broad macro items from contributing zero
# weight to every instrument outside their explicit keyword list.
ASSET_CLASS_BASELINE_RELEVANCE = 0.15


def relevance_for_symbol(entities: list[str], symbol: str) -> float:
    normalized_entities = [e.lower() for e in entities]
    weights = [
        ENTITY_RELEVANCE[entity][symbol]
        for entity in normalized_entities
        if entity in ENTITY_RELEVANCE and symbol in ENTITY_RELEVANCE[entity]
    ]
    if weights:
        return max(weights)

    inst = get_instrument(symbol)
    if inst and inst.asset_class == AssetClass.CRYPTO and "crypto" in normalized_entities:
        return 0.6
    return ASSET_CLASS_BASELINE_RELEVANCE
