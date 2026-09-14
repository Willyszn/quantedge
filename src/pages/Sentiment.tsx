import { useState } from "react";
import { useAggregateSentiment, useSentiment } from "@/api/sentimentApi";
import { getSentimentSymbols } from "@/mocks/sentiment";
import { PageContainer } from "@/components/layout/PageContainer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { SentimentOverview } from "@/components/sentiment/SentimentOverview";
import { SentimentSourceRow } from "@/components/sentiment/SentimentSourceRow";
import { SentimentTimeline } from "@/components/sentiment/SentimentTimeline";

export function Sentiment() {
  const [symbol, setSymbol] = useState<string>("MARKET");
  const aggregate = useAggregateSentiment();
  const perSymbol = useSentiment(symbol);
  const active = symbol === "MARKET" ? aggregate : perSymbol;

  return (
    <PageContainer
      title="Market Sentiment"
      subtitle="Aggregated sentiment across news, commentary, social, and macro sources."
      actions={
        <Select value={symbol} onValueChange={setSymbol}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Scope" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="MARKET">Overall Market</SelectItem>
            {getSentimentSymbols().map((s) => (
              <SelectItem key={s} value={s}>
                {s}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      }
    >
      {active.isLoading || !active.data ? (
        <Skeleton className="h-[500px] rounded-lg" />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>{symbol === "MARKET" ? "Overall Sentiment" : `${symbol} Sentiment`}</CardTitle>
            </CardHeader>
            <CardContent>
              <SentimentOverview split={active.data.split} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Sentiment Sources</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="divide-y divide-line">
                {active.data.sources.map((source) => (
                  <SentimentSourceRow key={source.id} source={source} />
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Sentiment Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <SentimentTimeline points={active.data.timeline} />
            </CardContent>
          </Card>
        </div>
      )}
    </PageContainer>
  );
}
