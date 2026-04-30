# General / Other Languages

Load this when the user is working in a language not covered by the other stack-specific files (Java, Go, C#, Rust, PHP, Ruby, Kotlin, Swift, etc.) or when the question is language-agnostic.

The principles in `01-principles.md`, `02-naming-and-functions.md`, etc. apply universally. This file covers the language-specific touchpoints where senior judgment matters most.

## Match the language's idioms

The single most important rule when working in any language: **write code that looks like the rest of that language's ecosystem**. A Pythonic Python codebase, an idiomatic Go codebase, a Rusty Rust codebase. Fighting the language's conventions creates code that's harder to read for everyone who knows that language.

This means:
- **In Go:** small interfaces, error returns (not exceptions), no inheritance, package-level organization
- **In Rust:** ownership and borrowing first-class, `Result<T, E>` for fallibility, traits for polymorphism
- **In Java:** classes for everything, exceptions for errors, package-by-feature, dependency injection
- **In C#:** properties not getters/setters, LINQ for collections, `async/await` everywhere
- **In Ruby:** blocks and yield, `each` over `for`, monkey-patching used sparingly
- **In PHP:** PSR standards, Composer for deps, modern PHP (8.x+) features
- **In Kotlin:** null-safe types, data classes, extension functions, scope functions
- **In Swift:** value types preferred, optionals first-class, Swift naming conventions

If you're writing code that "looks like Java in Python" or "looks like Python in Go," you're causing readers extra friction.

## Java / Kotlin

### Naming
- Classes: `PascalCase` (`UserService`)
- Methods, variables: `camelCase` (`calculateTotal`, `userCount`)
- Constants: `SCREAMING_SNAKE_CASE`
- Packages: lowercase, reverse-domain (`com.example.users`)

### Common pitfalls
- **Using `null` everywhere.** In Kotlin, use nullable types (`String?`) and the safe-call operator. In modern Java (8+), use `Optional<T>` for returns where absence is meaningful.
- **`equals`/`hashCode`/`toString` boilerplate.** Use Lombok in Java or data classes in Kotlin.
- **Checked exceptions in Java.** Most senior Java devs avoid them; wrap them in unchecked exceptions at the boundary.
- **Static state.** Avoid mutable static fields; they're impossible to test cleanly.

### Project structure
Standard Maven/Gradle layout:
```
src/
├── main/
│   ├── java/         (or kotlin/)
│   │   └── com/example/myapp/
│   │       ├── users/
│   │       ├── orders/
│   │       └── billing/
│   └── resources/
└── test/
    └── java/
```

Feature-based packages within the company namespace.

## Go

### Naming
- Exported (public): `PascalCase` (`UserService`, `CalculateTotal`)
- Unexported (private): `camelCase`
- Acronyms stay capitalized: `HTTPServer`, `userID`, not `HttpServer` or `userId`
- Package names: short, lowercase, no underscores (`http`, `users`, `db`)

### The Go way
- **Errors are values, not exceptions.** Every fallible function returns `(result, error)`. Check it.
- **Small interfaces.** "The bigger the interface, the weaker the abstraction." Define interfaces where they're consumed, not where they're implemented.
- **No inheritance.** Composition only. Embedding is your tool.
- **Goroutines and channels for concurrency.** But don't reach for them if a simple sequential function works.
- **`gofmt` is law.** No style debates.

### Common pitfalls
- **Ignoring errors.** `result, _ := doThing()` is almost always wrong. Handle the error or wrap it.
- **Naked `interface{}` (or `any`)** — defeats type safety. Use a real type.
- **Goroutine leaks.** Every goroutine must have a clear exit path.
- **Mutating shared state without locks.** Use `sync.Mutex` or channels.
- **Excessive interfaces.** Don't define an interface for every struct; only when there's a real polymorphism need.

### Project structure
The community standard:
```
cmd/                    ← main packages, one per binary
  myapp/
    main.go
internal/               ← private packages (not importable externally)
  users/
  orders/
pkg/                    ← public packages (importable by others) — only if you publish
go.mod
go.sum
```

## Rust

### Naming
- Functions, variables, modules: `snake_case`
- Types, traits, enums: `PascalCase`
- Constants, statics: `SCREAMING_SNAKE_CASE`

### The Rust way
- **Ownership rules are the design tool.** Don't fight the borrow checker — let it shape the design.
- **`Result<T, E>` for fallibility.** No exceptions. Use `?` for propagation.
- **Iterators over loops.** `.iter().filter().map().collect()` is the idiom.
- **Traits over inheritance.** Compose behavior with traits; use trait objects (`Box<dyn Trait>`) only when needed.
- **`cargo fmt` and `cargo clippy`** in CI. Clippy catches an enormous amount of style and bug issues.

### Common pitfalls
- **Reaching for `unwrap()`.** Fine in tests and prototypes; not fine in production code unless you can justify why the failure case is impossible.
- **Cloning everything to satisfy the borrow checker.** Sometimes correct, often a sign your design is wrong. Try borrowing first.
- **`Box<dyn Trait>` everywhere.** Static dispatch (generics) is faster; use trait objects only when you need heterogeneous collections or storage.
- **Re-implementing standard iterators.** Read the `Iterator` trait — it has 70+ methods.

## C#

### Naming
- Classes, methods, properties, public fields: `PascalCase`
- Local variables, parameters: `camelCase`
- Private fields: `_camelCase` (leading underscore)
- Interfaces: `IName` prefix (`IUserService`)

### The C# way
- **Properties over public fields.** `public string Name { get; set; }`, not `public string Name`.
- **`async/await` everywhere I/O happens.** Async-by-default for any modern app.
- **LINQ for collection operations.** `.Where().Select().ToList()` over manual loops.
- **`record` types for immutable data** (C# 9+). Replaces a lot of boilerplate classes.
- **Null-state analysis enabled.** `<Nullable>enable</Nullable>` in `.csproj`.
- **Dependency injection** via the built-in container (most modern .NET apps).

### Common pitfalls
- **`async void` outside of event handlers.** Always `async Task` for fire-and-await.
- **Blocking on async code.** `task.Result` and `task.Wait()` cause deadlocks. Always `await`.
- **String concatenation in loops.** Use `StringBuilder` for many concatenations.
- **Disposing resources without `using`.** `using var stream = ...;` is the modern syntax.

## PHP

### Modern PHP (8.x+) is good

If you're stuck mentally on PHP from 2010, look again. Modern PHP has:
- Strict typing (`declare(strict_types=1);`)
- Type hints, including return types and union types (`int|string`)
- Named arguments
- Enums (PHP 8.1+)
- Readonly properties (PHP 8.2+)
- First-class callable syntax

### The PHP way (modern)
- **PSR standards.** PSR-12 for style, PSR-4 for autoloading.
- **Composer for everything.** Don't include PHP files manually.
- **A real framework** for non-trivial apps: Laravel or Symfony.
- **Type-hint everything.**

### Common pitfalls
- **Mixing HTML and PHP** outside of templates. Use Blade/Twig, never `<?php echo $x ?>` scattered through markup.
- **`mysql_*` functions** — long deprecated. Use PDO or a query builder.
- **Suppressing errors with `@`.** Hides real problems. Handle errors properly.
- **Global state.** `$_GLOBALS`, `$_SESSION` directly accessed everywhere makes testing impossible. Inject dependencies.

## Ruby

### Naming
- Methods, variables: `snake_case`
- Classes, modules: `PascalCase`
- Constants: `SCREAMING_SNAKE_CASE`
- Boolean methods end in `?`: `valid?`, `empty?`
- Mutating methods end in `!`: `sort!`, `strip!`

### The Ruby way
- **Blocks and `each`** over manual loops.
- **Express intent through method names.** `users.select(&:active?)` reads as English.
- **Convention over configuration.** Rails leans hard into this; embrace it if you're in Rails.
- **Don't be too clever with metaprogramming.** It's powerful but obscure. Save it for libraries, not application code.

### Common pitfalls
- **Monkey-patching core classes** in application code. OK in tiny scopes (refinements), bad otherwise.
- **N+1 queries in Rails.** Always check your `includes` / `preload`.
- **Long Active Record callbacks.** Move logic to service objects.
- **Massive controllers.** "Skinny controllers, fat models" — but not too fat. Extract service objects.

## Universal: things that apply regardless of language

### Always

- **Lint and format with the language's standard tools.** Don't argue.
- **Type-check where possible.** Even Python and Ruby have static analyzers (mypy, sorbet).
- **Pin dependencies.** Lock files exist for a reason.
- **Pre-commit hooks.** Catch problems before they reach CI.
- **CI runs the same tools as your local environment.** No "works on my machine."

### Naming across languages

The vocabulary is universal:
- Names should reveal intent
- Booleans answer questions (`is`, `has`, `should`, `can`)
- Functions are verbs; types are nouns
- Don't encode types in names (`userList` for a list of users — just `users`)

### Error handling across languages

The mechanism varies (exceptions, Result types, error returns), but the principles are the same:
- Distinguish recoverable from unrecoverable
- Validate at boundaries; trust internally
- Never swallow errors silently
- Specific over generic
- Provide context when re-raising/wrapping

### Testing across languages

The framework varies, but:
- Test behavior, not implementation
- AAA structure (Arrange, Act, Assert)
- Independent tests
- Mock at the boundary, not internally
- 70–80% coverage of business logic

## When the language fights you

Sometimes you'll work in a language where the convention is wrong by modern standards (legacy Java EE, old PHP, classic JavaScript). Two options:

1. **Match the existing codebase's conventions.** Even if outdated. Consistency beats correctness for readability.
2. **Modernize incrementally** if you have buy-in. Boy Scout Rule: each file you touch gets a little better.

Don't be the engineer who refactors a 10-year-old codebase into a half-modernized mess where some files use the old style and some use the new. Either fully migrate or fully leave alone.

## A senior's universal checklist

Regardless of language, before you ship any code:

- [ ] It does what was asked, no more, no less
- [ ] Names reveal intent
- [ ] Functions are small and do one thing
- [ ] Error paths are handled
- [ ] Tests cover the new behavior including failure modes
- [ ] No secrets in code
- [ ] No commented-out code
- [ ] Linter and formatter pass
- [ ] Type-checker passes (if applicable)
- [ ] Commit message follows conventional commits

If all those are true, ship.
