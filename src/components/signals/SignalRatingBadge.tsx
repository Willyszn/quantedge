import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import type { SignalDirection, SignalRating } from "@/types";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const RATING_CONFIG: Record<SignalRating, { label: string; variant: "positive" | "negative" | "default" }> = {
  "strong-buy": { label: "STRONG BUY", variant: "positive" },
  buy: { label: "BUY", variant: "positive" },
  neutral: { label: "NEUTRAL", variant: "default" },
  sell: { label: "SELL", variant: "negative" },
  "strong-sell": { label: "STRONG SELL", variant: "negative" },
};

export function SignalRatingBadge({ rating }: { rating: SignalRating }) {
  const config = RATING_CONFIG[rating];
  return <Badge variant={config.variant}>{config.label}</Badge>;
}

export function DirectionBadge({ direction, className }: { direction: SignalDirection; className?: string }) {
  const positive = direction === "long";
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold",
        positive ? "bg-edge-positive-soft text-edge-positive" : "bg-edge-negative-soft text-edge-negative",
        className
      )}
    >
      {positive ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
      {positive ? "LONG" : "SHORT"}
    </span>
  );
}
