import { useResolvedTheme } from "@/hooks/useResolvedTheme";
import { getChartPalette } from "@/lib/chartColors";

const SIZE = 168;
const STROKE = 14;
const RADIUS = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = Math.PI * RADIUS; // half circle

function colorFor(confidence: number, palette: ReturnType<typeof getChartPalette>) {
  if (confidence >= 70) return palette.positive;
  if (confidence >= 45) return palette.warning;
  return palette.negative;
}

export function ConfidenceGauge({ confidence, label = "Signal Confidence" }: { confidence: number; label?: string }) {
  const palette = getChartPalette(useResolvedTheme());
  const clamped = Math.min(100, Math.max(0, confidence));
  const offset = CIRCUMFERENCE * (1 - clamped / 100);
  const color = colorFor(clamped, palette);

  return (
    <div className="flex flex-col items-center">
      <svg width={SIZE} height={SIZE / 2 + STROKE} viewBox={`0 0 ${SIZE} ${SIZE / 2 + STROKE}`}>
        <g transform={`translate(${STROKE / 2}, ${STROKE / 2})`}>
          <path
            d={`M 0 ${RADIUS} A ${RADIUS} ${RADIUS} 0 0 1 ${RADIUS * 2} ${RADIUS}`}
            fill="none"
            stroke={palette.surfaceSubtle}
            strokeWidth={STROKE}
            strokeLinecap="round"
          />
          <path
            d={`M 0 ${RADIUS} A ${RADIUS} ${RADIUS} 0 0 1 ${RADIUS * 2} ${RADIUS}`}
            fill="none"
            stroke={color}
            strokeWidth={STROKE}
            strokeLinecap="round"
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 0.6s ease-out" }}
          />
        </g>
      </svg>
      <div className="-mt-9 flex flex-col items-center">
        <span className="tnum text-4xl font-bold text-ink">{Math.round(clamped)}%</span>
      </div>
      <p className="mt-2 text-xs font-medium uppercase tracking-wide text-ink-secondary">{label}</p>
    </div>
  );
}
