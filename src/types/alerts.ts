export type AlertType =
  | "new-signal"
  | "confidence-up"
  | "confidence-down"
  | "entry-zone"
  | "risk-change"
  | "sentiment-change"
  | "backtest-complete";

export interface AlertItem {
  id: string;
  type: AlertType;
  title: string;
  description: string;
  symbol?: string;
  createdAt: string;
  read: boolean;
}

export interface WatchlistItem {
  symbol: string;
  addedAt: string;
}
