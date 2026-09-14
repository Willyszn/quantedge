import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { FlaskConical } from "lucide-react";
import { useRunBacktest } from "@/api/backtestApi";
import { STRATEGIES } from "@/mocks/backtests";
import { INSTRUMENTS } from "@/mocks/instruments";
import { PageContainer } from "@/components/layout/PageContainer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MetricCard } from "@/components/analytics/MetricCard";
import { EquityCurve } from "@/components/analytics/EquityCurve";
import { DrawdownChart } from "@/components/analytics/DrawdownChart";
import { PerformanceBarChart } from "@/components/analytics/PerformanceBarChart";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/StatusStates";
import { formatPrice } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

const schema = z.object({
  symbol: z.string().min(1),
  strategy: z.string().min(1),
  startDate: z.string().min(1),
  endDate: z.string().min(1),
  initialCapital: z.number().positive(),
  riskPerTradePercent: z.number().min(0.1).max(10),
  slippageBps: z.number().min(0).max(50),
  commissionBps: z.number().min(0).max(50),
});

type FormValues = z.infer<typeof schema>;

const defaultValues: FormValues = {
  symbol: "XAUUSD",
  strategy: STRATEGIES[0],
  startDate: "2025-01-01",
  endDate: "2025-09-01",
  initialCapital: 100000,
  riskPerTradePercent: 1,
  slippageBps: 2,
  commissionBps: 1,
};

export function Backtesting() {
  const { mutate, data: result, isPending } = useRunBacktest();
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues });

  function onSubmit(values: FormValues) {
    mutate({
      symbol: values.symbol,
      strategy: values.strategy,
      startDate: values.startDate,
      endDate: values.endDate,
      initialCapital: values.initialCapital,
      riskPerTradePercent: values.riskPerTradePercent,
      slippageBps: values.slippageBps,
      commissionBps: values.commissionBps,
    });
  }

  return (
    <PageContainer title="Backtesting" subtitle="Configure and run a historical simulation before risking capital.">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[340px_1fr]">
        <Card className="h-fit">
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="symbol">Instrument</Label>
                <Select value={watch("symbol")} onValueChange={(v) => setValue("symbol", v)}>
                  <SelectTrigger id="symbol">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {INSTRUMENTS.map((inst) => (
                      <SelectItem key={inst.symbol} value={inst.symbol}>
                        {inst.symbol}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex flex-col gap-1.5">
                <Label htmlFor="strategy">Strategy</Label>
                <Select value={watch("strategy")} onValueChange={(v) => setValue("strategy", v)}>
                  <SelectTrigger id="strategy">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {STRATEGIES.map((s) => (
                      <SelectItem key={s} value={s}>
                        {s}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="startDate">Start date</Label>
                  <Input id="startDate" type="date" {...register("startDate")} />
                </div>
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="endDate">End date</Label>
                  <Input id="endDate" type="date" {...register("endDate")} />
                </div>
              </div>

              <div className="flex flex-col gap-1.5">
                <Label htmlFor="initialCapital">Initial capital ($)</Label>
                <Input id="initialCapital" type="number" step="1000" {...register("initialCapital", { valueAsNumber: true })} />
                {errors.initialCapital && <p className="text-xs text-edge-negative">Enter a valid amount.</p>}
              </div>

              <div className="flex flex-col gap-1.5">
                <Label htmlFor="riskPerTradePercent">Risk per trade (%)</Label>
                <Input id="riskPerTradePercent" type="number" step="0.1" {...register("riskPerTradePercent", { valueAsNumber: true })} />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="slippageBps">Slippage (bps)</Label>
                  <Input id="slippageBps" type="number" step="0.5" {...register("slippageBps", { valueAsNumber: true })} />
                </div>
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="commissionBps">Commission (bps)</Label>
                  <Input id="commissionBps" type="number" step="0.5" {...register("commissionBps", { valueAsNumber: true })} />
                </div>
              </div>

              <Button type="submit" disabled={isPending} className="mt-1">
                <FlaskConical className="h-4 w-4" />
                {isPending ? "Running backtest…" : "Run Backtest"}
              </Button>
              <p className="text-[11px] leading-relaxed text-ink-faint">
                Backtest results are simulated on historical data and never guarantee future performance.
              </p>
            </form>
          </CardContent>
        </Card>

        <div className="flex flex-col gap-6">
          {isPending ? (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-24 rounded-lg" />
              ))}
            </div>
          ) : !result ? (
            <EmptyState
              icon={FlaskConical}
              title="No backtest run yet"
              description="Configure your parameters on the left and run a simulation to see performance results."
            />
          ) : (
            <>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <MetricCard label="Total Return" value={`${result.totalReturnPercent}%`} tone={result.totalReturnPercent >= 0 ? "positive" : "negative"} />
                <MetricCard label="Win Rate" value={`${result.winRate}%`} />
                <MetricCard label="Profit Factor" value={result.profitFactor.toFixed(2)} />
                <MetricCard label="Max Drawdown" value={`${result.maxDrawdownPercent}%`} tone="negative" />
                <MetricCard label="Sharpe-Like" value={result.sharpeLike.toFixed(2)} />
                <MetricCard label="Total Trades" value={String(result.totalTrades)} />
                <MetricCard label="Avg Trade" value={`${result.averageTradePercent}%`} />
                <MetricCard label="Expectancy" value={result.expectancy.toFixed(2)} />
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Equity Curve</CardTitle>
                </CardHeader>
                <CardContent>
                  <EquityCurve points={result.equityCurve} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Drawdown</CardTitle>
                </CardHeader>
                <CardContent>
                  <DrawdownChart points={result.equityCurve} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Monthly Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <PerformanceBarChart
                    data={result.monthlyReturns.map((m) => ({ label: m.month, returnPercent: m.returnPercent, winRate: 0, trades: 0 }))}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Trade Results</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="max-h-96 overflow-y-auto rounded-md border border-line">
                    <Table>
                      <TableHeader>
                        <TableRow className="hover:bg-transparent">
                          <TableHead>Entry</TableHead>
                          <TableHead>Exit</TableHead>
                          <TableHead>Direction</TableHead>
                          <TableHead className="text-right">R Multiple</TableHead>
                          <TableHead className="text-right">P&L %</TableHead>
                          <TableHead>Outcome</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {result.trades.slice(0, 40).map((trade) => (
                          <TableRow key={trade.id}>
                            <TableCell className="text-ink-secondary">
                              {new Date(trade.entryDate).toLocaleDateString()}
                            </TableCell>
                            <TableCell className="text-ink-secondary">
                              {new Date(trade.exitDate).toLocaleDateString()}
                            </TableCell>
                            <TableCell className="capitalize">{trade.direction}</TableCell>
                            <TableCell className="tnum text-right">{trade.rMultiple.toFixed(2)}R</TableCell>
                            <TableCell
                              className={`tnum text-right font-medium ${
                                trade.pnlPercent >= 0 ? "text-edge-positive" : "text-edge-negative"
                              }`}
                            >
                              {trade.pnlPercent.toFixed(2)}%
                            </TableCell>
                            <TableCell>
                              <Badge variant={trade.outcome === "win" ? "positive" : trade.outcome === "loss" ? "negative" : "default"}>
                                {trade.outcome}
                              </Badge>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </PageContainer>
  );
}
