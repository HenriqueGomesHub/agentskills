# File and Class Size Limits

Load this when the user asks "is this file too big?", "should I split this?", or when reviewing a file approaching size limits.

## The honest answer about file size

There is no universally correct file size. The right size depends on cohesion: a file should be as large as it needs to be to express one coherent idea, and no larger. The numerical limits below are *guidelines based on collective experience* — they exist because past a certain size, human cognition breaks down regardless of how cohesive the code is.

## Empirical limits from authoritative sources

| Source | Function/Method | File/Class |
|---|---|---|
| Robert C. Martin (*Clean Code*) | < 20 lines | 200–500 lines |
| Steve McConnell (*Code Complete*) | ~150–200 lines for routines | No fixed rule — based on cohesion |
| Martin Fowler (*Refactoring*) | Extract when "you need to scroll" | Driven by code smells |
| PMD static analyzer (default) | 100 lines | 1000 lines |
| Checkstyle (default) | 50 lines | 1500 lines |
| Rule of 30 (Lippert) | < 30 lines avg | < 30 methods (~900 lines) |
| Practitioner consensus | < 20 lines | 200–300 sweet spot, 500 ceiling |

**Working rule:** Aim for 200–300 lines per file. Treat 500 as a yellow flag. Treat 800+ as a red flag that needs justification.

## Why the limits exist

The real reason for size limits isn't aesthetic — it's cognitive:

1. **Working memory.** Humans hold ~7 things in mind at once. A 1000-line file forces context-swapping that exhausts mental capacity.
2. **Diff readability.** A small change to a 2000-line file produces a diff that's painful to review. Reviewers approve without really reading.
3. **Merge conflicts.** Big files concentrate changes; multiple developers touching the same big file = constant conflicts.
4. **Test surface area.** Big files have many responsibilities; testing them requires elaborate setup.
5. **Search cost.** Finding "where does this happen?" gets slower as files grow.
6. **Onboarding cost.** A new dev opening a 1500-line component thinks "I'll never understand this codebase."

Short files don't *cause* good design, but long files almost always *signal* poor design.

## How to know your file is too big

Quantitative signs:
- More than 300 lines
- More than 10–15 functions/methods
- More than ~5 distinct concerns (data, validation, API calls, UI, formatting...)
- Imports span more than 15 packages

Qualitative signs (more important):
- You can't summarize what the file does in one sentence without using "and"
- Different developers tend to edit different parts (suggests SRP violation)
- You scroll multiple times to read it
- Tests for this file have elaborate setup with many mocks
- Bugs in this file frequently affect unrelated features
- New team members ask "what does this file do?"

## How to split a file that's too big

The split should follow **cohesion** — group code that changes together, separate code that changes independently.

### Strategy 1: Split by responsibility (SRP-driven)

If your file does three things, make three files.

**Before (`UserController.ts` — 600 lines):**
- HTTP route handlers
- Validation logic
- Database queries
- Email sending

**After:**
- `UserController.ts` (100 lines) — just HTTP routing
- `UserValidator.ts` (80 lines) — validation
- `UserRepository.ts` (150 lines) — database
- `UserNotifier.ts` (90 lines) — emails

### Strategy 2: Split by feature (folder-by-feature)

When a single feature spans multiple files, group them in a folder.

**Before (flat structure):**
```
src/
  components/
    UserList.tsx
    UserCard.tsx
    UserForm.tsx
    UserAvatar.tsx
    OrderList.tsx
    OrderCard.tsx
    OrderForm.tsx
```

**After (feature folders):**
```
src/
  features/
    users/
      UserList.tsx
      UserCard.tsx
      UserForm.tsx
      UserAvatar.tsx
      index.ts          # barrel export
    orders/
      OrderList.tsx
      OrderCard.tsx
      OrderForm.tsx
      index.ts
```

This keeps related files close and unrelated files apart. It also makes refactoring easier: you can move/rename a feature folder atomically.

### Strategy 3: Split by layer (separation of concerns)

For a single feature, separate the layers:

```
features/orders/
  Order.tsx              # presentation
  useOrder.ts            # state management hook
  orderApi.ts            # network calls
  orderUtils.ts          # pure helpers
  orderTypes.ts          # types/interfaces
  orderConstants.ts      # constants
  index.ts               # barrel export
```

Each file has one clear responsibility. The barrel `index.ts` keeps imports tidy elsewhere in the codebase.

### Strategy 4: Extract a class or module

If a chunk of a class consistently operates on a subset of the data, that's a sign it wants to be its own class.

**Before (one big class):**
```python
class Order:
    def calculate_subtotal(self): ...
    def calculate_tax(self): ...
    def calculate_shipping(self): ...
    def calculate_discount(self): ...
    def calculate_total(self): ...

    def send_confirmation_email(self): ...
    def send_shipping_email(self): ...
    def send_refund_email(self): ...
```

**After (extracted classes):**
```python
class Order: ...

class OrderPriceCalculator:
    def __init__(self, order: Order): ...
    def subtotal(self): ...
    def tax(self): ...
    # etc

class OrderEmailSender:
    def __init__(self, order: Order): ...
    def send_confirmation(self): ...
    # etc
```

## Class size guidelines

A class should:
- Have **< 10 methods** ideally; **20** is the ceiling
- Have **< 5–7 instance variables**
- Fit on one screen for the public interface (the method signatures)

If your class has 30 methods, it's almost certainly violating SRP. Split it.

The famous C3 project — birthplace of Extreme Programming — averaged 12 methods per class. That's a useful benchmark.

## Function-per-file vs. multi-function files

Different ecosystems have different conventions:
- **JavaScript/TypeScript:** small modules with multiple related functions are normal
- **Java/C#:** typically one public class per file
- **Python:** modules group related functions; one-class-per-file is rare
- **Go:** packages can contain many small files; small files are encouraged

Match the ecosystem's conventions. Don't impose Java-style "one class per file" on a Python project.

## Special cases where bigger files are OK

- **Configuration files** (route tables, schema definitions, large JSON-like constants) — splitting them often hurts readability
- **Generated code** — don't manually split what tools regenerate
- **Single coherent enum/type definitions** — a 300-line `ErrorCode` enum might be fine if it's one concept
- **Tightly coupled state machines** — sometimes the cohesion is so strong that splitting harms understanding

In these cases, document why the file is large in a top-of-file comment.

## Refactoring an oversized file: practical sequence

1. **Don't refactor the whole thing at once.** Big-bang refactors fail.
2. **Start with the obvious.** Extract one cohesive group at a time.
3. **Run tests after each extraction.** If you don't have tests, write characterization tests first (see *Working Effectively with Legacy Code*).
4. **Commit after each successful extraction.** Atomic commits make reverts safe.
5. **Stop when the file is "good enough."** You don't need to hit a specific line count — you need to make the file understandable.

## When NOT to split

Don't split a file just to hit a line count. Splits that hurt readability:

- Splitting a 250-line file into 5 fifty-line files when the 250 lines were cohesive
- Creating one-function files when those functions are only ever called together
- Adding folder structure deeper than 3–4 levels (people stop navigating)
- Extracting interfaces that have only one implementation and no test mock

The goal is *understandability*, not file count.

## Quick decision rule

When deciding whether to split:

1. Can I describe this file's purpose in one sentence with no "and"? → keep it
2. Do all functions in this file change together? → keep it
3. Would a new developer understand this file in 5 minutes? → keep it
4. If any answer is "no" → split

Don't split based on line count alone. Split based on cohesion.
