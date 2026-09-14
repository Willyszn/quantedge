import type { BacktestTrade } from "@/types";
import { INSTRUMENTS } from "./instruments";
import { pick, randRange, seededFrom } from "./seed";

/** DEMO DATA — synthetic executed-trade history for local development only. */

export function getMockTradeHistory(count = 48): BacktestTrade[] {
  const rand = seededFrom("trade-history");
  const trades: BacktestTrade[] = [];
  const cursor = new Date();
  cursor.setDate(cursor.getDate() - count * 2);

  for (let i = 0; i < count; i++) {
    const inst = pick(rand, INSTRUMENTS);
    const direction = pick(rand, ["long", "short"] as const);
    const win = rand() < 0.57;
    const rMultiple = win ? Number(randRange(rand, 0.3, 3.4).toFixed(2)) : Number(randRange(rand, -1.3, -0.15).toFixed(2));
    const entryPrice = Number((inst.basePrice * randRange(rand, 0.96, 1.04)).toFixed(inst.decimals));
    const exitPrice = Number((entryPrice * (1 + rMultiple * 0.01)).toFixed(inst.decimals));
    const entryDate = new Date(cursor);
    cursor.setDate(cursor.getDate() + Math.round(randRange(rand, 1, 3)));
    const exitDate = new Date(cursor);

    trades.push({
      id: `hist-${i}`,
      symbol: inst.symbol,
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

  return trades.reverse();
}
