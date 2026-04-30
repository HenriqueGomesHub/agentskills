# Code Review Checklist

A pasteable checklist for self-reviewing your code before opening a PR, or for reviewing someone else's PR.

Copy what's relevant. Skip what isn't. Use the comments to flag what you found.

## Before opening the PR (self-review)

### The basics
- [ ] I read my own diff line by line
- [ ] All tests pass locally
- [ ] Linter passes with no new warnings
- [ ] Formatter has been run
- [ ] Type-checker passes (if applicable)
- [ ] No `console.log`, `print()`, or debugging output left in
- [ ] No commented-out code
- [ ] No `TODO` without a ticket reference

### The diff itself
- [ ] PR is under 400 changed lines (split if larger)
- [ ] Each commit is atomic — one logical change per commit
- [ ] Commit messages follow Conventional Commits
- [ ] No mixing of refactor + feature in the same commit
- [ ] No unrelated changes (drive-by formatting, unrelated typo fixes — those go in separate commits)

### The code
- [ ] Names reveal intent
- [ ] Functions are small (< 20 lines) and do one thing
- [ ] No deep nesting (3+ levels) without good reason
- [ ] No magic numbers or magic strings
- [ ] No empty catch blocks
- [ ] Errors are handled or propagated explicitly
- [ ] No secrets or credentials in code
- [ ] No hardcoded environment-specific values

### Tests
- [ ] New behavior has tests
- [ ] Failure modes have tests, not just happy paths
- [ ] Tests are named in domain language ("rejects orders below minimum"), not implementation language ("test_validate_returns_false")
- [ ] No flaky tests introduced
- [ ] No tests that would still pass if the production code were broken (mutation check: would a deliberate bug be caught?)

### The PR description
- [ ] **What** the PR does (one sentence)
- [ ] **Why** (link to ticket or explain motivation)
- [ ] **How** (brief approach if non-obvious)
- [ ] **What to check** (specific concerns for reviewer)
- [ ] **What I tested** (manual + automated)
- [ ] **Risks / known limitations**

## When reviewing someone else's PR

### Priority 1 — correctness and safety
- [ ] Does this do what it claims?
- [ ] Are the failure modes handled?
- [ ] Are there any obvious security issues? (auth gaps, injection, secrets, PII leakage)
- [ ] Will this break in production at scale, with real data?

### Priority 2 — clarity and maintainability
- [ ] Will I understand this code in 6 months?
- [ ] Are names clear?
- [ ] Are functions small and focused?
- [ ] Is the file structure sensible?
- [ ] Are there any code smells (long method, large class, feature envy, primitive obsession, etc.)?

### Priority 3 — tests
- [ ] Do the tests cover the new behavior?
- [ ] Do they cover failure modes?
- [ ] Do they actually test the contract, or are they testing implementation details?
- [ ] Would they catch a real bug, or just pass while the code is broken?

### Priority 4 — operational
- [ ] Will I be able to debug this from logs and metrics?
- [ ] Are migrations safe (forward and backward)?
- [ ] Is anything obviously O(n²) on user data?
- [ ] Any N+1 query risks?

### Priority 5 — style (last)
- [ ] Style is consistent with the codebase
- [ ] (Don't bikeshed; the linter handles most of this)

## Review tone — how to leave comments

**Be specific.** Don't say "this seems wrong." Say "this will throw if `user` is null on line 42 because we don't check before accessing `user.email`."

**Suggest, don't demand.** "Consider X because Y" lands better than "Use X."

**Distinguish must-fix from nice-to-have.** Prefix optional comments with `nit:` so the author knows what's optional.

**Praise good work.** Reviews that only criticize exhaust authors. A "nice extraction here" goes a long way.

**Don't re-architect in review.** If you'd have designed it completely differently, that's not a PR comment — that's a design discussion.

**Pull and run for non-trivial changes.** Don't review only on the diff for anything more complex than a typo fix.

## Common things to flag

If you see any of these, leave a comment:

- Empty catch blocks
- Functions over 30 lines
- Files over 500 lines
- Magic numbers or strings
- More than 3 positional parameters
- Boolean flags as parameters (sign of a function doing two things)
- Mutation of inputs
- Variables named `data`, `temp`, `thing`, `info`, `obj`
- Commented-out code
- `TODO` without a ticket
- Network/DB/file I/O without error handling
- Loops that perform DB queries (N+1)
- Tests that only cover the happy path
- Code paths with no test coverage
- Inconsistent style with the rest of the codebase

## Review is communication

A code review is a conversation between two professionals about how to ship the best version of this change. It is not a gatekeeping ritual, a status display, or a personal critique.

If you find yourself getting irritated at a PR, step away. Come back later. The author isn't trying to make your life hard.

If you find yourself getting defensive at review feedback, step away. Come back later. The reviewer isn't trying to make you look bad.

The goal: ship better code. That's it.
