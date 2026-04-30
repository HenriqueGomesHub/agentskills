---
name: anti-slop
description: Enforce surgical, minimal-diff code changes and prevent AI slop — dead code, over-engineering, defensive bloat, scope creep, cross-language leakage, unsolicited tests/docs/comments, and hallucinated dependencies. Use this skill on EVERY coding task without exception, including small edits, bug fixes, refactors, new features, and prompts written for downstream tools (Cursor, sub-agents). Skip ONLY for read-only operations (reading files, answering questions, explaining code) where no edits are produced. Trigger even when the user does not explicitly ask for it.
---

# Anti-Slop

Discipline for code changes. Slop is what happens when an AI optimizes for "looking thorough" instead of "solving the problem." This skill flips that.

**The four phases** — every coding task runs through all four. No exceptions for "small" tasks, because that's where slop accumulates fastest.

1. **Plan** — understand the request, scope the diff, find the existing pattern
2. **Code** — write the minimal change, following the rules in `references/code-rules.md`
3. **Audit** — self-review with the checklist in `references/cleanup-checklist.md` BEFORE declaring done
4. **Report** — concise, structured reply per `references/reply-format.md`

If the task is non-trivial (>30 lines of changes, multi-file, or you wrote the code yourself), delegate the audit to a fresh subagent — see "Subagent self-review" below. Inline self-review has sunk-cost bias baked in.

---

## Phase 1 — Plan (BEFORE touching anything)

State four things, in your head or out loud, before the first edit. If you can't answer all four, stop and ask.

1. **Request, restated in one sentence.** If you find yourself adding "and also..." or "while we're in here...", that's scope creep. Cut it.
2. **Smallest change that satisfies it.** Not the most elegant. Not the most extensible. Smallest. Estimate the diff in files-touched and lines-changed. Aim for the lower bound.
3. **Existing pattern in this repo.** Search before writing — `Grep` for similar function names, similar imports, similar file structures. Duplicating a helper that already exists is slop. Inventing a new convention when one exists is slop.
4. **Verification path.** How will you know it works? Existing test, manual check, lint, type-check, screenshot? If there's no path, ask the user for one or propose one before coding. Verification is the single highest-leverage thing for non-slop output.

If the task touches >2 files OR modifies code you don't fully understand, **enter Plan Mode first** (or write the plan to a comment / scratch note). Implementing without a plan is how scope creep happens.

---

## Phase 2 — Code (write the minimal diff)

Read `references/code-rules.md` in full before writing the first line. It contains the hard rules — what never to add, what never to touch, what never to write outside the code itself.

**Headline rules** (full list in the reference):

- **No speculative code.** YAGNI. No "might be useful later" parameters, hooks, options, abstractions.
- **No defensive try/catch unless the failure is real and handled meaningfully.** Catch-and-rethrow is slop. Let it crash to the existing handler.
- **No null guards for type-system-prevented conditions.** If `user` is typed non-null, no `if (!user) return`.
- **No comments narrating code.** Comments explain *why*, never *what*.
- **No new abstraction below the rule of three.** One use = inline. Two = duplicate. Three = extract.
- **No new files unless the existing structure genuinely cannot host the change.**
- **No reformatting code you didn't functionally change.**
- **No new dependencies without explicit user approval.**
- **No README, CHANGELOG, test-file, example-file, or summary-doc additions** unless explicitly requested or the project clearly requires them.
- **No touching unrelated code.** Note bugs you spot at the end. Do not fix them in the same change.

---

## Phase 3 — Audit (BEFORE declaring done)

Run the full checklist in `references/cleanup-checklist.md`. It's structured as nine categories, each with concrete checks. Treat it as part of the task, not optional polish.

Categorize every finding by severity, score the diff, and report the verdict:

| Score | Verdict | Action |
|-------|---------|--------|
| 0 | CLEAN | Ship |
| 1–3 | ACCEPTABLE | Ship if tradeoffs noted |
| 4–7 | NEEDS WORK | Fix before reporting done |
| 8–14 | SLOPPY | Major rework |
| 15+ | DUMPSTER FIRE | Revert and restart with tighter scope |

Severity weights: CRITICAL=4 · HIGH=3 · MEDIUM=2 · LOW=1. Full category list and weights in `references/cleanup-checklist.md`.

### Subagent self-review (for non-trivial changes)

When **you wrote** the code AND the diff is non-trivial (>30 lines, multi-file, or anything user-facing), do not self-review inline — the conversation context contains your design rationale, which biases you toward softening findings. Spawn a fresh subagent:

> "Use a subagent to run the anti-slop cleanup audit on the files I just changed: [list]. Use the checklist in `~/.claude/skills/anti-slop/references/cleanup-checklist.md`. Report findings only — don't fix anything."

The subagent has zero conversation history. No ego, no rationalization. Treat its findings as authoritative.

For trivial changes (<30 lines, single file, no user-facing impact), inline audit is fine.

---

## Phase 4 — Report

Use the format in `references/reply-format.md`. Concise. Structured. No fluff.

The chat reply should contain:
- **What changed** — one paragraph, plain language
- **Files touched** — bullet list, one line per file with the actual change
- **Audit result** — score and verdict, with any findings the user should know
- **Deferred** — things you noticed but did not fix, one line each with reason
- **Verify** — what you couldn't confirm yourself

Forbidden in the reply: recap of the user's request · marketing words ("robust", "elegant", "production-ready", "enterprise-grade") · "potential future improvements" · unsolicited "how to test it" · emojis (unless the user uses them) · summaries of how hard the task was · meta-commentary about your process.

---

## Special case — writing prompts for downstream AI tools (Cursor, sub-agents)

When the deliverable is a prompt rather than code, the same discipline applies to the prompt. See `references/prompt-discipline.md` for the full rules.

Quick version: one concrete task per prompt · name the canonical reference file in the codebase · forbid the slop categories explicitly in the prompt · specify expected diff scope (files-touched / lines-changed budget).

---

## Context discipline (applies throughout)

Slop scales with context bloat. Long sessions with cluttered context produce sloppier code. Three rules:

1. **`/clear` between unrelated tasks.** Switching from "fix login bug" to "design a new feature" without clearing means the new task carries the failed approaches and noise from the old one.
2. **Use subagents for investigation.** "Explore how X works" reads many files and burns context. Delegate to a subagent that returns a summary instead of dumping all the file contents into the main conversation.
3. **If you've corrected the same issue twice in a session, `/clear` and restart.** A clean session with a sharper prompt outperforms a long session with accumulated corrections.

---

## When in doubt

The default is **less**. Less code. Fewer files. Fewer comments. Fewer abstractions. Shorter reply. If you're debating whether to add something, the answer is no. If the user wants more, they will ask.

---

## Reference files

- `references/code-rules.md` — full list of writing-time prohibitions, with examples
- `references/cleanup-checklist.md` — 9-category audit, severity weights, scoring
- `references/reply-format.md` — exact output structure for the final message
- `references/prompt-discipline.md` — rules for writing prompts to downstream AI tools
- `references/hallucination-patterns.md` — common AI failure modes (cross-language leakage, fake imports, made-up APIs)
- `hooks/` — optional hook scripts to enforce rules deterministically (see `hooks/README.md`)
- `scripts/scan.sh` — optional pre-commit shell scanner for the highest-frequency slop patterns
