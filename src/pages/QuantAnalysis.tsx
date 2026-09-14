import { useMemo, useState } from "react";
import { useSignals } from "@/api/signalApi";
import { useMarketQuotes } from "@/api/marketApi";
import { PageContainer } from "@/components/layout/PageContainer";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Sparkline } from "@/components/market/Sparkline";

export function QuantAnalysis() {
  const { data: signals, isLoading } = useSignals();
  const { data: quotes } = useMarketQuotes();
  const [symbol, setSymbol] = useState<string | null>(null);

  const activeSymbol = symbol ?? signals?.[0]?.symbol ?? "";
  const signal = signals?.find((s) => s.symbol === activeSymbol);
  const quote = quotes?.find((q) => q.symbol === activeSymbol);

  const risk = useMemo(() => {
    if (!signal) return null;
    const stopDistance = Math.abs(
      (signal.direction === "long" ? signal.entryLow : signal.entryHigh) - signal.stopLoss
    );
    const mid = (signal.entryLow + signal.entryHigh) / 2;
    const stopDistancePercent = (stopDistance / mid) * 100;
    return {
      stopDistancePercent,
      positionRiskPercent: Math.min(2, stopDistancePercent * 0.35),
    };
  }, [signal]);

  return (
    <PageContainer
      title="Quantitative Analysis"
      subtitle="Momentum, trend, volatility, and risk broken down per instrument."
      actions={
        <Select value={activeSymbol} onValueChange={setSymbol}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Instrument" />
          </SelectTrigger>
          <SelectContent>
            {signals?.map((s) => (
              <SelectItem key={s.symbol} value={s.symbol}>
                {s.symbol}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      }
    >
      {isLoading || !signal ? (
        <Skeleton className="h-[420px] rounded-lg" />
      ) : (
        <Card>
          <CardContent className="pt-5">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-ink">{signal.symbol}</h2>
                <p className="text-xs text-ink-secondary">{signal.name}</p>
              </div>
              {quote && (
                <div className="w-28">
                  <Sparkline data={quote.spark} positive={quote.changePercent >= 0} />
                </div>
              )}
            </div>

            <Tabs defaultValue="momentum">
              <TabsList>
                <TabsTrigger value="momentum">Momentum</TabsTrigger>
                <TabsTrigger value="trend">Trend</TabsTrigger>
                <TabsTrigger value="volatility">Volatility</TabsTrigger>
                <TabsTrigger value="risk">Risk</TabsTrigger>
              </TabsList>

              <TabsContent value="momentum">
                <AnalysisSection
                  score={signal.scores.momentum}
                  rows={[
                    { label: "Momentum Score", value: `${signal.scores.momentum}/100` },
                    {
                      label: "Rate of Change",
                      value: signal.factors.find((f) => f.id === "momentum")?.statusLabel ?? "—",
                    },
                    { label: "Trend Strength", value: `${signal.scores.trend}/100` },
                  ]}
                  explanation={signal.factors.find((f) => f.id === "momentum")?.explanation}
                />
              </TabsContent>

              <TabsContent value="trend">
                <AnalysisSection
                  score={signal.scores.trend}
                  rows={[
                    { label: "Direction", value: signal.direction === "long" ? "Bullish bias" : "Bearish bias" },
                    { label: "Trend Score", value: `${signal.scores.trend}/100` },
                    {
                      label: "Moving-Average Relationship",
                      value: signal.factors.find((f) => f.id === "trend")?.statusLabel ?? "—",
                    },
                  ]}
                  explanation={signal.factors.find((f) => f.id === "trend")?.explanation}
                />
              </TabsContent>

              <TabsContent value="volatility">
                <AnalysisSection
                  score={signal.factors.find((f) => f.id === "volatility")?.score ?? 0}
                  rows={[
                    {
                      label: "Volatility Regime",
                      value: signal.factors.find((f) => f.id === "volatility")?.statusLabel ?? "—",
                    },
                    {
                      label: "Volatility Score",
                      value: `${signal.factors.find((f) => f.id === "volatility")?.score ?? 0}/100`,
                    },
                  ]}
                  explanation={signal.factors.find((f) => f.id === "volatility")?.explanation}
                />
              </TabsContent>

              <TabsContent value="risk">
                <AnalysisSection
                  score={signal.scores.risk}
                  rows={[
                    { label: "Risk Score", value: `${signal.scores.risk}/100` },
                    { label: "Expected Risk/Reward", value: `1 : ${signal.riskRewardRatio.toFixed(1)}` },
                    { label: "Stop Distance", value: risk ? `${risk.stopDistancePercent.toFixed(2)}%` : "—" },
                    {
                      label: "Suggested Position Risk",
                      value: risk ? `${risk.positionRiskPercent.toFixed(2)}% of capital` : "—",
                    },
                  ]}
                  explanation={signal.factors.find((f) => f.id === "risk-conditions")?.explanation}
                />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </PageContainer>
  );
}

function AnalysisSection({
  score,
  rows,
  explanation,
}: {
  score: number;
  rows: { label: string; value: string }[];
  explanation?: string;
}) {
  const color = score >= 70 ? "bg-edge-positive" : score >= 45 ? "bg-edge-warning" : "bg-edge-negative";
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-[220px_1fr]">
      <div>
        <p className="text-[11px] font-medium uppercase tracking-wide text-ink-faint">Composite Score</p>
        <p className="tnum mt-1 text-3xl font-bold text-ink">{score}</p>
        <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-surface-subtle">
          <div className={`h-full rounded-full ${color}`} style={{ width: `${score}%` }} />
        </div>
      </div>
      <div>
        <dl className="divide-y divide-line">
          {rows.map((row) => (
            <div key={row.label} className="flex items-center justify-between py-2 text-sm">
              <dt className="text-ink-secondary">{row.label}</dt>
              <dd className="tnum font-medium text-ink">{row.value}</dd>
            </div>
          ))}
        </dl>
        {explanation && <p className="mt-3 text-xs leading-relaxed text-ink-secondary">{explanation}</p>}
      </div>
    </div>
  );
}
