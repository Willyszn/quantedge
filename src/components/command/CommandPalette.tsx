import { useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Compass, Gauge, ListChecks, Newspaper, FlaskConical, ArrowRight } from "lucide-react";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command";
import { useUiStore } from "@/store/uiStore";
import { ALL_NAV_ITEMS } from "@/lib/nav";
import { INSTRUMENTS } from "@/mocks/instruments";
import { useWatchlistStore } from "@/store/watchlistStore";

export function CommandPalette() {
  const open = useUiStore((s) => s.commandOpen);
  const setOpen = useUiStore((s) => s.setCommandOpen);
  const navigate = useNavigate();
  const watchlist = useWatchlistStore((s) => s.items);

  useEffect(() => {
    function handler(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen(!open);
      }
    }
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [open, setOpen]);

  const watchlistSymbols = useMemo(() => new Set(watchlist.map((w) => w.symbol)), [watchlist]);

  function go(path: string) {
    navigate(path);
    setOpen(false);
  }

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Search instruments, signals, pages…" />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        <CommandGroup heading="Pages">
          {ALL_NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <CommandItem key={item.path} onSelect={() => go(item.path)} value={`page ${item.label}`}>
                <Icon className="h-4 w-4 text-ink-secondary" />
                <span>{item.label}</span>
              </CommandItem>
            );
          })}
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Instruments">
          {INSTRUMENTS.map((inst) => (
            <CommandItem
              key={inst.symbol}
              value={`instrument ${inst.symbol} ${inst.name}`}
              onSelect={() => go(`/signals/${inst.symbol}`)}
            >
              <Compass className="h-4 w-4 text-ink-secondary" />
              <span className="font-medium">{inst.symbol}</span>
              <span className="text-ink-secondary">{inst.name}</span>
              {watchlistSymbols.has(inst.symbol) && <CommandShortcut>Watching</CommandShortcut>}
            </CommandItem>
          ))}
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Quick actions">
          <CommandItem value="quick trade signals" onSelect={() => go("/signals")}>
            <Gauge className="h-4 w-4 text-ink-secondary" />
            <span>View all trade signals</span>
            <ArrowRight className="ml-auto h-3.5 w-3.5 text-ink-faint" />
          </CommandItem>
          <CommandItem value="quick watchlist" onSelect={() => go("/watchlist")}>
            <ListChecks className="h-4 w-4 text-ink-secondary" />
            <span>Open watchlist</span>
            <ArrowRight className="ml-auto h-3.5 w-3.5 text-ink-faint" />
          </CommandItem>
          <CommandItem value="quick sentiment" onSelect={() => go("/sentiment")}>
            <Newspaper className="h-4 w-4 text-ink-secondary" />
            <span>Check market sentiment</span>
            <ArrowRight className="ml-auto h-3.5 w-3.5 text-ink-faint" />
          </CommandItem>
          <CommandItem value="quick backtest" onSelect={() => go("/backtesting")}>
            <FlaskConical className="h-4 w-4 text-ink-secondary" />
            <span>Run a new backtest</span>
            <ArrowRight className="ml-auto h-3.5 w-3.5 text-ink-faint" />
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
