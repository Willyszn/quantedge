# QUANTEDGE

A premium quantitative and sentiment trading-analysis dashboard. QUANTEDGE is a
**manual trading decision-support tool** — it analyzes market data, quantitative
signals, sentiment, risk, and historical performance, then presents clear,
explainable trade opportunities. It never places trades automatically.

## Tech stack

- **Vite + React 19 + TypeScript** (strict mode)
- **Tailwind CSS** with a centralized design-token system
- **Radix UI** primitives, composed shadcn-style, in `src/components/ui`
- **TanStack Query** for all server/data state
- **Zustand** for client state (watchlist, UI shell state)
- **Zod + React Hook Form** for the backtest configuration form
- **Recharts** for all charts, including a custom candlestick renderer
- **cmdk** for the Cmd/Ctrl+K command palette, **sonner** for toasts
- Self-hosted **Manrope** (UI) and **IBM Plex Mono** (tabular figures) via `@fontsource`

## Getting started

```bash
npm install
npm run dev       # start the dev server
npm run build     # type-check + production build
npm run lint       # ESLint (flat config, TypeScript-aware)
npm run preview   # preview the production build locally
```

The app runs entirely on local mock data out of the box — no backend or API
keys required.

## Demo data vs. a live backend

QUANTEDGE ships in **demo mode**. Every page is fully explorable using
deterministic, clearly-labeled mock data (see the `DEMO DATA` badge in the
top bar). Nothing in the UI ever presents mock data as if it were live.

To connect a real backend later:

1. Copy `.env.example` to `.env.local`.
2. Set `VITE_DEMO_MODE=false` and `VITE_API_BASE_URL=https://your-backend/api`.
3. That's it — every hook in `src/api/*.ts` already branches on `IS_DEMO_MODE`
   and calls `apiFetch()` against your backend instead of the mock layer in
   `src/mocks/*.ts`. No page or component code needs to change.

Expected REST shape per domain (see each `src/api/*.ts` file for exact paths
and types): `/markets`, `/signals`, `/sentiment`, `/backtests`, `/performance`,
`/alerts`, `/trades/history`.

## Project structure

```
src/
  api/          Typed TanStack Query hooks — the only data-access layer pages use
  mocks/        Deterministic demo-data generators (seeded, so data is stable)
  types/        Shared domain types (Market, Signal, Sentiment, Backtest, ...)
  store/        Zustand stores (watchlist, UI shell state)
  components/
    ui/         Radix-based primitives (button, card, dialog, table, ...)
    layout/     Sidebar, Topbar, mobile nav, page container, app shell
    market/     Market cards, sparkline, candlestick chart, status pill
    signals/    Confidence gauge, factor breakdown, trade plan, signal cards
    sentiment/  Sentiment overview, source rows, timeline
    analytics/  Metric cards, equity curve, drawdown, performance bar chart
    scanner/    The market scanner table (search/sort/filter/pagination)
    command/    Cmd/Ctrl+K command palette
    alerts/     Alerts popover
    common/     Empty/error state components
  pages/        One file per route
```

## Key behaviors

- **Explainability first.** Every signal shows *why* it fired — a per-factor
  breakdown (momentum, trend, volatility, sentiment, risk) with a plain-language
  explanation, not just a number.
- **Never fabricates conclusions.** If a data source fails, the UI shows an
  explicit error/retry state — never a placeholder "BUY" or invented price.
- **Config-driven chart timeframes.** The timeframe buttons on the trade-detail
  chart are driven by each instrument's reported capabilities
  (`useMarketCapabilities`), not a hard-coded list.
- **Backtests are simulations.** Every backtest result is labeled and never
  implies a guarantee of future performance.
- **Responsive by design.** Persistent sidebar on desktop, collapsible on
  tablet, bottom nav + drawer on mobile. Tables scroll horizontally on narrow
  screens rather than being squeezed.

## Dark mode

Light is the shipped default — QUANTEDGE never opts a person into dark mode
based on their OS preference. Dark and "match system" are explicit, persisted
choices via the theme toggle in the top bar or Settings → Appearance.

Every color in the app is a CSS variable (`src/index.css`, both a `:root` and
a `.dark` block), and `tailwind.config.js` points every Tailwind color token
at one of those variables. That means the vast majority of components need no
theme-specific code at all — `bg-canvas`, `text-ink`, `border-line`, and the
`bg-edge-*` signal colors just resolve differently once `.dark` is on
`<html>`.

Two things that *can't* read CSS variables needed explicit handling instead:

- **Recharts/raw SVG** — `src/lib/chartColors.ts` is a small light/dark hex
  palette kept in sync with the CSS variables, consumed via the
  `useResolvedTheme()` hook in every chart component.
- **Solid-fill elements** (primary buttons, the active sidebar item, solid
  badges, the tooltip bubble) — these use a dedicated `primary` /
  `primary-foreground` token pair that co-varies with the theme, rather than
  assuming "ink" is always near-black. Modal/sheet overlays intentionally stay
  a fixed `bg-black/50` scrim in both themes.

## Live alert engine (demo mode only)

`src/hooks/useAlertEngine.tsx` runs for the lifetime of the app and simulates
a live feed on top of the deterministic demo data:

- Every 16 seconds it nudges one factor score per signal
  (`mocks/liveState.ts`), recomputes that signal's confidence and rating from
  the same rules used to generate it, and nudges each instrument's price by a
  small amount.
- It compares the new state against the previous tick and raises a toast +
  an entry in the alerts panel when confidence moves ≥6 points, price enters
  a signal's proposed entry zone, or the risk-conditions factor changes tier.
- Updated data is written straight into the TanStack Query cache
  (`queryClient.setQueryData`), so the dashboard, scanner, and trade-detail
  pages update in the same tick as the toast — no extra polling required.

This only runs when `VITE_DEMO_MODE` is true. Against a real backend, alerts
would come from the backend's `/alerts` endpoint instead.

## Notes on the candlestick chart

`src/components/market/MarketChart.tsx` implements candlesticks on top of
Recharts using the "range bar" technique (`dataKey` resolving to a `[low, high]`
tuple) rather than a dedicated candlestick chart type, since Recharts doesn't
ship one. This keeps rendering correct without reaching into Recharts'
internal scale objects.
