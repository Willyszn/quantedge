import type { SentimentLabel, SentimentSource, SentimentSourceType, SymbolSentiment } from "@/types";
import { INSTRUMENTS } from "./instruments";
import { randRange, seededFrom } from "./seed";

/** DEMO DATA — synthetic sentiment readings for local development only. */

const SOURCE_DEFS: { type: SentimentSourceType; label: string }[] = [
  { type: "news", label: "Financial News" },
  { type: "commentary", label: "Market Commentary" },
  { type: "social", label: "Social Sentiment" },
  { type: "macro", label: "Macro Sentiment" },
];

function labelFromScore(score: number): SentimentLabel {
  if (score >= 75) return "strong-positive";
  if (score >= 58) return "positive";
  if (score >= 42) return "neutral";
  if (score >= 25) return "negative";
  return "strong-negative";
}

function buildSources(rand: () => number): SentimentSource[] {
  return SOURCE_DEFS.map((def, i) => {
    const score = Math.round(randRange(rand, 20, 90));
    return {
      id: `src-${def.type}`,
      type: def.type,
      label: def.label,
      sentiment: labelFromScore(score),
      confidence: Math.round(randRange(rand, 55, 95)),
      contributionPercent: [40, 25, 20, 15][i],
      updatedAt: new Date(Date.now() - randRange(rand, 5, 180) * 60 * 1000).toISOString(),
    };
  });
}

function buildTimeline(rand: () => number) {
  const hours = [9, 11, 13, 15, 17];
  let score = randRange(rand, 40, 60);
  return hours.map((h) => {
    score = Math.min(92, Math.max(12, score + randRange(rand, -10, 14)));
    return {
      time: `${h.toString().padStart(2, "0")}:00`,
      label: labelFromScore(score),
      score: Math.round(score),
    };
  });
}

export function getMockSentiment(symbol: string): SymbolSentiment {
  const rand = seededFrom(`${symbol}-sentiment-${new Date().toDateString()}`);
  const bullish = Math.round(randRange(rand, 45, 80));
  const bearish = Math.round(randRange(rand, 5, 100 - bullish - 5));
  const neutral = 100 - bullish - bearish;

  return {
    symbol,
    split: { bullish, neutral, bearish },
    sources: buildSources(rand),
    timeline: buildTimeline(rand),
  };
}

export function getMockAggregateSentiment(): SymbolSentiment {
  return getMockSentiment("MARKET");
}

export function getSentimentSymbols(): string[] {
  return INSTRUMENTS.map((i) => i.symbol);
}
