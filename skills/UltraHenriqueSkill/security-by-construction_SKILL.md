---
name: security-by-construction
description: Generation-time security rules. Apply when writing code that touches untrusted input, persistence, auth/sessions, secrets, file uploads, or outbound calls. Skip for pure UI, isolated algorithms, or scripts with no user data, network, or secrets.
---

# Security by Construction

Prescriptive defaults. Deviate only by naming the reason in a comment or PR — never silently.

## 1. Data in

- **Parameterize every query.** No string concatenation or interpolation into SQL, NoSQL filters, or raw ORM. Use prepared statements or query builders. Includes admin and "internal" code.
- **Validate input with a schema.** Zod, Joi, Pydantic, class-validator. Reject unknown fields. Validate type, length, range, format. Treat headers, cookies, and query strings as input too.
- **Authorize in the query, not after the fetch.** Scope by `tenantId` / `userId` in the `WHERE` clause. Fetch-then-check leaks existence and creates IDOR holes. Never load by client-supplied ID without an ownership predicate.
- **Escape output for its destination.** Rely on framework auto-escape (React, Jinja, ERB) for HTML. For redirects, allowlist destinations — never redirect to a URL from the request.

## 2. Endpoints

- **Default deny.** Every route has an explicit auth check. Mark public routes explicitly; mount auth at the router level so a forgotten decorator can't expose a route.
- **Authorize the action, not just the session.** "Logged in" ≠ "allowed." Check this user can perform this action on this resource.
- **Fail closed.** If auth, validation, or a permission check throws, the request is denied. Never wrap a security check in `try/catch` that continues. Never default a missing claim to "allowed."
- **Cap body size and rate-limit auth endpoints.** Login, password reset, signup, and any expensive operation. Without limits, every endpoint is a DoS vector.
- **No internals in error responses.** Log stacks server-side; return stable error codes/messages. No SQL errors, file paths, or stack frames over the wire.

## 3. Auth, sessions, cookies

- **Use the platform's auth library.** NextAuth, Lucia, Passport, Devise, ASP.NET Identity, Spring Security. Hand-rolled auth is the highest-risk thing in a codebase — if unavoidable, flag it loudly.
- **Hash passwords with bcrypt, cost ≥12** (max input 72 bytes). Argon2id (19 MiB / 2 iter / parallelism 1) when available and not memory-constrained. Never SHA-*, MD5, unsalted, or reversibly "encrypted."
- **Session tokens: CSPRNG, ≥128 bits.** `crypto.randomBytes(32)`, `secrets.token_urlsafe(32)`. Never `Math.random`, timestamps, or sequential IDs.
- **Rotate the session token on privilege change** (login, role elevation, password change, MFA enrollment). Reusing the pre-login token enables session fixation.
- **Session cookies: `HttpOnly`, `Secure`, `SameSite=Lax`** (`Strict` for sensitive flows). Set idle and absolute timeouts.
- **Default to server-side sessions for first-party web apps; reserve JWTs for stateless service-to-service or short-lived API access tokens.** JWTs can't be revoked instantly and tempt people to put state in them.
- **JWTs: pin the algorithm.** Reject `alg: none`. Verify against an explicit allowlist, never the token's own header. JWTs are signed, not encrypted — no PII or role decisions in the payload. Short expiry (≤15 min) with refresh tokens for longevity.
- **Log auth events** (login success/failure, logout, password change, permission change, MFA changes) with user ID and timestamp.

## 4. Secrets and outbound calls

- **Never commit secrets.** Env vars or secret manager. A committed key is burned — rotate, don't just delete.
- **Never log secrets or auth headers.** Redact `Authorization`, `Cookie`, `Set-Cookie`, `password`, `apiKey`, and anything token-shaped.
- **Allowlist user-influenced URLs.** Block private ranges (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16` — especially `169.254.169.254`, cloud metadata) and non-HTTP schemes. Re-check after every redirect.
- **Set timeouts on every external call.** HTTP, DB, cache, queue. No infinite waits.

## 5. Files and dependencies

- **Validate uploads by content, not extension.** Inspect magic bytes; don't trust `Content-Type`. Cap size at the framework level.
- **Store uploads outside the web root, serve through an authenticated endpoint.** Generate the on-disk filename; keep the user's filename as metadata only. No user input in filesystem paths.
- **Prefer standard library or framework primitives over fresh dependencies.** Every new package is supply-chain surface. For crypto, use the language's standard module or one well-known package — never invent a scheme.
