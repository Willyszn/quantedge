import type { SignalScoreBreakdown } from "@/types";

const ROWS: { key: keyof SignalScoreBreakdown; label: string }[] = [
  { key: "quant", label: "Quant Score" },
  { key: "momentum", label: "Momentum" },
  { key: "trend", label: "Trend" },
  { key: "sentiment", label: "Sentiment" },
  { key: "risk", label: "Risk" },
];

function colorFor(score: number) {
  if (score >= 70) return "bg-edge-positive";
  if (score >= 45) return "bg-edge-warning";
  return "bg-edge-negative";
}

export function ConfidenceBreakdown({ scores }: { scores: SignalScoreBreakdown }) {
  return (
    <div className="flex flex-col gap-3">
      {ROWS.map((row) => {
        const value = scores[row.key];
        return (
          <div key={row.key} className="flex items-center gap-3">
            <span className="w-24 shrink-0 text-xs font-medium text-ink-secondary">{row.label}</span>
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-surface-subtle">
              <div
                className={`h-full rounded-full ${colorFor(value)} transition-all duration-500`}
                style={{ width: `${value}%` }}
              />
            </div>
            <span className="tnum w-8 shrink-0 text-right text-sm font-semibold text-ink">{value}</span>
          </div>
        );
      })}
    </div>
  );
}
