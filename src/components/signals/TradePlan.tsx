import type { TradeSignal } from "@/types";
import { formatPrice } from "@/lib/utils";

export function TradePlan({ signal }: { signal: TradeSignal }) {
  const items = [
    {
      label: "Entry Zone",
      value: `${formatPrice(signal.entryLow, signal.decimals)} – ${formatPrice(signal.entryHigh, signal.decimals)}`,
      tone: "text-ink",
    },
    {
      label: "Stop Loss",
      value: formatPrice(signal.stopLoss, signal.decimals),
      tone: "text-edge-negative",
    },
    {
      label: "Target",
      value: formatPrice(signal.target, signal.decimals),
      tone: "text-edge-positive",
    },
    {
      label: "Risk / Reward",
      value: `1 : ${signal.riskRewardRatio.toFixed(1)}`,
      tone: "text-ink",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      {items.map((item) => (
        <div key={item.label} className="rounded-md border border-line bg-surface-subtle px-3 py-2.5">
          <p className="text-[11px] font-medium uppercase tracking-wide text-ink-faint">{item.label}</p>
          <p className={`tnum mt-1 text-[15px] font-semibold ${item.tone}`}>{item.value}</p>
        </div>
      ))}
    </div>
  );
}
