import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { TrendingDown, TrendingUp, Target, ShieldAlert } from "lucide-react";
import { IS_DEMO_MODE } from "@/api/client";
import { driftMarketQuotes, driftSignals, getLiveMarketQuotes, getLiveSignals } from "@/mocks/liveState";
import type { AlertItem, AlertType, FactorStatus, MarketQuote, TradeSignal } from "@/types";

const TICK_MS = 16_000;
const CONFIDENCE_ALERT_THRESHOLD = 6;

interface SignalSnapshot {
  confidence: number;
  inEntryZone: boolean;
  riskStatus: FactorStatus;
}

function buildSnapshot(signal: TradeSignal, quote: MarketQuote | undefined): SignalSnapshot {
  const inEntryZone = Boolean(quote) && quote!.price >= signal.entryLow && quote!.price <= signal.entryHigh;
  const riskStatus = signal.factors.find((f) => f.id === "risk-conditions")?.status ?? "neutral";
  return { confidence: signal.confidence, inEntryZone, riskStatus };
}

/**
 * Runs once for the lifetime of the app (mounted from AppShell). On each
 * tick it nudges the in-memory demo data (mocks/liveState.ts) and compares
 * the new state against the previous snapshot per symbol — when confidence
 * moves meaningfully, price enters a signal's entry zone, or risk
 * conditions shift tier, it raises a toast and prepends an entry to the
 * alerts panel. Only runs in demo mode; a live backend would push real
 * alerts instead of this client-side simulation.
 */
export function useAlertEngine() {
  const queryClient = useQueryClient();
  const snapshotsRef = useRef<Map<string, SignalSnapshot>>(new Map());

  useEffect(() => {
    if (!IS_DEMO_MODE) return;

    // Establish a baseline without alerting, so the very first tick after
    // mount doesn't fire spurious "changes" from nothing.
    const baseline = new Map<string, SignalSnapshot>();
    const initialSignals = getLiveSignals();
    const initialQuotes = getLiveMarketQuotes();
    initialSignals.forEach((signal) => {
      const quote = initialQuotes.find((q) => q.symbol === signal.symbol);
      baseline.set(signal.symbol, buildSnapshot(signal, quote));
    });
    snapshotsRef.current = baseline;

    const interval = setInterval(() => {
      const quotes = driftMarketQuotes();
      const signals = driftSignals();

      queryClient.setQueryData<MarketQuote[]>(["market-quotes"], quotes);
      queryClient.setQueryData<TradeSignal[]>(["signals"], signals);
      quotes.forEach((q) => queryClient.setQueryData<MarketQuote>(["market-quote", q.symbol], q));
      signals.forEach((s) => queryClient.setQueryData<TradeSignal>(["signal", s.symbol], s));
      const topSignal = signals.slice().sort((a, b) => b.confidence - a.confidence)[0];
      if (topSignal) queryClient.setQueryData<TradeSignal>(["signal-primary"], topSignal);

      const previous = snapshotsRef.current;
      const next = new Map<string, SignalSnapshot>();

      signals.forEach((signal) => {
        const quote = quotes.find((q) => q.symbol === signal.symbol);
        const snapshot = buildSnapshot(signal, quote);
        next.set(signal.symbol, snapshot);

        const prevSnapshot = previous.get(signal.symbol);
        if (!prevSnapshot) return;

        const confidenceDelta = snapshot.confidence - prevSnapshot.confidence;
        if (Math.abs(confidenceDelta) >= CONFIDENCE_ALERT_THRESHOLD) {
          const up = confidenceDelta > 0;
          raiseAlert(queryClient, {
            type: up ? "confidence-up" : "confidence-down",
            title: up ? "Confidence increased" : "Confidence decreased",
            description: `${signal.symbol} signal confidence ${up ? "rose" : "fell"} to ${snapshot.confidence}%.`,
            symbol: signal.symbol,
          });
          if (up) {
            toast.success(`${signal.symbol} confidence rose to ${snapshot.confidence}%`, {
              icon: <TrendingUp className="h-4 w-4" />,
            });
          } else {
            toast(`${signal.symbol} confidence fell to ${snapshot.confidence}%`, {
              icon: <TrendingDown className="h-4 w-4" />,
            });
          }
        }

        if (snapshot.inEntryZone && !prevSnapshot.inEntryZone) {
          raiseAlert(queryClient, {
            type: "entry-zone",
            title: "Entry zone reached",
            description: `${signal.symbol} has reached its proposed entry zone.`,
            symbol: signal.symbol,
          });
          toast(`${signal.symbol} reached its entry zone`, { icon: <Target className="h-4 w-4" /> });
        }

        if (snapshot.riskStatus !== prevSnapshot.riskStatus) {
          raiseAlert(queryClient, {
            type: "risk-change",
            title: "Risk condition changed",
            description: `Risk conditions for ${signal.symbol} shifted to ${snapshot.riskStatus}.`,
            symbol: signal.symbol,
          });
          toast(`${signal.symbol} risk conditions shifted`, { icon: <ShieldAlert className="h-4 w-4" /> });
        }
      });

      snapshotsRef.current = next;
    }, TICK_MS);

    return () => clearInterval(interval);
  }, [queryClient]);
}

function raiseAlert(
  queryClient: ReturnType<typeof useQueryClient>,
  partial: { type: AlertType; title: string; description: string; symbol: string }
) {
  const alert: AlertItem = {
    id: `live-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    createdAt: new Date().toISOString(),
    read: false,
    ...partial,
  };
  queryClient.setQueryData<AlertItem[]>(["alerts"], (old) => [alert, ...(old ?? [])].slice(0, 30));
}
