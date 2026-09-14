import { create } from "zustand";
import { persist } from "zustand/middleware";

export type ThemePreference = "light" | "dark" | "system";

interface ThemeState {
  theme: ThemePreference;
  setTheme: (theme: ThemePreference) => void;
}

// Light is the shipped default — QUANTEDGE never opts a first-time visitor
// into dark mode on their behalf, even if their OS prefers it. Choosing
// "System" or "Dark" here is always an explicit, persisted choice.
export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: "light",
      setTheme: (theme) => set({ theme }),
    }),
    { name: "quantedge-theme" }
  )
);
