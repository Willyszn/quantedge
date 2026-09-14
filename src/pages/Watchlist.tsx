import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowDown, ArrowUp, Plus, Search, X } from "lucide-react";
import { useMarketQuotes } from "@/api/marketApi";
import { useSignals } from "@/api/signalApi";
import { useWatchlistStore } from "@/store/watchlistStore";
import { INSTRUMENTS } from "@/mocks/instruments";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/StatusStates";
import { SignalRatingBadge } from "@/components/signals/SignalRatingBadge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { formatPercent, formatPrice } from "@/lib/utils";
import { toast } from "sonner";

export function Watchlist() {
  const { items, add, remove, reorder } = useWatchlistStore();
  const { data: quotes, isLoading: quotesLoading } = useMarketQuotes();
  const { data: signals } = useSignals();
  const [search, setSearch] = useState("");

  const availableToAdd = useMemo(
    () => INSTRUMENTS.filter((i) => !items.some((w) => w.symbol === i.symbol)),
    [items]
  );

  const rows = useMemo(() => {
    return items
      .map((item, index) => ({
        index,
        symbol: item.symbol,
        quote: quotes?.find((q) => q.symbol === item.symbol),
        signal: signals?.find((s) => s.symbol === item.symbol),
      }))
      .filter((row) => row.symbol.toLowerCase().includes(search.toLowerCase()));
  }, [items, quotes, signals, search]);

  return (
    <PageContainer
      title="Watchlist"
      subtitle="Track the instruments you care about most."
      actions={
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button size="sm" disabled={availableToAdd.length === 0}>
              <Plus className="h-4 w-4" /> Add symbol
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="max-h-72 overflow-y-auto">
            {availableToAdd.map((inst) => (
              <DropdownMenuItem
                key={inst.symbol}
                onSelect={() => {
                  add(inst.symbol);
                  toast.success(`${inst.symbol} added to watchlist`);
                }}
              >
                <span className="font-medium">{inst.symbol}</span>
                <span className="text-ink-secondary">{inst.name}</span>
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      }
    >
      <div className="relative mb-4 max-w-xs">
        <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint" />
        <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search watchlist…" className="pl-8" />
      </div>

      {items.length === 0 ? (
        <EmptyState
          title="Your watchlist is empty"
          description="Add instruments to track their price, trend, and signal in one place."
        />
      ) : (
        <div className="overflow-hidden rounded-lg border border-line">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead className="w-16"></TableHead>
                <TableHead>Symbol</TableHead>
                <TableHead className="text-right">Price</TableHead>
                <TableHead className="text-right">24h Change</TableHead>
                <TableHead>Trend</TableHead>
                <TableHead>Momentum</TableHead>
                <TableHead>Sentiment</TableHead>
                <TableHead>Signal</TableHead>
                <TableHead className="w-12"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.symbol}>
                  <TableCell>
                    <div className="flex items-center gap-0.5">
                      <button
                        disabled={row.index === 0}
                        onClick={() => reorder(row.index, row.index - 1)}
                        className="rounded p-0.5 text-ink-faint hover:bg-surface-subtle hover:text-ink disabled:opacity-30"
                        aria-label="Move up"
                      >
                        <ArrowUp className="h-3.5 w-3.5" />
                      </button>
                      <button
                        disabled={row.index === items.length - 1}
                        onClick={() => reorder(row.index, row.index + 1)}
                        className="rounded p-0.5 text-ink-faint hover:bg-surface-subtle hover:text-ink disabled:opacity-30"
                        aria-label="Move down"
                      >
                        <ArrowDown className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Link to={`/signals/${row.symbol}`} className="font-semibold text-ink hover:underline">
                      {row.symbol}
                    </Link>
                  </TableCell>
                  {quotesLoading || !row.quote ? (
                    <TableCell colSpan={5}>
                      <Skeleton className="h-4 w-full" />
                    </TableCell>
                  ) : (
                    <>
                      <TableCell className="tnum text-right">{formatPrice(row.quote.price)}</TableCell>
                      <TableCell
                        className={`tnum text-right font-medium ${
                          row.quote.changePercent >= 0 ? "text-edge-positive" : "text-edge-negative"
                        }`}
                      >
                        {formatPercent(row.quote.changePercent)}
                      </TableCell>
                      <TableCell className="text-ink-secondary">
                        {row.signal?.factors.find((f) => f.id === "trend")?.statusLabel ?? "—"}
                      </TableCell>
                      <TableCell className="text-ink-secondary">
                        {row.signal?.factors.find((f) => f.id === "momentum")?.statusLabel ?? "—"}
                      </TableCell>
                      <TableCell className="text-ink-secondary">
                        {row.signal?.factors.find((f) => f.id === "sentiment-factor")?.statusLabel ?? "—"}
                      </TableCell>
                    </>
                  )}
                  <TableCell>{row.signal ? <SignalRatingBadge rating={row.signal.rating} /> : "—"}</TableCell>
                  <TableCell>
                    <button
                      onClick={() => {
                        remove(row.symbol);
                        toast(`${row.symbol} removed from watchlist`);
                      }}
                      className="rounded p-1 text-ink-faint hover:bg-surface-subtle hover:text-edge-negative"
                      aria-label={`Remove ${row.symbol}`}
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </PageContainer>
  );
}
