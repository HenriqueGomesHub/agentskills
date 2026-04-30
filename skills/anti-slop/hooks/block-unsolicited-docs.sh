#!/usr/bin/env bash
# Blocks writes to common AI-slop documentation files unless ANTI_SLOP_ALLOW_DOCS=1.
# Set ANTI_SLOP_ALLOW_DOCS=1 in the environment to allow (e.g., when you actually want a README).

set -uo pipefail

PATHS="${CLAUDE_FILE_PATHS:-}"

if [[ -z "$PATHS" ]]; then
  exit 0
fi

if [[ "${ANTI_SLOP_ALLOW_DOCS:-0}" == "1" ]]; then
  exit 0
fi

# Patterns that are almost always slop when created without explicit user request
BLOCKED_PATTERNS=(
  "CHANGES.md"
  "CHANGES.txt"
  "WHAT_I_DID.md"
  "IMPLEMENTATION_NOTES.md"
  "IMPLEMENTATION.md"
  "SUMMARY.md"
  "NOTES.md"
  "AI_NOTES.md"
  "CLAUDE_NOTES.md"
  "TODO.md"
  "EXAMPLE.md"
  "DEMO.md"
  "USAGE.md"
)

for path in $PATHS; do
  basename=$(basename "$path")
  for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if [[ "$basename" == "$pattern" ]]; then
      echo "anti-slop: blocked unsolicited doc file: $path" >&2
      echo "If you genuinely need this, set ANTI_SLOP_ALLOW_DOCS=1 and retry." >&2
      exit 2
    fi
  done
done

# Block README/CHANGELOG creation (allow edits to existing ones)
for path in $PATHS; do
  basename=$(basename "$path")
  case "$basename" in
    README.md|README.rst|README.txt|CHANGELOG.md|CHANGELOG.rst|CHANGELOG.txt|HISTORY.md)
      if [[ ! -f "$path" ]]; then
        echo "anti-slop: blocked creation of $basename — only edits to existing files allowed." >&2
        echo "If you genuinely need this, set ANTI_SLOP_ALLOW_DOCS=1 and retry." >&2
        exit 2
      fi
      ;;
  esac
done

exit 0
