import { Link } from "react-router-dom";
import type { TradeSignal } from "@/types";
import { formatPrice, timeAgo } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { DirectionBadge, SignalRatingBadge } from "./SignalRatingBadge";

export function SignalCard({ signal }: { signal: TradeSignal }) {
  return (
    <Link to={`/signals/${signal.symbol}`}>
      <Card className="h-full transition-shadow hover:shadow-panel">
        <CardContent className="pt-5">
          <div className="flex items-start justify-between gap-2">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-base font-bold text-ink">{signal.symbol}</p>
                <DirectionBadge direction={signal.direction} />
              </div>
              <p className="mt-0.5 text-xs text-ink-secondary">{signal.name}</p>
            </div>
            <SignalRatingBadge rating={signal.rating} />
          </div>

          <div className="mt-4 grid grid-cols-3 gap-2 text-center">
            <div>
              <p className="text-[10px] uppercase tracking-wide text-ink-faint">Confidence</p>
              <p className="tnum mt-0.5 text-sm font-semibold text-ink">{signal.confidence}%</p>
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-wide text-ink-faint">Entry</p>
              <p className="tnum mt-0.5 text-sm font-semibold text-ink">{formatPrice(signal.entryLow, signal.decimals)}</p>
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-wide text-ink-faint">R:R</p>
              <p className="tnum mt-0.5 text-sm font-semibold text-ink">1:{signal.riskRewardRatio.toFixed(1)}</p>
            </div>
          </div>

          <p className="mt-4 line-clamp-2 text-xs leading-relaxed text-ink-secondary">{signal.narrative}</p>
          <p className="mt-3 text-[11px] text-ink-faint">Signal age · {timeAgo(signal.generatedAt)}</p>
        </CardContent>
      </Card>
    </Link>
  );
}
