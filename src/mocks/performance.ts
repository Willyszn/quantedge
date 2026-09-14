import type { EquityPoint, PerformanceBySlice, PerformanceMetrics } from "@/types";
import { INSTRUMENTS } from "./instruments";
import { randRange, seededFrom } from "./seed";

/** DEMO DATA — synthetic portfolio performance for local development only. */

export function getMockPerformanceMetrics(): PerformanceMetrics {
  const rand = seededFrom("performance-overview");
  return {
    totalReturnPercent: Number(randRange(rand, 8, 34).toFixed(1)),
    winRate: Number(randRange(rand, 48, 64).toFixed(1)),
    profitFactor: Number(randRange(rand, 1.2, 2.4).toFixed(2)),
    maxDrawdownPercent: -Number(randRange(rand, 4, 14).toFixed(1)),
    averageR: Number(randRange(rand, 0.2, 0.9).toFixed(2)),
    expectancy: Number(randRange(rand, 0.15, 0.6).toFixed(2)),
    bestTradePercent: Number(randRange(rand, 4, 11).toFixed(1)),
    worstTradePercent: -Number(randRange(rand, 2, 6).toFixed(1)),
  };
}

export function getMockPortfolioEquityCurve(): EquityPoint[] {
  const rand = seededFrom("performance-equity-curve");
  let equity = 100000;
  let peak = equity;
  const points: EquityPoint[] = [];
  const days = 180;
  const now = Date.now();

  for (let i = days; i >= 0; i--) {
    equity *= 1 + randRange(rand, -0.012, 0.017);
    peak = Math.max(peak, equity);
    points.push({
      date: new Date(now - i * 24 * 60 * 60 * 1000).toISOString(),
      equity: Number(equity.toFixed(2)),
      drawdownPercent: Number((((equity - peak) / peak) * 100).toFixed(2)),
    });
  }
  return points;
}

export function getPerformanceByInstrument(): PerformanceBySlice[] {
  const rand = seededFrom("performance-by-instrument");
  return INSTRUMENTS.map((inst) => ({
    label: inst.symbol,
    returnPercent: Number(randRange(rand, -6, 14).toFixed(1)),
    winRate: Number(randRange(rand, 40, 70).toFixed(0)),
    trades: Math.round(randRange(rand, 8, 60)),
  }));
}

export function getPerformanceBySignalType(): PerformanceBySlice[] {
  const rand = seededFrom("performance-by-signal-type");
  return ["Strong Buy", "Buy", "Neutral", "Sell", "Strong Sell"].map((label) => ({
    label,
    returnPercent: Number(randRange(rand, -5, 16).toFixed(1)),
    winRate: Number(randRange(rand, 38, 72).toFixed(0)),
    trades: Math.round(randRange(rand, 5, 45)),
  }));
}

export function getPerformanceByMonth(): PerformanceBySlice[] {
  const rand = seededFrom("performance-by-month");
  const months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"];
  return months.map((label) => ({
    label,
    returnPercent: Number(randRange(rand, -4, 9).toFixed(1)),
    winRate: Number(randRange(rand, 42, 68).toFixed(0)),
    trades: Math.round(randRange(rand, 10, 34)),
  }));
}

export function getPerformanceByRegime(): PerformanceBySlice[] {
  const rand = seededFrom("performance-by-regime");
  return ["Trending", "Ranging", "High Volatility", "Low Volatility"].map((label) => ({
    label,
    returnPercent: Number(randRange(rand, -5, 13).toFixed(1)),
    winRate: Number(randRange(rand, 40, 70).toFixed(0)),
    trades: Math.round(randRange(rand, 12, 50)),
  }));
}
