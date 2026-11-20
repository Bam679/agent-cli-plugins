#!/bin/sh
# Copy each tool's skill reference into the shared skill (progressive
# disclosure). Run from the repo root with the CLI repos checked out next to it.
set -eu
dst=plugins/agent-cli/skills/agent-cli/references
for pair in apple-mail:apple-mail-cli apple-notes:apple-notes-cli apple-calendar:apple-calendar-cli apple-reminders:apple-reminders-cli paperless:paperless-cli; do
  bin=${pair%%:*}; repo=${pair#*:}
  src=../$repo/plugin/skills/$bin
  [ -f "$src/SKILL.md" ] || { echo "skip $bin: $src not found"; continue; }
  { awk 'n >= 2 { print; next } /^---$/ { n++ }' "$src/SKILL.md"; echo; cat "$src/reference.md"; } > "$dst/$bin.md"
done
echo "references synced"
