# Prompt Discipline (for downstream AI tools)

When the deliverable is a prompt for Cursor, a sub-agent, an agent SDK script, or any other AI tool that will then write code — the same anti-slop discipline applies *to the prompt itself*. A sloppy prompt produces sloppy output, and the slop scales with whatever the downstream tool does.

This is especially important when generating Cursor prompts: Cursor reads the codebase directly and shouldn't need long explanations from you. Your job is to constrain its scope, not to teach it.

---

## The five rules

### 1. One concrete task per prompt
Not a bundle. Not "while you're at it." Not "and also fix X."

If you have three things to do, write three prompts. Bundling tasks into one prompt is the single biggest cause of downstream slop because the tool will (a) lose focus, (b) blur the diff scope, and (c) "interpret" relationships between the tasks that don't exist.

**Bad:** "Add the unsubscribe link to all transactional emails, refactor the email helper to support attachments, and update the documentation."
**Good (3 prompts):** "Add unsubscribe link to all transactional emails." | "Add attachment support to lib/email.ts." | "Document the email helper API."

### 2. Name the canonical reference, don't describe the pattern
Cursor reads the codebase. If you describe a pattern in prose when a real file already implements it, you're (a) wasting tokens, (b) introducing drift if your description doesn't match exactly, and (c) signaling to the tool that the pattern is fluid.

**Bad:** "Use a debounced state hook that batches updates over 200ms with a useEffect cleanup..."
**Good:** "Match the pattern in `src/hooks/useDebouncedSearch.ts`."

### 3. Forbid the slop categories explicitly in the prompt
Even if the downstream tool has its own anti-slop rules, restate the relevant ones in the prompt. Tools follow the most recent / most specific instruction.

**Standard footer to add to Cursor prompts:**
```
Constraints:
- Touch only the files listed above. Do not modify others.
- No new files unless absolutely necessary.
- No comments narrating code. No "added by AI" markers.
- No README / CHANGELOG / test-file additions unless I asked.
- No reformatting code you didn't functionally change.
- No new dependencies. No new abstractions.
- Match the existing style in the file you're editing.
```

### 4. Specify the diff budget
Give the tool a concrete budget for files-touched and lines-changed. This prevents scope creep mechanically.

**Bad:** "Refactor the auth module."
**Good:** "Refactor the auth module. Expected diff: 2–3 files, ~80 lines changed total."

If the tool exceeds the budget significantly, that's a signal that either your prompt was wrong or the task was bigger than you thought. Either way, stop and reassess instead of accepting the bloat.

### 5. No open-ended clarification questions in the prompt
Don't write "Let me know if you have questions" or "Ask if anything is unclear." The downstream tool isn't a coworker — it will either execute or hallucinate. If you have a question, ask it of the user before writing the prompt, not after.

---

## Cursor prompt template

For day-to-day Cursor work, this template captures the discipline:

```
## Task
[One sentence. The smallest possible change that satisfies the request.]

## Reference
Match the pattern in: [path/to/canonical/file.ext]

## Files to touch
- [path/to/file1] — [what changes]
- [path/to/file2] — [what changes]

## Out of scope
- [thing that's adjacent and tempting but NOT part of this task]
- [another thing]

## Diff budget
~[N] files, ~[M] lines.

## Constraints
- Touch only the files listed above.
- No new files unless absolutely necessary.
- No comments narrating code. No "added by AI" markers.
- No README / CHANGELOG / test-file additions unless I asked.
- No reformatting code you didn't functionally change.
- No new dependencies. No new abstractions (rule of three).
- Match the existing style in the file you're editing.

## Done when
[The concrete verification — a passing test, a working manual check, a successful build, etc.]
```

---

## When the user asks for "a Cursor prompt for X"

The user wants a prompt, not a conversation. Generate the prompt using the template above and present it as a single code block they can copy. Do not surround it with "Here's the prompt" / "Let me know if you want adjustments" — both of those make it harder to copy cleanly.

Output format:

````
[The prompt itself, in a code block, ready to paste]
````

Then *after* the prompt block, one short line if necessary about a decision you made (e.g., "I assumed `useDebouncedSearch.ts` is the right reference — swap it if there's a closer one"). Otherwise nothing.

---

## When generating sub-agent prompts (Claude Code subagent invocations)

Same discipline, with one addition: the sub-agent has no conversation history, so the prompt must be fully self-contained. Don't say "the file we discussed" — name it. Don't say "the pattern from earlier" — name the pattern.

Subagent prompt template:

```
You are reviewing/implementing [specific scope].

Read these files first:
- [path] — [why]
- [path] — [why]

Task: [one sentence]

Constraints: [the standard list]

Return: [exactly what you want back — a list of findings, a diff, a summary, etc.]
```

The "Return" line is critical. Without it the subagent will produce a wall of text. With it, you get a structured response you can act on.
