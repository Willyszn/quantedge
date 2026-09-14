import { Menu, Search, User } from "lucide-react";
import { useUiStore } from "@/store/uiStore";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { AlertsPanel } from "@/components/alerts/AlertsPanel";
import { ThemeToggle } from "./ThemeToggle";
import { IS_DEMO_MODE } from "@/api/client";
import { Logo } from "./Logo";
import { useNavigate } from "react-router-dom";

export function Topbar() {
  const setCommandOpen = useUiStore((s) => s.setCommandOpen);
  const setMobileNavOpen = useUiStore((s) => s.setMobileNavOpen);
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-line bg-canvas/95 px-4 backdrop-blur">
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden"
        onClick={() => setMobileNavOpen(true)}
        aria-label="Open navigation"
      >
        <Menu className="h-5 w-5" />
      </Button>

      <div className="md:hidden">
        <Logo />
      </div>

      <button
        onClick={() => setCommandOpen(true)}
        className="ml-1 flex h-9 flex-1 max-w-md items-center gap-2 rounded-md border border-line bg-surface-subtle px-3 text-sm text-ink-secondary transition-colors hover:border-line-strong hover:bg-canvas"
      >
        <Search className="h-4 w-4" />
        <span className="hidden sm:inline">Search instruments, signals, pages…</span>
        <span className="sm:hidden">Search…</span>
        <kbd className="ml-auto hidden rounded border border-line bg-canvas px-1.5 py-0.5 text-[10px] font-medium text-ink-faint sm:inline-block">
          ⌘K
        </kbd>
      </button>

      <div className="ml-auto flex items-center gap-1.5">
        {IS_DEMO_MODE && (
          <Badge variant="warning" className="hidden sm:inline-flex">
            DEMO DATA
          </Badge>
        )}

        <AlertsPanel />
        <ThemeToggle />

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="ml-1 flex items-center gap-2 rounded-md p-1 pr-2 transition-colors hover:bg-surface-subtle">
              <Avatar>
                <AvatarFallback>W</AvatarFallback>
              </Avatar>
              <span className="hidden text-sm font-medium text-ink md:inline">Williams</span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel>Williams Okafor</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onSelect={() => navigate("/settings")}>
              <User className="h-4 w-4" /> Settings
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
