#!/usr/bin/env bash
# Blocks writes containing what look like secrets (API keys, tokens, private keys).
# Use as a PreToolUse hook on Write/Edit/MultiEdit.

set -uo pipefail

PATHS="${CLAUDE_FILE_PATHS:-}"

if [[ -z "$PATHS" ]]; then
  exit 0
fi

# Patterns that strongly suggest a secret in source code
PATTERNS=(
  "sk_live_[A-Za-z0-9]{10,}"
  "sk_test_[A-Za-z0-9]{10,}"
  "ghp_[A-Za-z0-9]{30,}"
  "github_pat_[A-Za-z0-9_]{40,}"
  "AKIA[0-9A-Z]{16}"
  "AIza[0-9A-Za-z_-]{35}"
  "sk-ant-api[0-9a-zA-Z_-]+"
  "hf_[a-zA-Z0-9]{30,}"
  "glpat-[0-9a-zA-Z_-]{20,}"
  "xox[abps]-[A-Za-z0-9-]{10,}"
  "BEGIN (RSA|OPENSSH|EC|PGP|DSA) PRIVATE KEY"
)

for path in $PATHS; do
  [[ -f "$path" ]] || continue
  for pattern in "${PATTERNS[@]}"; do
    if grep -qE "$pattern" "$path" 2>/dev/null; then
      echo "anti-slop: blocked write — file appears to contain a secret matching pattern: $pattern" >&2
      echo "Move secrets to environment variables or a secrets manager." >&2
      exit 2
    fi
  done
done

exit 0
