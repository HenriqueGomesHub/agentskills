---
name: UltraHenriqueSkill
description: Henrique's full coding discipline stack. Apply to ANY coding task — writing, editing, reviewing, refactoring, or planning code in any language or framework. Loads six behavioral skills that together shape engineering judgment, security, performance, accessibility, and conflict resolution. Skip only for read-only operations (explaining code, answering conceptual questions) where no code is produced.
---

# UltraHenriqueSkill

This is a manifest. It does not contain rules itself — it tells you which skills to consult on any coding task. All six are in scope simultaneously; `skill-precedence` resolves collisions between them.

## Skills in this stack

1. **`senior-dev`** — engineering discipline: clean code, naming, structure, error handling, code review judgment. Applies to all code.
2. **`anti-slop`** — surgical minimal-diff changes; no dead code, defensive bloat, scope creep, or unsolicited tests/docs/comments. Applies to all code edits.
3. **`security-by-construction`** — generation-time security rules. Applies when code touches untrusted input, persistence, auth, sessions, secrets, file uploads, or outbound calls.
4. **`performance-first`** — generation-time performance rules. Applies to data access, async/network code, frontend rendering, loops over collections, or imports/bundling.
5. **`accessibility-guardian`** — WCAG 2.2 AA defaults. Applies when writing user-facing UI (HTML, JSX/TSX, Vue/Svelte, forms, modals, custom widgets).
6. **`skill-precedence`** — tiebreaker when two of the above collide on the same line. Most apparent conflicts are false; consult this skill before forcing a trade-off.

## How to apply

- All applicable skills engage in parallel — not in sequence.
- For each line of code, ask which skills' triggers fire. Apply each one's rules.
- When two skills demand incompatible code shapes, consult `skill-precedence` (false conflicts first, default order second).
- Lower-tier concerns are named in comments/PRs when overridden — never silently dropped.

## What this manifest doesn't replace

- Reading the actual `SKILL.md` of each sub-skill for the rule details. This file lists what's in scope; it does not duplicate the rules.
- Project-specific conventions (`CLAUDE.md`, `AGENTS.md`, repo style guides). Those override defaults from this stack when they conflict on style/idiom; safety and a11y rules still apply.
