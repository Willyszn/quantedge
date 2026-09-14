import { NavLink } from "react-router-dom";
import { LayoutDashboard, Radar, Gauge, Newspaper, ListChecks } from "lucide-react";
import { cn } from "@/lib/utils";

const BOTTOM_ITEMS = [
  { label: "Home", path: "/", icon: LayoutDashboard },
  { label: "Markets", path: "/markets", icon: Radar },
  { label: "Signals", path: "/signals", icon: Gauge },
  { label: "Sentiment", path: "/sentiment", icon: Newspaper },
  { label: "Watchlist", path: "/watchlist", icon: ListChecks },
];

export function BottomNav() {
  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-30 flex items-stretch justify-around border-t border-line bg-canvas/95 backdrop-blur pb-[env(safe-area-inset-bottom)] md:hidden"
      aria-label="Primary"
    >
      {BOTTOM_ITEMS.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              cn(
                "flex flex-1 flex-col items-center gap-1 py-2 text-[11px] font-medium transition-colors",
                isActive ? "text-ink" : "text-ink-faint"
              )
            }
          >
            <Icon className="h-5 w-5" />
            {item.label}
          </NavLink>
        );
      })}
    </nav>
  );
}
