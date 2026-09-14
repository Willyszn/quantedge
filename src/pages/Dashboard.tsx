import { useMemo } from "react";
import { useMarketQuotes } from "@/api/marketApi";
import { usePrimarySignal, useSignals } from "@/api/signalApi";
import { MarketCard } from "@/components/market/MarketCard";
import { PrimarySignalPanel } from "@/components/signals/PrimarySignalPanel";
import { SignalCard } from "@/components/signals/SignalCard";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/common/StatusStates";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

function greeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

export function Dashboard() {
  const { data: quotes, isLoading: quotesLoading, isError: quotesError, refetch: refetchQuotes } = useMarketQuotes();
  const { data: primarySignal, isLoading: signalLoading, isError: signalError, refetch: refetchSignal } = usePrimarySignal();
  const { data: signals } = useSignals();

  const topSignals = useMemo(
    () => (signals ?? []).slice().sort((a, b) => b.confidence - a.confidence).slice(0, 3),
    [signals]
  );

  return (
    <div className="mx-auto w-full max-w-[1400px] px-4 pb-24 pt-6 sm:px-6 md:pb-10 lg:px-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-ink sm:text-[28px]">{greeting()}, Williams</h1>
        <p className="mt-1 text-sm text-ink-secondary">Market intelligence at a glance.</p>
      </div>

      <section className="mb-8">
        <h2 className="mb-3 text-[15px] font-semibold text-ink">Market Overview</h2>
        {quotesError ? (
          <ErrorState onRetry={() => refetchQuotes()} />
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {quotesLoading
              ? Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-[124px] rounded-lg" />)
              : quotes?.map((quote) => <MarketCard key={quote.symbol} quote={quote} />)}
          </div>
        )}
      </section>

      <section className="mb-8">
        {signalError ? (
          <ErrorState onRetry={() => refetchSignal()} />
        ) : signalLoading || !primarySignal ? (
          <Skeleton className="h-[420px] rounded-lg" />
        ) : (
          <PrimarySignalPanel signal={primarySignal} />
        )}
      </section>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-[15px] font-semibold text-ink">Other high-confidence signals</h2>
          <Button asChild variant="ghost" size="sm">
            <Link to="/signals">
              View all <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </Button>
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {topSignals.map((signal) => (
            <SignalCard key={signal.id} signal={signal} />
          ))}
        </div>
      </section>
    </div>
  );
}
