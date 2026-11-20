# agent-cli-plugins: agent guide

This is the umbrella repo of the agent-cli family. It holds:
- the Claude Code marketplace
- the shared `agent-cli` skill
- the shared Go core and repo scaffold that every CLI repo vendors

## Layout
- `.claude-plugin/marketplace.json`: lists `agent-cli` (local) and the five CLI plugins (`git-subdir` of each repo's `plugin/`, pinned to release tags)
- `plugins/agent-cli/`: the shared skill (`skills/agent-cli/SKILL.md` plus `references/<tool>.md`) and hooks (SessionStart detection, PreToolUse guard)
- `scaffold/go/internal/{agentcli,osa}`: the canonical shared Go code. Module path placeholder: `MODULE`.
- `scaffold/repo/`: templates (CI, release, docs, plugin manifest). `scaffold/render.py` renders them into a CLI repo.
- `docs/adr/`: cross-repo decisions (stack, plugin distribution, permission model, macOS bridge)

## Commands
- `make check`: scaffold tests (race), lint, govulncheck, gitleaks, plugin validation
- `make install-smoke`: install every plugin into a throwaway `CLAUDE_CONFIG_DIR`
- `make references`: refresh the per-tool references from sibling repos
- `make drift`: check that sibling repos match the scaffold
- `scripts/bump.sh <plugin> vX.Y.Z`: pin a released CLI plugin

## Rules
1. Change shared code here first. Then run `python3 scaffold/render.py ../<repo>` for every repo, and run `make check` there.
2. Never weaken the write gate, the policy loading (fixed paths, fail closed) or the static-script rule.
3. Marketplace entries pin release tags. Never point them at branches.
4. Keep `SKILL.md` files short. Details belong in the references (progressive disclosure).
5. Use Conventional Commits. Don't use `--no-verify` or force-pushes.
