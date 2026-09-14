import { useMemo, useState } from "react";
import { useSignals } from "@/api/signalApi";
import { PageContainer } from "@/components/layout/PageContainer";
import { SignalCard } from "@/components/signals/SignalCard";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState, EmptyState } from "@/components/common/StatusStates";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { SignalDirection } from "@/types";

export function TradeSignals() {
  const { data: signals, isLoading, isError, refetch } = useSignals();
  const [direction, setDirection] = useState<SignalDirection | "all">("all");
  const [sort, setSort] = useState<"confidence" | "recent">("confidence");

  const filtered = useMemo(() => {
    let list = (signals ?? []).slice();
    if (direction !== "all") list = list.filter((s) => s.direction === direction);
    if (sort === "confidence") list.sort((a, b) => b.confidence - a.confidence);
    else list.sort((a, b) => new Date(b.generatedAt).getTime() - new Date(a.generatedAt).getTime());
    return list;
  }, [signals, direction, sort]);

  return (
    <PageContainer
      title="Trade Signals"
      subtitle="Every active signal with full quantitative and sentiment reasoning."
      actions={
        <div className="flex gap-2">
          <Select value={direction} onValueChange={(v) => setDirection(v as SignalDirection | "all")}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Direction" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All directions</SelectItem>
              <SelectItem value="long">Long only</SelectItem>
              <SelectItem value="short">Short only</SelectItem>
            </SelectContent>
          </Select>
          <Select value={sort} onValueChange={(v) => setSort(v as "confidence" | "recent")}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Sort" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="confidence">Highest confidence</SelectItem>
              <SelectItem value="recent">Most recent</SelectItem>
            </SelectContent>
          </Select>
        </div>
      }
    >
      {isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : isLoading ? (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-[190px] rounded-lg" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState title="No signals match this filter" />
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((signal) => (
            <SignalCard key={signal.id} signal={signal} />
          ))}
        </div>
      )}
    </PageContainer>
  );
}
