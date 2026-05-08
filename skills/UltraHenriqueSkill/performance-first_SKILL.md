---
name: performance-first
description: Generation-time performance rules. Apply when writing data access, async/network code, frontend rendering, loops over collections, or imports/bundling. Encodes decisions made at the keystroke (query shape, indexes, parallelism, image dimensions) — not optimizations that need profiling. Skip for one-off scripts or prototypes where load is negligible.
---

# Performance First

Write code like someone paying the server bill. Rules below catch the things you can get wrong while typing — not the things that need a profiler.

Web Vitals targets baked in: **LCP ≤2.5s, INP ≤200ms, CLS ≤0.1** (75th percentile). INP replaced FID in 2024.

## 1. Data access

- **Never query inside a loop.** Iterating a list and fetching per item is an N+1. Use `JOIN`, `IN (...)`, `prefetch_related`/`select_related` (Django), `include` (Prisma), `JOIN FETCH` (Hibernate), or DataLoader. The N+1 is the single biggest source of "fast in dev, dies in prod."
- **Index foreign keys and any column you filter, sort, or join on.** Defining the column in the model is half the work; the index is the other half. Multi-column queries need composite indexes in the right column order.
- **Select only the columns you need.** No `SELECT *` in app code. Use ORM projections (`select`, `.only()`, `Pick<>` types).
- **Paginate any list that can grow.** Default page size, hard max, cursor-based for large or sorted-by-time datasets. Never return unbounded result sets to a client.
- **Set timeouts on every database, cache, and queue call.** No infinite waits.

## 2. Network and I/O

- **Parallelize independent async work.** `Promise.all`, `asyncio.gather`, errgroups. Two awaits in sequence that don't depend on each other waste a round-trip.
- **Stream large payloads, don't buffer.** File downloads, large JSON exports, LLM completions — stream. Loading 50MB into memory to send it is an OOM waiting to happen.
- **Cache idempotent reads at the closest layer.** HTTP cache headers and DB query caching before reaching for Redis. Cache invalidation is hard — fewer cache layers is fewer bugs.
- **Compress responses** (`gzip`/`brotli`) at the server. One config line, large win.

## 3. Frontend rendering

- **Set `width` and `height` on every image, video, and iframe.** Prevents layout shift — drives CLS.
- **Lazy-load below-the-fold images** (`loading="lazy"`); for the hero/LCP image use `fetchpriority="high"` or `<link rel="preload">`. Drives LCP.
- **Keep the main thread free.** Long-running computation goes in a Web Worker, `requestIdleCallback`, or a server endpoint. Break long tasks into chunks. Drives INP.
- **Virtualize lists over ~100 items.** `react-window`, `TanStack Virtual`, or native `content-visibility: auto` for simple cases.
- **Don't memoize speculatively.** No `useMemo`, `useCallback`, or `React.memo` without a measured render problem. Use them only when (a) the computation is genuinely expensive (filtering 10k items, parsing a large blob), (b) the value is a stable prop to a `React.memo`-wrapped child, or (c) it's a context value. The bookkeeping costs more than trivial work it "saves." Same direction as anti-slop: don't add infrastructure on speculation.

## 4. Loops and data shapes

- **No nested loops over the same data.** Matching two lists is `O(n²)` — build a `Map`/`Set` once, look up in `O(1)`.
- **Hoist invariants out of hot paths.** Compile regex, instantiate schemas, create DB clients at module level — not inside loops or per-request handlers.
- **Iterate, don't materialize, when the dataset is large.** Streams and generators over `.toArray().map().filter()` chains for 100k+ rows.

## 5. Bundle and load

- **Code-split at the route level.** Dynamic imports for heavy or rarely-visited routes. Don't ship the admin bundle to public visitors.
- **Tree-shake-friendly imports.** `import { x } from 'lib'` — never `import * as lib`. Avoid deep paths the bundler can't analyze.
- **Audit before adding a dep.** One full `lodash` or `moment` import can dwarf the rest of the app. Prefer `date-fns`, native `Intl`, or single-function imports.

## Cross-cutting

- **Measure before micro-optimizing.** `EXPLAIN ANALYZE`, Lighthouse, browser perf panel, language profiler. If the number doesn't move, the optimization isn't real.
- **Better algorithm beats clever loop.** Pick the right data structure first; constant-factor tuning second.
