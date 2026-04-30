# Hallucination Patterns

The recurring AI failure modes that produce code that looks right but isn't. Verify against this list during the audit.

---

## 1. Cross-language idiom leakage

AI models are trained on multi-language corpora and routinely leak idioms from one language into another. Each language section below shows the foreign idiom (slop) and the correct native form.

### In Python files

| Slop | Source | Correct |
|------|--------|---------|
| `items.push("x")` | JS | `items.append("x")` |
| `items.length` | JS | `len(items)` |
| `console.log("x")` | JS | `print("x")` or proper logger |
| `const x = 5` | JS | `x = 5` (Python has no `const`) |
| `value === other` | JS | `value == other` or `value is other` |
| `null` | JS/Java | `None` |
| `undefined` | JS | `None` |
| `true` / `false` | JS/Java | `True` / `False` |
| `obj.toString()` | Java | `str(obj)` |
| `name.equals(other)` | Java | `name == other` |
| `name.ToLower()` | C# | `name.lower()` |
| `string.Empty` | C# | `""` |
| `fmt.Println("x")` | Go | `print("x")` |
| `:=` | Go | `=` |
| `switch ... case` (C-style) | C/Java | `match ... case` (3.10+) or if/elif |
| `// comment` | C/Java/JS | `# comment` |
| `function foo()` | JS | `def foo():` |
| `=>` arrow functions | JS | `lambda` or named `def` |
| `async function foo()` | JS | `async def foo():` |
| `try { ... } catch (e) { ... }` | JS/Java | `try: ... except Exception as e: ...` |

### In JavaScript / TypeScript files

| Slop | Source | Correct |
|------|--------|---------|
| `len(arr)` | Python | `arr.length` |
| `arr.append(x)` | Python | `arr.push(x)` |
| `print("x")` | Python | `console.log("x")` |
| `True` / `False` | Python | `true` / `false` |
| `None` | Python | `null` or `undefined` (different meanings) |
| `def foo() {}` | Python | `function foo() {}` or `const foo = () => {}` |
| `# comment` | Python | `// comment` |
| `elif` | Python | `else if` |
| `str(x)` | Python | `String(x)` or `x.toString()` |
| `dict[key]` access where key doesn't exist returning undefined | Python `dict` | JS objects throw / return undefined; Maps have `.get()` |

### In Go files

| Slop | Source | Correct |
|------|--------|---------|
| `console.log` | JS | `fmt.Println` |
| `print` | Python | `fmt.Println` (`print` exists but is for debugging) |
| `try/catch` | Java/JS | Go uses `if err != nil` |
| `throw err` | JS/Java | `return err` |
| `null` | JS | `nil` |
| `class Foo { ... }` | Java/JS | `type Foo struct { ... }` + methods |

### In Rust files

| Slop | Source | Correct |
|------|--------|---------|
| `null` / `None` (capitalized in wrong place) | Various | `None` (in `Option`) |
| `throw err` | JS/Java | `return Err(...)` or `?` operator |
| `class Foo` | OOP languages | `struct Foo` + `impl` |
| `for (let i = 0; i < n; i++)` | C-style | `for i in 0..n` |

---

## 2. Hallucinated imports

Common patterns where AI invents packages or modules that don't exist.

**Verification process:** for any import you didn't see in the surrounding code, check the project's dependency manifest:
- JavaScript / TypeScript: `package.json`
- Python: `requirements.txt`, `pyproject.toml`, `Pipfile`, `poetry.lock`
- Rust: `Cargo.toml`
- Go: `go.mod`
- Ruby: `Gemfile`
- Java: `pom.xml`, `build.gradle`

**Common hallucinations to watch for:**

- **Composite package names** — `lodash-utils`, `react-helpers`, `axios-extras`. AI loves to invent these. Real packages tend to have established names.
- **Plausible-but-fake AWS SDK paths** — `import { S3Manager } from 'aws-sdk-helpers'`. The real AWS SDK has specific module paths (`@aws-sdk/client-s3`).
- **Submodule paths that don't exist** — `import x from 'libname/utils'` when `libname` doesn't expose `/utils`.
- **Older package names that have been renamed** — AI training data may include old names. Check for the modern equivalent.

---

## 3. Hallucinated method calls

AI invents method names on real types. Common patterns:

- `array.findLast()` — real in modern JS (ES2023), but AI invents similar-sounding methods like `findLastWhere`, `findReverse`, `lastFind`.
- `Object.entries(...).map(([k,v]) => ...)` is real; `Object.mapValues(...)` is not — that's Lodash, not native.
- `string.replaceAll()` — real (ES2021); `string.replaceFirst()` is not (it's `replace()` without `/g`).
- Python: `list.sort_by()` is not real (use `sorted(list, key=...)` or `list.sort(key=...)`).
- Python: `dict.has_key()` was removed in Python 3 (use `key in dict`).

**Verification:** if you call a method you didn't see in the surrounding code, look it up. Don't guess.

---

## 4. Hallucinated environment variables / config keys

Patterns where AI invents env var names or config keys based on what "should" exist.

- `STRIPE_API_KEY` when the project actually uses `STRIPE_SECRET_KEY`
- `DATABASE_URL` vs `DB_URL` vs `DB_CONNECTION_STRING` — the project uses one, not all three
- Made-up feature flags: `FEATURE_NEW_AUTH_ENABLED` when the project uses `flags.newAuth`

**Verification:** grep the codebase for env var usage (`process.env.`, `os.getenv(`, `os.environ[`, `ENV[`) and config-loading code. Use what already exists.

---

## 5. Hallucinated framework features

AI invents features in popular frameworks based on what "would be reasonable":

- React: `useDebouncedState` is not a built-in hook (it's userland); `useTransition` and `useDeferredValue` are real.
- Next.js: `getServerProps` doesn't exist; it's `getServerSideProps`.
- Express: `app.use(cors())` requires the `cors` package, not built-in.
- Django: `models.JSONField()` exists in 3.1+; in older versions it was `JSONField` from `django.contrib.postgres`.
- Tailwind: `bg-blur` is not a class; it's `backdrop-blur` or `blur-*`.

**Verification:** when using a framework feature you're not 100% sure about, check the framework's actual docs OR look for an existing use in the codebase.

---

## 6. Date / version hallucination

AI may "remember" old versions of APIs.

- Node.js APIs from before they were promisified
- Python 2-style print statements in Python 3 code
- React class-component patterns in a modern hooks-only codebase
- Old AWS SDK v2 patterns when the project uses v3

**Verification:** look at adjacent code. If the surrounding code uses one style consistently, match it.

---

## 7. Confident-sounding wrong syntax

Patterns where the syntax looks plausible and even compiles, but does the wrong thing.

- `JSON.parse(JSON.stringify(obj))` as "deep clone" — works for plain data, fails for Dates, functions, undefined, circular refs.
- `await Promise.all(arr.map(async x => ...))` is fine; `await arr.forEach(async ...)` is broken (forEach doesn't await).
- Python: `mutable_default=[]` — every call shares the same list (see Code Rules A13).
- `==` vs `===` in JS, `==` vs `is` in Python — different semantics, AI sometimes picks wrong.
- TypeScript: `as any` to "fix" a type error is hiding the real issue, not solving it.

---

## 8. Made-up "best practices"

AI sometimes invents conventions that sound authoritative but aren't real:

- "The X foundation recommends..." (no such recommendation)
- "It's standard practice to..." (it isn't)
- "The official Y style guide says..." (it doesn't)

**Verification:** if you find yourself citing an authority for a code decision, either link to the actual source or drop the citation.
