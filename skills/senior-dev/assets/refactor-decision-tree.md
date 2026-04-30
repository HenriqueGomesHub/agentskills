# Refactor Decision Tree

When you spot something in the code that could be cleaner, should you refactor now or later? Use this decision tree.

## Step 1: Is the code wrong, or just imperfect?

**Wrong** = produces incorrect behavior, has a security flaw, will fail under known conditions, or will lose data.
**Imperfect** = the code works, but it's harder to read, organize, or test than it could be.

- **Wrong** → fix it now, regardless of what else is going on. File a bug if you can't fix it immediately.
- **Imperfect** → continue to step 2.

## Step 2: Are you currently in this file for another reason?

- **Yes (you were going to edit this file anyway for a feature/fix)** → continue to step 3.
- **No (you're just passing through and noticed something)** → continue to step 6.

## Step 3: Is the imperfect code in the path of the change you're making?

If you have to read it, understand it, or modify it to make your change, it's "in your path." If you can complete your work without touching it, it's not.

- **Yes** → continue to step 4. Doing the small refactor will probably make your actual change easier.
- **No** → continue to step 6.

## Step 4: Do you have tests covering the affected code?

- **Yes** → safe to refactor. Continue to step 5.
- **No** → write characterization tests first (tests that capture current behavior, even if buggy). Then refactor. Then make your feature change. Three commits.

## Step 5: How big is the refactor?

- **Tiny** (rename a variable, extract a 5-line function, replace magic number with constant) → just do it. **Commit it separately** from your feature change. Don't even mention it in the PR description unless asked.

- **Small** (extract a function, split a class into two, introduce a parameter object) → do it. Commit separately. Mention briefly in the PR description.

- **Medium** (restructure a module, change a public API, introduce a new abstraction) → check with the team. This deserves its own PR, ideally before the feature PR. Don't bundle medium refactors with feature work.

- **Large** (replace a framework, redesign a subsystem, introduce a new architectural pattern) → this is a project, not a refactor. Get explicit buy-in. Do it as a series of small PRs over time, never as one big rewrite.

## Step 6: Should you refactor when you're "just passing through"?

The Boy Scout Rule says: leave the file slightly cleaner than you found it.

That means: yes to **tiny** cleanups even when passing through. No to anything larger.

- **Tiny cleanup** (rename a confusing variable, delete a `// TODO` from 2019, remove commented-out code, name a magic number) → do it. Commit it separately as `refactor: small cleanups in <area>`.

- **Anything larger** → don't do it now. File a ticket / write it down. You'll come back when you have time, or when someone else picks it up.

## Step 7: Are you under a deadline?

If yes, refactor *less*, not more. Pressure is when bugs ship.

- **Critical deadline (production fire, demo in 2 hours)** → no refactoring, only the fix. Boy Scout Rule suspended. Come back when calm and clean up.
- **Tight deadline (end of sprint, end of week)** → tiny cleanups only. Defer anything larger.
- **Normal pace** → follow the steps above.

## Anti-patterns to avoid

### "I'll just refactor this whole file while I'm here"
Almost always wrong. You'll blow up the PR scope, mix concerns, make review impossible, and possibly miss the original deadline. Stay focused; file a ticket for the rest.

### "I'll refactor everything to my preferred style"
Style is least important. If the codebase has a consistent style and yours is different, **match the codebase**. Consistency for readers beats your preferences.

### "I'll refactor this code I don't fully understand"
Don't. Refactoring requires understanding the invariants the code is preserving. If you don't know what the code is supposed to do, your refactor will silently break things. Either understand it first, or leave it alone.

### "I'll add an abstraction in case we need it later"
That's not a refactor. That's speculative complexity (YAGNI violation). Don't.

### "Big bang refactor weekend"
The classic developer fantasy: take a weekend to "fix everything." It never works. Big-bang refactors lose track of behavior, miss invariants, and introduce more bugs than they fix. Refactor incrementally, in small steps, over weeks.

## Quick lookup

| Situation | Decision |
|---|---|
| Bug or security issue | Fix now |
| Tiny cleanup, passing through | Do it, separate commit |
| Tiny cleanup, in your path | Do it, separate commit |
| Small refactor, in your path, has tests | Do it, separate commit |
| Small refactor, no tests | Write characterization tests first |
| Medium refactor | Separate PR, before feature PR |
| Large refactor | Series of PRs with team buy-in |
| Tight deadline | Tiny only; defer the rest |
| Don't fully understand the code | Don't refactor |
| Code about to be deleted | Don't refactor |
| Style preference vs codebase style | Match the codebase |

## The one rule that matters most

**Never mix refactoring and feature work in the same commit.**

Even if you're doing both in the same session, separate them:
1. Refactor commit (no behavior change)
2. Feature commit (no structural change beyond what's needed)

This makes review possible, makes reverts safe, and makes your git history a real record of what you did.
