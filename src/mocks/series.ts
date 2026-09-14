import type { Candle, MarketCapabilities, MarketSeries, Timeframe } from "@/types";
import { getInstrument } from "./instruments";
import { randRange, seededFrom } from "./seed";

/** DEMO DATA — synthetic OHLC candles for local development only. */

const TIMEFRAME_MINUTES: Record<Timeframe, number> = {
  "1m": 1,
  "5m": 5,
  "15m": 15,
  "1H": 60,
  "4H": 240,
  "1D": 1440,
};

// In a real deployment, this comes from the backend's /capabilities
// endpoint per symbol. Only timeframes reported here should render as
// selectable chart controls.
const SUPPORTED_TIMEFRAMES: Record<string, Timeframe[]> = {
  GBPUSD: ["5m", "15m", "1H", "4H", "1D"],
  USDJPY: ["5m", "15m", "1H", "4H", "1D"],
  EURUSD: ["1m", "5m", "15m", "1H", "4H", "1D"],
  GBPJPY: ["5m", "15m", "1H", "4H", "1D"],
  XAUUSD: ["1m", "5m", "15m", "1H", "4H", "1D"],
  XAGUSD: ["15m", "1H", "4H", "1D"],
  US500: ["5m", "15m", "1H", "4H", "1D"],
  US100: ["5m", "15m", "1H", "4H", "1D"],
  BTCUSD: ["1m", "5m", "15m", "1H", "4H", "1D"],
  ETHUSD: ["5m", "15m", "1H", "4H", "1D"],
};

export function getMarketCapabilities(symbol: string): MarketCapabilities {
  return { supportedTimeframes: SUPPORTED_TIMEFRAMES[symbol] ?? ["1H", "4H", "1D"] };
}

export function getMockSeries(symbol: string, timeframe: Timeframe, count = 140): MarketSeries {
  const inst = getInstrument(symbol);
  const rand = seededFrom(`${symbol}-${timeframe}-series`);
  const minutes = TIMEFRAME_MINUTES[timeframe];
  const candles: Candle[] = [];

  let price = inst.basePrice * randRange(rand, 0.97, 1.03);
  const now = Date.now();

  for (let i = count - 1; i >= 0; i--) {
    const drift = randRange(rand, -0.0025, 0.0027);
    const open = price;
    const close = open * (1 + drift);
    const high = Math.max(open, close) * (1 + randRange(rand, 0, 0.0012));
    const low = Math.min(open, close) * (1 - randRange(rand, 0, 0.0012));
    const volume = Math.round(randRange(rand, 800, 6200));
    const time = new Date(now - i * minutes * 60 * 1000).toISOString();

    candles.push({
      time,
      open: Number(open.toFixed(inst.decimals)),
      high: Number(high.toFixed(inst.decimals)),
      low: Number(low.toFixed(inst.decimals)),
      close: Number(close.toFixed(inst.decimals)),
      volume,
    });

    price = close;
  }

  return { symbol, timeframe, candles };
}
