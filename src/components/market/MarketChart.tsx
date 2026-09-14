import { useMemo, useState } from "react";
import { Bar, Brush, ComposedChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { RotateCcw } from "lucide-react";
import type { Candle, Timeframe } from "@/types";
import { cn, formatPrice } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useResolvedTheme } from "@/hooks/useResolvedTheme";
import { getChartPalette } from "@/lib/chartColors";

interface MarketChartProps {
  candles: Candle[];
  timeframe: Timeframe;
  timeframes: Timeframe[];
  onTimeframeChange: (tf: Timeframe) => void;
  decimals: number;
  entry?: number;
  stopLoss?: number;
  target?: number;
}

interface ChartRow extends Candle {
  isUp: boolean;
  wickRange: [number, number];
  bodyRange: [number, number];
}

function WickShape(props: any) {
  const { x, y, width, height, payload, palette } = props;
  const color = payload.isUp ? palette.positive : palette.negative;
  const cx = x + width / 2;
  return <line x1={cx} x2={cx} y1={y} y2={y + height} stroke={color} strokeWidth={1.25} />;
}

function BodyShape(props: any) {
  const { x, y, width, height, payload, palette } = props;
  const color = payload.isUp ? palette.positive : palette.negative;
  const bodyWidth = Math.max(width * 0.6, 2);
  const bx = x + (width - bodyWidth) / 2;
  return <rect x={bx} y={y} width={bodyWidth} height={Math.max(height, 1.5)} fill={color} rx={1} />;
}

function CustomTooltip({ active, payload, decimals, palette }: any) {
  if (!active || !payload?.length) return null;
  const candle: Candle = payload[0].payload;
  return (
    <div
      className="rounded-md border px-3 py-2 text-xs shadow-elevated"
      style={{ backgroundColor: palette.tooltipBg, borderColor: palette.tooltipBorder, color: palette.tooltipText }}
    >
      <p className="mb-1 font-medium">{new Date(candle.time).toLocaleString()}</p>
      <div className="tnum grid grid-cols-2 gap-x-3 gap-y-0.5" style={{ color: palette.inkSecondary }}>
        <span>O {formatPrice(candle.open, decimals)}</span>
        <span>H {formatPrice(candle.high, decimals)}</span>
        <span>L {formatPrice(candle.low, decimals)}</span>
        <span>C {formatPrice(candle.close, decimals)}</span>
      </div>
    </div>
  );
}

export function MarketChart({
  candles,
  timeframe,
  timeframes,
  onTimeframeChange,
  decimals,
  entry,
  stopLoss,
  target,
}: MarketChartProps) {
  const [brushKey, setBrushKey] = useState(0);
  const palette = getChartPalette(useResolvedTheme());

  const { data, domain } = useMemo(() => {
    if (candles.length === 0) return { data: [] as ChartRow[], domain: [0, 1] as [number, number] };
    const rows: ChartRow[] = candles.map((c) => ({
      ...c,
      isUp: c.close >= c.open,
      wickRange: [c.low, c.high],
      bodyRange: [Math.min(c.open, c.close), Math.max(c.open, c.close)],
    }));
    const min = Math.min(...candles.map((c) => c.low));
    const max = Math.max(...candles.map((c) => c.high));
    const padding = (max - min) * 0.08 || max * 0.01 || 1;
    return { data: rows, domain: [min - padding, max + padding] as [number, number] };
  }, [candles]);

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-1 rounded-md bg-surface-subtle p-1">
          {timeframes.map((tf) => (
            <button
              key={tf}
              onClick={() => onTimeframeChange(tf)}
              className={cn(
                "rounded-sm px-2.5 py-1 text-xs font-medium transition-colors",
                tf === timeframe ? "bg-canvas text-ink shadow-subtle" : "text-ink-secondary hover:text-ink"
              )}
            >
              {tf}
            </button>
          ))}
        </div>
        <Button variant="ghost" size="sm" onClick={() => setBrushKey((k) => k + 1)}>
          <RotateCcw className="h-3.5 w-3.5" /> Reset
        </Button>
      </div>

      <ResponsiveContainer width="100%" height={380}>
        <ComposedChart key={brushKey} data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <XAxis
            dataKey="time"
            tickFormatter={(v) => formatTick(v, timeframe)}
            tick={{ fontSize: 11, fill: palette.inkSecondary }}
            axisLine={{ stroke: palette.line }}
            tickLine={false}
            minTickGap={40}
          />
          <YAxis
            domain={domain}
            tick={{ fontSize: 11, fill: palette.inkSecondary }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => formatPrice(v, decimals)}
            width={72}
            orientation="right"
          />
          <Tooltip
            content={<CustomTooltip decimals={decimals} palette={palette} />}
            cursor={{ stroke: palette.inkFaint, strokeDasharray: "3 3" }}
          />
          {entry !== undefined && (
            <ReferenceLine
              y={entry}
              stroke={palette.info}
              strokeDasharray="4 4"
              label={{ value: "Entry", position: "insideTopRight", fontSize: 10, fill: palette.info }}
            />
          )}
          {stopLoss !== undefined && (
            <ReferenceLine
              y={stopLoss}
              stroke={palette.negative}
              strokeDasharray="4 4"
              label={{ value: "Stop", position: "insideBottomRight", fontSize: 10, fill: palette.negative }}
            />
          )}
          {target !== undefined && (
            <ReferenceLine
              y={target}
              stroke={palette.positive}
              strokeDasharray="4 4"
              label={{ value: "Target", position: "insideTopRight", fontSize: 10, fill: palette.positive }}
            />
          )}
          <Bar dataKey="wickRange" shape={(props: any) => <WickShape {...props} palette={palette} />} isAnimationActive={false} />
          <Bar dataKey="bodyRange" shape={(props: any) => <BodyShape {...props} palette={palette} />} isAnimationActive={false} />
          <Brush
            dataKey="time"
            height={22}
            stroke={palette.lineStrong}
            fill={palette.surfaceSubtle}
            tickFormatter={() => ""}
            travellerWidth={8}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

function formatTick(iso: string, timeframe: Timeframe) {
  const date = new Date(iso);
  if (timeframe === "1D" || timeframe === "4H") {
    return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  }
  return date.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}
