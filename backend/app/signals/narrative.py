"""
Signal narrative (spec section 21). Built entirely from the already-computed
factors — this function has no access to anything an LLM could hallucinate
from; it's string templates over real numbers. An LLM could later be layered
on top purely as a *presentation* rewrite of this same factual content, but
it would never be the source of the underlying claims.
"""

from app.signals.factors import SignalFactor


def _find(factors: list[SignalFactor], factor_id: str) -> SignalFactor | None:
    return next((f for f in factors if f.id == factor_id), None)


def build_narrative(symbol: str, direction: str, factors: list[SignalFactor]) -> str:
    momentum = _find(factors, "momentum")
    trend = _find(factors, "trend")
    sentiment = _find(factors, "sentiment-factor")
    risk = _find(factors, "risk-conditions")

    dir_word = "upside" if direction == "long" else "downside"
    article = "an" if direction == "long" else "a"

    supporting = [f for f in factors if f.status == "favorable"]
    weakening = [f for f in factors if f.status == "unfavorable"]

    # 1) What the market is doing + 2) why the signal exists
    parts = [
        f"{symbol} shows {trend.status_label.lower() if trend else 'mixed'} trend structure "
        f"with {momentum.status_label.lower() if momentum else 'unclear'} momentum, "
        f"giving the quantitative engine a basis for {article} {dir_word} read."
    ]

    # 3) What supports the setup
    if supporting:
        supporting_labels = ", ".join(f.label.lower() for f in supporting)
        parts.append(f"Supporting factors: {supporting_labels}.")
    else:
        parts.append("No factor currently scores as strongly favorable — conviction is limited.")

    # 4) What weakens the setup
    if weakening:
        weakening_labels = ", ".join(f.label.lower() for f in weakening)
        parts.append(f"Weighing against the setup: {weakening_labels}.")
    elif sentiment and sentiment.status == "neutral":
        parts.append("Sentiment is balanced rather than strongly aligned, which tempers conviction.")

    # 5) Primary risk
    if risk:
        parts.append(f"Primary risk: {risk.explanation[0].lower()}{risk.explanation[1:]}")

    return " ".join(parts)
