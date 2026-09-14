import type { MarketStatus as MarketStatusType } from "@/types";
import { cn } from "@/lib/utils";

const STATUS_CONFIG: Record<MarketStatusType, { label: string; dot: string; text: string }> = {
  open: { label: "Open", dot: "bg-edge-positive", text: "text-edge-positive" },
  closed: { label: "Closed", dot: "bg-ink-faint", text: "text-ink-secondary" },
  "pre-market": { label: "Pre-Market", dot: "bg-edge-warning", text: "text-edge-warning" },
  "after-hours": { label: "After Hours", dot: "bg-edge-info", text: "text-edge-info" },
};

export function MarketStatus({ status, className }: { status: MarketStatusType; className?: string }) {
  const config = STATUS_CONFIG[status];
  return (
    <span className={cn("inline-flex items-center gap-1.5 text-xs font-medium", config.text, className)}>
      <span className={cn("h-1.5 w-1.5 rounded-full", config.dot)} />
      {config.label}
    </span>
  );
}
