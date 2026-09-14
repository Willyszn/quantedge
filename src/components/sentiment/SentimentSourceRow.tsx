import { Newspaper, MessageSquare, Users, Globe } from "lucide-react";
import type { SentimentSource, SentimentSourceType } from "@/types";
import { timeAgo } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

const ICONS: Record<SentimentSourceType, React.ElementType> = {
  news: Newspaper,
  commentary: MessageSquare,
  social: Users,
  macro: Globe,
};

const LABEL_VARIANT: Record<SentimentSource["sentiment"], "positive" | "negative" | "warning" | "default"> = {
  "strong-positive": "positive",
  positive: "positive",
  neutral: "warning",
  negative: "negative",
  "strong-negative": "negative",
};

const LABEL_TEXT: Record<SentimentSource["sentiment"], string> = {
  "strong-positive": "Strong Positive",
  positive: "Positive",
  neutral: "Neutral",
  negative: "Negative",
  "strong-negative": "Strong Negative",
};

export function SentimentSourceRow({ source }: { source: SentimentSource }) {
  const Icon = ICONS[source.type];
  return (
    <div className="flex items-center gap-3 py-3">
      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-surface-subtle text-ink-secondary">
        <Icon className="h-4 w-4" />
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <p className="text-sm font-medium text-ink">{source.label}</p>
          <Badge variant={LABEL_VARIANT[source.sentiment]}>{LABEL_TEXT[source.sentiment]}</Badge>
        </div>
        <p className="mt-0.5 text-xs text-ink-secondary">
          {source.confidence}% confidence · {source.contributionPercent}% contribution · {timeAgo(source.updatedAt)}
        </p>
      </div>
    </div>
  );
}
