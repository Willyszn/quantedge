import type { SignalFactor } from "@/types";
import { cn } from "@/lib/utils";

const STATUS_DOT: Record<SignalFactor["status"], string> = {
  favorable: "bg-edge-positive",
  neutral: "bg-edge-warning",
  unfavorable: "bg-edge-negative",
};

const STATUS_TEXT: Record<SignalFactor["status"], string> = {
  favorable: "text-edge-positive",
  neutral: "text-edge-warning",
  unfavorable: "text-edge-negative",
};

export function SignalBreakdown({ factors }: { factors: SignalFactor[] }) {
  return (
    <div className="flex flex-col divide-y divide-line">
      {factors.map((factor) => (
        <div key={factor.id} className="flex flex-col gap-1.5 py-3 first:pt-0 last:pb-0">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className={cn("h-1.5 w-1.5 rounded-full", STATUS_DOT[factor.status])} />
              <span className="text-sm font-medium text-ink">{factor.label}</span>
            </div>
            <span className={cn("text-sm font-semibold", STATUS_TEXT[factor.status])}>{factor.statusLabel}</span>
          </div>
          <p className="pl-3.5 text-xs leading-relaxed text-ink-secondary">{factor.explanation}</p>
        </div>
      ))}
    </div>
  );
}
