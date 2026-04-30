# Code Rules

The full list of what to never add, never touch, and never write outside the code itself. Read in full before writing the first line of a non-trivial change.

Each rule has a one-line statement, a short rationale, and a concrete example of the slop it prevents.

---

## Section A — What never to add to the code

### A1. No speculative parameters, options, or hooks
**Why:** YAGNI. Speculation is wrong 90% of the time, and the wrong abstraction costs more than no abstraction.
**Slop:**
```python
def send_email(to, subject, body, retry_count=3, retry_delay=1, on_failure=None, dry_run=False, ...):
```
**When user asked:** "send an email to a single recipient when an order ships."

### A2. No defensive try/catch unless the failure is real and meaningfully handled
**Why:** Catch-and-rethrow, catch-and-log, catch-and-ignore — all slop. Hides bugs. The existing top-level handler is almost always better than a local one.
**Slop:**
```js
try {
  return JSON.parse(input);
} catch (e) {
  console.error(e);
  throw e;
}
```
**Allowed:** catch where you have a real fallback, a real recovery path, or a real translation to a domain error.

### A3. No null/undefined guards for type-system-prevented conditions
**Why:** If the type contract says non-null, the guard is dead code that lies about the contract.
**Slop (TypeScript, `user: User` is non-nullable):**
```ts
function getEmail(user: User) {
  if (!user) return null;
  return user.email;
}
```

### A4. No comments narrating code
**Why:** Comments that restate what the code does add noise, drift out of sync, and signal that the code itself isn't clear.
**Slop:**
```python
# Increment the counter
counter += 1

# Loop through users
for user in users:
    # Send the email
    send(user)
```
**Allowed:** comments that explain *why* (a non-obvious decision, a workaround for a known bug, a reference to a spec/issue).

### A5. No new abstraction below the rule of three
**Why:** Premature abstraction locks in the wrong shape and costs more to undo than to write.
- One use → inline.
- Two uses → duplicate, with a `// duplicate of X` comment if non-obvious.
- Three uses → extract.

### A6. No new files unless the existing structure can't host the change
**Why:** New files are the loudest form of slop. They fragment navigation, break grep flow, and signal "the AI didn't bother to find where this belongs."
**Test:** if you can't name an existing file in the same module that the change logically belongs to within 10 seconds, ask the user.

### A7. No reformatting of code you didn't functionally change
**Why:** Diff noise hides the real change, bloats reviews, and triggers merge conflicts.
**Common slop:** "while I was in this file I also reordered the imports." No.

### A8. No new dependencies without explicit user approval
**Why:** Dependencies are a long-term liability. Approval should be conscious.
**Includes:** npm, pip, gem, cargo, go mod, sub-libraries within a monorepo. Even tiny ones (`is-odd`, `left-pad`).
**Process:** mention the need in the reply, propose 1–2 candidates with one-line justifications, wait for the call.

### A9. No "marker" comments
**Why:** Slop signature.
**Forbidden:** `// added by Claude`, `// AI-generated`, `// new`, `// updated`, `// fixed bug here`, naked `// TODO`, `// FIXME` without an issue or owner.

### A10. No debug residue
**Why:** Loose `console.log`, `print()`, `pp`, `dump()`, `breakpoint()`, `pdb.set_trace()`, `debugger;` left in committed code is the most basic slop tell.
**If the project has a real logger pattern**, use that. Otherwise, remove before declaring done.

### A11. No cross-language leakage
**Why:** AI models trained on multi-language corpora frequently leak idioms across language boundaries. This is a hallucination signal.
**Slop in Python:**
```python
items.push("new")          # JS → use .append()
if items.length > 10:      # JS → use len()
console.log("debug")       # JS → use print()
const x = 5                # JS → no `const` in Python
value === other            # JS → use ==
user.toString()            # Java → use str()
fmt.Println("hello")       # Go → use print()
```
See `hallucination-patterns.md` for the full leakage table by language.

### A12. No hallucinated imports / fake APIs
**Why:** AI generates plausible-looking imports for packages that don't exist or method names that the library doesn't have. Always verify.
**Process:** if you import a package or call a method you didn't see in the surrounding code, verify it exists before declaring done. `package.json` / `requirements.txt` / `Cargo.toml` membership is the minimum check.

### A13. No mutable default arguments (Python) / no shared mutable defaults (any language)
**Slop:**
```python
def add_item(item, items=[]):  # bug: shared across calls
    items.append(item)
    return items
```

### A14. No bare `except:` / `catch (e)` without a type
**Why:** Catches `SystemExit`, `KeyboardInterrupt`, programming errors. Hides bugs.

### A15. No hedging language in code or comments
**Why:** "should work", "for now", "hopefully", "I think this handles it", "quick fix" — these are admissions that the code isn't done. Either finish it or surface the gap explicitly to the user.

### A16. No hardcoded secrets, keys, tokens, URLs to staging/prod
**Why:** Security and environment portability. Always env vars or config.
**Includes:** API keys, DB connection strings, OAuth client secrets, webhook URLs, signed tokens, internal hostnames.

### A17. No single-method classes or empty classes
**Why:** Over-engineering signal. A class with one method is a function with extra steps.
**Exception:** classes that satisfy a framework contract (e.g., a Django model, a React class component if the codebase uses them).

---

## Section B — What never to touch

### B1. Unrelated code in files you're editing
Saw a bug on the way? Saw an old TODO? Note it at the end of the reply. Do not fix it in the same change.

### B2. Code style inconsistent with the file you're editing
Match what's there. Quotes, semicolons, indentation, naming, import order. If the file uses `snake_case`, you use `snake_case`. If it uses double quotes, you use double quotes. Do not "improve" it.

### B3. Dependency versions
Do not bump versions to fix something unless that's the explicit task.

### B4. Generated / vendored / migration files
Never edit by hand: lock files, migration files (in projects with migration tooling), generated types, vendored copies of third-party code, build artifacts, `.min.js` files.

### B5. Tests for code you're changing — without thinking
If you change a function's signature or behavior, the existing tests are the spec. Read them. If they break, update them — but with the user's awareness, not silently.

---

## Section C — What never to write outside the code

### C1. No README updates unless asked
Even if your change "could be documented." If documentation matters to the user, they'll ask.

### C2. No CHANGELOG entries unless the project clearly maintains one and the user asked
Look for a `CHANGELOG.md` with recent dated entries. If it's stale or missing, don't start.

### C3. No new test files unless asked or the project clearly requires them
"Clearly requires" = there's a test file pattern adjacent to every source file in the relevant area, AND the testing convention is obvious from the existing files. Otherwise, mention "tests would be valuable here for X reason — want me to add them?" at the end of the reply.

### C4. No example/demo files
Never create `example.py`, `demo.html`, `usage-sample.tsx`. If the user wants an example, they'll ask.

### C5. No "summary of changes" markdown files written to disk
The chat reply IS the summary. Files like `CHANGES.md`, `WHAT_I_DID.md`, `IMPLEMENTATION_NOTES.md` are pure slop.

### C6. No new config files unless the existing config genuinely cannot host the change
Same rule as A6 but for `.eslintrc`, `tsconfig.json`, `.prettierrc`, etc. Add to the existing one.

### C7. No commit messages that say "various improvements" or "updates"
Commit messages must say what changed and why, in one line plus optional body. If you're committing on the user's behalf, follow their existing commit style — read the last 5 commits with `git log --oneline -5` first.

---

## Section D — Stop conditions (when to stop and ask)

Stop and ask the user, do not guess, when any of these happen:

- The "smallest change" requires modifying >3 files
- You can't find an existing pattern in the repo for what you're being asked to do
- The change requires a new dependency
- The change requires deleting code you don't fully understand
- The change requires modifying generated/vendored/migration files
- The user's request contains an ambiguity that materially affects the diff shape
- You catch yourself "interpreting" what the user "probably meant" — that's the moment to ask, not to guess

Asking one clarifying question costs less than producing a 200-line slop diff.
