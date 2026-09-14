export type SignalDirection = "long" | "short";

export type SignalStrength = "strong" | "moderate" | "weak";

export type FactorStatus = "favorable" | "neutral" | "unfavorable";

export interface SignalFactor {
  id: string;
  label: string;
  score: number; // 0-100
  status: FactorStatus;
  statusLabel: string;
  explanation: string;
}

export interface SignalScoreBreakdown {
  quant: number;
  momentum: number;
  trend: number;
  sentiment: number;
  risk: number;
}

export type SignalRating = "strong-buy" | "buy" | "neutral" | "sell" | "strong-sell";

export interface TradeSignal {
  id: string;
  symbol: string;
  name: string;
  direction: SignalDirection;
  rating: SignalRating;
  confidence: number; // 0-100
  entryLow: number;
  entryHigh: number;
  stopLoss: number;
  target: number;
  riskRewardRatio: number;
  generatedAt: string;
  scores: SignalScoreBreakdown;
  factors: SignalFactor[];
  narrative: string;
  decimals: number;
}
