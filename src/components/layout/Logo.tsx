import { cn } from "@/lib/utils";

export function Logo({ collapsed = false, className }: { collapsed?: boolean; className?: string }) {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <svg
        width="26"
        height="26"
        viewBox="0 0 26 26"
        fill="none"
        aria-hidden="true"
        className="shrink-0 text-ink"
      >
        <rect x="1" y="1" width="24" height="24" rx="7" stroke="currentColor" strokeWidth="1.6" />
        <circle cx="13" cy="12" r="5.5" stroke="currentColor" strokeWidth="1.6" />
        <path d="M16.6 15.8L20 19" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      </svg>
      {!collapsed && (
        <span className="text-[15px] font-bold leading-none tracking-tight text-ink">
          QUANT<span className="font-semibold text-ink-secondary">EDGE</span>
        </span>
      )}
    </div>
  );
}
