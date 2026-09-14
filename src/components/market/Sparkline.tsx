import { Line, LineChart, ResponsiveContainer, YAxis } from "recharts";
import { useResolvedTheme } from "@/hooks/useResolvedTheme";
import { getChartPalette } from "@/lib/chartColors";

export function Sparkline({ data, positive }: { data: number[]; positive: boolean }) {
  const palette = getChartPalette(useResolvedTheme());
  const points = data.map((value, i) => ({ i, value }));
  const color = positive ? palette.positive : palette.negative;

  return (
    <ResponsiveContainer width="100%" height={32}>
      <LineChart data={points} margin={{ top: 2, bottom: 2, left: 0, right: 0 }}>
        <YAxis domain={["dataMin", "dataMax"]} hide />
        <Line type="monotone" dataKey="value" stroke={color} strokeWidth={1.75} dot={false} isAnimationActive={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
