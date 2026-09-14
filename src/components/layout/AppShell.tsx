import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { MobileNav } from "./MobileNav";
import { BottomNav } from "./BottomNav";
import { CommandPalette } from "@/components/command/CommandPalette";
import { useAlertEngine } from "@/hooks/useAlertEngine";

export function AppShell() {
  useAlertEngine();

  return (
    <div className="flex h-screen w-full overflow-hidden bg-canvas">
      <Sidebar />
      <MobileNav />
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
      <BottomNav />
      <CommandPalette />
    </div>
  );
}
