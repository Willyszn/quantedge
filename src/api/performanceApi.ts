import { useQuery } from "@tanstack/react-query";
import type { EquityPoint, PerformanceBySlice, PerformanceMetrics } from "@/types";
import { apiFetch, IS_DEMO_MODE, simulateLatency } from "./client";
import {
  getMockPerformanceMetrics,
  getMockPortfolioEquityCurve,
  getPerformanceByInstrument,
  getPerformanceByMonth,
  getPerformanceByRegime,
  getPerformanceBySignalType,
} from "@/mocks/performance";

async function fetchMetrics(): Promise<PerformanceMetrics> {
  if (IS_DEMO_MODE) return simulateLatency(getMockPerformanceMetrics());
  return apiFetch<PerformanceMetrics>("/performance/metrics");
}

async function fetchEquityCurve(): Promise<EquityPoint[]> {
  if (IS_DEMO_MODE) return simulateLatency(getMockPortfolioEquityCurve());
  return apiFetch<EquityPoint[]>("/performance/equity-curve");
}

async function fetchSlices(
  by: "instrument" | "signal-type" | "month" | "regime"
): Promise<PerformanceBySlice[]> {
  if (IS_DEMO_MODE) {
    const map = {
      instrument: getPerformanceByInstrument,
      "signal-type": getPerformanceBySignalType,
      month: getPerformanceByMonth,
      regime: getPerformanceByRegime,
    } as const;
    return simulateLatency(map[by]());
  }
  return apiFetch<PerformanceBySlice[]>(`/performance/by/${by}`);
}

export function usePerformanceMetrics() {
  return useQuery({ queryKey: ["performance-metrics"], queryFn: fetchMetrics });
}

export function usePortfolioEquityCurve() {
  return useQuery({ queryKey: ["performance-equity-curve"], queryFn: fetchEquityCurve });
}

export function usePerformanceSlices(by: "instrument" | "signal-type" | "month" | "regime") {
  return useQuery({ queryKey: ["performance-slices", by], queryFn: () => fetchSlices(by) });
}
