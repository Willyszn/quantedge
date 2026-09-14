import { Bell, TrendingUp, TrendingDown, Target, ShieldAlert, Newspaper, FlaskConical, CircleDot } from "lucide-react";
import { useAlerts } from "@/api/alertsApi";
import { useUiStore } from "@/store/uiStore";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { timeAgo } from "@/lib/utils";
import type { AlertType } from "@/types";

const ALERT_ICONS: Record<AlertType, React.ElementType> = {
  "new-signal": CircleDot,
  "confidence-up": TrendingUp,
  "confidence-down": TrendingDown,
  "entry-zone": Target,
  "risk-change": ShieldAlert,
  "sentiment-change": Newspaper,
  "backtest-complete": FlaskConical,
};

export function AlertsPanel() {
  const open = useUiStore((s) => s.alertsOpen);
  const setOpen = useUiStore((s) => s.setAlertsOpen);
  const { data: alerts, isLoading } = useAlerts();
  const unreadCount = alerts?.filter((a) => !a.read).length ?? 0;

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative" aria-label="Alerts">
          <Bell className="h-4 w-4" />
          {unreadCount > 0 && (
            <span className="absolute right-1.5 top-1.5 flex h-2 w-2 rounded-full bg-edge-negative" />
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-80 p-0">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <p className="text-sm font-semibold text-ink">Alerts</p>
          {unreadCount > 0 && <Badge variant="info">{unreadCount} new</Badge>}
        </div>
        <ScrollArea className="h-80">
          <div className="flex flex-col divide-y divide-line">
            {isLoading &&
              Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex gap-3 px-4 py-3">
                  <Skeleton className="h-8 w-8 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-3 w-2/3" />
                    <Skeleton className="h-3 w-full" />
                  </div>
                </div>
              ))}
            {alerts?.map((alert) => {
              const Icon = ALERT_ICONS[alert.type];
              return (
                <div key={alert.id} className={cnUnread(alert.read)}>
                  <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-surface-subtle text-ink-secondary">
                    <Icon className="h-3.5 w-3.5" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-ink">{alert.title}</p>
                    <p className="mt-0.5 text-xs leading-relaxed text-ink-secondary">{alert.description}</p>
                    <p className="mt-1 text-[11px] text-ink-faint">{timeAgo(alert.createdAt)}</p>
                  </div>
                  {!alert.read && <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-edge-info" />}
                </div>
              );
            })}
          </div>
        </ScrollArea>
      </PopoverContent>
    </Popover>
  );
}

function cnUnread(read: boolean) {
  return `flex gap-3 px-4 py-3 ${read ? "" : "bg-edge-info-soft/40"}`;
}
