# React / Next.js Specific Guidance

Load this when working in React, Next.js, or any React-based framework.

## Component file structure

A typical well-organized component file follows this top-to-bottom order:

```typescript
// 1. External imports
import { useState, useMemo, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// 2. Internal imports
import { Button } from '@/components/ui/Button';
import { useUser } from '@/features/auth/hooks';
import { formatCurrency } from '@/lib/format';

// 3. Types
interface OrderListProps {
  customerId: string;
  initialFilter?: OrderFilter;
}

// 4. Constants
const DEFAULT_PAGE_SIZE = 20;

// 5. The component itself
export function OrderList({ customerId, initialFilter }: OrderListProps) {
  // hooks first, in a stable order
  // computed values
  // event handlers
  // JSX
}

// 6. Internal helpers (if small and only used here)
function formatOrderRow(order: Order) { /* ... */ }
```

## Component size

Same general rule: 200–300 lines is a good target. **Beyond that, almost certainly a multi-component or a hook needs to be extracted.**

Common refactorings for oversized components:

1. **Extract a custom hook** when state + effect logic is complex
   ```typescript
   // Before: 400-line component with 8 useStates and 5 useEffects
   // After: 150-line component using useOrderManagement(customerId)
   ```

2. **Extract child components** for visually distinct sections
   ```typescript
   // Before: one OrderPage with header, filters, list, pagination, modal all inline
   // After: OrderPage composes <OrderHeader>, <OrderFilters>, <OrderList>, <OrderPagination>, <OrderModal>
   ```

3. **Extract pure helpers** for formatting/computation
   ```typescript
   // Before: inline formatting logic everywhere in JSX
   // After: formatOrderStatus(), formatOrderTotal(), getStatusColor() as helpers
   ```

## Hooks discipline

### Rules of hooks (the official ones, but worth restating)

1. Only call hooks at the top level of components or other hooks
2. Don't call hooks inside loops, conditions, or nested functions
3. Custom hook names must start with `use`

### Custom hook design

A custom hook should have one job, with a clear, named return.

```typescript
// Good — focused, named return
export function useOrderForm(initialOrder?: Order) {
  const [values, setValues] = useState(initialOrder ?? emptyOrder);
  const [errors, setErrors] = useState<FormErrors>({});

  const validate = useCallback(() => { /* ... */ }, [values]);
  const submit = useCallback(async () => { /* ... */ }, [values, validate]);

  return { values, errors, setValues, validate, submit };
}

// Usage is self-documenting
const { values, errors, setValues, submit } = useOrderForm(order);
```

### Avoid the prop-drilling-via-hooks anti-pattern

Don't put 15 unrelated values in one big "useEverything" hook. Split by concern. Compose hooks within hooks.

## State management

### Decision order for "where does this state live?"

1. **Local component state (`useState`)** — if only this component cares
2. **Lifted to nearest common parent** — if siblings need it, lift it
3. **React Context** — if many components across the tree need it AND it changes infrequently (auth, theme, locale)
4. **State management library** (Zustand, Redux Toolkit, Jotai) — if you have complex cross-cutting state with frequent updates
5. **Server state library** (TanStack Query, SWR, RTK Query) — for anything fetched from a backend

**Don't use Context for everything.** Context re-renders all consumers when value changes; that's expensive for hot paths.

**Don't use Redux for simple state.** Redux's boilerplate tax only pays off for genuinely complex global state.

**Server state ≠ client state.** Don't put fetched data in `useState` and then manually manage caching, refetching, invalidation. That's TanStack Query / SWR's job.

### useState anti-patterns

```typescript
// Bad — multiple useStates that should be one object
const [firstName, setFirstName] = useState('');
const [lastName, setLastName] = useState('');
const [email, setEmail] = useState('');
const [age, setAge] = useState(0);

// Good — one structured state
const [form, setForm] = useState({ firstName: '', lastName: '', email: '', age: 0 });
const updateField = (field: keyof typeof form, value: string | number) =>
  setForm(prev => ({ ...prev, [field]: value }));

// Better — useReducer when state changes have multiple actions
const [form, dispatch] = useReducer(formReducer, initialForm);
```

### useEffect anti-patterns

```typescript
// Bad — derived state in useEffect
const [user, setUser] = useState();
const [isAdmin, setIsAdmin] = useState(false);
useEffect(() => {
  setIsAdmin(user?.role === 'admin');  // unnecessary
}, [user]);

// Good — compute it directly
const isAdmin = user?.role === 'admin';

// Bad — fetching in useEffect with manual everything
useEffect(() => {
  setLoading(true);
  fetch('/api/orders')
    .then(r => r.json())
    .then(data => setOrders(data))
    .catch(err => setError(err))
    .finally(() => setLoading(false));
}, []);

// Good — use TanStack Query / SWR
const { data: orders, error, isLoading } = useQuery({ queryKey: ['orders'], queryFn: fetchOrders });
```

**useEffect is for synchronizing with external systems** (subscriptions, DOM APIs, browser APIs). It's not for data fetching, derived state, or event handling.

## Performance: don't optimize prematurely

React is fast by default. Most performance "optimizations" are noise that adds complexity without measurable benefit.

**Don't reach for `useMemo`, `useCallback`, `React.memo` until you've measured a problem.** They have a real cost (extra dependency arrays to maintain, stale closure bugs, mental overhead).

**Use them when:**
- A child component is expensive to render AND its parent re-renders frequently
- A computation is genuinely expensive (sorting/filtering large lists)
- A callback is being passed as a dependency to a deeply-memoized child

**Don't use them when:**
- The render is fast and infrequent
- The computation is trivial (`a + b`)
- You're "just being safe"

The rule: profile first, optimize second.

## Accessibility (a11y)

Senior React engineers ship accessible code. This is non-negotiable for production apps.

### The minimum

- **Semantic HTML.** Use `<button>` for buttons, `<a>` for links, `<form>` for forms. Don't `<div onClick>` everything.
- **Alt text on images.** `<img alt="">` (empty alt) for decorative; descriptive alt for content.
- **Labels on form inputs.** Either `<label htmlFor>` or `aria-label`. Never label-less inputs.
- **Keyboard navigation works.** Tab through your UI; if you can't reach something with the keyboard, it's broken.
- **Color contrast.** Text vs background must meet WCAG AA (4.5:1 for body text). Use a contrast checker.
- **Focus visible.** Don't `outline: none` without a replacement. Keyboard users need to see focus.

### Run an audit

Use Lighthouse, axe DevTools, or a CI plugin like `eslint-plugin-jsx-a11y`. Catches most issues automatically.

## Error boundaries

Every production React app should have error boundaries:

```typescript
// app/error.tsx (Next.js App Router)
'use client';
export default function ErrorBoundary({ error, reset }: { error: Error; reset: () => void }) {
  // Log to error tracking
  useEffect(() => { errorTracker.report(error); }, [error]);

  return (
    <div>
      <h2>Something went wrong</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

Without error boundaries, a single component error crashes the entire app to a blank page.

## Forms: don't reinvent

For non-trivial forms, use a library: **React Hook Form** + **Zod** is the current best-in-class combination.

Manual `useState`-per-field forms work for 2–3 fields; beyond that you reinvent validation, error display, dirty tracking, and submission state.

## Folder structure: feature-based

For non-trivial apps, organize by **feature**, not by **type**.

**Bad (organized by type — every feature change touches every folder):**
```
src/
├── components/
├── hooks/
├── utils/
├── types/
└── api/
```

**Good (organized by feature — change one feature, touch one folder):**
```
src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api.ts
│   │   ├── types.ts
│   │   └── index.ts          ← barrel export
│   ├── orders/
│   │   └── ...
│   └── billing/
│       └── ...
├── shared/                    ← truly shared across features
│   ├── ui/                    ← Button, Input, Modal, etc.
│   ├── lib/                   ← formatCurrency, parseDate, etc.
│   └── types/                 ← global types
└── app/                       ← routing (Next.js)
```

Move features as units. Delete features as units. Onboard new devs by feature.

## Common React anti-patterns

- **Using `index` as a key in dynamic lists.** Breaks reconciliation when items reorder. Use a stable id.
- **Mutating state directly.** `state.items.push(newItem)` doesn't trigger a re-render. Use `setState([...state.items, newItem])` or Immer.
- **Putting business logic in components.** Components should orchestrate; logic lives in hooks, services, or pure functions.
- **Massive prop drilling.** If a prop traverses 5+ components, lift to context, state library, or component composition.
- **Inline object/array literals as props for memoized children.** Creates a new reference every render, breaks memoization. Move outside the component or `useMemo`.
- **`useEffect` chains where each effect updates state that triggers another effect.** Almost always a sign that the logic should be derived, not effected.
- **Using `dangerouslySetInnerHTML` with user-supplied content.** XSS waiting to happen. Sanitize first or don't.

## Testing React components

- **Test what the user sees, not implementation details.** Don't test "useState was called with X." Test "the page shows 'Welcome, Alice' after login."
- **React Testing Library is the right tool.** It pushes you toward behavior-based tests.
- **Don't test framework features.** Don't test that `useState` works.
- **Mock at the network level**, not at the hook level. MSW (Mock Service Worker) is the gold standard.

```typescript
// Good — tests behavior
test('shows error when login fails', async () => {
  server.use(
    http.post('/api/login', () => HttpResponse.json({ error: 'Invalid' }, { status: 401 }))
  );
  render(<LoginForm />);
  await user.type(screen.getByLabelText(/email/i), 'a@b.com');
  await user.type(screen.getByLabelText(/password/i), 'wrong');
  await user.click(screen.getByRole('button', { name: /log in/i }));
  expect(await screen.findByText(/invalid/i)).toBeInTheDocument();
});
```
