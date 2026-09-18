import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { WatchlistItem } from "@/types";

interface WatchlistState {
  items: WatchlistItem[];
  add: (symbol: string) => void;
  remove: (symbol: string) => void;
  reorder: (fromIndex: number, toIndex: number) => void;
  has: (symbol: string) => boolean;
}

// Local-first state. Structured so a future backend can hydrate `items`
// and `add`/`remove`/`reorder` can be swapped for API-backed mutations
// without touching the components that consume this store.
export const useWatchlistStore = create<WatchlistState>()(
  persist(
    (set, get) => ({
      items: [],
      add: (symbol) =>
        set((state) => {
          if (state.items.some((i) => i.symbol === symbol)) return state;
          return { items: [...state.items, { symbol, addedAt: new Date().toISOString() }] };
        }),
      remove: (symbol) => set((state) => ({ items: state.items.filter((i) => i.symbol !== symbol) })),
      reorder: (fromIndex, toIndex) =>
        set((state) => {
          const next = [...state.items];
          const [moved] = next.splice(fromIndex, 1);
          next.splice(toIndex, 0, moved);
          return { items: next };
        }),
      has: (symbol) => get().items.some((i) => i.symbol === symbol),
    }),
    { name: "quantedge-watchlist" }
  )
);
