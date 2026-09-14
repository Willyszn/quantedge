import { Link } from "react-router-dom";
import { ArrowRight, Clock } from "lucide-react";
import type { TradeSignal } from "@/types";
import { timeAgo } from "@/lib/utils";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ConfidenceGauge } from "./ConfidenceGauge";
import { ConfidenceBreakdown } from "./ConfidenceBreakdown";
import { SignalBreakdown } from "./SignalBreakdown";
import { TradePlan } from "./TradePlan";
import { DirectionBadge } from "./SignalRatingBadge";

export function PrimarySignalPanel({ signal }: { signal: TradeSignal }) {
  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex-row items-start justify-between gap-4 border-b border-line pb-5">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-wide text-ink-faint">Quantedge Signal</p>
          <div className="mt-1.5 flex items-center gap-2.5">
            <h2 className="text-2xl font-bold tracking-tight text-ink">{signal.symbol}</h2>
            <DirectionBadge direction={signal.direction} />
          </div>
          <p className="mt-1 flex items-center gap-1 text-xs text-ink-secondary">
            <Clock className="h-3 w-3" /> Generated {timeAgo(signal.generatedAt)}
          </p>
        </div>
        <Button asChild size="sm" variant="outline" className="shrink-0">
          <Link to={`/signals/${signal.symbol}`}>
            Full analysis <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </Button>
      </CardHeader>

      <CardContent className="pt-5">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-[168px_1fr]">
          <div className="flex justify-center lg:justify-start">
            <ConfidenceGauge confidence={signal.confidence} />
          </div>

          <div className="flex flex-col gap-6">
            <TradePlan signal={signal} />
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-ink-faint">
                Signal Reasoning
              </p>
              <SignalBreakdown factors={signal.factors} />
            </div>
          </div>
        </div>

        <div className="mt-6 border-t border-line pt-6">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-ink-faint">
            Confidence Breakdown
          </p>
          <ConfidenceBreakdown scores={signal.scores} />
        </div>
      </CardContent>
    </Card>
  );
}
