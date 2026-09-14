import type { BacktestConfig, BacktestResult, BacktestTrade, EquityPoint } from "@/types";
import { getInstrument } from "./instruments";
import { pick, randRange, seededFrom } from "./seed";

/** DEMO DATA — synthetic backtest results for local development only. */

export const STRATEGIES = [
  "Momentum Breakout",
  "Trend Continuation",
  "Mean Reversion",
  "Sentiment Confluence",
];

function buildTrades(rand: () => number, symbol: string, count: number, decimals: number): BacktestTrade[] {
  const trades: BacktestTrade[] = [];
  const cursor = new Date();
  cursor.setDate(cursor.getDate() - count * 3);

  for (let i = 0; i < count; i++) {
    const direction = pick(rand, ["long", "short"] as const);
    const win = rand() < 0.56;
    const rMultiple = win ? Number(randRange(rand, 0.4, 3.2).toFixed(2)) : Number(randRange(rand, -1.2, -0.2).toFixed(2));
    const entryPrice = Number(randRange(rand, 0.9, 1.1).toFixed(decimals));
    const exitPrice = Number((entryPrice * (1 + rMultiple * 0.01)).toFixed(decimals));
    const entryDate = new Date(cursor);
    cursor.setDate(cursor.getDate() + Math.round(randRange(rand, 1, 4)));
    const exitDate = new Date(cursor);

    trades.push({
      id: `bt-trade-${i}`,
      symbol,
      direction,
      entryDate: entryDate.toISOString(),
      exitDate: exitDate.toISOString(),
      entryPrice,
      exitPrice,
      rMultiple,
      outcome: rMultiple > 0.05 ? "win" : rMultiple < -0.05 ? "loss" : "breakeven",
      pnlPercent: Number((rMultiple * 0.8).toFixed(2)),
    });
  }
  return trades;
}

function buildEquityCurve(rand: () => number, trades: BacktestTrade[], initialCapital: number): EquityPoint[] {
  let equity = initialCapital;
  let peak = initialCapital;
  return trades.map((t) => {
    equity = equity * (1 + t.pnlPercent / 100);
    peak = Math.max(peak, equity);
    const drawdownPercent = Number((((equity - peak) / peak) * 100).toFixed(2));
    return { date: t.exitDate, equity: Number(equity.toFixed(2)), drawdownPercent };
  });
}

function buildMonthlyReturns(rand: () => number) {
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return months.map((month) => ({ month, returnPercent: Number(randRange(rand, -4.5, 6.5).toFixed(2)) }));
}

export function runMockBacktest(config: BacktestConfig): BacktestResult {
  const inst = getInstrument(config.symbol);
  const rand = seededFrom(`${config.symbol}-${config.strategy}-${config.startDate}-${config.endDate}`);
  const tradeCount = Math.round(randRange(rand, 40, 140));
  const trades = buildTrades(rand, config.symbol, tradeCount, inst.decimals);
  const equityCurve = buildEquityCurve(rand, trades, config.initialCapital);

  const wins = trades.filter((t) => t.outcome === "win");
  const losses = trades.filter((t) => t.outcome === "loss");
  const grossWin = wins.reduce((s, t) => s + Math.abs(t.pnlPercent), 0);
  const grossLoss = losses.reduce((s, t) => s + Math.abs(t.pnlPercent), 0) || 1;
  const finalEquity = equityCurve[equityCurve.length - 1]?.equity ?? config.initialCapital;

  return {
    id: `bt-${Date.now()}`,
    config,
    totalReturnPercent: Number((((finalEquity - config.initialCapital) / config.initialCapital) * 100).toFixed(2)),
    winRate: Number(((wins.length / trades.length) * 100).toFixed(1)),
    profitFactor: Number((grossWin / grossLoss).toFixed(2)),
    maxDrawdownPercent: Math.min(...equityCurve.map((e) => e.drawdownPercent)),
    sharpeLike: Number(randRange(rand, 0.6, 2.1).toFixed(2)),
    totalTrades: trades.length,
    averageTradePercent: Number((trades.reduce((s, t) => s + t.pnlPercent, 0) / trades.length).toFixed(2)),
    expectancy: Number((trades.reduce((s, t) => s + t.rMultiple, 0) / trades.length).toFixed(2)),
    equityCurve,
    monthlyReturns: buildMonthlyReturns(rand),
    trades,
    completedAt: new Date().toISOString(),
  };
}
