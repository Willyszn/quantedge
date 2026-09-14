import type { SentimentTimelinePoint } from "@/types";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useResolvedTheme } from "@/hooks/useResolvedTheme";
import { getChartPalette } from "@/lib/chartColors";

const LABEL_TEXT: Record<SentimentTimelinePoint["label"], string> = {
  "strong-positive": "Strong Positive",
  positive: "Positive",
  neutral: "Neutral",
  negative: "Negative",
  "strong-negative": "Strong Negative",
};

export function SentimentTimeline({ points }: { points: SentimentTimelinePoint[] }) {
  const palette = getChartPalette(useResolvedTheme());
  const gradientId = "sentimentFill";

  return (
    <div>
      <ResponsiveContainer width="100%" height={160}>
        <AreaChart data={points} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={palette.info} stopOpacity={0.22} />
              <stop offset="100%" stopColor={palette.info} stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="time" tick={{ fontSize: 11, fill: palette.inkSecondary }} axisLine={false} tickLine={false} />
          <YAxis hide domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              borderRadius: 8,
              border: `1px solid ${palette.tooltipBorder}`,
              fontSize: 12,
              backgroundColor: palette.tooltipBg,
              color: palette.tooltipText,
            }}
            formatter={(value: any, _name: any, item: any) => [
              `${LABEL_TEXT[item.payload.label as SentimentTimelinePoint["label"]]} (${value})`,
              "Sentiment",
            ]}
          />
          <Area
            type="monotone"
            dataKey="score"
            stroke={palette.info}
            strokeWidth={2}
            fill={`url(#${gradientId})`}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
      <div className="mt-2 flex justify-between px-1 text-[11px] text-ink-faint">
        {points.map((p) => (
          <span key={p.time}>{p.time}</span>
        ))}
      </div>
    </div>
  );
}
