import type { MarketQuote, SignalFactor, TradeSignal } from "@/types";
import { getInstrument } from "./instruments";
import { getMockMarketQuotes } from "./markets";
import { FACTOR_DEFS, factorStatus, getMockSignals, narrativeFor, ratingFor } from "./signals";

/**
 * DEMO DATA — this module holds the single in-memory copy of "live" quotes
 * and signals that the app reads from in demo mode.
 *
 * The initial values are the same deterministic, seeded data as before (see
 * mocks/markets.ts and mocks/signals.ts), so a fresh page load is always
 * stable. What's new is `driftMarketQuotes()` / `driftSignals()`: small,
 * controlled, one-directional-at-a-time nudges that `useAlertEngine` calls
 * on an interval so there's something for confidence/entry-zone/risk alerts
 * to actually react to. Nothing here is presented as real market data — the
 * DEMO DATA badge in the top bar covers this state too.
 */

let quotesState: MarketQuote[] | null = null;
let signalsState: TradeSignal[] | null = null;

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

export function getLiveMarketQuotes(): MarketQuote[] {
  if (!quotesState) quotesState = getMockMarketQuotes();
  return quotesState;
}

export function getLiveMarketQuote(symbol: string): MarketQuote | undefined {
  return getLiveMarketQuotes().find((q) => q.symbol === symbol);
}

export function getLiveSignals(): TradeSignal[] {
  if (!signalsState) signalsState = getMockSignals();
  return signalsState;
}

export function getLiveSignal(symbol: string): TradeSignal | undefined {
  return getLiveSignals().find((s) => s.symbol === symbol);
}

export function getLivePrimarySignal(): TradeSignal {
  return getLiveSignals().slice().sort((a, b) => b.confidence - a.confidence)[0];
}

function driftQuote(quote: MarketQuote): MarketQuote {
  const inst = getInstrument(quote.symbol);
  const pctMove = (Math.random() - 0.5) * 0.22; // small step, roughly balanced
  const price = Number((quote.price * (1 + pctMove / 100)).toFixed(inst.decimals));
  const changePercent = Number((((price - inst.basePrice) / inst.basePrice) * 100).toFixed(2));
  const changeAbsolute = Number((price - inst.basePrice).toFixed(inst.decimals));
  const spark = [...quote.spark.slice(1), price];
  return { ...quote, price, changePercent, changeAbsolute, spark, updatedAt: new Date().toISOString() };
}

export function driftMarketQuotes(): MarketQuote[] {
  quotesState = getLiveMarketQuotes().map(driftQuote);
  return quotesState;
}

function driftSignal(signal: TradeSignal): TradeSignal {
  // Nudge exactly one factor per tick so a person can trace *why* a
  // confidence change happened, rather than every number moving at once.
  const idx = Math.floor(Math.random() * signal.factors.length);
  const target = signal.factors[idx];
  const def = FACTOR_DEFS.find((d) => d.id === target.id)!;
  const delta = (Math.random() - 0.5) * 16; // -8..+8
  const newScore = Math.round(clamp(target.score + delta, 8, 97));
  const status = factorStatus(newScore);
  const [statusLabel, explanation] = def[status];

  const factors: SignalFactor[] = signal.factors.map((f, i) =>
    i === idx ? { ...f, score: newScore, status, statusLabel, explanation } : f
  );

  const avgFactorScore = Math.round(factors.reduce((s, f) => s + f.score, 0) / factors.length);
  const noise = (Math.random() - 0.5) * 5;
  const confidence = Math.round(clamp(avgFactorScore + noise, 12, 98));
  const rating = ratingFor(confidence, signal.direction);

  const momentum = factors.find((f) => f.id === "momentum")!.score;
  const trend = factors.find((f) => f.id === "trend")!.score;
  const sentimentScore = factors.find((f) => f.id === "sentiment-factor")!.score;
  const riskScore = factors.find((f) => f.id === "risk-conditions")!.score;

  return {
    ...signal,
    factors,
    confidence,
    rating,
    scores: { quant: avgFactorScore, momentum, trend, sentiment: sentimentScore, risk: riskScore },
    narrative: narrativeFor(signal.symbol, signal.direction, factors),
  };
}

export function driftSignals(): TradeSignal[] {
  signalsState = getLiveSignals().map(driftSignal);
  return signalsState;
}
