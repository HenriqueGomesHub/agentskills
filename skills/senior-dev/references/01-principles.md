# Foundational Principles

Load this when the user asks about software design principles, "good code", or when you need to justify a design decision based on first principles.

## KISS — Keep It Simple, Stupid

**Core idea:** Build systems only as complex as they need to be — and no more.

KISS is not about writing the *shortest* code. It's about avoiding *unnecessary* complexity. Some problems are inherently complex; KISS tells you not to add complexity that doesn't come from the problem itself.

**Apply when:**
- Choosing between two solutions of similar capability
- Tempted to introduce a design pattern, abstraction, or framework "for flexibility"
- Reviewing code that feels harder to read than the problem warrants

**Anti-patterns KISS catches:**
- Command pattern for a one-off calculation
- Factory class to instantiate a single object type
- Custom event system when standard callbacks work
- Microservices for a 3-developer team
- Dependency injection container for an app with 4 services

**The KISS test:** If you removed this complexity, would the code still work? If yes, the complexity didn't belong.

**When KISS doesn't apply:** When the problem itself requires the complexity. A distributed systems problem can't be solved with a single function. Don't oversimplify away essential complexity — only accidental complexity.

## DRY — Don't Repeat Yourself

**Core idea:** Every piece of *knowledge* should have a single, unambiguous, authoritative representation in the system.

The most important word above is **knowledge**. DRY is not about deleting duplicate-looking code. It's about not duplicating the *meaning* behind the code.

**The crucial distinction:**
- Two functions with similar code that represent the **same business concept** → extract a shared function (true DRY)
- Two functions with similar code that represent **different business concepts** that happen to look alike right now → leave them duplicated (false DRY)

**Example of false DRY (bad):**
```javascript
// "I see User.fullName() and Company.displayName() both concatenate strings,
// let me make a generic concatNames() function!"
```
A year later, User.fullName needs to handle middle names and Company.displayName needs to handle legal suffixes. Now your "shared" function has flags and conditionals, and both callers are coupled to each other for no reason.

**Example of true DRY (good):**
```javascript
// Three places in the codebase calculate sales tax with the same logic
// because there's one tax rule. Extract calculateSalesTax(amount, region).
```

**The DRY test:** When this rule changes, how many places in the code need to change? If the answer should be "one" but is currently "three", DRY violation. If the answer should legitimately be "three" because they're three different rules, leave them.

**Premature DRY is worse than duplication.** Wait for the third occurrence before extracting. Two occurrences might be coincidence; three is a pattern.

## YAGNI — You Aren't Gonna Need It

**Core idea:** Don't build features, abstractions, or flexibility for needs that aren't real *yet*.

YAGNI exists to protect code from imaginary futures. Most speculative features never get used; their complexity stays behind anyway.

**Apply when tempted to:**
- Add a config option "in case someone wants to customize this"
- Build an abstraction layer for "future database swaps"
- Create a plugin system for an app with one plugin
- Add a `priority` field to a queue that always processes FIFO
- Generalize a function to accept any input type when only one type is used

**The YAGNI dialogue:**
- "But what if we need it later?" → If you need it later, add it later. Code is easier to add than to remove.
- "It's only 5 lines now." → It's only 5 lines now. In 6 months it'll be 50, with tests, docs, and edge cases.
- "It would be more flexible." → Flexibility is a cost, not a benefit. You pay for it in cognitive load on every reader.

**When YAGNI doesn't apply:**
- Security: build security in from day one, don't bolt it on later
- Data integrity: foreign keys, validation, types — these are not "future flexibility", they prevent corruption
- Logging and observability: you can't debug what you didn't log

**The YAGNI test:** Is there a real, currently-known requirement for this? If you can't name a concrete user or use case, don't build it.

## SOLID Principles

Five principles that together prevent the most common object-oriented design failures.

### S — Single Responsibility Principle (SRP)

**Each class, module, or function has one reason to change.**

A `User` class that handles authentication AND profile data AND email notifications has three reasons to change. Auth team changes it, profile team changes it, marketing team changes it — three sources of conflict, three sources of bugs.

**Test:** Describe what this class does in one sentence with no "and". If you can't, split it.

**Bad:**
```python
class User:
    def authenticate(self, password): ...
    def update_profile(self, data): ...
    def send_welcome_email(self): ...
```

**Good:**
```python
class User: ...                    # Just the data
class AuthService: ...             # Authentication
class ProfileService: ...          # Profile updates
class NotificationService: ...     # Emails
```

### O — Open/Closed Principle

**Open for extension, closed for modification.**

You should be able to add new behavior without changing existing code. Achieved through polymorphism, strategy pattern, plugins, or composition.

**Bad (every new payment type modifies the existing function):**
```javascript
function processPayment(type, amount) {
  if (type === 'credit') { /* ... */ }
  else if (type === 'paypal') { /* ... */ }
  else if (type === 'crypto') { /* ... */ }  // Just added
}
```

**Good (new payment types are new classes, no modification):**
```javascript
class CreditPayment { process(amount) { /* ... */ } }
class PaypalPayment { process(amount) { /* ... */ } }
class CryptoPayment { process(amount) { /* ... */ } }
function processPayment(method, amount) { return method.process(amount); }
```

**Don't over-apply.** OCP is for parts of the system that you have evidence will need extension. YAGNI still wins for one-off code.

### L — Liskov Substitution Principle

**Subclasses must be drop-in replacements for their parents.**

If `Bird` has a `fly()` method and `Penguin extends Bird`, you have a Liskov violation. Code that works with any `Bird` will break for `Penguin`.

**The test:** Anywhere the parent type is used, can I substitute any subclass without breaking the program's correctness? If no, your inheritance hierarchy is wrong — favor composition.

### I — Interface Segregation Principle

**Many small, focused interfaces beat one large interface.**

Don't force classes to implement methods they don't need.

**Bad:**
```typescript
interface Worker {
  work(): void;
  eat(): void;
  sleep(): void;
}
class Robot implements Worker { /* eat() and sleep() are nonsense */ }
```

**Good:**
```typescript
interface Workable { work(): void; }
interface Eatable { eat(): void; }
interface Sleepable { sleep(): void; }
class Human implements Workable, Eatable, Sleepable { /* all three */ }
class Robot implements Workable { /* just work */ }
```

### D — Dependency Inversion Principle

**Depend on abstractions, not concretions.**

High-level modules shouldn't depend on low-level modules. Both should depend on interfaces.

**Bad:**
```python
class OrderService:
    def __init__(self):
        self.db = PostgresDatabase()  # Hard-coded dependency
```

**Good:**
```python
class OrderService:
    def __init__(self, db: Database):  # Depends on abstraction
        self.db = db
```

Now `OrderService` works with Postgres, MySQL, SQLite, or a mock for tests. The concrete choice is made at the composition root (where you wire the app together), not buried inside business logic.

## How these principles interact

The principles sometimes pull in opposite directions:
- **DRY vs KISS:** Extracting a shared abstraction (DRY) can make code harder to follow (anti-KISS). Choose KISS when the duplication is small and the abstraction would be complex.
- **OCP vs YAGNI:** Designing for extension (OCP) violates YAGNI when no extension is actually needed. Choose YAGNI by default; refactor to OCP when the second variant appears.
- **SRP vs file proliferation:** Aggressively splitting classes (SRP) creates many small files. That's usually fine, but watch for "shotgun surgery" — if changing one feature requires touching 12 files, your splits are wrong.

**Senior judgment:** principles are tensions to manage, not laws to obey. Recognize the tension, pick consciously, and be ready to refactor when context changes.

## Other principles worth knowing

- **Law of Demeter:** A class should only talk to its immediate friends. `user.account.balance.amount` is a smell — `user.getAccountBalance()` is better.
- **Tell, Don't Ask:** Don't ask an object for its state and then act on that state — tell the object what to do. `if (user.isLoggedIn()) showProfile()` → `user.showProfile()` (and let `User` handle the check internally).
- **Composition over Inheritance:** Inheritance creates strong coupling between parent and child. Composition (has-a) is more flexible than inheritance (is-a). Default to composition; reach for inheritance only when the relationship is truly is-a.
- **Convention over Configuration:** Sensible defaults beat exhaustive options. Frameworks like Rails and Next.js work because they pick reasonable defaults.

## When to break the rules

Senior engineers break these rules constantly — but consciously. You break a rule when:

1. You can name *which* rule you're breaking
2. You can explain *why* the cost of following it exceeds the cost of breaking it
3. You document the decision (comment, commit message, or design doc)

If you can't do all three, follow the rule.
