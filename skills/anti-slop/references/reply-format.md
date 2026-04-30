# Reply Format

The exact structure of the final message after a coding task. Copy this template. Don't decorate it.

---

## Template

```
[One paragraph: what changed and why. Plain language. No marketing.]

Files touched:
- path/to/file.ext — [actual change in 8 words or fewer]
- path/to/other.ext — [actual change in 8 words or fewer]

Audit: [score] — [verdict]
[If any findings worth surfacing: bullet list, severity-prefixed]

Deferred:
- [thing noticed but not fixed] — [one-line reason]

Verify:
- [thing the user should confirm because you couldn't]
```

Sections that have no content get omitted, not left empty with "N/A" or "None."

---

## Examples

### Trivial change, clean audit

```
Fixed the off-by-one in the pagination calculation — the last page was being skipped because the loop used < instead of <=.

Files touched:
- src/lib/pagination.ts — fixed loop bound

Audit: 0 — CLEAN

Verify:
- Run the existing pagination tests; the failing one should now pass.
```

### Multi-file change, one minor finding

```
Added the unsubscribe link to the order-confirmation email and the welcome email. Used the existing `unsubscribeUrl(userId)` helper from `lib/email-links.ts`.

Files touched:
- templates/email/order-confirmation.hbs — added unsubscribe link in footer
- templates/email/welcome.hbs — added unsubscribe link in footer

Audit: 1 — ACCEPTABLE
- LOW: I used the existing helper but the welcome template imports it via a path alias I haven't seen elsewhere in this folder. Worth a glance.

Deferred:
- The password-reset email also has no unsubscribe link, but you asked for the two transactional ones — left it alone.
```

### Bigger change, subagent audit

```
Implemented the OAuth callback handler. Token exchange uses the existing `httpClient`, session writes go through `sessionStore.create` like the email/password flow. New route mounted at /auth/google/callback in the router.

Files touched:
- src/routes/auth.ts — added callback route
- src/auth/google.ts — new file: token exchange + profile fetch
- src/auth/index.ts — exported googleAuth from new module

Audit: 2 — ACCEPTABLE (subagent review)
- LOW: src/auth/google.ts is a new file but the existing auth/ directory has one file per provider, so it matches the pattern.
- LOW: I didn't add tests; the project has tests for email/password auth but no clear pattern for the OAuth providers.

Deferred:
- Refresh token rotation isn't implemented — you didn't ask for it and the existing email/password flow doesn't have it either, so consistency wins for now.

Verify:
- I couldn't test the actual Google token exchange without credentials; the rest is unit-testable. Want me to add tests next?
```

---

## Forbidden in replies

These patterns are LOW slop findings each, MEDIUM if more than two appear:

- **Recap of the user's request.** They wrote it; they remember.
- **Marketing words.** "robust", "elegant", "production-ready", "comprehensive", "enterprise-grade", "battle-tested", "industry-standard", "best-in-class". Cut them all.
- **"Potential future improvements" section.** Unsolicited and noisy. Use the `Deferred` section if you actually deferred something specific.
- **"How to test" section** unless asked or unless verification is genuinely non-obvious.
- **Emojis** unless the user used them first.
- **Process meta-commentary.** "I started by reading...", "I considered three approaches...", "It took some thought to..." — the user wants the result, not the journey.
- **Apologies for things that aren't your fault.** "Sorry the codebase was hard to navigate." Don't.
- **Closing flourish.** "Let me know if you need anything else!" — already implied.
- **Restating what you did in different words** as a closing summary. The opening paragraph said it. Stop.

---

## Length guidance

- Trivial change (<10 lines, one file): 3–5 sentences, no `Files touched` list (mention the file inline).
- Small change (10–50 lines, 1–2 files): use the full template, but each section is brief.
- Medium change (50–200 lines, 2–5 files): full template, no embellishment.
- Large change (>200 lines or >5 files): full template + a short "Decisions" section listing 2–3 non-obvious calls you made and why.

If your reply is longer than the change itself measured in lines, it's slop.
