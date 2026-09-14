import { Link } from "react-router-dom";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import type { MarketQuote } from "@/types";
import { formatPercent, formatPrice } from "@/lib/utils";
import { Sparkline } from "./Sparkline";
import { MarketStatus } from "./MarketStatus";
import { Card } from "@/components/ui/card";

export function MarketCard({ quote }: { quote: MarketQuote }) {
  const positive = quote.changePercent >= 0;

  return (
    <Link to={`/signals/${quote.symbol}`}>
      <Card className="group h-full p-4 transition-shadow hover:shadow-panel">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-semibold text-ink">{quote.symbol}</p>
            <p className="mt-0.5 line-clamp-1 text-xs text-ink-secondary">{quote.name}</p>
          </div>
          <MarketStatus status={quote.status} />
        </div>

        <div className="mt-3 flex items-end justify-between gap-2">
          <div>
            <p className="tnum text-xl font-semibold text-ink">{formatPrice(quote.price, quoteDecimals(quote))}</p>
            <p
              className={`tnum mt-0.5 flex items-center gap-1 text-xs font-medium ${
                positive ? "text-edge-positive" : "text-edge-negative"
              }`}
            >
              {positive ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
              {formatPercent(quote.changePercent)}
            </p>
          </div>
          <div className="w-24">
            <Sparkline data={quote.spark} positive={positive} />
          </div>
        </div>
      </Card>
    </Link>
  );
}

function quoteDecimals(quote: MarketQuote) {
  if (quote.assetClass === "crypto") return 1;
  if (quote.symbol.includes("JPY")) return 2;
  if (quote.assetClass === "index") return 1;
  return quote.assetClass === "forex" ? 4 : 2;
}
