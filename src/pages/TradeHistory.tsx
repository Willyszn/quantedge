import { useMemo, useState } from "react";
import { useTradeHistory } from "@/api/historyApi";
import { PageContainer } from "@/components/layout/PageContainer";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState, ErrorState } from "@/components/common/StatusStates";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { INSTRUMENTS } from "@/mocks/instruments";

export function TradeHistory() {
  const { data: trades, isLoading, isError, refetch } = useTradeHistory();
  const [symbol, setSymbol] = useState("all");
  const [outcome, setOutcome] = useState("all");

  const filtered = useMemo(() => {
    return (trades ?? []).filter((t) => {
      const matchesSymbol = symbol === "all" || t.symbol === symbol;
      const matchesOutcome = outcome === "all" || t.outcome === outcome;
      return matchesSymbol && matchesOutcome;
    });
  }, [trades, symbol, outcome]);

  return (
    <PageContainer
      title="Trade History"
      subtitle="A record of previously closed positions for post-trade review."
      actions={
        <div className="flex gap-2">
          <Select value={symbol} onValueChange={setSymbol}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Instrument" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All instruments</SelectItem>
              {INSTRUMENTS.map((i) => (
                <SelectItem key={i.symbol} value={i.symbol}>
                  {i.symbol}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={outcome} onValueChange={setOutcome}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Outcome" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All outcomes</SelectItem>
              <SelectItem value="win">Wins</SelectItem>
              <SelectItem value="loss">Losses</SelectItem>
              <SelectItem value="breakeven">Breakeven</SelectItem>
            </SelectContent>
          </Select>
        </div>
      }
    >
      {isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-full" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState title="No trades match this filter" />
      ) : (
        <div className="overflow-hidden rounded-lg border border-line">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>Symbol</TableHead>
                <TableHead>Direction</TableHead>
                <TableHead>Entry Date</TableHead>
                <TableHead>Exit Date</TableHead>
                <TableHead className="text-right">Entry</TableHead>
                <TableHead className="text-right">Exit</TableHead>
                <TableHead className="text-right">R Multiple</TableHead>
                <TableHead className="text-right">P&L %</TableHead>
                <TableHead>Outcome</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.slice(0, 60).map((trade) => (
                <TableRow key={trade.id}>
                  <TableCell className="font-medium text-ink">{trade.symbol}</TableCell>
                  <TableCell className="capitalize text-ink-secondary">{trade.direction}</TableCell>
                  <TableCell className="text-ink-secondary">{new Date(trade.entryDate).toLocaleDateString()}</TableCell>
                  <TableCell className="text-ink-secondary">{new Date(trade.exitDate).toLocaleDateString()}</TableCell>
                  <TableCell className="tnum text-right">{trade.entryPrice}</TableCell>
                  <TableCell className="tnum text-right">{trade.exitPrice}</TableCell>
                  <TableCell className="tnum text-right">{trade.rMultiple.toFixed(2)}R</TableCell>
                  <TableCell
                    className={`tnum text-right font-medium ${
                      trade.pnlPercent >= 0 ? "text-edge-positive" : "text-edge-negative"
                    }`}
                  >
                    {trade.pnlPercent.toFixed(2)}%
                  </TableCell>
                  <TableCell>
                    <Badge variant={trade.outcome === "win" ? "positive" : trade.outcome === "loss" ? "negative" : "default"}>
                      {trade.outcome}
                    </Badge>
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
