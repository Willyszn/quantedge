import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowDown, ArrowUp, ArrowUpDown, ChevronLeft, ChevronRight, Search } from "lucide-react";
import type { MarketQuote, SignalRating, TradeSignal } from "@/types";
import { formatPercent, formatPrice } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { EmptyState } from "@/components/common/StatusStates";
import { SignalRatingBadge } from "@/components/signals/SignalRatingBadge";

interface ScannerRow {
  quote: MarketQuote;
  signal: TradeSignal | undefined;
}

type SortKey = "symbol" | "price" | "change" | "confidence" | "rr";

const FILTERS: { label: string; value: SignalRating | "all" }[] = [
  { label: "All", value: "all" },
  { label: "Strong Buy", value: "strong-buy" },
  { label: "Buy", value: "buy" },
  { label: "Neutral", value: "neutral" },
  { label: "Sell", value: "sell" },
  { label: "Strong Sell", value: "strong-sell" },
];

function factorLabel(signal: TradeSignal | undefined, id: string): string {
  return signal?.factors.find((f) => f.id === id)?.statusLabel ?? "—";
}

function SortIcon({ active, dir }: { active: boolean; dir: "asc" | "desc" }) {
  if (!active) return <ArrowUpDown className="h-3 w-3 text-ink-faint" />;
  return dir === "asc" ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />;
}

export function MarketTable({ quotes, signals }: { quotes: MarketQuote[]; signals: TradeSignal[] }) {
  const [search, setSearch] = useState("");
  const [ratingFilter, setRatingFilter] = useState<SignalRating | "all">("all");
  const [minConfidence, setMinConfidence] = useState(0);
  const [sortKey, setSortKey] = useState<SortKey>("confidence");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);
  const pageSize = 8;

  const rows: ScannerRow[] = useMemo(
    () => quotes.map((quote) => ({ quote, signal: signals.find((s) => s.symbol === quote.symbol) })),
    [quotes, signals]
  );

  const filtered = useMemo(() => {
    return rows
      .filter((row) => {
        const matchesSearch =
          row.quote.symbol.toLowerCase().includes(search.toLowerCase()) ||
          row.quote.name.toLowerCase().includes(search.toLowerCase());
        const matchesRating = ratingFilter === "all" || row.signal?.rating === ratingFilter;
        const matchesConfidence = (row.signal?.confidence ?? 0) >= minConfidence;
        return matchesSearch && matchesRating && matchesConfidence;
      })
      .sort((a, b) => {
        const dir = sortDir === "asc" ? 1 : -1;
        switch (sortKey) {
          case "symbol":
            return a.quote.symbol.localeCompare(b.quote.symbol) * dir;
          case "price":
            return (a.quote.price - b.quote.price) * dir;
          case "change":
            return (a.quote.changePercent - b.quote.changePercent) * dir;
          case "confidence":
            return ((a.signal?.confidence ?? 0) - (b.signal?.confidence ?? 0)) * dir;
          case "rr":
            return ((a.signal?.riskRewardRatio ?? 0) - (b.signal?.riskRewardRatio ?? 0)) * dir;
          default:
            return 0;
        }
      });
  }, [rows, search, ratingFilter, minConfidence, sortKey, sortDir]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const pageRows = filtered.slice((page - 1) * pageSize, page * pageSize);

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  return (
    <div>
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full sm:max-w-xs">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint" />
          <Input
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            placeholder="Search symbol or name…"
            className="pl-8"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Select
            value={String(minConfidence)}
            onValueChange={(v) => {
              setMinConfidence(Number(v));
              setPage(1);
            }}
          >
            <SelectTrigger className="w-[168px]">
              <SelectValue placeholder="Confidence" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="0">Any confidence</SelectItem>
              <SelectItem value="60">60%+ confidence</SelectItem>
              <SelectItem value="75">75%+ confidence</SelectItem>
              <SelectItem value="85">85%+ confidence</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-1.5">
        {FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => {
              setRatingFilter(f.value);
              setPage(1);
            }}
            className={
              "rounded-full border px-3 py-1 text-xs font-medium transition-colors " +
              (ratingFilter === f.value
                ? "border-primary bg-primary text-primary-foreground"
                : "border-line text-ink-secondary hover:border-line-strong")
            }
          >
            {f.label}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <EmptyState title="No instruments match your filters" description="Try widening your search or resetting the confidence threshold." />
      ) : (
        <div className="overflow-hidden rounded-lg border border-line">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>
                  <button onClick={() => toggleSort("symbol")} className="flex items-center gap-1">
                    Symbol <SortIcon active={sortKey === "symbol"} dir={sortDir} />
                  </button>
                </TableHead>
                <TableHead className="text-right">
                  <button onClick={() => toggleSort("price")} className="ml-auto flex items-center gap-1">
                    Price <SortIcon active={sortKey === "price"} dir={sortDir} />
                  </button>
                </TableHead>
                <TableHead className="text-right">
                  <button onClick={() => toggleSort("change")} className="ml-auto flex items-center gap-1">
                    Change <SortIcon active={sortKey === "change"} dir={sortDir} />
                  </button>
                </TableHead>
                <TableHead>Momentum</TableHead>
                <TableHead>Trend</TableHead>
                <TableHead>Sentiment</TableHead>
                <TableHead>Volatility</TableHead>
                <TableHead>Signal</TableHead>
                <TableHead className="text-right">
                  <button onClick={() => toggleSort("confidence")} className="ml-auto flex items-center gap-1">
                    Confidence <SortIcon active={sortKey === "confidence"} dir={sortDir} />
                  </button>
                </TableHead>
                <TableHead className="text-right">
                  <button onClick={() => toggleSort("rr")} className="ml-auto flex items-center gap-1">
                    R:R <SortIcon active={sortKey === "rr"} dir={sortDir} />
                  </button>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {pageRows.map(({ quote, signal }) => (
                <TableRow key={quote.symbol}>
                  <TableCell>
                    <Link to={`/signals/${quote.symbol}`} className="font-semibold text-ink hover:underline">
                      {quote.symbol}
                    </Link>
                  </TableCell>
                  <TableCell className="tnum text-right">{formatPrice(quote.price, decimalsFor(quote))}</TableCell>
                  <TableCell
                    className={`tnum text-right font-medium ${
                      quote.changePercent >= 0 ? "text-edge-positive" : "text-edge-negative"
                    }`}
                  >
                    {formatPercent(quote.changePercent)}
                  </TableCell>
                  <TableCell className="text-ink-secondary">{factorLabel(signal, "momentum")}</TableCell>
                  <TableCell className="text-ink-secondary">{factorLabel(signal, "trend")}</TableCell>
                  <TableCell className="text-ink-secondary">{factorLabel(signal, "sentiment-factor")}</TableCell>
                  <TableCell className="text-ink-secondary">{factorLabel(signal, "volatility")}</TableCell>
                  <TableCell>{signal ? <SignalRatingBadge rating={signal.rating} /> : <Badge>—</Badge>}</TableCell>
                  <TableCell className="tnum text-right font-semibold text-ink">
                    {signal ? `${signal.confidence}%` : "—"}
                  </TableCell>
                  <TableCell className="tnum text-right text-ink-secondary">
                    {signal ? `1:${signal.riskRewardRatio.toFixed(1)}` : "—"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {filtered.length > 0 && (
        <div className="mt-4 flex items-center justify-between text-xs text-ink-secondary">
          <span>
            Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, filtered.length)} of {filtered.length}
          </span>
          <div className="flex items-center gap-1">
            <Button variant="outline" size="icon" disabled={page === 1} onClick={() => setPage((p) => p - 1)}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="tnum px-2">
              {page} / {totalPages}
            </span>
            <Button
              variant="outline"
              size="icon"
              disabled={page === totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function decimalsFor(quote: MarketQuote) {
  if (quote.assetClass === "crypto") return 1;
  if (quote.symbol.includes("JPY")) return 2;
  if (quote.assetClass === "index") return 1;
  return quote.assetClass === "forex" ? 4 : 2;
}
