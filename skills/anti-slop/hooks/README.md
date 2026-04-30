# Hooks (deterministic enforcement)

Skill instructions are advisory — Claude *should* follow them. Hooks are deterministic — they *will* run. For things that matter, use a hook.

This directory contains optional hook configurations you can drop into `.claude/settings.json` (or `~/.claude/settings.json` for global) to enforce the highest-leverage anti-slop rules at the tool level.

---

## Quick install

In your project's `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/skills/anti-slop/scripts/scan.sh $CLAUDE_FILE_PATHS"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/skills/anti-slop/scripts/scan.sh --diff HEAD~1 || echo 'anti-slop findings above — review before declaring done'"
          }
        ]
      }
    ]
  }
}
```

Adjust the path if your skill is project-local instead of global.

---

## Recommended hooks

### 1. PostToolUse — scan after every Edit / Write / MultiEdit
Runs the slop scanner on every file Claude touches. If the file contains a CRITICAL finding (secret, mutable default, bare except), Claude sees the warning immediately and can fix it in the same turn.

### 2. Stop — final scan before Claude declares done
Runs the scanner against the diff of the whole session. Catches accumulated slop that didn't show up file-by-file. The warning enters the conversation context, prompting Claude to address it.

### 3. UserPromptSubmit — inject the anti-slop reminder
For users who want belt-and-suspenders — prepend a short reminder to every prompt:

```json
{
  "UserPromptSubmit": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "echo '[anti-slop active: minimal diff, no unsolicited tests/docs, audit before reporting done]'"
        }
      ]
    }
  ]
}
```

This adds about 25 tokens per turn — cheap insurance.

### 4. PreToolUse — block writes to forbidden paths
If you want to mechanically prevent Claude from creating README.md, CHANGELOG.md, or summary docs without explicit approval:

```json
{
  "PreToolUse": [
    {
      "matcher": "Write",
      "hooks": [
        {
          "type": "command",
          "command": "bash ~/.claude/skills/anti-slop/hooks/block-unsolicited-docs.sh"
        }
      ]
    }
  ]
}
```

The `block-unsolicited-docs.sh` script (in this directory) checks `$CLAUDE_FILE_PATHS` and exits non-zero if it matches forbidden patterns, blocking the write.

---

## Why hooks > skill rules alone

Skill rules are advice. Claude reads them, files them in context, and *usually* follows them. But:

- Long sessions degrade adherence as context fills.
- Skill content can get evicted by auto-compaction.
- Specific user requests can override them ("just do it real quick").
- Models occasionally just... forget.

Hooks are subprocess calls that always run. The scanner's output enters Claude's context as a tool result. Claude can't "forget" a CRITICAL finding because it was just shown to it 200ms ago.

The combination — skill for nuance, hooks for non-negotiables — is much stronger than either alone.

---

## Hook reference (for writing your own)

The full list of hook events supported by Claude Code:

| Event              | When it fires                                | Use for |
|--------------------|----------------------------------------------|---------|
| `UserPromptSubmit` | Right before your prompt is sent to Claude   | Inject reminders, validate prompts |
| `PreToolUse`       | Before Claude runs any tool                  | Block forbidden actions |
| `PostToolUse`      | After Claude runs any tool                   | Run scanners, formatters, post-processing |
| `Notification`     | When Claude prompts for permission           | Custom permission UX (this is how "yolo mode" works) |
| `Stop`             | When Claude finishes a turn                  | Final cleanup, full-diff scan |
| `SubagentStop`     | When a subagent finishes                     | Aggregate subagent results |
| `SessionStart`     | When a Claude Code session starts            | Load custom context, environment setup |
| `SessionEnd`       | When a session ends                          | Persistence, logging |

Useful environment variables in hooks:
- `$CLAUDE_FILE_PATHS` — files affected by the current tool call
- `$CLAUDE_TOOL_NAME` — which tool is being used
- `$CLAUDE_PROJECT_DIR` — project root

---

## Files in this directory

- `block-unsolicited-docs.sh` — exits non-zero if Claude tries to write README / CHANGELOG / SUMMARY / NOTES files
- `block-secrets.sh` — exits non-zero if Claude tries to write a file containing what looks like a secret

(These are referenced from the example settings.json above.)
