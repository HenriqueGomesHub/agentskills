# Refactoring Catalog and Code Smells

Load this when refactoring existing code, reviewing code, dealing with legacy code, or when the user asks "how do I clean this up?"

This file is a condensed senior-engineer's reference to Martin Fowler's *Refactoring* (2nd ed.) and Uncle Bob's *Clean Code*. The goal is to give you a precise vocabulary for recognizing problems and a catalog of safe transformations.

## How to refactor safely

Refactoring is changing code structure without changing behavior. The key word is **safely** — and safe means:

1. **You have tests.** Without tests, you're not refactoring; you're rewriting and hoping.
2. **You take small steps.** Each step keeps the code working.
3. **You commit after each successful step.** So you can revert if something breaks.
4. **You change either structure OR behavior — never both at once.** Don't refactor and add a feature in the same commit.

If the code has no tests, write **characterization tests** first — tests that capture the current behavior, even if that behavior is buggy. Then refactor; then fix the bugs separately.

## The code smell vocabulary

Naming a problem precisely is half the fix. When reviewing code, identify the smell by name.

### Smell: Long Method
**Symptom:** A function/method that's grown past 20–30 lines.
**Why it's bad:** Hard to read, hard to test, almost certainly violates SRP.
**Fix:** *Extract Method* — pull cohesive chunks into named functions.

### Smell: Large Class
**Symptom:** A class with too many responsibilities, fields, or methods (> 200–500 lines, > 20 methods).
**Why it's bad:** Violates SRP. Multiple developers conflict editing it.
**Fix:** *Extract Class* — peel off cohesive subsets of fields and methods into new classes.

### Smell: Long Parameter List
**Symptom:** A function with 4+ parameters.
**Why it's bad:** Callers can't remember the order; refactoring is painful.
**Fix:** *Introduce Parameter Object* — bundle related parameters into a single object/struct.

### Smell: Duplicated Code
**Symptom:** The same (or nearly the same) code in two or more places.
**Why it's bad:** Bug fixes require finding and fixing every copy.
**Fix:** *Extract Method* (if same logic), *Extract Class* (if same data + logic), or recognize they're not actually duplicates of the same *concept*.
**⚠️ Caution:** Don't extract just because code looks similar. Two functions that look alike but represent different business concepts should stay separate. See `01-principles.md` for the DRY discussion.

### Smell: Divergent Change
**Symptom:** "Every time I change feature X, I have to change this class. Every time I change feature Y, I also have to change this class."
**Why it's bad:** The class has multiple reasons to change — SRP violation.
**Fix:** *Extract Class* — split the class so each part has only one reason to change.

### Smell: Shotgun Surgery
**Symptom:** "Every time I make a single conceptual change, I have to edit 12 different files."
**Why it's bad:** The opposite of Divergent Change — related logic is scattered.
**Fix:** *Move Method* / *Move Field* — gather related code into a single place.

### Smell: Feature Envy
**Symptom:** A method in class A spends most of its time accessing data from class B.
**Why it's bad:** The method belongs in B, not A.
**Fix:** *Move Method* — relocate the method to the class whose data it actually uses.

### Smell: Data Clumps
**Symptom:** The same group of variables appears together in multiple places (e.g., `street, city, state, zip` everywhere).
**Why it's bad:** They're conceptually one thing — an Address — but scattered.
**Fix:** *Introduce Parameter Object* / *Extract Class* — make `Address` a real type.

### Smell: Primitive Obsession
**Symptom:** Using primitive types (string, int) for domain concepts that deserve their own type.
**Why it's bad:** No type safety, easy to mix up, no place to put related logic.
**Fix:** Create a value object: `Email`, `Money`, `PhoneNumber`, `UserId`. The type system catches mistakes.

```typescript
// Bad
function sendEmail(to: string, subject: string) { /* ... */ }
sendEmail('Subject', 'recipient@example.com'); // typo: arguments swapped

// Good
class EmailAddress { constructor(public readonly value: string) { /* validate */ } }
function sendEmail(to: EmailAddress, subject: string) { /* ... */ }
```

### Smell: Switch Statements / Long Conditionals
**Symptom:** Long `if/else` chains or `switch` statements based on a type field.
**Why it's bad:** Adding a new case requires modifying the conditional everywhere it appears (OCP violation).
**Fix:** *Replace Conditional with Polymorphism* — make each case a subclass with its own implementation.

### Smell: Comments Explaining Code
**Symptom:** A comment that explains *what* the code does (not *why*).
**Why it's bad:** The code should be clear enough not to need it.
**Fix:** *Extract Method* with a name that captures the intent, then delete the comment.

```javascript
// Bad
// Check if user can access admin panel
if (user.isActive && user.role === 'admin' && !user.suspended) { /* ... */ }

// Good
if (canAccessAdminPanel(user)) { /* ... */ }
```

### Smell: Dead Code
**Symptom:** Unreachable code, unused functions, commented-out blocks.
**Why it's bad:** Pollution. Confuses readers.
**Fix:** Delete it. Git remembers.

### Smell: Speculative Generality
**Symptom:** "We might need this someday" abstractions, unused parameters, abstract classes with one implementation.
**Why it's bad:** Pays a complexity cost for a benefit that never arrives (YAGNI violation).
**Fix:** *Inline* the speculative abstraction; remove unused options.

### Smell: Temporary Field
**Symptom:** A class field that's only used in some scenarios; `null`/empty otherwise.
**Why it's bad:** Confusing — readers can't tell when it's safe to use.
**Fix:** *Extract Class* — pull the temporary field plus the methods that use it into a separate class.

### Smell: Refused Bequest
**Symptom:** A subclass overrides parent methods to do nothing or throw.
**Why it's bad:** The inheritance hierarchy is wrong — Liskov violation.
**Fix:** Replace inheritance with composition.

### Smell: Inappropriate Intimacy
**Symptom:** Two classes that know too much about each other's internals.
**Why it's bad:** They can't evolve independently.
**Fix:** *Move Method* / *Move Field* to relocate functionality, or extract a third class to mediate.

## Core refactorings

These are the most-used transformations from Fowler's catalog. Each is safe when done in small steps with tests.

### Extract Method (or Extract Function)

The single most important refactoring. Pull a coherent chunk of code into its own function.

**Before:**
```python
def print_invoice(order):
    print(f"Customer: {order.customer.name}")
    print(f"Date: {order.date}")
    print("Items:")
    for item in order.items:
        print(f"  - {item.name}: ${item.price}")

    subtotal = sum(item.price for item in order.items)
    tax = subtotal * 0.08
    total = subtotal + tax
    print(f"Subtotal: ${subtotal}")
    print(f"Tax: ${tax}")
    print(f"Total: ${total}")
```

**After:**
```python
def print_invoice(order):
    print_header(order)
    print_items(order.items)
    print_totals(order.items)

def print_header(order):
    print(f"Customer: {order.customer.name}")
    print(f"Date: {order.date}")

def print_items(items):
    print("Items:")
    for item in items:
        print(f"  - {item.name}: ${item.price}")

def print_totals(items):
    subtotal = sum(item.price for item in items)
    tax = subtotal * 0.08
    total = subtotal + tax
    print(f"Subtotal: ${subtotal}")
    print(f"Tax: ${tax}")
    print(f"Total: ${total}")
```

**When to apply:** Any time a function is doing more than one thing. Any time you'd want to write a comment to explain a block.

### Inline Function

The opposite of Extract. Use when an indirection adds nothing.

**Before:**
```javascript
function getRating(driver) {
  return moreThanFiveLateDeliveries(driver) ? 2 : 1;
}
function moreThanFiveLateDeliveries(driver) {
  return driver.numberOfLateDeliveries > 5;
}
```

**After:**
```javascript
function getRating(driver) {
  return driver.numberOfLateDeliveries > 5 ? 2 : 1;
}
```

### Rename (Variable / Function / Class)

Cheap and high-value. Modern IDEs do this safely. If a name doesn't reveal intent, rename it.

### Replace Magic Number with Named Constant

```javascript
// Before
if (user.age >= 18) { /* ... */ }

// After
const LEGAL_ADULT_AGE = 18;
if (user.age >= LEGAL_ADULT_AGE) { /* ... */ }
```

### Introduce Parameter Object

When the same group of parameters travels together, make them a real type.

**Before:**
```typescript
function bookFlight(from: string, to: string, depart: Date, return_: Date, passengers: number) { /* ... */ }
```

**After:**
```typescript
interface FlightSearch {
  from: string;
  to: string;
  depart: Date;
  return_: Date;
  passengers: number;
}
function bookFlight(search: FlightSearch) { /* ... */ }
```

### Replace Conditional with Polymorphism

When a switch/if-chain dispatches based on type, convert to subclasses.

**Before:**
```python
def calculate_pay(employee):
    if employee.type == 'engineer':
        return employee.hours * employee.rate
    elif employee.type == 'manager':
        return employee.salary
    elif employee.type == 'salesperson':
        return employee.salary + employee.commission
```

**After:**
```python
class Employee: pass
class Engineer(Employee):
    def calculate_pay(self): return self.hours * self.rate
class Manager(Employee):
    def calculate_pay(self): return self.salary
class Salesperson(Employee):
    def calculate_pay(self): return self.salary + self.commission
```

Now adding a new role doesn't require modifying existing code.

**When NOT to apply:** If you only have 2 cases and they'll never grow, the if/else is simpler. OCP isn't worth the abstraction overhead for small static sets.

### Replace Loop with Pipeline (Functional)

```javascript
// Before
const adults = [];
for (const person of people) {
  if (person.age >= 18) {
    adults.push(person.name);
  }
}

// After
const adults = people
  .filter(person => person.age >= 18)
  .map(person => person.name);
```

The pipeline reads as a sequence of transformations, which usually beats imperative loops for cognitive load.

### Guard Clauses (Early Return)

Replace nested conditionals with early exits.

```javascript
// Before
function getPayAmount(employee) {
  let result;
  if (employee.isSeparated) {
    result = { amount: 0, reasonCode: 'SEP' };
  } else {
    if (employee.isRetired) {
      result = { amount: 0, reasonCode: 'RET' };
    } else {
      // calculate normal pay...
      result = { amount: calc, reasonCode: 'OK' };
    }
  }
  return result;
}

// After
function getPayAmount(employee) {
  if (employee.isSeparated) return { amount: 0, reasonCode: 'SEP' };
  if (employee.isRetired) return { amount: 0, reasonCode: 'RET' };
  // calculate normal pay...
  return { amount: calc, reasonCode: 'OK' };
}
```

## The "two hats" rule

When working on existing code, you wear one of two hats — never both at once:

1. **Refactoring hat:** Improve structure without changing behavior. No new features. No bug fixes.
2. **Feature hat:** Add or change behavior. No structural changes beyond what's required.

If you're refactoring and notice a bug, write a ticket and keep refactoring. If you're adding a feature and notice ugly code, finish the feature, commit, then put the refactoring hat on.

This discipline prevents commits that mix structural and behavioral changes — the kind that are nearly impossible to review or revert safely.

## When NOT to refactor

- **Code that's about to be deleted.** Don't polish what's leaving.
- **Code without tests AND no time to write them.** Refactoring without tests is gambling.
- **Code outside your responsibility / area of expertise.** You might break invariants you don't understand.
- **Right before a release.** Refactor in calm waters, not under deadline pressure.
- **Working code that nobody reads or modifies.** If it ain't broke and you ain't touching it, leave it.

## The Boy Scout Rule in practice

Leave every file slightly cleaner than you found it. This doesn't mean overhauling files you touch — it means:

- Renamed a confusing variable while fixing a bug? Commit it.
- Noticed a `// TODO: remove this` from 2019 that's no longer needed? Delete it.
- Saw a 5-line block of commented-out code? Delete it.
- Spotted a magic number? Name it.

Tiny cleanups, every time you touch the code. Over a year, this rebuilds the whole codebase from the inside out.

## How to give a code review using this vocabulary

When reviewing code, name the smell precisely:

❌ Vague: "This function is too complex."
✅ Specific: "This is a Long Method with Feature Envy — `calculateOrderTotal` mostly accesses `customer` data. I'd Move Method to put it on `Customer`, then Extract Method on the price-calculation block."

The vocabulary makes feedback actionable. The author knows exactly which refactoring to apply.
