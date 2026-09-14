import { useQuery } from "@tanstack/react-query";
import type { TradeSignal } from "@/types";
import { apiFetch, IS_DEMO_MODE, simulateLatency } from "./client";
import { getLivePrimarySignal, getLiveSignal, getLiveSignals } from "@/mocks/liveState";

async function fetchSignals(): Promise<TradeSignal[]> {
  if (IS_DEMO_MODE) return simulateLatency(getLiveSignals());
  return apiFetch<TradeSignal[]>("/signals");
}

async function fetchSignal(symbol: string): Promise<TradeSignal | undefined> {
  if (IS_DEMO_MODE) return simulateLatency(getLiveSignal(symbol));
  return apiFetch<TradeSignal>(`/signals/${symbol}`);
}

async function fetchPrimarySignal(): Promise<TradeSignal> {
  if (IS_DEMO_MODE) return simulateLatency(getLivePrimarySignal());
  return apiFetch<TradeSignal>("/signals/primary");
}

export function useSignals() {
  return useQuery({ queryKey: ["signals"], queryFn: fetchSignals, refetchInterval: 30000 });
}

export function useSignal(symbol: string) {
  return useQuery({
    queryKey: ["signal", symbol],
    queryFn: () => fetchSignal(symbol),
    enabled: Boolean(symbol),
  });
}

export function usePrimarySignal() {
  return useQuery({ queryKey: ["signal-primary"], queryFn: fetchPrimarySignal, refetchInterval: 30000 });
}
