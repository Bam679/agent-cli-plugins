#!/bin/sh
# SessionStart hook: tell the agent which agent-cli tools are installed.
# Prints one line; never reads input, never fails the session.
installed=""; missing=""
for b in apple-mail apple-notes apple-calendar apple-reminders paperless; do
  if command -v "$b" >/dev/null 2>&1; then
    v=$("$b" version 2>/dev/null | awk '{print $2}')
    installed="$installed $b@${v:-?}"
  else
    missing="$missing $b"
  fi
done
[ -n "$installed" ] || installed=" none"
echo "agent-cli tools installed:$installed; not installed:${missing:- none}. Use the agent-cli skill before calling them; writes need the user's policy and --confirm."
exit 0
