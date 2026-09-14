import { PageContainer } from "@/components/layout/PageContainer";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { IS_DEMO_MODE } from "@/api/client";
import { useState } from "react";
import { Monitor, Moon, Sun } from "lucide-react";
import { useThemeStore, type ThemePreference } from "@/store/themeStore";
import { cn } from "@/lib/utils";

const THEME_OPTIONS: { value: ThemePreference; label: string; icon: React.ElementType }[] = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "system", label: "System", icon: Monitor },
];

export function Settings() {
  const [confidenceAlerts, setConfidenceAlerts] = useState(true);
  const [entryAlerts, setEntryAlerts] = useState(true);
  const [sentimentAlerts, setSentimentAlerts] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const theme = useThemeStore((s) => s.theme);
  const setTheme = useThemeStore((s) => s.setTheme);

  return (
    <PageContainer title="Settings" subtitle="Manage data mode, alert preferences, and interface behavior.">
      <div className="flex max-w-2xl flex-col gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
            <CardDescription>Light is the default. Dark and System are opt-in.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-2">
              {THEME_OPTIONS.map((option) => {
                const Icon = option.icon;
                const active = theme === option.value;
                return (
                  <button
                    key={option.value}
                    onClick={() => setTheme(option.value)}
                    className={cn(
                      "flex flex-col items-center gap-2 rounded-md border px-3 py-3 text-sm font-medium transition-colors",
                      active
                        ? "border-primary bg-primary text-primary-foreground"
                        : "border-line text-ink-secondary hover:border-line-strong hover:text-ink"
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {option.label}
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Data Mode</CardTitle>
            <CardDescription>Controls whether QUANTEDGE reads from demo data or a live backend.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between rounded-md border border-line bg-surface-subtle px-4 py-3">
              <div>
                <p className="text-sm font-medium text-ink">Current mode</p>
                <p className="text-xs text-ink-secondary">
                  Set VITE_DEMO_MODE=false and VITE_API_BASE_URL to connect a live backend.
                </p>
              </div>
              <Badge variant={IS_DEMO_MODE ? "warning" : "positive"}>{IS_DEMO_MODE ? "DEMO DATA" : "LIVE"}</Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Alert Preferences</CardTitle>
            <CardDescription>Choose which events trigger notifications.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <SettingRow
              label="Confidence changes"
              description="Notify when a signal's confidence increases or decreases meaningfully."
              checked={confidenceAlerts}
              onCheckedChange={setConfidenceAlerts}
            />
            <Separator />
            <SettingRow
              label="Entry zone reached"
              description="Notify when price enters a signal's proposed entry zone."
              checked={entryAlerts}
              onCheckedChange={setEntryAlerts}
            />
            <Separator />
            <SettingRow
              label="Sentiment shifts"
              description="Notify when aggregated sentiment on a watched instrument changes."
              checked={sentimentAlerts}
              onCheckedChange={setSentimentAlerts}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Accessibility</CardTitle>
          </CardHeader>
          <CardContent>
            <SettingRow
              label="Reduce motion"
              description="Minimize chart transitions and animated UI effects."
              checked={reducedMotion}
              onCheckedChange={setReducedMotion}
            />
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
}

function SettingRow({
  label,
  description,
  checked,
  onCheckedChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onCheckedChange: (v: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div>
        <Label className="text-sm font-medium text-ink">{label}</Label>
        <p className="mt-0.5 text-xs text-ink-secondary">{description}</p>
      </div>
      <Switch checked={checked} onCheckedChange={onCheckedChange} />
    </div>
  );
}
