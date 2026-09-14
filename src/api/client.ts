/**
 * Central API configuration.
 *
 * QUANTEDGE ships in demo mode by default so the interface is fully
 * explorable without a backend. Once the QUANTEDGE backend is available,
 * set VITE_API_BASE_URL and VITE_DEMO_MODE=false and each api/*.ts module
 * will call the real endpoints instead of the mock data layer — no
 * component code needs to change, since pages only depend on the
 * TanStack Query hooks exposed by this folder.
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export const IS_DEMO_MODE = import.meta.env.VITE_DEMO_MODE !== "false";

/** Simulated network latency so loading states are visible in demo mode. */
export function simulateLatency<T>(value: T, ms = 420): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms));
}

export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    throw new ApiError(`Request failed: ${path}`, res.status);
  }
  return res.json() as Promise<T>;
}
