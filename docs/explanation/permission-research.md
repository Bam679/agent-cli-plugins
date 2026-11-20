# Is a binary-enforced policy overkill? A review of comparable tools

Before the first release we asked whether the agent-cli permission model was too heavy, and whether a hook that each user sets up would be enough. This page summarises what we found in November 2026 and why the model was slimmed down rather than replaced. The decision itself is recorded in [ADR-0003](../adr/0003-permission-model.md).

## How comparable tools handle permissions

| Project | Mechanism | Enforced in | Source |
|---|---|---|---|
| GitHub MCP server | `--read-only`, toolsets, `--exclude-tools` | Server flags | [docs](https://github.com/github/github-mcp-server/blob/main/docs/server-configuration.md) |
| steipete/gogcli (Google) | `--readonly`, command allowlists, safety profiles compiled into the binary | Binary | [safety profiles](https://github.com/steipete/gogcli/blob/main/docs/safety-profiles.md) |
| taylorwilsdon/google_workspace_mcp | `--read-only`, tool tiers, per-service permissions | Server flags | [repo](https://github.com/taylorwilsdon/google_workspace_mcp) |
| korotovsky/slack-mcp-server | Writes off by default, optional channel allowlist | Server environment | [repo](https://github.com/korotovsky/slack-mcp-server) |
| makenotion/notion-mcp-server | Capabilities of the API token | Upstream API | [repo](https://github.com/makenotion/notion-mcp-server) |
| steipete/remindctl | `--force` on delete | Binary | [repo](https://github.com/steipete/remindctl) |
| intelligrit/mail-app-cli | `--dry-run` on bulk changes | Binary | [repo](https://github.com/intelligrit/mail-app-cli) |
| FradSer/mcp-server-apple-events | Confirmation per write, made opt-in after user complaints | Server | [repo](https://github.com/FradSer/mcp-server-apple-events) |
| OrellBuehler/paperless-mcp | `PAPERLESS_READ_ONLY`, disabled tools | Server environment | [repo](https://github.com/OrellBuehler/paperless-mcp) |
| barryw/PaperlessMCP | `confirm=true` for destructive operations, dry run by default for bulk operations | Server | [repo](https://github.com/barryw/PaperlessMCP) |

The common pattern is a coarse switch inside the tool: read-only mode, disabled tools, and writes that stay off until the user turns them on. No tool scopes reads by container, and none has a second, root-owned policy layer.

## What agents offer

Claude Code has permission rules (allow, ask, deny), hooks and an OS-level sandbox. Its documentation says that Bash rules only match the command line Claude usually produces and are not a security boundary, and that Read and Edit rules don't apply to scripts that open files themselves ([permissions](https://code.claude.com/docs/en/permissions)). Plugins cannot ship permission rules ([plugins reference](https://code.claude.com/docs/en/plugins-reference)). The sandbox restricts writes to the project and temporary directories, routes network traffic through an allowlist and blocks Apple Events; `excludedCommands` lets named commands run outside it ([sandboxing](https://code.claude.com/docs/en/sandboxing)).

Other agents have hooks too, but each in its own format. Codex describes its hooks as a guardrail rather than a complete enforcement boundary ([Codex hooks](https://learn.chatgpt.com/docs/hooks)). Cursor's hooks fail open unless `failClosed` is set ([Cursor hooks](https://cursor.com/docs/hooks)). Gemini CLI and GitHub Copilot can deny tool calls from a hook ([Gemini CLI](https://geminicli.com/docs/hooks/reference/), [Copilot](https://docs.github.com/en/copilot/reference/hooks-reference)).

OWASP's entry on excessive agency asks for minimal permissions and for authorisation to happen in the downstream system, not in the model ([LLM06](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)). The MCP security best practices make the same point about server-side checks ([MCP](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices)). Anthropic reports that users approve about 93 % of permission prompts, which is a reason not to rely on prompts alone ([auto mode](https://www.anthropic.com/news/claude-code-auto-mode)).

## Arguments on both sides

For a policy in the binary: it is the only check that works the same under every agent. It sees the container an item really belongs to, which a command-line rule cannot. The most common failure is a cooperative agent that writes to the wrong place, and that agent calls the CLI as instructed, so a read-only default and write scopes stop it. Mature tools such as the GitHub MCP server and gogcli enforce inside the tool as well.

Against it: on its own it does not stop a malicious agent with a shell, which can call `osascript` or `curl` directly. `--confirm` is typed by the agent, so it is not a human approval. Read scopes, a system policy layer and result limits go beyond what any comparable tool offers, and each feature copied into five repositories adds maintenance.

## What we decided

The policy stays, slimmer. The read-only default, operation allow and deny lists, write scopes, batch limits, the fixed path and fail-closed loading are cheap and match what comparable tools do. Read scopes stay as an optional privacy filter. The root-owned system layer and the `max_results` limit were removed.

The largest gain came from a setting rather than from code. With the Claude Code sandbox enabled and only the CLI excluded, an agent cannot reach Apple Events, the network or the policy file directly, so the CLI and its policy become the only way to the data. `<bin> policy --claude-settings` prints that configuration. We tested it on macOS 26: `apple-reminders` ran as an excluded command and read through EventKit, while `osascript` inside the sandbox failed with error -600.

The plugin hook that blocks edits to the policy file also stays, although the review suggested dropping it. It is the only protection a plugin can install without any user action, and it already exists. The documentation describes it as best effort.
