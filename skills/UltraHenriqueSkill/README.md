# UltraHenriqueSkill

Henrique's full coding discipline stack — a behavioral OS for AI-generated code.

This `.skill` package contains seven skills that together shape engineering judgment, security, performance, accessibility, and conflict resolution at code-generation time.

## What's in this package

The bundle ships **five skills**:

- `UltraHenriqueSkill/` — the manifest. Triggers on any coding task and references the others.
- `security-by-construction/` — OWASP ASVS 5.0 / Top 10:2025 rules at generation time.
- `performance-first/` — N+1 prevention, Web Vitals targets, no speculative memoization.
- `accessibility-guardian/` — WCAG 2.2 AA rules targeting the six errors that account for 96% of real-world a11y failures.
- `skill-precedence/` — tiebreaker for when two skills' rules collide.

## Required companions (install separately)

The manifest also references two skills you already have in your `claude-skills` repo:

- `senior-dev/`
- `anti-slop/`

If they aren't installed alongside, the manifest still works — Claude will apply the four bundled skills — but the full discipline stack expects all six sub-skills to be available.

## How to install

### Option 1: Drop into Claude Code's skills folder

Unzip the `.skill` package into your skills directory:

```bash
unzip UltraHenriqueSkill.skill -d ~/.claude/skills/
```

You should end up with:

```
~/.claude/skills/
├── UltraHenriqueSkill/
├── security-by-construction/
├── performance-first/
├── accessibility-guardian/
├── skill-precedence/
├── senior-dev/        ← from your existing claude-skills repo
└── anti-slop/         ← from your existing claude-skills repo
```

### Option 2: Add to your `claude-skills` repo

Copy each folder into `skills/` in your repo, then re-run `scripts/build_all.py` to rebuild your `dist/` archives.

## How it triggers

The manifest's `description` field says "apply to ANY coding task." Claude loads it on every prompt that involves writing, editing, refactoring, or planning code — and from there pulls in the relevant sub-skills based on what the task actually touches.

You don't need to invoke it manually.

## How conflicts are resolved

Two skills demand incompatible code? Most "conflicts" are false (covered in `skill-precedence`'s false-conflict list). When a real conflict remains, the default order is:

1. Correctness
2. Security and Accessibility (same tier)
3. Performance
4. Maintainability
5. Brevity

Lower-tier concerns are named in comments or PR descriptions, never silently dropped.

## Token cost

Manifest: ~326 words. Each sub-skill: ~493–740 words. Full stack loaded: ~3,400 words / ~4,500 tokens.

For comparison: this is roughly the size of a single mid-length Stack Overflow answer. The whole stack pays for itself the first time it prevents an N+1, an inaccessible modal, or a hardcoded secret.

## Sources

Each skill is built on authoritative external standards:

- **security-by-construction** — OWASP ASVS 5.0 (May 2025), OWASP Top 10:2025 (Nov 2025), OWASP Cheat Sheet Series, NIST SP 800-63B
- **performance-first** — Google Web Vitals (LCP/INP/CLS thresholds current as of 2026), React docs on memoization, OWASP MySQL/SQL performance references
- **accessibility-guardian** — WCAG 2.2 (W3C, October 2023), WebAIM Million 2025/2026 reports for failure-frequency targeting
- **skill-precedence** — Hierarchy of Controls (NIOSH/OSHA), Google SRE practices, ISO/IEC 25010 quality model, CIA triad
