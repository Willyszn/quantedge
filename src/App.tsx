import { Suspense, lazy } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/toaster";
import { AppShell } from "@/components/layout/AppShell";
import { ThemeSync } from "@/components/layout/ThemeSync";
import { Skeleton } from "@/components/ui/skeleton";

const Dashboard = lazy(() => import("@/pages/Dashboard").then((m) => ({ default: m.Dashboard })));
const MarketScanner = lazy(() => import("@/pages/MarketScanner").then((m) => ({ default: m.MarketScanner })));
const Watchlist = lazy(() => import("@/pages/Watchlist").then((m) => ({ default: m.Watchlist })));
const TradeSignals = lazy(() => import("@/pages/TradeSignals").then((m) => ({ default: m.TradeSignals })));
const TradeDetail = lazy(() => import("@/pages/TradeDetail").then((m) => ({ default: m.TradeDetail })));
const QuantAnalysis = lazy(() => import("@/pages/QuantAnalysis").then((m) => ({ default: m.QuantAnalysis })));
const Sentiment = lazy(() => import("@/pages/Sentiment").then((m) => ({ default: m.Sentiment })));
const Backtesting = lazy(() => import("@/pages/Backtesting").then((m) => ({ default: m.Backtesting })));
const Performance = lazy(() => import("@/pages/Performance").then((m) => ({ default: m.Performance })));
const TradeHistory = lazy(() => import("@/pages/TradeHistory").then((m) => ({ default: m.TradeHistory })));
const Settings = lazy(() => import("@/pages/Settings").then((m) => ({ default: m.Settings })));
const NotFound = lazy(() => import("@/pages/NotFound").then((m) => ({ default: m.NotFound })));

function RouteFallback() {
  return (
    <div className="mx-auto w-full max-w-[1400px] px-4 pb-24 pt-6 sm:px-6 lg:px-8">
      <Skeleton className="mb-6 h-8 w-56" />
      <Skeleton className="h-[420px] w-full rounded-lg" />
    </div>
  );
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 10_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider delayDuration={150}>
        <ThemeSync />
        <BrowserRouter>
          <Suspense fallback={<RouteFallback />}>
            <Routes>
              <Route element={<AppShell />}>
                <Route path="/" element={<Dashboard />} />
                <Route path="/markets" element={<MarketScanner />} />
                <Route path="/watchlist" element={<Watchlist />} />
                <Route path="/signals" element={<TradeSignals />} />
                <Route path="/signals/:symbol" element={<TradeDetail />} />
                <Route path="/analysis" element={<QuantAnalysis />} />
                <Route path="/sentiment" element={<Sentiment />} />
                <Route path="/backtesting" element={<Backtesting />} />
                <Route path="/performance" element={<Performance />} />
                <Route path="/history" element={<TradeHistory />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<NotFound />} />
              </Route>
            </Routes>
          </Suspense>
        </BrowserRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
