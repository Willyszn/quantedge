import { useMarketQuotes } from "@/api/marketApi";
import { useSignals } from "@/api/signalApi";
import { PageContainer } from "@/components/layout/PageContainer";
import { MarketTable } from "@/components/scanner/MarketTable";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/common/StatusStates";

export function MarketScanner() {
  const { data: quotes, isLoading: quotesLoading, isError: quotesError, refetch: refetchQuotes } = useMarketQuotes();
  const { data: signals, isLoading: signalsLoading, isError: signalsError, refetch: refetchSignals } = useSignals();

  const isLoading = quotesLoading || signalsLoading;
  const isError = quotesError || signalsError;

  return (
    <PageContainer title="Market Scanner" subtitle="Screen every supported instrument by quantitative signal and confidence.">
      {isError ? (
        <ErrorState
          onRetry={() => {
            refetchQuotes();
            refetchSignals();
          }}
        />
      ) : isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-11 w-full" />
          ))}
        </div>
      ) : (
        <MarketTable quotes={quotes ?? []} signals={signals ?? []} />
      )}
    </PageContainer>
  );
}
