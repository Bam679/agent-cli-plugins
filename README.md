# agent-cli-plugins

[![ci](https://github.com/Bam679/agent-cli-plugins/actions/workflows/ci.yml/badge.svg)](https://github.com/Bam679/agent-cli-plugins/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/Bam679/agent-cli-plugins/badge)](https://scorecard.dev/viewer/?uri=github.com/Bam679/agent-cli-plugins)

**Claude Code marketplace for the agent-cli family.** These are small, dependency-free Go CLIs that give AI coding agents safe, token-efficient access to personal data apps. All of them are **read-only by default** and enforce a user-owned policy file inside the binary.

| CLI | Repo | What it does |
|---|---|---|
| `apple-mail` | [apple-mail-cli](https://github.com/Bam679/apple-mail-cli) | List, search and read mail; triage (mark, move, trash). **Never sends.** |
| `apple-notes` | [apple-notes-cli](https://github.com/Bam679/apple-notes-cli) | List, search and read notes; create, append and move |
| `apple-calendar` | [apple-calendar-cli](https://github.com/Bam679/apple-calendar-cli) | Events and search via EventKit; create, update and delete |
| `apple-reminders` | [apple-reminders-cli](https://github.com/Bam679/apple-reminders-cli) | Lists and due tasks via EventKit; add, complete and update |
| `paperless` | [paperless-cli](https://github.com/Bam679/paperless-cli) | Paperless-ngx: search, read and download; upload and tagging |

## Install

1. Install the CLIs you want. Each repo's README has signed release binaries and `go install` instructions.
2. Add the marketplace and the plugins:

```sh
claude plugin marketplace add Bam679/agent-cli-plugins
claude plugin install agent-cli@agent-cli-plugins        # shared skill + detection (recommended)
claude plugin install apple-mail@agent-cli-plugins       # per-tool skill + policy guard hook
claude plugin install apple-reminders@agent-cli-plugins  # …only the tools you use
```

Each CLI repo is also a single-plugin marketplace (`claude plugin marketplace add Bam679/apple-mail-cli`). Install each plugin from **one** source only.

## How the plugins work

- **`agent-cli`** ships the shared skill. It explains the common contract once (output, pagination, exit codes, the write sequence `--dry-run` then `--confirm`, the policy) and links one reference file per tool. The agent opens a reference only when it needs that tool (progressive disclosure). A `SessionStart` hook prints which CLIs are installed, with versions, so the agent never guesses.
- **Per-tool plugins** (`apple-mail`, …) ship that tool's skill plus a `PreToolUse` guard (`<tool> guard`). The guard denies Edit, Write and Bash calls that try to modify agent-cli policy files.
- Marketplace entries are `git-subdir` sources pinned to release tags of each CLI repo (`plugin/` folder).

See [ADR-0002](docs/adr/0002-plugin-distribution.md).

## Permission model

Writes need **all** of the following, checked in this order inside the binary:

1. **Policy:** the operation and every touched container are allowed by `~/.config/agent-cli/<tool>.json`. Without that file, the tool is read-only.
2. **`--dry-run`** previews the change and is also policy-checked.
3. **`--confirm`** is required to change anything.

```json
{
  "version": 1,
  "operations": { "allow": ["read", "add", "complete"], "deny": ["delete"] },
  "scopes": {
    "read":  { "allow": ["*"], "deny": ["Health*"] },
    "write": { "allow": ["Agent*"] }
  },
  "limits": { "max_results": 200, "max_write_batch": 10 }
}
```

- The policy path is fixed: the home directory comes from the user database, not `$HOME`. No flag or env var can point to another file.
- Broken, insecure or foreign-owned files make the tool **fail closed**.
- A root-owned `/Library/Application Support/agent-cli/<tool>.json` is intersected with the user file, so admins can lock policies.
- `<tool> policy --claude-settings` prints matching Claude Code permission rules: read commands allowed, writes `ask`, policy files denied.

See [ADR-0003](docs/adr/0003-permission-model.md).

## Threat model (summary)

| Threat | Mitigation |
|---|---|
| Prompt injection via mail, notes or documents | Read-only default. Binary-enforced op and scope allowlists. Skills tell agents that returned data is untrusted. Mail has no send capability. |
| Agent rewrites its own permissions | Fixed policy path, ownership and mode checks, guard hooks, deny rules, root-owned system policy |
| Script injection | Static JXA scripts with JSON argv, fuzzed. Typed HTTP parameters for Paperless. |
| Supply chain | Zero third-party Go dependencies. SHA-pinned actions, CodeQL, gosec, govulncheck, gitleaks, Scorecard. Cosign-signed releases with SBOM and SLSA provenance. |

## Protecting PII with AI agents

Everything an agent reads is sent to the model provider. To reduce what leaves your machine:

- **Hide sensitive containers** with `scopes.read.deny` (private folders, health or finance lists, `tag:medical`). Hidden data never reaches the agent.
- **Request less:** use `--fields`, `--limit` and `--max-chars`. The skills instruct agents to do this.
- **Scan tool output with hooks.** A Claude Code `PostToolUse` hook can pipe output through a detector and block or redact it:
  - [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks): secrets and tokens
  - [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog): verified secret detection
  - [data-privacy-stack/presidio](https://github.com/data-privacy-stack/presidio) (formerly microsoft/presidio): PII detection and anonymization (names, emails, IBANs, phone numbers)
- **Keep data out of issues:** use redacted or synthetic examples only.

## Shared scaffold

`scaffold/` keeps the five repos identical where it matters:

- `scaffold/go`: the shared core (argument parsing, output contract, exit codes, policy, write gate, guard) and the JXA runner, with tests, fuzz targets and golden files.
- `scaffold/repo`: CI (lint, race tests, coverage gate, govulncheck, gosec, CodeQL, gitleaks, dependency review, Scorecard, all SHA-pinned), release (release-please, GoReleaser, SBOM, cosign, provenance), governance docs, `AGENTS.md`, Claude Code settings and hooks, and plugin manifests.
- `python3 scaffold/render.py <repo>` renders the scaffold into a repo; `--check` reports drift.

Decisions: [docs/adr](docs/adr). Contributing: [CONTRIBUTING.md](CONTRIBUTING.md). Security: [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
