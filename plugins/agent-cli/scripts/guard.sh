#!/bin/sh
# PreToolUse hook: delegate to the first installed agent-cli binary's
# `guard`, which denies tool calls that would modify agent-cli policy files.
for b in apple-mail apple-notes apple-calendar apple-reminders paperless; do
  if command -v "$b" >/dev/null 2>&1; then
    exec "$b" guard
  fi
done
exit 0
