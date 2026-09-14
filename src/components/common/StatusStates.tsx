import { AlertTriangle, Inbox } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
  className,
}: {
  icon?: React.ElementType;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-line py-14 text-center", className)}>
      <Icon className="h-6 w-6 text-ink-faint" />
      <p className="text-sm font-medium text-ink">{title}</p>
      {description && <p className="max-w-xs text-xs text-ink-secondary">{description}</p>}
      {action}
    </div>
  );
}

export function ErrorState({
  title = "Data unavailable",
  description = "We couldn't load this data. Check your connection and try again.",
  onRetry,
  className,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col items-center justify-center gap-2 rounded-lg border border-line bg-surface-subtle py-14 text-center", className)}>
      <AlertTriangle className="h-6 w-6 text-edge-negative" />
      <p className="text-sm font-medium text-ink">{title}</p>
      <p className="max-w-xs text-xs text-ink-secondary">{description}</p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry} className="mt-1">
          Retry
        </Button>
      )}
    </div>
  );
}
