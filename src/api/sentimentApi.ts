import { useQuery } from "@tanstack/react-query";
import type { SymbolSentiment } from "@/types";
import { apiFetch, IS_DEMO_MODE, simulateLatency } from "./client";
import { getMockAggregateSentiment, getMockSentiment } from "@/mocks/sentiment";

async function fetchSentiment(symbol: string): Promise<SymbolSentiment> {
  if (IS_DEMO_MODE) return simulateLatency(getMockSentiment(symbol));
  return apiFetch<SymbolSentiment>(`/sentiment/${symbol}`);
}

async function fetchAggregateSentiment(): Promise<SymbolSentiment> {
  if (IS_DEMO_MODE) return simulateLatency(getMockAggregateSentiment());
  return apiFetch<SymbolSentiment>("/sentiment/market");
}

export function useSentiment(symbol: string) {
  return useQuery({
    queryKey: ["sentiment", symbol],
    queryFn: () => fetchSentiment(symbol),
    enabled: Boolean(symbol),
  });
}

export function useAggregateSentiment() {
  return useQuery({ queryKey: ["sentiment-market"], queryFn: fetchAggregateSentiment });
}
