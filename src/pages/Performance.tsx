import {
  usePerformanceMetrics,
  usePerformanceSlices,
  usePortfolioEquityCurve,
} from "@/api/performanceApi";
import { PageContainer } from "@/components/layout/PageContainer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MetricCard } from "@/components/analytics/MetricCard";
import { EquityCurve } from "@/components/analytics/EquityCurve";
import { PerformanceBarChart } from "@/components/analytics/PerformanceBarChart";
import { Skeleton } from "@/components/ui/skeleton";

export function Performance() {
  const { data: metrics, isLoading: metricsLoading } = usePerformanceMetrics();
  const { data: equity, isLoading: equityLoading } = usePortfolioEquityCurve();
  const byInstrument = usePerformanceSlices("instrument");
  const bySignalType = usePerformanceSlices("signal-type");
  const byMonth = usePerformanceSlices("month");
  const byRegime = usePerformanceSlices("regime");

  return (
    <PageContainer title="Performance" subtitle="Portfolio-level results across instruments, signal types, and market regimes.">
      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {metricsLoading || !metrics
          ? Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-24 rounded-lg" />)
          : [
              { label: "Total Return", value: `${metrics.totalReturnPercent}%`, tone: "positive" as const },
              { label: "Win Rate", value: `${metrics.winRate}%` },
              { label: "Profit Factor", value: metrics.profitFactor.toFixed(2) },
              { label: "Max Drawdown", value: `${metrics.maxDrawdownPercent}%`, tone: "negative" as const },
              { label: "Average R", value: metrics.averageR.toFixed(2) },
              { label: "Expectancy", value: metrics.expectancy.toFixed(2) },
              { label: "Best Trade", value: `${metrics.bestTradePercent}%`, tone: "positive" as const },
              { label: "Worst Trade", value: `${metrics.worstTradePercent}%`, tone: "negative" as const },
            ].map((m) => <MetricCard key={m.label} label={m.label} value={m.value} tone={m.tone} />)}
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Portfolio Equity Curve</CardTitle>
        </CardHeader>
        <CardContent>
          {equityLoading || !equity ? <Skeleton className="h-64 w-full" /> : <EquityCurve points={equity} />}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Performance Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="instrument">
            <TabsList>
              <TabsTrigger value="instrument">By Instrument</TabsTrigger>
              <TabsTrigger value="signal">By Signal Type</TabsTrigger>
              <TabsTrigger value="month">By Month</TabsTrigger>
              <TabsTrigger value="regime">By Regime</TabsTrigger>
            </TabsList>
            <TabsContent value="instrument">
              {byInstrument.isLoading || !byInstrument.data ? (
                <Skeleton className="h-60 w-full" />
              ) : (
                <PerformanceBarChart data={byInstrument.data} />
              )}
            </TabsContent>
            <TabsContent value="signal">
              {bySignalType.isLoading || !bySignalType.data ? (
                <Skeleton className="h-60 w-full" />
              ) : (
                <PerformanceBarChart data={bySignalType.data} />
              )}
            </TabsContent>
            <TabsContent value="month">
              {byMonth.isLoading || !byMonth.data ? (
                <Skeleton className="h-60 w-full" />
              ) : (
                <PerformanceBarChart data={byMonth.data} />
              )}
            </TabsContent>
            <TabsContent value="regime">
              {byRegime.isLoading || !byRegime.data ? (
                <Skeleton className="h-60 w-full" />
              ) : (
                <PerformanceBarChart data={byRegime.data} />
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </PageContainer>
  );
}
