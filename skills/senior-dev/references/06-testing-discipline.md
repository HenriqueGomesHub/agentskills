# Testing Discipline

Load this when writing tests, talking about TDD, coverage, mocking, or test organization.

## Why tests exist

Tests exist for one practical reason: **so you can change the code with confidence**. Without tests, every change is a gamble. With tests, you can refactor mercilessly, upgrade dependencies, and ship Friday afternoon.

Tests are not for proving correctness (impossible) or catching every bug (impossible). They're for catching regressions and making the codebase modifiable.

## What to test (in order of priority)

1. **Business logic** — the rules that make your application valuable. Pricing, permissions, validation, state transitions. **70–80% coverage minimum** here.
2. **Integration points** — places where modules connect, especially across boundaries (API endpoints, DB queries, message handlers).
3. **Bug fixes** — every bug fix gets a regression test. The bug existed because no test caught it; add the test.
4. **Critical paths** — signup, payment, login, anything where failure is expensive.
5. **Edge cases** — empty inputs, null, max values, concurrent access, unicode.

## What NOT to test

- **Framework code.** React's `useState`, Express's routing, the database driver — that's their team's job.
- **Third-party libraries.** Trust them or replace them; don't test them.
- **Trivial getters/setters with no logic.** Testing `obj.foo = 1; assert obj.foo === 1` adds noise without value.
- **Implementation details.** If you test that `userService.create` calls `userRepo.insert` 1 time with specific args, you've coupled your test to the implementation. Test the *behavior* (a user got created), not the *implementation* (which functions got called).
- **Code that's about to be deleted.**

The rule of thumb: **test the contract, not the implementation**. If the test breaks every time you refactor, the test was wrong.

## Test-Driven Development (TDD)

TDD's three laws (Uncle Bob):

1. You may not write production code until you have written a failing unit test.
2. You may not write more of a unit test than is sufficient to fail (and not compiling counts as failing).
3. You may not write more production code than is sufficient to pass the currently failing test.

The cycle: **Red → Green → Refactor**.

- **Red:** write a test that fails (because the code doesn't exist yet)
- **Green:** write the minimum code that makes the test pass (ugly is OK)
- **Refactor:** clean up the code while keeping all tests green

### TDD-aware (the pragmatic stance)

Strict TDD isn't always the right choice. **TDD-aware** means:

- For **business logic** with clear inputs/outputs → TDD is excellent
- For **UI work** where you're discovering the design → write code first, then tests for the parts that solidify
- For **prototypes / spikes** → tests come after the design stabilizes
- For **bug fixes** → always write the failing test first; that's TDD at its best

Don't be religious about it. The goal is good tested code, not adherence to a process.

## The structure of a good test

Every test follows the **Arrange-Act-Assert** (AAA) pattern:

```javascript
test('rejects orders below minimum amount', () => {
  // Arrange — set up the world
  const cart = new Cart();
  cart.addItem({ id: 1, price: 0.50 });

  // Act — perform the operation under test
  const result = checkout(cart);

  // Assert — verify the outcome
  expect(result.ok).toBe(false);
  expect(result.error).toBe('MINIMUM_ORDER_NOT_MET');
});
```

These three sections should be visually separate. If your test mixes them, it's hard to read.

## Test naming

A test name should describe the **behavior being verified** in the language of the domain. Bad names test implementation; good names test contract.

```javascript
// Bad — describes the function
test('test_create_user', () => { /* ... */ });
test('test_create_user_with_invalid_email', () => { /* ... */ });

// Good — describes the behavior
test('rejects signup with invalid email format', () => { /* ... */ });
test('sends welcome email after successful signup', () => { /* ... */ });
test('does not send welcome email if signup fails', () => { /* ... */ });
```

A test name should make sense to a non-technical product owner. If they can't tell what the test verifies, the name is wrong.

## The FIRST principles

Good tests are:

- **Fast** — milliseconds per test, not seconds. If tests are slow, developers stop running them.
- **Independent** — tests don't depend on each other. Any test should run in isolation.
- **Repeatable** — same result every time, in any environment, regardless of when it ran. No dependency on `Date.now()`, network, filesystem state, etc.
- **Self-validating** — pass or fail clearly; no manual interpretation required.
- **Timely** — written close to the production code (TDD: before; pragmatic: same commit).

## One assertion per test (the spirit, not the letter)

The rule is sometimes stated as "one assertion per test." A more useful version: **one concept per test**.

A test verifying "checkout flow with valid input" might assert:
- The checkout returned success
- The order was saved
- The inventory was decremented
- The user got a confirmation email

That's one *concept* (checkout flow), four assertions, one test — fine.

A test asserting both "valid input succeeds" AND "invalid input fails" — that's two concepts. Split it.

## Test isolation: don't share state

Each test starts from a clean slate. Don't rely on test order. Don't rely on shared mutable state.

```javascript
// Bad — tests depend on each other
let users = [];
test('creates a user', () => {
  users.push(createUser('alice'));
  expect(users.length).toBe(1);
});
test('finds a user', () => {
  const found = findUser(users[0].id); // depends on previous test
  expect(found).toBeDefined();
});

// Good — each test sets up its own state
beforeEach(() => clearUsersTable());
test('creates a user', () => {
  const u = createUser('alice');
  expect(u).toBeDefined();
});
test('finds a user', () => {
  const u = createUser('alice');
  const found = findUser(u.id);
  expect(found).toBeDefined();
});
```

## Mocking: use sparingly

Every mock is a place where your test diverges from reality. Heavy mocking is a smell.

**Mock when:**
- The dependency is slow (network, DB)
- The dependency is non-deterministic (current time, randomness, third-party API)
- You're testing the boundary explicitly (e.g., testing that `OrderService` calls the payment provider correctly)

**Don't mock when:**
- You can use the real thing cheaply (in-memory DB, real internal class)
- The mock is just "this function returns this" — you're testing your mock, not your code
- The mock has more lines than the test logic

### Mock the boundary, not the internals

```javascript
// Bad — mocks every internal call
test('places order', () => {
  const validate = jest.fn().mockReturnValue(true);
  const calculate = jest.fn().mockReturnValue(100);
  const save = jest.fn();
  const notify = jest.fn();
  // ... this test verifies nothing about your real code
});

// Good — mock only the external boundary
test('places order', () => {
  const fakePaymentProvider = { charge: jest.fn().mockResolvedValue({ ok: true }) };
  const service = new OrderService(fakePaymentProvider);
  const result = await service.place(validOrder);
  expect(result.status).toBe('completed');
  expect(fakePaymentProvider.charge).toHaveBeenCalledWith(validOrder.amount);
});
```

## Coverage targets

Coverage is a useful **floor** indicator and a useless **ceiling** indicator. 100% coverage doesn't mean your tests are good; 0% coverage means you definitely have problems.

Reasonable targets:
- **Business logic / domain code:** 80–95%
- **API/controller layer:** 70–85%
- **Utility / pure functions:** 90%+ (they're cheap to test)
- **UI components:** 50–70% (high-value paths, not every styling tweak)
- **Generated code, glue code, configuration:** Don't measure

Don't chase 100%. The last 10% is where tests start testing trivia.

**More important than coverage:**
- Are the critical paths tested?
- Are the failure modes tested?
- Do tests fail loudly when something genuinely breaks?

## Test types and pyramid

Different test types serve different purposes. The classical pyramid:

```
       /\
      /E2E\        — few, slow, brittle, high confidence
     /------\
    /  Integ \     — some, medium speed, good for boundaries
   /----------\
  /    Unit    \   — many, fast, focused
 /--------------\
```

- **Unit tests:** Test a single function/class in isolation. Fast (ms). Most of your tests.
- **Integration tests:** Test that modules work together (e.g., a route handler hitting the DB). Slower (seconds). Cover boundaries.
- **End-to-end (E2E) tests:** Test the system from outside (browser → API → DB). Slow (minutes). Cover only critical user flows.

Heavy on unit, moderate on integration, light on E2E. The opposite (heavy E2E, light unit) is the **ice cream cone anti-pattern** — slow, brittle, expensive to maintain.

## Tests are code too

Tests follow all the same quality rules as production code:
- Clear names
- Small functions
- No duplication (use helpers, fixtures, factories)
- No magic values
- Refactored as the code evolves

Sloppy tests rot. When tests start failing intermittently or are commented out, the test suite stops mattering.

## Writing the first test for an untested codebase

If you inherit code with no tests:

1. **Don't try to test it all.** You'll burn out.
2. **Write a regression test for the next bug you fix.** Now that bug is permanently caught.
3. **Write characterization tests around code you're about to refactor.** These capture the *current* behavior (even if buggy) so you know your refactor didn't change anything.
4. **Add tests for new code as you write it.** The tested area expands organically.

Within 6 months, you'll have a meaningful safety net.

## Common test smells

- **Tests that pass when they shouldn't.** Mutate the production code; if a test still passes, it wasn't testing anything.
- **Tests that fail when they shouldn't.** Refactor the production code without changing behavior; if tests break, they're testing implementation, not contract.
- **Slow tests that no one runs.** Speed it up or delete it.
- **Flaky tests.** Either fix the flakiness (race conditions, time dependencies, network) or delete the test. A flaky test poisons the whole suite by training people to ignore failures.
- **Tests that need a paragraph of setup.** Either the production code is too coupled or the test is testing too much.
- **Mocking the system under test.** If you're mocking the very thing you're testing, you're not testing it.

## How to know your tests are good

Mutation testing. Tools like Stryker (JS), mutmut (Python), or PIT (Java) deliberately introduce bugs into your production code and check if your tests catch them. If a mutated version of your code still passes all tests, your tests are weak.

Less rigorous but useful: **periodically delete a function and see if tests fail loudly.** If they don't, the function isn't tested at the contract level.
