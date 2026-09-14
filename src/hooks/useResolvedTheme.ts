import { useSyncExternalStore } from "react";
import { useThemeStore } from "@/store/themeStore";

const DARK_QUERY = "(prefers-color-scheme: dark)";

function subscribeToSystemTheme(callback: () => void) {
  const mql = window.matchMedia(DARK_QUERY);
  mql.addEventListener("change", callback);
  return () => mql.removeEventListener("change", callback);
}

function getSystemPrefersDark() {
  return window.matchMedia(DARK_QUERY).matches;
}

/**
 * Resolves the person's theme preference ("light" | "dark" | "system")
 * against the OS setting when "system" is selected, and stays in sync if
 * the OS preference changes while the app is open.
 */
export function useResolvedTheme(): "light" | "dark" {
  const preference = useThemeStore((s) => s.theme);
  const systemPrefersDark = useSyncExternalStore(
    subscribeToSystemTheme,
    getSystemPrefersDark,
    () => false
  );

  if (preference === "system") return systemPrefersDark ? "dark" : "light";
  return preference;
}
