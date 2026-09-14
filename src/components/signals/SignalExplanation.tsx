import { Sparkles } from "lucide-react";

export function SignalExplanation({ narrative }: { narrative: string }) {
  return (
    <div className="rounded-md border border-line bg-surface-subtle p-4">
      <div className="mb-2 flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-ink-secondary" />
        <p className="text-sm font-semibold text-ink">Why QUANTEDGE likes this setup</p>
      </div>
      <p className="text-sm leading-relaxed text-ink-secondary">{narrative}</p>
    </div>
  );
}
