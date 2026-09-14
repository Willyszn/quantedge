import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Clock, Star } from "lucide-react";
import { useSignal } from "@/api/signalApi";
import { useMarketCapabilities, useMarketSeries } from "@/api/marketApi";
import { useWatchlistStore } from "@/store/watchlistStore";
import { PageContainer } from "@/components/layout/PageContainer";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/common/StatusStates";
import { DirectionBadge, SignalRatingBadge } from "@/components/signals/SignalRatingBadge";
import { ConfidenceGauge } from "@/components/signals/ConfidenceGauge";
import { ConfidenceBreakdown } from "@/components/signals/ConfidenceBreakdown";
import { SignalBreakdown } from "@/components/signals/SignalBreakdown";
import { SignalExplanation } from "@/components/signals/SignalExplanation";
import { TradePlan } from "@/components/signals/TradePlan";
import { MarketChart } from "@/components/market/MarketChart";
import { timeAgo } from "@/lib/utils";
import type { Timeframe } from "@/types";
import { toast } from "sonner";

export function TradeDetail() {
  const { symbol = "" } = useParams<{ symbol: string }>();
  const { data: signal, isLoading, isError, refetch } = useSignal(symbol);
  const { data: capabilities } = useMarketCapabilities(symbol);
  const [timeframe, setTimeframe] = useState<Timeframe>("1H");
  const { has, add, remove } = useWatchlistStore();
  const watching = has(symbol);

  const activeTimeframe = capabilities?.supportedTimeframes.includes(timeframe)
    ? timeframe
    : capabilities?.supportedTimeframes[0] ?? "1H";

  const { data: series, isLoading: seriesLoading } = useMarketSeries(symbol, activeTimeframe);

  if (isError) {
    return (
      <PageContainer>
        <ErrorState onRetry={() => refetch()} />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <Link to="/signals" className="mb-4 inline-flex items-center gap-1.5 text-sm text-ink-secondary hover:text-ink">
        <ArrowLeft className="h-3.5 w-3.5" /> Back to Trade Signals
      </Link>

      {isLoading || !signal ? (
        <Skeleton className="h-[500px] rounded-lg" />
      ) : (
        <div className="flex flex-col gap-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold tracking-tight text-ink sm:text-[28px]">{signal.symbol}</h1>
                <DirectionBadge direction={signal.direction} />
                <SignalRatingBadge rating={signal.rating} />
              </div>
              <p className="mt-1 text-sm text-ink-secondary">{signal.name}</p>
              <p className="mt-1 flex items-center gap-1 text-xs text-ink-faint">
                <Clock className="h-3 w-3" /> Signal generated {timeAgo(signal.generatedAt)}
              </p>
            </div>
            <Button
              variant={watching ? "subtle" : "outline"}
              size="sm"
              onClick={() => {
                if (watching) {
                  remove(signal.symbol);
                  toast(`${signal.symbol} removed from watchlist`);
                } else {
                  add(signal.symbol);
                  toast.success(`${signal.symbol} added to watchlist`);
                }
              }}
            >
              <Star className={watching ? "fill-current" : ""} />
              {watching ? "On Watchlist" : "Add to Watchlist"}
            </Button>
          </div>

          <Card>
            <CardContent className="pt-5">
              {seriesLoading || !series ? (
                <Skeleton className="h-[380px] w-full" />
              ) : (
                <MarketChart
                  candles={series.candles}
                  timeframe={activeTimeframe}
                  timeframes={capabilities?.supportedTimeframes ?? ["1H"]}
                  onTimeframeChange={setTimeframe}
                  decimals={signal.decimals}
                  entry={(signal.entryLow + signal.entryHigh) / 2}
                  stopLoss={signal.stopLoss}
                  target={signal.target}
                />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex flex-col gap-6 pt-5">
              <div>
                <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-ink-faint">Trade Plan</p>
                <TradePlan signal={signal} />
              </div>
              <SignalExplanation narrative={signal.narrative} />
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card>
              <CardContent className="pt-5">
                <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-ink-faint">
                  Signal Reasoning
                </p>
                <SignalBreakdown factors={signal.factors} />
              </CardContent>
            </Card>
            <Card>
              <CardContent className="flex flex-col items-center gap-6 pt-5 sm:flex-row">
                <ConfidenceGauge confidence={signal.confidence} />
                <div className="w-full">
                  <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-ink-faint">
                    Confidence Breakdown
                  </p>
                  <ConfidenceBreakdown scores={signal.scores} />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
