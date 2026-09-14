import { useQuery } from "@tanstack/react-query";
import type { MarketCapabilities, MarketQuote, MarketSeries, Timeframe } from "@/types";
import { apiFetch, IS_DEMO_MODE, simulateLatency } from "./client";
import { getLiveMarketQuote, getLiveMarketQuotes } from "@/mocks/liveState";
import { getMarketCapabilities, getMockSeries } from "@/mocks/series";

async function fetchMarketQuotes(): Promise<MarketQuote[]> {
  if (IS_DEMO_MODE) return simulateLatency(getLiveMarketQuotes());
  return apiFetch<MarketQuote[]>("/markets/quotes");
}

async function fetchMarketQuote(symbol: string): Promise<MarketQuote | undefined> {
  if (IS_DEMO_MODE) return simulateLatency(getLiveMarketQuote(symbol));
  return apiFetch<MarketQuote>(`/markets/quotes/${symbol}`);
}

async function fetchMarketSeries(symbol: string, timeframe: Timeframe): Promise<MarketSeries> {
  if (IS_DEMO_MODE) return simulateLatency(getMockSeries(symbol, timeframe), 300);
  return apiFetch<MarketSeries>(`/markets/${symbol}/series?timeframe=${timeframe}`);
}

async function fetchCapabilities(symbol: string): Promise<MarketCapabilities> {
  if (IS_DEMO_MODE) return simulateLatency(getMarketCapabilities(symbol), 150);
  return apiFetch<MarketCapabilities>(`/markets/${symbol}/capabilities`);
}

export function useMarketQuotes() {
  return useQuery({
    queryKey: ["market-quotes"],
    queryFn: fetchMarketQuotes,
    refetchInterval: 15000,
  });
}

export function useMarketQuote(symbol: string) {
  return useQuery({
    queryKey: ["market-quote", symbol],
    queryFn: () => fetchMarketQuote(symbol),
    refetchInterval: 15000,
    enabled: Boolean(symbol),
  });
}

export function useMarketSeries(symbol: string, timeframe: Timeframe) {
  return useQuery({
    queryKey: ["market-series", symbol, timeframe],
    queryFn: () => fetchMarketSeries(symbol, timeframe),
    enabled: Boolean(symbol),
  });
}

export function useMarketCapabilities(symbol: string) {
  return useQuery({
    queryKey: ["market-capabilities", symbol],
    queryFn: () => fetchCapabilities(symbol),
    enabled: Boolean(symbol),
    staleTime: Infinity,
  });
}
