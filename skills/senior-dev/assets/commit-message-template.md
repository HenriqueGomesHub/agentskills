# Conventional Commits Cheat Sheet

A pasteable reference for writing commit messages. Stick to this and your git history becomes a real document.

## The format

```
<type>(<scope>): <subject>

<body — optional, wrap at 72 chars>

<footer — optional>
```

- **type:** required, lowercase (`feat`, `fix`, `refactor`, etc.)
- **scope:** optional, in parentheses (`auth`, `api`, `users`, `billing`)
- **subject:** required, imperative mood, no period, ≤50 chars
- **body:** optional, explains *why* (not what), wrap at 72 chars
- **footer:** optional, references issues and breaking changes

## Types

| Type | When to use | Example |
|---|---|---|
| `feat` | New feature for the user | `feat(auth): add OAuth login` |
| `fix` | Bug fix | `fix(api): handle null user in profile endpoint` |
| `refactor` | Code change that neither fixes a bug nor adds a feature | `refactor(orders): extract OrderValidator class` |
| `docs` | Documentation only | `docs(readme): update setup instructions` |
| `style` | Formatting, whitespace (no logic change) | `style: run prettier on src/` |
| `test` | Adding or modifying tests | `test(orders): cover edge case for zero items` |
| `chore` | Build process, deps, tooling, no production code change | `chore: bump typescript to 5.4` |
| `perf` | Performance improvement | `perf(search): add index on users.email` |
| `build` | Build system or external dependencies | `build: switch to esbuild` |
| `ci` | CI/CD configuration | `ci: add type-check action` |
| `revert` | Revert a previous commit | `revert: feat(auth): add OAuth login` |

## Subject line rules

✅ **Imperative mood:** `add login` (reads as "this commit will *add login*")
❌ Past: `added login` / Present: `adds login`

✅ **No period at the end**
❌ `fix: handle null user.`

✅ **≤ 50 characters**
❌ `fix(api): handle the case where the user object is null when calling the profile endpoint`

✅ **Specific**
❌ `fix: bug fix` / `update: changes` / `wip` / `more stuff`

✅ **Lowercase first letter** (most projects)
❌ `feat(auth): Add OAuth login`

## When to use scope

The scope identifies *what part* of the codebase changed. It's optional but very useful in larger codebases.

Common scopes:
- A feature area: `auth`, `users`, `orders`, `billing`, `search`
- A layer: `api`, `db`, `ui`, `cli`
- A specific module: `OrderService`, `payment-gateway`
- An infrastructure piece: `docker`, `ci`, `deploy`

For tiny projects, scope is often unnecessary. For solo projects with under 20 files, skip it.

## Bad vs good examples

| ❌ Bad | ✅ Good |
|---|---|
| `update` | `fix(auth): refresh token before expiry` |
| `wip` | `feat(orders): partial — order creation flow` |
| `fixed bug` | `fix(api): return 404 instead of 500 for missing user` |
| `more changes` | `refactor(orders): split OrderService into 3 classes` |
| `working on stuff` | `feat(billing): add support for promo codes` |
| `nit` | `style: fix indentation in OrderService` |
| `tests` | `test(users): cover edge cases for password validation` |
| `cleanup` | `refactor(api): remove deprecated v1 endpoints` |

## The body — explain *why*

The diff shows what changed. The body explains why.

When to add a body:
- The change is non-obvious
- There's important context (a ticket, a design decision, a workaround)
- A reader 6 months from now might wonder "why?"

When to skip the body:
- Tiny changes that are self-explanatory (`fix: typo in README`)
- The subject already says enough

### Good body example

```
fix(api): return 404 instead of 500 for missing user

Previously, requests for non-existent users hit a NullPointerException
in the auth middleware before reaching the controller. The exception
was caught too late and returned a generic 500.

Now we check existence in the controller and return 404 explicitly,
which is what the OpenAPI spec promised.

Closes #1234
```

The body explains the bug history, the fix, and links to the ticket.

## The footer

Use the footer for:

### Issue references
```
Closes #1234
Fixes #567
Refs #890
```

### Breaking changes (mark with `BREAKING CHANGE:` or `!` after type)

```
feat(api)!: change /users response format

BREAKING CHANGE: The /users endpoint now returns { users: [...] }
instead of [...]. Clients must update to read response.users.

Migration guide: <link>
```

The `!` and `BREAKING CHANGE:` footer flag this for changelog tools and semantic versioning.

### Co-authors (when pairing or pulling in someone else's work)
```
Co-authored-by: Alice Example <alice@example.com>
```

## Common patterns

### Bug fix with context
```
fix(auth): clear session on logout

Sessions were persisting after logout because we cleared the cookie
but not the server-side session record. Users staying on the same
device could have their session hijacked from a previous login.

Closes SEC-42
```

### New feature, simple
```
feat(orders): add CSV export
```

### New feature, complex
```
feat(billing): support promo codes

Adds a new PromoCode entity with code, discount type (percentage or
fixed), and usage limits. Validates codes at checkout before applying
discount.

- New /promo-codes endpoint for admin management
- Cart now accepts an optional promoCode field
- Frontend shows discount applied at checkout

Closes #2341
```

### Refactor
```
refactor(orders): extract pricing into PriceCalculator

The pricing logic in OrderService had grown to 200 lines and was
called from three places. Extracted to a dedicated class with its
own tests. No behavior change.
```

### Atomic series for one logical change
```
1. refactor(orders): extract pricing into PriceCalculator
2. test(orders): add tests for PriceCalculator
3. feat(orders): support tiered discounts in PriceCalculator
4. test(orders): cover tiered discount scenarios
5. feat(orders): wire tiered discounts into checkout UI
```

Five small commits, each understandable on its own, each revertable independently. Compare to the alternative: one giant `add tiered discounts` commit with 800 lines changed.

## Quick "do I need a body?" test

Look at the subject line.

- "Could a teammate read this and immediately understand what changed and why?" → No body needed.
- "Would a teammate ask 'why?'" → Add a body.

## When you mess up

If you wrote a bad commit message and haven't pushed yet:

```bash
git commit --amend          # edit the most recent message
git rebase -i HEAD~5        # edit messages of the last 5 commits
```

If you've already pushed to a feature branch (and it's just yours):

```bash
git push --force-with-lease
```

If you've pushed to `main` or a shared branch: leave it. Bad commit messages aren't worth rewriting public history.

## The one rule above all

A commit message should answer the question: **"If this commit broke something, what was the author trying to do?"**

If the message answers that, it's good enough. Everything else is polish.
