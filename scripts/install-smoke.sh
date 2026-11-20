#!/bin/sh
# Add the marketplace and install every plugin into an isolated, temporary
# Claude Code config directory (never touches the user's real config).
set -eu
src=${1:-Bam679/agent-cli-plugins}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
export CLAUDE_CONFIG_DIR="$tmp"
claude plugin marketplace add "$src"
for p in $(python3 -c 'import json;print(" ".join(x["name"] for x in json.load(open(".claude-plugin/marketplace.json"))["plugins"]))'); do
  claude plugin install "$p@agent-cli-plugins"
done
claude plugin list
