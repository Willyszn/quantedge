import type { AssetClass, MarketQuote, MarketStatus } from "@/types";
import { INSTRUMENTS } from "./instruments";
import { randRange, seededFrom } from "./seed";

/**
 * DEMO DATA — generated locally for development only.
 * This is never a substitute for a live market feed.
 */

// FX/metals trade nearly continuously: open from Sunday 22:00 UTC (Sydney
// open) through Friday 22:00 UTC (NY close), closed on the weekend gap.
// Every forex/metals instrument shares this same check, so they can never
// contradict each other (e.g. USDJPY "closed" while GBPUSD "open").
function isFxSessionOpen(now: Date): boolean {
  const day = now.getUTCDay(); // 0 = Sunday, 6 = Saturday
  const hour = now.getUTCHours();
  if (day === 6) return false; // all Saturday
  if (day === 0) return hour >= 22; // Sunday, after 22:00 UTC
  if (day === 5) return hour < 22; // Friday, before 22:00 UTC
  return true; // Mon-Thu
}

// Index CFDs roughly track the underlying cash market's day: a pre-market
// window ahead of the US open, a regular session, then closed overnight.
function indexStatus(now: Date): MarketStatus {
  const day = now.getUTCDay();
  if (day === 0 || day === 6) return "closed";
  const hour = now.getUTCHours();
  if (hour >= 8 && hour < 13) return "pre-market";
  if (hour >= 13 && hour < 21) return "open";
  return "closed";
}

function statusFor(assetClass: AssetClass, now: Date): MarketStatus {
  if (assetClass === "crypto") return "open";
  if (assetClass === "index") return indexStatus(now);
  return isFxSessionOpen(now) ? "open" : "closed"; // forex, metals
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
  const now = new Date();
  return INSTRUMENTS.map((inst) => {
    const rand = seededFrom(`${inst.symbol}-quote-${now.toDateString()}`);
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
      status: statusFor(inst.assetClass, now),
      spark: buildSpark(rand, inst.basePrice),
      updatedAt: now.toISOString(),
    };
  });
}

export function getMockMarketQuote(symbol: string): MarketQuote | undefined {
  return getMockMarketQuotes().find((q) => q.symbol === symbol);
}
