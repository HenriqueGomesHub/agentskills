# Cleanup Checklist

The audit you run BEFORE declaring a task done. Nine categories. Each finding gets a severity weight. Sum the weights for the diff's slop score and apply the verdict.

| Severity | Weight |
|----------|--------|
| CRITICAL | 4 |
| HIGH     | 3 |
| MEDIUM   | 2 |
| LOW      | 1 |

| Score | Verdict | Action |
|-------|---------|--------|
| 0     | CLEAN | Ship |
| 1–3   | ACCEPTABLE | Ship if tradeoffs noted in reply |
| 4–7   | NEEDS WORK | Fix before reporting done |
| 8–14  | SLOPPY | Major rework before reporting done |
| 15+   | DUMPSTER FIRE | Revert the diff and restart with tighter scope |

---

## Category 1 — Stubs & placeholders (HIGH)

Check every file in the diff for:

- `pass` bodies in functions that should have logic
- `...` placeholder bodies (Python type stubs are fine, but not in implementation)
- Naked `TODO` / `FIXME` / `XXX` without an owner or issue link
- `NotImplementedError` / `throw new Error("not implemented")` left over
- Empty `except:` / `catch` blocks
- Placeholder strings like `"replace this"`, `"your name here"`, `"TODO: change me"`
- Functions returning `null` / `undefined` / `None` where real logic was supposed to go

---

## Category 2 — Hallucination signals (CRITICAL)

The most dangerous category — the code "looks right" but is wrong.

- Imports of packages not in `package.json` / `requirements.txt` / `Cargo.toml` / `go.mod` / `Gemfile`
- Method calls on types that don't expose those methods (verify against the actual library, not memory)
- Cross-language idioms (see `hallucination-patterns.md` for the full table)
- API endpoints, env var names, config keys you didn't see in the surrounding code
- Type signatures that don't match the actual library

---

## Category 3 — Hedging & uncertainty (MEDIUM)

Grep the diff for these strings and treat each match as a finding:

- `"should work"` / `"should be fine"` / `"hopefully"`
- `"for now"` / `"temporary"` / `"quick fix"`
- `"not sure if"` / `"I think this"` / `"probably"`
- `"workaround"` without a linked explanation of what it works around
- `// HACK` / `// XXX` without context

If you wrote any of these, either finish the code properly or surface the gap to the user explicitly. Hedging in code is unfinished work pretending to be finished work.

---

## Category 4 — Security & secrets (CRITICAL)

Block-on-find. Even one of these is a HIGH-or-above finding.

- API keys, tokens, secrets in literal strings (look for: `sk_`, `pk_`, `ghp_`, `github_pat_`, `xox`, `AKIA`, `AIza`, `sk-ant-`, `hf_`, `glpat-`, `eyJ` JWT prefix)
- Database connection strings with credentials
- Hardcoded `password = "..."` / `secret = "..."` / `token = "..."`
- `eval()` / `exec()` / `Function()` with user input
- SQL string concatenation with user input (use parameterized queries)
- Disabled SSL verification (`verify=False`, `rejectUnauthorized: false`)
- CORS wide-open in production code (`Access-Control-Allow-Origin: *`)
- `debug=True` / `DEBUG = true` in code paths that ship to production
- Private keys in source (look for `-----BEGIN`)

---

## Category 5 — Dead code & noise (LOW, but accumulates)

- Unused imports added during the change
- Unused variables / parameters added speculatively
- Old function being replaced — left commented-out instead of deleted
- Commented-out code blocks of any kind
- Debug residue: `console.log`, `print()`, `pp`, `dump()`, `debugger`, `breakpoint()`, `pdb.set_trace()`
- Empty files or empty functions
- Trailing whitespace, missing final newlines (if the rest of the file is consistent)

---

## Category 6 — Defensive bloat (MEDIUM)

- `try/catch` around code that has no real failure mode or no real handling
- Null / undefined guards for type-system-prevented conditions
- `if (x === undefined && x === null)` and similar redundant predicates
- Re-validation of arguments already validated upstream
- Logging that just says "entering function X" / "leaving function X"
- Wrapping standard library calls in your own thin wrapper "just in case"

---

## Category 7 — Over-engineering (MEDIUM)

- New abstraction with fewer than 3 concrete uses (rule of three)
- Single-method classes (unless framework-mandated)
- Empty classes, empty interfaces, empty modules
- Generic / template / dependency-injection scaffolding for code with one caller
- Strategy / factory / builder patterns where a function would do
- Configuration files for values that have one site of use
- Renaming a clear name to a more "professional" name

---

## Category 8 — Documentation mismatch (MEDIUM)

- Docstrings that don't match the actual parameters or return value (you changed the signature without updating the doc, OR you wrote a doc that drifted from the code)
- Comments that describe code from a previous version
- README sections that reference deleted files / functions
- Type annotations that lie about the actual runtime type

---

## Category 9 — Structural smells (LOW)

- Files >500 lines after your change (consider splitting if you're already touching the file substantially)
- Functions >50 lines after your change
- Functions with >5 parameters after your change
- Sequential numbered variables (`item1`, `item2`, `item3` — should be a list)
- Deeply nested code (>4 levels of indentation)

---

## Cross-cutting checks (apply once for the diff as a whole)

After the per-category checks, look at the diff in aggregate:

### Diff-shape audit
- **Files touched > planned?** If you said "1–2 files" in Phase 1 and the diff touches 6, find out which 4 are slop and revert them.
- **Lines changed > 3× the smallest possible diff?** Same question.
- **Did you touch any file that wasn't strictly necessary for the request?** Revert those edits.

### Outside-the-code audit
- **Did you create any of the following without being asked?**
  - README / CHANGELOG / docs
  - Test files
  - Example / demo files
  - Summary markdown files (`CHANGES.md`, etc.)
  - New config files
- **Did you bump dependency versions?** Did you add dependencies?
- **Did you reformat code you didn't functionally change?**

Each "yes" above is a HIGH finding.

### Reply-shape audit (run on your own draft reply before sending)
- **Marketing language?** ("robust", "elegant", "production-ready", "comprehensive", "enterprise-grade", "battle-tested")
- **Recap of the user's request?**
- **"Potential future improvements" section?**
- **Unsolicited "how to test it" section?**
- **Emojis the user didn't use first?**

Each "yes" is a LOW finding individually but they compound — three of them in one reply is a MEDIUM finding.

---

## Reporting findings

After scoring, the reply must include:

```
Audit: [score] — [verdict]
Findings: [list, severity-prefixed, one line each]
Fixed before reporting: [list]
Not fixed (with reason): [list]
```

If the verdict is NEEDS WORK or worse, **do not declare the task done**. Fix the findings, re-audit, then report.
