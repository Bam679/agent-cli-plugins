# Security policy

## Supported versions
Only the latest release gets security fixes.

## Reporting a vulnerability
Please report it **privately** via [GitHub private vulnerability reporting](https://github.com/Bam679/agent-cli-plugins/security/advisories/new). Don't open a public issue. You can expect an acknowledgement within 7 days.

Especially relevant reports:
- any way to make `agent-cli` perform a write that the policy file denies (flags, env vars, stdin, argument tricks)
- any way for input to become script code (AppleScript/JXA injection) or a shell command
- secrets or personal data appearing in logs, errors or crash output

## Scope
This repository holds the Claude Code marketplace, the shared `agent-cli` skill and hooks, and the shared Go core (`scaffold/go`) that all agent-cli tools vendor. A vulnerability in the core affects every tool, so please report it here.
