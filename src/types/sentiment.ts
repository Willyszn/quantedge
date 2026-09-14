export type SentimentLabel =
  | "strong-positive"
  | "positive"
  | "neutral"
  | "negative"
  | "strong-negative";

export interface SentimentSplit {
  bullish: number;
  neutral: number;
  bearish: number;
}

export type SentimentSourceType = "news" | "commentary" | "social" | "macro";

export interface SentimentSource {
  id: string;
  type: SentimentSourceType;
  label: string;
  sentiment: SentimentLabel;
  confidence: number;
  contributionPercent: number;
  updatedAt: string;
}

export interface SentimentTimelinePoint {
  time: string;
  label: SentimentLabel;
  score: number;
}

export interface SymbolSentiment {
  symbol: string;
  split: SentimentSplit;
  sources: SentimentSource[];
  timeline: SentimentTimelinePoint[];
}
