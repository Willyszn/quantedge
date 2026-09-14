import type { MarketQuote, MarketStatus } from "@/types";
import { INSTRUMENTS } from "./instruments";
import { randRange, seededFrom } from "./seed";

/**
 * DEMO DATA — generated locally for development only.
 * This is never a substitute for a live market feed.
 */
function statusFor(assetClass: string, rand: () => number): MarketStatus {
  if (assetClass === "crypto") return "open";
  const roll = rand();
  if (roll > 0.85) return "closed";
  if (roll > 0.75) return "pre-market";
  return "open";
}

function buildSpark(rand: () => number, base: number, points = 24): number[] {
  const spark: number[] = [];
  let value = base * randRange(rand, 0.985, 1.015);
  for (let i = 0; i < points; i++) {
    value += value * randRange(rand, -0.003, 0.0032);
    spark.push(Number(value.toFixed(5)));
  }
  return spark;
}

export function getMockMarketQuotes(): MarketQuote[] {
  return INSTRUMENTS.map((inst) => {
    const rand = seededFrom(`${inst.symbol}-quote-${new Date().toDateString()}`);
    const changePercent = Number(randRange(rand, -1.8, 1.8).toFixed(2));
    const price = Number((inst.basePrice * (1 + changePercent / 100)).toFixed(inst.decimals));
    const changeAbsolute = Number((price - inst.basePrice).toFixed(inst.decimals));

    return {
      symbol: inst.symbol,
      name: inst.name,
      assetClass: inst.assetClass,
      price,
      changePercent,
      changeAbsolute,
      status: statusFor(inst.assetClass, rand),
      spark: buildSpark(rand, inst.basePrice),
      updatedAt: new Date().toISOString(),
    };
  });
}

export function getMockMarketQuote(symbol: string): MarketQuote | undefined {
  return getMockMarketQuotes().find((q) => q.symbol === symbol);
}
