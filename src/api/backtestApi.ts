import { useMutation } from "@tanstack/react-query";
import type { BacktestConfig, BacktestResult } from "@/types";
import { apiFetch, IS_DEMO_MODE, simulateLatency } from "./client";
import { runMockBacktest } from "@/mocks/backtests";

async function runBacktest(config: BacktestConfig): Promise<BacktestResult> {
  if (IS_DEMO_MODE) return simulateLatency(runMockBacktest(config), 900);
  return apiFetch<BacktestResult>("/backtests", {
    method: "POST",
    body: JSON.stringify(config),
  });
}

export function useRunBacktest() {
  return useMutation({ mutationFn: runBacktest });
}
