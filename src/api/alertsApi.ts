import { useQuery } from "@tanstack/react-query";
import type { AlertItem } from "@/types";
import { apiFetch, IS_DEMO_MODE, simulateLatency } from "./client";
import { getMockAlerts } from "@/mocks/alerts";

async function fetchAlerts(): Promise<AlertItem[]> {
  if (IS_DEMO_MODE) return simulateLatency(getMockAlerts());
  return apiFetch<AlertItem[]>("/alerts");
}

export function useAlerts() {
  // No refetchInterval here on purpose: once the initial demo alert feed
  // loads, new alerts arrive as push-style events from useAlertEngine
  // (via queryClient.setQueryData), not by polling. A timed refetch would
  // overwrite those live-injected alerts with the original static list.
  return useQuery({ queryKey: ["alerts"], queryFn: fetchAlerts, staleTime: Infinity });
}
