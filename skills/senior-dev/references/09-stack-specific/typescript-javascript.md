# TypeScript / JavaScript Specific Guidance

Load this when working in modern JavaScript or TypeScript, regardless of framework.

## TypeScript: use it properly

If you're using TypeScript, use it for what it's worth. Half-typed code is worse than untyped code — it lies to you.

### Strict mode is non-negotiable

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true
  }
}
```

Without `strict: true`, you're paying TypeScript's costs without getting most of its value.

### Avoid `any`

`any` disables type checking entirely. It's worse than `unknown` because it silently propagates.

```typescript
// Bad
function process(data: any) {
  return data.value;  // no error, even if data.value doesn't exist
}

// Good — `unknown` requires you to narrow before use
function process(data: unknown) {
  if (typeof data === 'object' && data !== null && 'value' in data) {
    return (data as { value: unknown }).value;
  }
  throw new Error('invalid input');
}

// Better — validate with Zod and get a real type
const schema = z.object({ value: z.string() });
function process(data: unknown) {
  const parsed = schema.parse(data);  // throws if invalid; parsed is { value: string }
  return parsed.value;
}
```

If you must use `any`, comment why: `// any: third-party library has no types`.

### Prefer `unknown` over `any` for boundary inputs

Anything coming from outside your trust zone (HTTP body, JSON parse, third-party API) is `unknown` until validated. Use a schema validator to convert `unknown` → typed.

### Use `as const` for literal types

```typescript
// Bad — type is string
const config = { env: 'production', port: 3000 };

// Good — type is { env: 'production', port: 3000 }
const config = { env: 'production', port: 3000 } as const;

// Useful for tagged unions
const ROLES = ['admin', 'user', 'guest'] as const;
type Role = typeof ROLES[number];  // 'admin' | 'user' | 'guest'
```

### Discriminated unions for state

When state has multiple shapes, model it with a discriminated union. Don't use optional fields that are "sometimes there."

```typescript
// Bad — many invalid states are representable
interface Request {
  loading: boolean;
  data?: User;
  error?: Error;
}
// What does { loading: true, data: someUser, error: someError } mean?

// Good — only valid states are representable
type Request =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: User }
  | { status: 'error'; error: Error };

// TypeScript narrows by checking the discriminator
function render(req: Request) {
  switch (req.status) {
    case 'idle': return null;
    case 'loading': return <Spinner />;
    case 'success': return <UserCard user={req.data} />;  // data is typed
    case 'error': return <Error message={req.error.message} />;  // error is typed
  }
}
```

### Don't fight the type system

If you find yourself reaching for `as any`, `// @ts-ignore`, or `as unknown as Foo`, stop. The type system is telling you something. Either:

- Your design is wrong and you should restructure
- The third-party types are wrong and you should fix them at the boundary (single `as` cast in one place, narrow as fast as possible)

Fighting the type system means you've lost the safety guarantee for that code path.

### Naming conventions

| Thing | Convention | Example |
|---|---|---|
| Variables, functions | camelCase | `userName`, `calculateTotal` |
| Classes, types, interfaces | PascalCase | `UserProfile`, `OrderStatus` |
| Constants (true compile-time) | SCREAMING_SNAKE_CASE | `MAX_RETRIES`, `API_VERSION` |
| Private fields | leading `_` (or use `private` modifier) | `_internalState` |
| Type parameters | Single capital, or `T`-prefixed | `T`, `TKey`, `TValue` |
| Interfaces | NO `I` prefix | `User`, not `IUser` |
| Booleans | `is`/`has`/`should`/`can` prefix | `isActive`, `hasPermission` |

## Modern JavaScript essentials

### Use `const` by default, `let` when reassignment is needed, never `var`

```javascript
const items = [1, 2, 3];           // immutable binding (the array's contents can still change)
let counter = 0; counter++;        // mutable binding
var x = 5;                          // function-scoped, hoisted, footgun — never use
```

### Use modern array/object operations

```javascript
// Bad — manual loops
const adultNames = [];
for (let i = 0; i < users.length; i++) {
  if (users[i].age >= 18) adultNames.push(users[i].name);
}

// Good — pipeline
const adultNames = users
  .filter(user => user.age >= 18)
  .map(user => user.name);
```

Common operations to know fluently: `map`, `filter`, `reduce`, `find`, `some`, `every`, `flatMap`, `sort`, `Object.entries`, `Object.keys`, `Object.values`, `Object.fromEntries`, spread/rest.

### Destructuring everywhere

```javascript
// Bad
function greet(user) {
  console.log('Hello ' + user.firstName + ' ' + user.lastName);
}

// Good
function greet({ firstName, lastName }) {
  console.log(`Hello ${firstName} ${lastName}`);
}

// Defaults with destructuring
function fetchUsers({ limit = 20, offset = 0 } = {}) { /* ... */ }
```

### Optional chaining and nullish coalescing

```javascript
// Bad — verbose null checks
const city = user && user.address && user.address.city ? user.address.city : 'Unknown';

// Good
const city = user?.address?.city ?? 'Unknown';
```

`?.` short-circuits if any link is null/undefined. `??` only falls back on null/undefined (unlike `||` which falls back on any falsy value, including `0` and `""`).

### async/await over promise chains

```javascript
// Bad — nested promises
function fetchUserData(id) {
  return fetch(`/users/${id}`)
    .then(r => r.json())
    .then(user => fetch(`/orders?userId=${user.id}`)
      .then(r => r.json())
      .then(orders => ({ ...user, orders }))
    );
}

// Good — sequential async/await
async function fetchUserData(id) {
  const user = await fetch(`/users/${id}`).then(r => r.json());
  const orders = await fetch(`/orders?userId=${user.id}`).then(r => r.json());
  return { ...user, orders };
}
```

### Parallelize when independent

```javascript
// Bad — sequential when they could be parallel
const user = await fetchUser(id);
const settings = await fetchSettings(id);
const notifications = await fetchNotifications(id);

// Good — parallel
const [user, settings, notifications] = await Promise.all([
  fetchUser(id),
  fetchSettings(id),
  fetchNotifications(id),
]);
```

`Promise.all` rejects on first failure. Use `Promise.allSettled` if you want to wait for all and inspect successes/failures separately.

### Immutability by default

Don't mutate. Return new objects/arrays.

```javascript
// Bad
const addItem = (cart, item) => { cart.items.push(item); return cart; };

// Good
const addItem = (cart, item) => ({ ...cart, items: [...cart.items, item] });
```

For complex immutable updates, use Immer (`produce`) — it lets you write mutating-looking code that's actually immutable.

### Equality

Use `===` and `!==`. Never `==` and `!=` (they coerce types in surprising ways).

```javascript
0 == ''       // true (?!)
null == undefined  // true (?!)
'1' == 1      // true (?!)
0 === ''      // false (sane)
```

Exception: `x == null` is sometimes used as a shorthand for `x === null || x === undefined`. It's the only acceptable use of `==`.

## Avoid these JavaScript footguns

### `this` is unpredictable in callbacks

Use arrow functions in callbacks; they preserve `this` from the enclosing scope.

```javascript
// Bad — `this` is wrong
class Counter {
  constructor() { this.count = 0; }
  start() { setInterval(function() { this.count++; }, 1000); }  // `this` is global, not Counter
}

// Good
class Counter {
  constructor() { this.count = 0; }
  start() { setInterval(() => { this.count++; }, 1000); }  // `this` is Counter
}
```

### Mutable default parameters

Don't use mutable objects as default parameters — they're shared across calls.

```javascript
// Bad
function addItem(item, list = []) {
  list.push(item);
  return list;
}
// First call: returns [item1]
// Second call: returns [item1, item2] — same array!

// Good
function addItem(item, list) {
  return [...(list ?? []), item];
}
```

### Number precision

JavaScript numbers are IEEE 754 floats. `0.1 + 0.2 !== 0.3`. For currency, use cents (integer) or a library like `decimal.js`. Never use floats for money.

### `JSON.parse` throws on invalid input

Always wrap in try/catch when parsing untrusted JSON.

```javascript
function safeParse(json) {
  try {
    return { ok: true, value: JSON.parse(json) };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}
```

## Module organization

### Prefer named exports over default exports

```typescript
// Bad — default export
export default function UserCard() { /* ... */ }

// Good — named export
export function UserCard() { /* ... */ }
```

Why: named exports are easier to refactor (rename works across the codebase), better for IDE autocomplete, and don't allow inconsistent renaming on import.

### Barrel exports for module boundaries

```typescript
// features/users/index.ts
export { UserCard } from './UserCard';
export { UserList } from './UserList';
export { useUser } from './useUser';
export type { User, UserRole } from './types';

// Consumer
import { UserCard, useUser } from '@/features/users';
```

This lets you reorganize internals of `features/users/` without breaking consumers.

### Avoid deep relative imports

```typescript
// Bad
import { Button } from '../../../components/ui/Button';

// Good — use path aliases
import { Button } from '@/components/ui/Button';
```

Configure path aliases in `tsconfig.json` and your bundler.

## Linting and formatting

Use both, configured strictly, in pre-commit and CI:

- **ESLint** for code quality (rules about logic, common bugs)
- **Prettier** for formatting (no debates about spaces vs tabs)
- **TypeScript ESLint** plugin if using TS

Recommended rule additions beyond defaults:
- `no-console` (warn) — forces explicit `console.log` discussion in PRs
- `no-unused-vars` (error) — catches dead code
- `eqeqeq` (error) — forces `===`
- `prefer-const` (error)
- `no-var` (error)
- `@typescript-eslint/no-explicit-any` (warn or error)
- `@typescript-eslint/no-floating-promises` (error) — catches missing `await`

Configure once, never argue about style again.
