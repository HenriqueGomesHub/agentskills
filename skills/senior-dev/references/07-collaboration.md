# Collaboration: Commits, Branches, PRs, Code Reviews

Load this when working with git, writing commit messages, creating PRs, doing code reviews, or planning branching strategy.

## The mental model

Git is a tool for **communication** as much as version control. Your commits and PRs are messages to:
- Your future self ("why did I change this?")
- Your teammates ("what is this person doing?")
- Reviewers ("what should I check?")
- The historian who will someday `git blame` to understand a bug

Treat the git history as a deliverable. A clean history is as valuable as clean code.

## Atomic commits

**One logical change per commit.** That's the rule. The unit isn't a file or a session — it's a *single coherent change*.

If you fixed a bug AND refactored a helper AND updated docs in one commit, you've made it impossible to:
- Review the changes (reviewers can't tell what's intentional)
- Revert just the broken part if one piece breaks production
- Understand the history later

### What "atomic" looks like in practice

You spent the afternoon on a feature. You should commit something like:

```
1. refactor: extract pricing logic into PriceCalculator
2. test: add tests for PriceCalculator
3. feat: add discount code support to PriceCalculator
4. test: add tests for discount code logic
5. feat: wire discount code UI into checkout
6. docs: document discount code API
```

Six commits, each understandable on its own, each revertable independently.

### When you mess up the granularity

Use `git rebase -i` (interactive rebase) before pushing to clean up. Squash typo-fix commits, split overstuffed commits, reorder. The history future-readers see should be the *clean* version, not the messy reality of how you actually worked.

After pushing to a shared branch, **don't rewrite history** — that breaks everyone else.

## Conventional Commits

A standardized commit message format that makes history scannable and tooling possible (changelogs, semantic versioning, etc.).

### Format

```
<type>(<scope>): <subject>

<body — optional, wrapped at 72 chars>

<footer — optional, references issues>
```

### Types (the common ones)

| Type | Meaning | Example |
|---|---|---|
| `feat` | New feature for the user | `feat(auth): add OAuth login` |
| `fix` | Bug fix | `fix(api): handle null user in profile endpoint` |
| `refactor` | Code change that neither fixes a bug nor adds a feature | `refactor(orders): extract OrderValidator class` |
| `docs` | Documentation only | `docs(readme): update setup instructions` |
| `style` | Formatting, whitespace (no code change) | `style: run prettier on src/` |
| `test` | Adding or modifying tests | `test(orders): cover edge case for zero items` |
| `chore` | Build process, deps, tooling | `chore: bump typescript to 5.4` |
| `perf` | Performance improvement | `perf(search): add index on users.email` |
| `build` | Build system changes | `build: switch to esbuild` |
| `ci` | CI/CD config | `ci: add GitHub Action for type-check` |
| `revert` | Revert a previous commit | `revert: feat(auth): add OAuth login` |

### Subject line rules

- **Imperative mood:** "add login" not "added login" / "adds login". Reads as "this commit will *add login*."
- **No period at the end.**
- **50 characters or fewer.**
- **Lowercase first letter** (style preference, but consistent in most projects).
- **Be specific:** `fix: handle null user` not `fix: bug fix`.

### Bad vs good commit messages

| Bad | Good |
|---|---|
| `update` | `fix(auth): refresh token before expiry` |
| `wip` | `feat(orders): partial — order creation flow` |
| `fixed bug` | `fix(api): return 404 instead of 500 for missing user` |
| `more changes` | `refactor(orders): split OrderService into 3 classes` |
| `asdf` | (don't even ask) |

### When to use the body

Use the body to explain **why**, not what. The diff shows what changed; the body explains the reasoning.

```
fix(api): return 404 instead of 500 for missing user

Previously, requests for non-existent users hit a NullPointerException
in the auth middleware before reaching the controller. This caught the
exception too late and returned a generic 500.

Now we check existence in the controller and return 404 explicitly,
which is what the OpenAPI spec promised.

Closes #1234
```

## Branching strategy: GitHub Flow

For most teams (especially small ones, solo founders, and SaaS products), **GitHub Flow** is the right default:

1. `main` is always deployable.
2. To work on anything, create a branch from `main`.
3. Push commits to that branch.
4. Open a Pull Request when ready (or earlier, as draft, for visibility).
5. Review, iterate, merge into `main`.
6. Delete the branch.

That's it. Simple, fast, low overhead.

### Branch naming

Match your team's convention. Common patterns:

- `feature/short-description`
- `fix/short-description`
- `chore/short-description`
- `[ticket-id]/short-description` — useful if you use issue tracking
- `[your-name]/short-description` — useful in solo or small-team contexts

Examples: `feature/oauth-login`, `fix/token-refresh-bug`, `JIRA-1234/discount-codes`.

### When NOT to use GitHub Flow

GitHub Flow assumes you have continuous deployment or near-continuous releases. If your release cycle is monthly with formal QA periods, look at **Git Flow** (with `develop`, `release/*`, `hotfix/*` branches). For most modern projects, this is overkill.

## Pull Requests / Merge Requests

The PR is where humans review what's about to enter production. Treat it as a deliverable.

### Keep PRs small

**Target: under 400 changed lines. Hard ceiling: 800.**

Why: research consistently shows that beyond ~400 lines, reviewers' ability to find issues drops sharply. A 200-line PR gets a real review; a 2000-line PR gets a rubber stamp ("LGTM").

If a feature legitimately needs 2000 lines, break it into 5 PRs that each ship a coherent slice.

### PR structure

Every PR description should answer:

1. **What does this PR do?** One sentence.
2. **Why?** Link to the ticket / explain the motivation.
3. **How?** Brief overview of the approach (only if non-obvious).
4. **What should the reviewer check?** Specific concerns: "Pay attention to the cache invalidation logic in `OrderCache.ts`."
5. **What did you test?** Manual steps, automated tests added, edge cases considered.
6. **Risks / known limitations.**

A template:

```markdown
## What
Adds OAuth login via Google.

## Why
Closes #1234. Users have requested social login; reduces signup friction.

## How
- Added `/auth/google` route that redirects to Google OAuth
- Added callback handler that exchanges code for token, fetches profile, finds-or-creates user
- Added `googleId` column to `users` table

## Testing
- Unit tests for the callback handler (happy path + 3 error cases)
- Manual test: signed in with Google account, verified user creation, signed out, signed back in

## Risks
- Rate limit on Google's API: 10k requests/day. Should be plenty.
- New `googleId` column requires a migration; deployed before merging.
```

### Self-review before requesting review

Before clicking "Request review":
1. Read your own diff. Yes, every line.
2. Run the tests locally.
3. Check the formatting/linter.
4. Remove debugging code, console.logs, commented-out blocks.
5. Verify your commit history is clean.

You'll catch 80% of what a reviewer would flag, and you'll respect their time.

## Code review

### As a reviewer

**Goal: ship better code, not show off.**

What to look for, in priority order:

1. **Correctness** — does it do what it claims? Does it handle the failure modes?
2. **Clarity** — will I understand this in 6 months? Will my teammate?
3. **Tests** — are they meaningful? Do they cover the new behavior?
4. **Security** — are there obvious leaks, injection risks, auth gaps?
5. **Performance** — is anything obviously O(n²) on user data, or making N+1 queries?
6. **Style** — last priority. Linters and formatters handle this; reviewers shouldn't.

**Don't:**
- Bikeshed on style (let the linter argue)
- Demand changes for personal preferences (own it: "nit: I'd prefer X but no need to change")
- Block on minor issues (use "approve with comments" liberally)
- Re-architect in review (if you'd do it differently, that's a different PR's worth of design discussion)

**Do:**
- Be specific: "This will throw if `user` is null on line 42" not "this seems wrong"
- Suggest, don't demand: "Consider X because Y" not "Use X"
- Praise good work: "Nice extraction here" — reviewers usually only criticize, which exhausts authors
- Distinguish must-fix from nice-to-have: prefix nits with "nit:" so authors know what's optional
- Pull the branch and run it for non-trivial changes

### As an author

- **Don't take feedback personally.** The reviewer is critiquing the code, not you.
- **Respond to every comment.** Either fix, or explain why not. Don't ignore.
- **If you disagree, push back.** Reviewers are sometimes wrong. Discuss it.
- **Don't argue minor stylistic points.** Pick your battles.
- **Update tests when changing logic.** Always.
- **Re-request review after substantive changes.** Don't merge silently after addressing comments.

## Merge strategies

Three options when merging a PR to main:

1. **Merge commit** — preserves the full branch history (including messy WIP commits). Useful for long-lived feature branches; produces noisy histories for normal PRs.
2. **Squash and merge** — combines all commits in the PR into one clean commit on main. Best default for most teams: clean main history, the PR's individual commits remain visible in the PR view.
3. **Rebase and merge** — replays each commit linearly onto main. Preserves atomic commits but rewrites their hashes. Useful if you've been disciplined about atomic commits within the PR.

For most teams: **squash by default**. It produces the cleanest, most navigable main history.

## .gitignore discipline

Things that should never be committed:
- Secrets (API keys, passwords, tokens) — use `.env` files, listed in `.gitignore`
- `node_modules/`, `venv/`, `target/`, build artifacts
- IDE config (unless your team has agreed on shared settings)
- OS files (`.DS_Store`, `Thumbs.db`)
- Personal scratch files

If a secret has been committed: **change it immediately**. Removing it from history doesn't help — it's already public on the internet by the time you notice.

## Pre-commit hooks

Automate the boring checks. Common pre-commit hooks:

- Linter (eslint, ruff, golangci-lint)
- Formatter (prettier, black, gofmt)
- Type-check (tsc --noEmit, mypy)
- Test runner (sometimes — but slow tests should run in CI, not pre-commit)
- Secret scanner (detect-secrets, gitleaks)

If a check is automatable, automate it. Reviewers should be reviewing logic, not catching missing semicolons.

## A senior's PR review checklist

Before approving:

- [ ] I understand what this PR does and why
- [ ] Tests cover the new behavior including failure modes
- [ ] No obvious security issues (auth, injection, secrets, PII leakage)
- [ ] Error handling is present where needed
- [ ] The diff is clean (no debugging code, no commented-out code, no console.logs)
- [ ] The commit history is sensible
- [ ] If I had to maintain this in 6 months, I could
- [ ] If something goes wrong in production, the logs/telemetry will tell me

If yes to all: approve. If no, leave specific actionable comments.
