# Error Handling

Load this when working with try/catch blocks, exception handling, validation, error messages, or when reviewing code for robustness.

Error handling is not a feature you add at the end. It's a design dimension that affects every function you write. Bad error handling is the source of more production incidents than bad business logic.

## The core principles

### 1. Errors are first-class concerns

Every function that can fail must declare and handle that fact explicitly. If a function does network I/O, file I/O, parses untrusted input, or calls another function that does any of these, it can fail.

Don't write the happy path first and "add error handling later." That's how silent failures end up in production.

### 2. Fail fast, fail loud — to the right audience

- **For developers/operators:** errors should produce loud, structured, actionable signals (logs, alerts, stack traces).
- **For end users:** errors should produce calm, helpful messages with no internal details.

Never confuse the two audiences. A user should never see `NullPointerException at OrderService.java:482`. An operator should never get a vague "something went wrong" with no diagnostics.

### 3. Distinguish recoverable from unrecoverable errors

- **Recoverable:** validation failures, transient network errors, user input mistakes, missing optional resources. Handle gracefully, retry where appropriate, return useful info to the caller.
- **Unrecoverable:** programming bugs (null where it shouldn't be), corrupted state, missing required configuration. Fail fast — let it crash, log everything, alert humans.

Trying to "recover" from a programming bug usually makes things worse. The bug stays hidden, data corruption spreads, and debugging gets harder.

## Anti-patterns: things that must never appear

### Never: empty catch blocks

```javascript
// CRIMINAL
try {
  riskyOperation();
} catch (e) {
  // ignore
}
```

This swallows errors silently. The bug exists, runs, and produces wrong results — but you never know. Empty catches are the single worst pattern in error handling.

If you genuinely want to ignore an error (rare), at minimum log it and explain why:

```javascript
try {
  await sendOptionalAnalyticsEvent(event);
} catch (e) {
  logger.warn('Analytics send failed (non-critical)', { error: e.message });
  // Intentionally swallowed: analytics are best-effort and must not block the request.
}
```

### Never: catch and rethrow with no value added

```python
# Pointless
try:
    do_thing()
except Exception as e:
    raise e
```

Either handle it, add context, or let it propagate. Catching just to rethrow with nothing added is noise.

```python
# Useful — add context
try:
    do_thing()
except IOError as e:
    raise IOError(f"Failed to load config from {path}") from e
```

### Never: expose stack traces to users

```javascript
// VERY BAD
app.use((err, req, res, next) => {
  res.status(500).send(err.stack);  // leaks file paths, dependency versions, internal logic
});
```

Stack traces leak architectural information that helps attackers. Show users a generic message; log the trace server-side.

```javascript
// Good
app.use((err, req, res, next) => {
  const errorId = generateId();
  logger.error('Request failed', { errorId, error: err, path: req.path });
  res.status(500).json({
    message: 'Something went wrong. Please try again.',
    errorId,  // user can quote this when contacting support
  });
});
```

### Never: catch overly broad exceptions

```python
# Bad — catches everything including KeyboardInterrupt, SystemExit
try:
    do_thing()
except:
    pass

# Better but still too broad
try:
    do_thing()
except Exception:
    pass

# Good — handle specific failure modes
try:
    do_thing()
except (ConnectionError, TimeoutError) as e:
    logger.warn('Network failure', exc_info=e)
    return fallback_value()
```

The narrower the catch, the more intentional the handling.

### Never: errors as control flow

```javascript
// Bad — using exceptions for normal flow
function findUser(id) {
  if (!users[id]) throw new Error('Not found');
  return users[id];
}
try {
  const u = findUser(id);
  // ...
} catch {
  // assume not found
}
```

Exceptions are expensive and signal *unexpected* conditions. "User not found" when looking up users is not unexpected — it's a normal outcome. Return `null`, `undefined`, or `Optional<User>` instead.

### Never: hardcoded sensitive data in error messages

```python
# Bad
raise AuthError(f"Invalid password for user with email {email} and token {token}")
```

Error messages get logged. Logs get aggregated. Suddenly your tokens and emails are in 5 systems. Log the user ID; never log secrets.

## Validation: the boundary principle

Validate at the boundaries of your system, not throughout it.

- **Boundary inputs:** HTTP requests, file uploads, message queue payloads, third-party API responses, user form data — anything coming from outside your trust zone.
- **Internal calls:** if you've already validated at the boundary, internal functions can trust their inputs (and use type systems to enforce that).

This is the **fail fast** principle. Reject bad input the moment it enters; never let it reach the core of the application.

```typescript
// At the boundary
app.post('/users', (req, res) => {
  const validation = userSchema.safeParse(req.body);
  if (!validation.success) {
    return res.status(400).json({ errors: validation.error.issues });
  }
  // From here on, the data is guaranteed valid
  return userService.create(validation.data);
});

// Internal — trust the input shape
class UserService {
  create(data: ValidatedUserData) {
    // No re-validation; the type system enforces shape
    return this.repo.insert(data);
  }
}
```

## Choose your error mechanism deliberately

Different languages and contexts favor different patterns:

### Exceptions

**When to use:** Truly unexpected conditions; deeply nested call stacks where checking returns at every level would be painful.

**Best practices:**
- Throw specific exception types, not generic ones (`InvalidEmailError`, not `Error`)
- Include context in the message (which field, what value, what was expected)
- Don't use exceptions for normal control flow

### Result/Either types

**When to use:** Functions where failure is a normal outcome (parsing, network calls, database lookups).

```typescript
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

function parseEmail(input: string): Result<Email, string> {
  if (!input.includes('@')) return { ok: false, error: 'Invalid email' };
  return { ok: true, value: new Email(input) };
}

const result = parseEmail(userInput);
if (!result.ok) return showError(result.error);
useEmail(result.value);
```

Result types make failure visible in the type signature. The caller can't accidentally ignore it.

### Null / Optional / undefined

**When to use:** "Not found" cases that aren't really errors.

```python
def find_user(id: int) -> Optional[User]:
    return db.query(User).filter_by(id=id).first()

user = find_user(123)
if user is None:
    return render('not_found.html')
```

### Error codes / tagged unions

**When to use:** APIs and protocols where you need to distinguish error types programmatically.

```json
{
  "ok": false,
  "error": {
    "code": "INSUFFICIENT_FUNDS",
    "message": "Account balance is below required minimum",
    "details": { "balance": 5.00, "required": 10.00 }
  }
}
```

## Error message quality

Good error messages tell you:

1. **What failed.** "Failed to load user profile."
2. **Why it failed (when known).** "Database connection timed out after 5s."
3. **What the user can do.** "Please retry. If the problem persists, contact support with error ID xyz."

Bad: "An error occurred."
Good: "Could not save your changes — your session expired. Please log in again."

For developer-facing errors (logs, devtools), include:
- Timestamps
- Request/correlation IDs
- The operation that failed
- The state that caused it (sanitized)
- The stack trace

## Logging discipline

Logs are how you debug what you can't reproduce. Treat them like a feature.

### Log levels — use them properly

- **DEBUG:** Verbose info for development. Disabled in production.
- **INFO:** Normal events worth recording (user logged in, order placed).
- **WARN:** Unusual but recoverable (slow query, retry succeeded after failure).
- **ERROR:** A failure that affected one operation (request failed, send email failed).
- **FATAL/CRITICAL:** A failure that affected the system (database down, out of memory).

If everything is logged at ERROR level, you can't filter for actual problems. If everything is logged at INFO, you drown in noise.

### Structured logging

Use structured (JSON) logs in production. They're searchable, filterable, and correlatable.

```javascript
// Bad — unparseable
console.log(`User ${userId} purchased item ${itemId} for $${amount}`);

// Good — structured
logger.info('purchase_completed', {
  userId,
  itemId,
  amountCents: amount * 100,
  currency: 'USD',
});
```

### Don't log sensitive data

Never log:
- Passwords (even hashed)
- API keys, tokens, secrets
- Full credit card numbers (PCI violation)
- Personal identifiable information without need
- Full request bodies that might contain any of the above

Log identifiers (`userId: 123`), not values.

## Defensive vs. offensive programming

**Defensive programming** = check everything, assume nothing.
**Offensive programming** = enforce contracts, fail loudly when violated.

The right approach depends on the boundary:

- **External boundary (API, user input, file parsing):** defensive. Validate, sanitize, reject bad input.
- **Internal boundary (between modules of the same app):** offensive. Use types and assertions to enforce contracts; let invalid inputs crash the app loudly so the bug gets fixed.

Defensive programming inside the app produces noise: every function checking that its arguments aren't null when the type system already guarantees that. Use the type system as your enforcement mechanism for internal calls.

## Retries: when, how, and how not

Retry only on **transient** failures: network timeouts, rate limits, temporary unavailability. Don't retry on 4xx errors (those are *your* fault — retrying won't help).

When retrying:
- **Use exponential backoff with jitter.** Don't hammer the failing service.
- **Cap retries.** 3–5 is usually right.
- **Make sure the operation is idempotent.** A retry that creates duplicate records is worse than a failure.
- **Log every retry.** Otherwise you can't tell why latency spiked.

```javascript
async function withRetry(fn, maxAttempts = 3) {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt === maxAttempts || !isRetryable(err)) throw err;
      const delay = Math.min(1000 * 2 ** attempt + Math.random() * 1000, 30000);
      logger.warn('retrying', { attempt, delay, error: err.message });
      await sleep(delay);
    }
  }
}
```

## Testing error paths

The error paths in your code are usually less tested than the happy paths. That's exactly backwards: errors only happen in production, where you can't easily debug them.

Write tests for:
- Each validation rule rejecting bad input
- Each external dependency failing (network, DB, third-party API)
- Each branch of error handling logic
- Edge cases: empty inputs, null, max sizes, unicode

If your error handling is untested, assume it's broken.

## A senior's mental model for error handling

Before shipping a function, ask:

1. **What can fail here?** List every external call, every parse, every assumption.
2. **For each failure, what's the right response?** Retry? Return error? Crash?
3. **What does the user see?** What does the operator see?
4. **What gets logged?** With what level? Containing what?
5. **What's tested?** Both the happy path AND each failure mode.

If you can't answer these, the function isn't done.
