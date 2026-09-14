import type { AlertItem, AlertType } from "@/types";
import { INSTRUMENTS } from "./instruments";
import { pick, randRange, seededFrom } from "./seed";

/** DEMO DATA — synthetic alert stream for local development only. */

const ALERT_TEMPLATES: Record<AlertType, (symbol: string) => string> = {
  "new-signal": (s) => `A new trade signal was generated for ${s}.`,
  "confidence-up": (s) => `Signal confidence on ${s} increased following updated momentum data.`,
  "confidence-down": (s) => `Signal confidence on ${s} decreased as trend structure weakened.`,
  "entry-zone": (s) => `${s} has reached its proposed entry zone.`,
  "risk-change": (s) => `Risk conditions for ${s} shifted; position sizing guidance updated.`,
  "sentiment-change": (s) => `Aggregated sentiment on ${s} moved to a new state.`,
  "backtest-complete": (s) => `Backtest for ${s} finished running.`,
};

const TITLES: Record<AlertType, string> = {
  "new-signal": "New signal",
  "confidence-up": "Confidence increased",
  "confidence-down": "Confidence decreased",
  "entry-zone": "Entry zone reached",
  "risk-change": "Risk condition changed",
  "sentiment-change": "Sentiment changed",
  "backtest-complete": "Backtest completed",
};

export function getMockAlerts(count = 9): AlertItem[] {
  const rand = seededFrom("alerts-feed");
  const types = Object.keys(ALERT_TEMPLATES) as AlertType[];

  return Array.from({ length: count }).map((_, i) => {
    const type = pick(rand, types);
    const symbol = pick(rand, INSTRUMENTS).symbol;
    return {
      id: `alert-${i}`,
      type,
      title: TITLES[type],
      description: ALERT_TEMPLATES[type](symbol),
      symbol,
      createdAt: new Date(Date.now() - randRange(rand, 2, 600) * 60 * 1000).toISOString(),
      read: i > 2,
    };
  });
}
