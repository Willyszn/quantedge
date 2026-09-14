import type {
  FactorStatus,
  SignalDirection,
  SignalFactor,
  SignalRating,
  TradeSignal,
} from "@/types";
import { INSTRUMENTS } from "./instruments";
import { pick, randRange, seededFrom } from "./seed";

/** DEMO DATA — synthetic signals for local development only. */

export function ratingFor(confidence: number, direction: SignalDirection): SignalRating {
  if (direction === "long") {
    if (confidence >= 78) return "strong-buy";
    if (confidence >= 60) return "buy";
    if (confidence >= 45) return "neutral";
    return "sell";
  }
  if (confidence >= 78) return "strong-sell";
  if (confidence >= 60) return "sell";
  if (confidence >= 45) return "neutral";
  return "buy";
}

export function factorStatus(score: number): FactorStatus {
  if (score >= 66) return "favorable";
  if (score >= 40) return "neutral";
  return "unfavorable";
}

export interface FactorDef {
  id: string;
  label: string;
  favorable: [string, string];
  neutral: [string, string];
  unfavorable: [string, string];
}

export const FACTOR_DEFS: FactorDef[] = [
  {
    id: "momentum",
    label: "Quantitative Momentum",
    favorable: ["Strong", "Rate of change is accelerating in the signal direction across recent bars."],
    neutral: ["Mixed", "Momentum readings are inconsistent across short and medium windows."],
    unfavorable: ["Weak", "Momentum is fading, reducing conviction in a continuation move."],
  },
  {
    id: "trend",
    label: "Trend Structure",
    favorable: ["Bullish", "Price is respecting the prevailing structure with clean higher highs and lows."],
    neutral: ["Transitional", "Structure is consolidating without a clearly dominant trend."],
    unfavorable: ["Bearish", "Structure is working against the proposed trade direction."],
  },
  {
    id: "volatility",
    label: "Volatility",
    favorable: ["Favorable", "Volatility is stable enough to support a defined stop and target."],
    neutral: ["Elevated", "Volatility is above average, widening realistic outcomes."],
    unfavorable: ["Erratic", "Volatility is unstable, making stop placement less reliable."],
  },
  {
    id: "sentiment-factor",
    label: "Sentiment",
    favorable: ["Positive", "Aggregated sentiment leans supportive without appearing crowded."],
    neutral: ["Balanced", "Sentiment sources are split without a clear lean."],
    unfavorable: ["Negative", "Sentiment is leaning against the proposed direction."],
  },
  {
    id: "risk-conditions",
    label: "Risk Conditions",
    favorable: ["Acceptable", "Stop distance and expected risk/reward remain within acceptable bounds."],
    neutral: ["Watch", "Risk conditions are workable but warrant a smaller position size."],
    unfavorable: ["Elevated", "Risk conditions currently argue for reduced size or standing aside."],
  },
];

function buildFactors(rand: () => number): SignalFactor[] {
  return FACTOR_DEFS.map((def) => {
    const score = Math.round(randRange(rand, 32, 94));
    const status = factorStatus(score);
    const [statusLabel, explanation] = def[status];
    return { id: def.id, label: def.label, score, status, statusLabel, explanation };
  });
}

export function narrativeFor(symbol: string, direction: SignalDirection, factors: SignalFactor[]): string {
  const momentum = factors.find((f) => f.id === "momentum")!;
  const trend = factors.find((f) => f.id === "trend")!;
  const sentiment = factors.find((f) => f.id === "sentiment-factor")!;
  const dirWord = direction === "long" ? "upside" : "downside";
  return `${momentum.status === "favorable" ? "Momentum is strengthening" : "Momentum is mixed"} while the prevailing trend remains ${trend.statusLabel.toLowerCase()}. Sentiment on ${symbol} is ${sentiment.statusLabel.toLowerCase()}, which ${
    sentiment.status === "favorable" ? "supports further" : "adds uncertainty to"
  } ${dirWord} continuation without signs of an extreme, crowded positioning.`;
}

export function getMockSignals(): TradeSignal[] {
  return INSTRUMENTS.map((inst) => {
    const rand = seededFrom(`${inst.symbol}-signal-${new Date().toDateString()}`);
    const direction: SignalDirection = pick(rand, ["long", "short"] as const);
    const factors = buildFactors(rand);
    const avgFactorScore = Math.round(factors.reduce((s, f) => s + f.score, 0) / factors.length);
    const confidence = Math.min(96, Math.max(28, avgFactorScore + Math.round(randRange(rand, -6, 6))));

    const entrySpread = inst.basePrice * 0.0011;
    const entryMid = inst.basePrice * (1 + randRange(rand, -0.004, 0.004));
    const entryLow = Number((entryMid - entrySpread).toFixed(inst.decimals));
    const entryHigh = Number((entryMid + entrySpread).toFixed(inst.decimals));

    const stopDistance = inst.basePrice * randRange(rand, 0.004, 0.009);
    const rr = Number(randRange(rand, 1.6, 3.1).toFixed(1));
    const targetDistance = stopDistance * rr;

    const stopLoss =
      direction === "long"
        ? Number((entryLow - stopDistance).toFixed(inst.decimals))
        : Number((entryHigh + stopDistance).toFixed(inst.decimals));
    const target =
      direction === "long"
        ? Number((entryHigh + targetDistance).toFixed(inst.decimals))
        : Number((entryLow - targetDistance).toFixed(inst.decimals));

    const momentum = factors.find((f) => f.id === "momentum")!.score;
    const trend = factors.find((f) => f.id === "trend")!.score;
    const sentimentScore = factors.find((f) => f.id === "sentiment-factor")!.score;
    const riskScore = factors.find((f) => f.id === "risk-conditions")!.score;

    return {
      id: `sig-${inst.symbol.toLowerCase()}`,
      symbol: inst.symbol,
      name: inst.name,
      direction,
      rating: ratingFor(confidence, direction),
      confidence,
      entryLow,
      entryHigh,
      stopLoss,
      target,
      riskRewardRatio: rr,
      generatedAt: new Date(Date.now() - randRange(rand, 5, 240) * 60 * 1000).toISOString(),
      scores: {
        quant: avgFactorScore,
        momentum,
        trend,
        sentiment: sentimentScore,
        risk: riskScore,
      },
      factors,
      narrative: narrativeFor(inst.symbol, direction, factors),
      decimals: inst.decimals,
    };
  });
}

export function getMockSignal(symbol: string): TradeSignal | undefined {
  return getMockSignals().find((s) => s.symbol === symbol);
}

export function getMockPrimarySignal(): TradeSignal {
  const signals = getMockSignals().slice().sort((a, b) => b.confidence - a.confidence);
  return signals[0];
}
