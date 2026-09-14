export type MarketStatus = "open" | "closed" | "pre-market" | "after-hours";

export type AssetClass = "forex" | "metals" | "index" | "crypto";

export interface MarketQuote {
  symbol: string;
  name: string;
  assetClass: AssetClass;
  price: number;
  changePercent: number;
  changeAbsolute: number;
  status: MarketStatus;
  /** Recent closes used to render a sparkline. Oldest first. */
  spark: number[];
  updatedAt: string;
}

export type Timeframe = "1m" | "5m" | "15m" | "1H" | "4H" | "1D";

export interface Candle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface MarketSeries {
  symbol: string;
  timeframe: Timeframe;
  candles: Candle[];
}

export interface MarketCapabilities {
  /** Timeframes the connected backend actually supports for a given symbol. */
  supportedTimeframes: Timeframe[];
}
