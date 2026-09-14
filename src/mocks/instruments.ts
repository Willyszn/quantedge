import type { AssetClass } from "@/types";

export interface InstrumentDef {
  symbol: string;
  name: string;
  assetClass: AssetClass;
  basePrice: number;
  decimals: number;
}

export const INSTRUMENTS: InstrumentDef[] = [
  { symbol: "GBPUSD", name: "British Pound / US Dollar", assetClass: "forex", basePrice: 1.3452, decimals: 4 },
  { symbol: "USDJPY", name: "US Dollar / Japanese Yen", assetClass: "forex", basePrice: 149.82, decimals: 2 },
  { symbol: "EURUSD", name: "Euro / US Dollar", assetClass: "forex", basePrice: 1.0812, decimals: 4 },
  { symbol: "GBPJPY", name: "British Pound / Japanese Yen", assetClass: "forex", basePrice: 201.45, decimals: 2 },
  { symbol: "XAUUSD", name: "Gold Spot / US Dollar", assetClass: "metals", basePrice: 2419.6, decimals: 2 },
  { symbol: "XAGUSD", name: "Silver Spot / US Dollar", assetClass: "metals", basePrice: 28.94, decimals: 2 },
  { symbol: "US500", name: "S&P 500 Index", assetClass: "index", basePrice: 5614.3, decimals: 1 },
  { symbol: "US100", name: "Nasdaq 100 Index", assetClass: "index", basePrice: 19842.0, decimals: 1 },
  { symbol: "BTCUSD", name: "Bitcoin / US Dollar", assetClass: "crypto", basePrice: 64230.0, decimals: 1 },
  { symbol: "ETHUSD", name: "Ethereum / US Dollar", assetClass: "crypto", basePrice: 3142.5, decimals: 1 },
];

export function getInstrument(symbol: string): InstrumentDef {
  const found = INSTRUMENTS.find((i) => i.symbol === symbol);
  if (!found) throw new Error(`Unknown instrument: ${symbol}`);
  return found;
}
