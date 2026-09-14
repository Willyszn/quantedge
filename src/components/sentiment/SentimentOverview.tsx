import type { SentimentSplit } from "@/types";
import { useResolvedTheme } from "@/hooks/useResolvedTheme";
import { getChartPalette } from "@/lib/chartColors";

export function SentimentOverview({ split }: { split: SentimentSplit }) {
  const palette = getChartPalette(useResolvedTheme());
  const segments = [
    { label: "Bullish", value: split.bullish, color: palette.positive },
    { label: "Neutral", value: split.neutral, color: palette.warning },
    { label: "Bearish", value: split.bearish, color: palette.negative },
  ];

  return (
    <div>
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-surface-subtle">
        {segments.map((seg) => (
          <div
            key={seg.label}
            style={{ width: `${seg.value}%`, backgroundColor: seg.color }}
            className="h-full first:rounded-l-full last:rounded-r-full"
          />
        ))}
      </div>
      <div className="mt-4 grid grid-cols-3 gap-3">
        {segments.map((seg) => (
          <div key={seg.label} className="rounded-md border border-line px-3 py-2.5 text-center">
            <p className="flex items-center justify-center gap-1.5 text-xs font-medium text-ink-secondary">
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: seg.color }} />
              {seg.label}
            </p>
            <p className="tnum mt-1 text-xl font-bold text-ink">{seg.value}%</p>
          </div>
        ))}
      </div>
    </div>
  );
}
