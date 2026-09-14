import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";

interface MetricCardProps {
  label: string;
  value: string;
  tone?: "positive" | "negative" | "neutral";
  hint?: string;
}

export function MetricCard({ label, value, tone = "neutral", hint }: MetricCardProps) {
  return (
    <Card>
      <CardContent className="pt-5">
        <p className="text-[11px] font-medium uppercase tracking-wide text-ink-faint">{label}</p>
        <p
          className={cn(
            "tnum mt-1.5 text-2xl font-bold",
            tone === "positive" && "text-edge-positive",
            tone === "negative" && "text-edge-negative",
            tone === "neutral" && "text-ink"
          )}
        >
          {value}
        </p>
        {hint && <p className="mt-1 text-xs text-ink-secondary">{hint}</p>}
      </CardContent>
    </Card>
  );
}
