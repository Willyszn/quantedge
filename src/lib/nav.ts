import {
  LayoutDashboard,
  LineChart,
  ListChecks,
  Radar,
  Gauge,
  Newspaper,
  FlaskConical,
  TrendingUp,
  History,
  Settings,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  label: string;
  path: string;
  icon: LucideIcon;
}

export interface NavGroup {
  label: string;
  items: NavItem[];
}

export const NAV_GROUPS: NavGroup[] = [
  {
    label: "Overview",
    items: [{ label: "Dashboard", path: "/", icon: LayoutDashboard }],
  },
  {
    label: "Markets",
    items: [
      { label: "Market Scanner", path: "/markets", icon: Radar },
      { label: "Watchlist", path: "/watchlist", icon: ListChecks },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { label: "Trade Signals", path: "/signals", icon: Gauge },
      { label: "Quant Analysis", path: "/analysis", icon: LineChart },
      { label: "Sentiment", path: "/sentiment", icon: Newspaper },
    ],
  },
  {
    label: "Research",
    items: [
      { label: "Backtesting", path: "/backtesting", icon: FlaskConical },
      { label: "Performance", path: "/performance", icon: TrendingUp },
      { label: "Trade History", path: "/history", icon: History },
    ],
  },
  {
    label: "System",
    items: [{ label: "Settings", path: "/settings", icon: Settings }],
  },
];

export const ALL_NAV_ITEMS: NavItem[] = NAV_GROUPS.flatMap((g) => g.items);
