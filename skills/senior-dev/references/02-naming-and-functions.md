# Naming and Functions

Load this when working on naming, function design, function size, arguments, or comments.

## Naming

Names are the most important documentation in your code. They appear on every line; comments don't.

### The intent test

Every name must reveal three things:
1. **What it is** (the concept)
2. **Why it exists** (the purpose)
3. **How it's used** (the contract)

If you need a comment to explain a name, **the name is wrong**. Rename instead of commenting.

**Bad:**
```javascript
let d = 7;  // days until expiration
```

**Good:**
```javascript
let daysUntilExpiration = 7;
```

### Naming rules by scope

The right name length depends on the variable's scope. **Name length is inversely proportional to scope size.**

- **Tiny scope (1–3 lines):** Single letters acceptable for indices and trivial cases.
  ```javascript
  for (let i = 0; i < items.length; i++) { /* fine */ }
  arr.map(x => x * 2)  // fine for one-liner
  ```

- **Function-scope variables:** One word, sometimes two.
  ```python
  def calculate_tax(income):
      rate = get_tax_rate(income)
      return income * rate
  ```

- **Class-level (instance variables):** Two words, descriptive.
  ```typescript
  class OrderService {
    private pendingOrders: Order[];
    private paymentGateway: PaymentGateway;
  }
  ```

- **Module-level / globals:** Long, fully descriptive — they're called from far away.
  ```typescript
  export const DEFAULT_SESSION_TIMEOUT_SECONDS = 3600;
  ```

- **Function names:** Inverse rule. *Public* functions in wide use should be **short** because they're called from everywhere. *Private* helpers should be **descriptive** because they're called from few places and need to explain themselves.

### Naming categories

**Variables and properties: nouns or noun phrases**
- ✅ `customerCount`, `activeUsers`, `paymentMethod`
- ❌ `getActive`, `processData` (sounds like a function)

**Functions and methods: verbs or verb phrases**
- ✅ `calculateTotal()`, `sendEmail()`, `isValid()`, `hasPermission()`
- ❌ `total()`, `email()`, `valid()` (ambiguous — is it doing or returning?)

**Booleans: questions starting with `is`, `has`, `should`, `can`**
- ✅ `isLoggedIn`, `hasUnreadMessages`, `shouldRetry`, `canEdit`
- ❌ `loggedIn`, `unread`, `retry`, `edit`

**Classes: nouns**
- ✅ `User`, `OrderProcessor`, `PaymentGateway`
- ❌ `ProcessOrder`, `Manage`

### Naming smells

These are signs the name is wrong:

- **Mental mapping required.** `accountList`, `accountArray`, `accountMap` — just call it `accounts`. Don't encode the type.
- **Disinformation.** `userList` that's actually a Set, not a List. Lying.
- **Meaningless distinctions.** `Customer`, `CustomerData`, `CustomerInfo`, `CustomerObject` — what's the difference? If you can't say, consolidate.
- **Hungarian notation.** `strName`, `iCount`, `bIsValid` — outdated and noisy.
- **Number-series.** `data1`, `data2`, `data3` — what do they mean? Use semantic names.
- **Cute names.** `holyHandGrenade`, `whackForeignKey` — fine for a hackathon, embarrassing in production.
- **Encoded meanings.** `usr_nm_str` — just write `userName`.

### Magic values

Replace magic numbers and magic strings with named constants. Always.

**Bad:**
```python
if user.role == 3:
    grant_access()
if order.status == "PND":
    notify_pending()
```

**Good:**
```python
if user.role == Roles.ADMIN:
    grant_access()
if order.status == OrderStatus.PENDING:
    notify_pending()
```

The exception: well-known values that don't benefit from naming. `0`, `1`, `-1`, `""`, `null` in obvious contexts are fine.

## Functions

Functions are where most of the readability damage happens. The rules below come from Uncle Bob's *Clean Code* and have held up across thousands of codebases.

### Rule 1: Functions should be small

The first rule of functions is they should be small. The second rule is they should be smaller than that.

**Targets:**
- **Ideal:** under 10 lines
- **Acceptable:** under 20 lines
- **Suspicious:** 20–30 lines (look hard for an extraction)
- **Wrong:** 30+ lines (almost certainly doing more than one thing)

These are guidelines, not laws. A 25-line switch statement that's truly cohesive is fine. A 15-line function with three nested if blocks is not.

### Rule 2: Functions do one thing

If you can describe what a function does using the word "and", it's doing too many things. Split it.

**Bad:**
```javascript
function processUserSignup(data) {
  // 1. Validate the data
  if (!data.email || !data.email.includes('@')) throw new Error('bad email');
  if (!data.password || data.password.length < 8) throw new Error('bad pwd');
  // 2. Save the user
  const user = db.users.create(data);
  // 3. Send welcome email
  emailService.send(user.email, 'welcome.html');
  // 4. Track analytics
  analytics.track('user_signup', { userId: user.id });
  return user;
}
```

**Good:**
```javascript
function processUserSignup(data) {
  validateSignupData(data);
  const user = db.users.create(data);
  sendWelcomeEmail(user);
  trackSignupEvent(user);
  return user;
}
```

The orchestration function reads like a paragraph. Each step is a separate function with a clear name.

### Rule 3: One level of abstraction per function

A function shouldn't mix high-level orchestration with low-level details.

**Bad (mixed levels):**
```python
def save_report(report):
    formatted = f"<html><body>{report.title}</body></html>"  # low-level string manipulation
    file = open('/tmp/report.html', 'w')                     # low-level file IO
    file.write(formatted)
    file.close()
    upload_to_s3('/tmp/report.html', 'reports')              # high-level
    notify_users(report.recipients)                          # high-level
```

**Good (single level — orchestration):**
```python
def save_report(report):
    file_path = render_report_to_file(report)
    upload_to_s3(file_path, 'reports')
    notify_users(report.recipients)
```

### Rule 4: Few arguments

Argument count, in order of preference:
- **0 (niladic)** — best, no input dependencies
- **1 (monadic)** — common and good
- **2 (dyadic)** — acceptable, but ordering matters: `copy(source, destination)`
- **3 (triadic)** — actively avoid; users have to remember argument order
- **4+ (polyadic)** — wrong; pass an object

**Bad:**
```javascript
createUser('Alice', 'alice@example.com', 25, 'admin', true, false, null);
```

**Good:**
```javascript
createUser({
  name: 'Alice',
  email: 'alice@example.com',
  age: 25,
  role: 'admin',
  isActive: true,
  isVerified: false,
});
```

### Rule 5: No flag arguments

Boolean flags are a sign your function is doing two things. Split it.

**Bad:**
```javascript
function render(item, isAdmin) {
  if (isAdmin) { /* one thing */ }
  else { /* a different thing */ }
}
```

**Good:**
```javascript
function renderForUser(item) { /* ... */ }
function renderForAdmin(item) { /* ... */ }
```

### Rule 6: No side effects

A function named `checkPassword(user, password)` should only check the password. If it also initializes the session, you've written a lie. The hidden side effect will surprise readers and cause bugs.

If you must do two things, name the function for both, or split it.

### Rule 7: Avoid output arguments

Don't pass an object to a function that mutates it without making that obvious.

**Bad:**
```javascript
function processOrder(order) {
  order.status = 'processed';  // mutation hidden inside
  order.processedAt = new Date();
}
```

**Better:**
```javascript
function processOrder(order) {
  return { ...order, status: 'processed', processedAt: new Date() };
}
```

Or if mutation is necessary, name it clearly: `mutateOrderToProcessed(order)`.

### Rule 8: Stepdown rule (vertical organization)

Code in a file should read top-to-bottom like a newspaper. Public/high-level functions at the top; private/lower-level helpers below.

```typescript
// File: orderService.ts

// Public API — top
export function placeOrder(items: Item[]) {
  validateItems(items);
  const total = calculateTotal(items);
  const order = createOrderRecord(items, total);
  notifyWarehouse(order);
  return order;
}

// Private helpers — below, in the order they're called
function validateItems(items: Item[]) { /* ... */ }
function calculateTotal(items: Item[]) { /* ... */ }
function createOrderRecord(items: Item[], total: number) { /* ... */ }
function notifyWarehouse(order: Order) { /* ... */ }
```

A reader can stop after the first function and have a complete mental model. They only dive deeper if needed.

### Rule 9: Limit nesting depth

Indent depth correlates with complexity. Targets:
- **0–2 levels:** healthy
- **3 levels:** smell — try to flatten
- **4+ levels:** refactor required

Use **guard clauses** and **early returns** to flatten:

**Bad:**
```javascript
function processUser(user) {
  if (user) {
    if (user.isActive) {
      if (user.hasPermission('edit')) {
        if (user.balance > 0) {
          // do the thing
        }
      }
    }
  }
}
```

**Good:**
```javascript
function processUser(user) {
  if (!user) return;
  if (!user.isActive) return;
  if (!user.hasPermission('edit')) return;
  if (user.balance <= 0) return;

  // do the thing
}
```

## Comments

Comments are a last resort. Most comments are apologies for code that should have been clearer.

### When comments are good

- **Why, not what.** Explain non-obvious decisions, business rules, or weird workarounds.
  ```python
  # Stripe rounds to 2 decimals; we round to 4 to avoid loss
  # when converting between currencies before final billing.
  ```

- **Legal/license headers.** Required by some projects.

- **Public API documentation.** JSDoc, docstrings, etc., for libraries consumed by others.

- **Warnings.**
  ```javascript
  // WARNING: This must run before initAuth() or sessions break.
  ```

- **Regex explanations.**
  ```python
  # Match international phone numbers: optional +, 7-15 digits
  PHONE_REGEX = re.compile(r'^\+?\d{7,15}$')
  ```

### When comments are bad

- **Explaining what the code does.** If you need this, rewrite the code.
  ```javascript
  // BAD: increment i by 1
  i++;
  ```
- **Commented-out code.** Delete it. Git remembers.
- **Redundant comments.** `// Constructor` above a constructor.
- **Noise.** `// the user` above `User user`.
- **Journal/changelog comments.** That's what version control is for.
- **TODO without a ticket.** `// TODO: handle errors` becomes permanent. Either fix it or file an issue and reference it: `// TODO(JIRA-1234): handle network errors`.
- **Closing brace markers.** `} // end of for loop` — your editor handles this.

### The comment test

Before writing a comment, ask: "Could I make this comment unnecessary by renaming a variable, extracting a function, or restructuring the code?" If yes, do that instead.
