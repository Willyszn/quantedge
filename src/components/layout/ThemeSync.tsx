import { useEffect } from "react";
import { useResolvedTheme } from "@/hooks/useResolvedTheme";

export function ThemeSync() {
  const resolvedTheme = useResolvedTheme();

  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("dark", resolvedTheme === "dark");
    root.style.colorScheme = resolvedTheme;
  }, [resolvedTheme]);

  return null;
}
