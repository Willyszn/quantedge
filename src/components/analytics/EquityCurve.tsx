import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { EquityPoint } from "@/types";
import { formatPrice } from "@/lib/utils";
import { useResolvedTheme } from "@/hooks/useResolvedTheme";
import { getChartPalette } from "@/lib/chartColors";

export function EquityCurve({ points }: { points: EquityPoint[] }) {
  const palette = getChartPalette(useResolvedTheme());
  const gradientId = "equityFill";

  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={points} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={palette.ink} stopOpacity={0.16} />
            <stop offset="100%" stopColor={palette.ink} stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis
          dataKey="date"
          tickFormatter={(v) => new Date(v).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
          tick={{ fontSize: 11, fill: palette.inkSecondary }}
          axisLine={{ stroke: palette.line }}
          tickLine={false}
          minTickGap={50}
        />
        <YAxis
          tick={{ fontSize: 11, fill: palette.inkSecondary }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => `$${Math.round(v / 1000)}k`}
          width={52}
        />
        <Tooltip
          formatter={(value: any) => [formatPrice(Number(value), 2), "Equity"]}
          labelFormatter={(v: any) => new Date(v).toLocaleDateString()}
          contentStyle={{
            borderRadius: 8,
            border: `1px solid ${palette.tooltipBorder}`,
            fontSize: 12,
            backgroundColor: palette.tooltipBg,
            color: palette.tooltipText,
          }}
        />
        <Area type="monotone" dataKey="equity" stroke={palette.ink} strokeWidth={2} fill={`url(#${gradientId})`} isAnimationActive={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
