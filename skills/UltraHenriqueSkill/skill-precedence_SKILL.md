---
name: skill-precedence
description: Tiebreaker for when rules from different skills collide on the same line of code. Invoke only when two skills point at the same code with opposing demands AND satisfying both isn't obviously possible. Not a filter applied on every keystroke — most code engages one skill or none.
---

# Skill Precedence

Most "conflicts" dissolve when stated clearly. Before invoking this skill, check the false-conflict list — that's where ~80% of apparent collisions go. Only when a real conflict remains does the default order apply.

## When this skill applies

- Two of `senior-dev`, `anti-slop`, `security-by-construction`, `performance-first`, `accessibility-guardian` engage on the same line.
- Their rules demand incompatible code shapes (not just different emphasis).
- No phrasing satisfies both.

If only one skill engages, or skills agree, this is not a precedence question — proceed normally.

## False conflicts (resolve these without invoking precedence)

- **"Security says validate, `performance-first` says skip validation in the hot path"** — Validate once at the trust boundary; downstream code trusts validated input. No conflict.
- **"`senior-dev` says extract, `anti-slop` says don't extract"** — Both agree: extract on the second caller, not the first. No conflict.
- **"`performance-first` says memoize, `anti-slop` says don't memoize"** — Both agree: don't memoize without a measured reason. No conflict.
- **"`accessibility-guardian` says use `<button>`, `performance-first` says a `<div>` would be faster"** — The performance delta is unmeasurable; the a11y cost is concrete. No conflict.
- **"Security says block this user input, `accessibility-guardian` says don't add a CAPTCHA"** — Both agree. Use rate limiting, server-side validation, behavioral signals. CAPTCHAs are not the security answer.

## Default order (when a real conflict remains)

1. **Correctness** — the code does what it claims. A fast wrong answer is not faster. A pretty wrong answer is not prettier.
2. **Security and Accessibility** — same tier, no trade-offs between them. Both have legal and ethical weight. If a security control creates an a11y barrier (CAPTCHAs, time limits, color-only error states), the design is wrong — find one that satisfies both. Same in reverse.
3. **Performance** — measurable user-impacting performance (Web Vitals, query latency, bundle size). Not micro-optimization.
4. **Maintainability** — readability, locality, simplicity (the `senior-dev` / `anti-slop` concerns).
5. **Brevity** — fewer lines, fewer abstractions.

## What "winning" means

When a higher-tier rule wins:

- The higher-tier rule's constraint is met in the generated code.
- The lower-tier rule's concern is **named** — in a comment, TODO, or PR description. Never silently dropped.
- The first attempt should still try to satisfy both. Most apparent conflicts are solvable with a different approach (different data structure, different control flow, different library). Default order is the fallback when that fails.

## What this skill is not

- Not a filter on every keystroke. Most code engages one skill or none.
- Not a replacement for thinking. The order is a default; a stated reason can override it for a specific situation.
- Not a hierarchy of skill importance. Lower-tier skills aren't less valuable — they're the tiebreaker for collisions, nothing more.
