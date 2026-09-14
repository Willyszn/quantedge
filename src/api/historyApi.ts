import { useQuery } from "@tanstack/react-query";
import type { BacktestTrade } from "@/types";
import { apiFetch, IS_DEMO_MODE, simulateLatency } from "./client";
import { getMockTradeHistory } from "@/mocks/history";

async function fetchTradeHistory(): Promise<BacktestTrade[]> {
  if (IS_DEMO_MODE) return simulateLatency(getMockTradeHistory());
  return apiFetch<BacktestTrade[]>("/trades/history");
}

export function useTradeHistory() {
  return useQuery({ queryKey: ["trade-history"], queryFn: fetchTradeHistory });
}
