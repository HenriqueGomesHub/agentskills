# anti-slop

A Claude Code skill that prevents AI slop — dead code, over-engineering, defensive bloat, scope creep, hallucinated dependencies, unsolicited docs/tests, and verbose theatrical replies.

## What "slop" means here

Code or output that *looks right* but isn't what you wanted: extra abstractions you didn't ask for, defensive try/catches around code that can't fail, comments narrating obvious lines, README updates nobody requested, made-up package imports, JS idioms in your Python file. AI tools produce slop because they optimize for "looking thorough." This skill flips that.

## What's in this skill

| File | What it is |
|------|------------|
| `SKILL.md` | The orchestration layer Claude reads when the skill triggers — phases, principles, pointers |
| `references/code-rules.md` | Full prohibitions during writing — what never to add, never touch, never write |
| `references/cleanup-checklist.md` | 9-category audit Claude runs before declaring done, with severity weights and scoring |
| `references/reply-format.md` | Exact format for the final message — concise, structured, no fluff |
| `references/prompt-discipline.md` | Rules for writing prompts to downstream AI tools (Cursor, sub-agents) |
| `references/hallucination-patterns.md` | Common AI failure modes — cross-language leakage, fake imports, made-up APIs |
| `scripts/scan.sh` | Optional pre-commit shell scanner for high-frequency slop patterns |
| `hooks/` | Optional Claude Code hooks for deterministic enforcement |

## Install

### Global (all your projects)
```bash
mkdir -p ~/.claude/skills
cp -r anti-slop ~/.claude/skills/anti-slop
```

### Project-local (one project only)
```bash
mkdir -p .claude/skills
cp -r anti-slop .claude/skills/anti-slop
git add .claude/skills/anti-slop
git commit -m "Add anti-slop skill"
```

The skill triggers automatically on any coding task. You can also invoke it explicitly with `/anti-slop` if you want to be sure.

## Optional: enable hooks for deterministic enforcement

The skill is *advisory* — Claude reads it and usually follows it. Hooks are *deterministic* — they always run. For non-negotiables (like blocking secrets in commits), use a hook.

See `hooks/README.md` for the recommended `.claude/settings.json` configuration.

## Optional: pre-commit hook with the scanner

Add to `.git/hooks/pre-commit`:
```bash
#!/usr/bin/env bash
~/.claude/skills/anti-slop/scripts/scan.sh
```

The scanner exits non-zero on a NEEDS WORK or worse verdict, blocking the commit until the slop is fixed.

## How the skill works in a session

When you ask Claude to do anything code-related, the skill triggers and Claude follows a four-phase loop:

1. **Plan** — restate the request, scope the diff, find the existing pattern, name the verification path
2. **Code** — write the minimal change following `code-rules.md`
3. **Audit** — score the diff against `cleanup-checklist.md`; for non-trivial changes, delegate to a subagent for unbiased review
4. **Report** — concise structured reply per `reply-format.md`

The audit produces a slop score (0+) and a verdict (CLEAN → DUMPSTER FIRE). NEEDS WORK or above means Claude fixes the findings before declaring the task done.

## Tuning

If a rule doesn't match your project (e.g., your project genuinely wants Claude to add tests), edit the relevant reference file directly. The skill is yours — it's not meant to be sacred.

If hooks are blocking something legitimate, set `ANTI_SLOP_ALLOW_DOCS=1` (for the docs hook) or `ANTI_SLOP_ALLOW_SECRETS=1` (you almost never want this) in your shell.
