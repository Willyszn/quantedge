export interface RiskMetrics {
  riskScore: number; // 0-100, higher is safer
  expectedRiskReward: number;
  stopDistancePercent: number;
  positionRiskPercent: number;
  volatilityRegime: "low" | "normal" | "elevated" | "extreme";
}

export type TradeOutcome = "win" | "loss" | "breakeven";

export interface BacktestTrade {
  id: string;
  symbol: string;
  direction: "long" | "short";
  entryDate: string;
  exitDate: string;
  entryPrice: number;
  exitPrice: number;
  rMultiple: number;
  outcome: TradeOutcome;
  pnlPercent: number;
}

export interface EquityPoint {
  date: string;
  equity: number;
  drawdownPercent: number;
}

export interface BacktestConfig {
  symbol: string;
  strategy: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  riskPerTradePercent: number;
  slippageBps: number;
  commissionBps: number;
}

export interface BacktestResult {
  id: string;
  config: BacktestConfig;
  totalReturnPercent: number;
  winRate: number;
  profitFactor: number;
  maxDrawdownPercent: number;
  sharpeLike: number;
  totalTrades: number;
  averageTradePercent: number;
  expectancy: number;
  equityCurve: EquityPoint[];
  monthlyReturns: { month: string; returnPercent: number }[];
  trades: BacktestTrade[];
  completedAt: string;
}

export interface PerformanceMetrics {
  totalReturnPercent: number;
  winRate: number;
  profitFactor: number;
  maxDrawdownPercent: number;
  averageR: number;
  expectancy: number;
  bestTradePercent: number;
  worstTradePercent: number;
}

export interface PerformanceBySlice {
  label: string;
  returnPercent: number;
  winRate: number;
  trades: number;
}
