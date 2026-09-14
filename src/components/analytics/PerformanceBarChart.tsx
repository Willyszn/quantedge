import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { PerformanceBySlice } from "@/types";
import { useResolvedTheme } from "@/hooks/useResolvedTheme";
import { getChartPalette } from "@/lib/chartColors";

export function PerformanceBarChart({ data }: { data: PerformanceBySlice[] }) {
  const palette = getChartPalette(useResolvedTheme());

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <XAxis dataKey="label" tick={{ fontSize: 11, fill: palette.inkSecondary }} axisLine={{ stroke: palette.line }} tickLine={false} />
        <YAxis
          tick={{ fontSize: 11, fill: palette.inkSecondary }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => `${v}%`}
          width={40}
        />
        <Tooltip
          formatter={(value: any, name: any) => [`${value}%`, name === "returnPercent" ? "Return" : name]}
          contentStyle={{
            borderRadius: 8,
            border: `1px solid ${palette.tooltipBorder}`,
            fontSize: 12,
            backgroundColor: palette.tooltipBg,
            color: palette.tooltipText,
          }}
        />
        <Bar dataKey="returnPercent" radius={[4, 4, 0, 0]} isAnimationActive={false}>
          {data.map((entry) => (
            <Cell key={entry.label} fill={entry.returnPercent >= 0 ? palette.positive : palette.negative} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
