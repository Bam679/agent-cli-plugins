# How to configure permissions for __BIN__

This guide shows you how to decide what an AI agent may do with `__BIN__`. It assumes the CLI is installed and works for reads. The [CLI reference](../reference/cli.md#policy-file) describes every field of the policy file.

## Check what is allowed now

```sh
__BIN__ policy
```

Without a policy file the output says `built-in default (read-only)`. In that state every write exits with code 4.__DEFAULT_NOTE__

## Allow writes in one container

1. Print a template:

   ```sh
   __BIN__ policy --example
   ```

2. Save it as `~/.config/agent-cli/__BIN__.json` and keep only the operations you want under `operations.allow`. The write operations are __WRITE_OPS__.
3. Put the containers the agent may change under `scopes.write.allow`. Scopes are glob patterns over __SCOPE_HELP__; `*` matches any text.
4. Make the file private to you:

   ```sh
   chmod 600 ~/.config/agent-cli/__BIN__.json
   ```

   The CLI refuses a policy that other users can write, or that someone else owns, and then denies everything.

5. Check the result with `__BIN__ policy`, then try a write with `--dry-run`. A dry run is checked against the policy too, so a denial shows up here before anything changes.

## Hide private containers from the agent

Add patterns to `scopes.read.deny`:

```json
{ "version": 1, "operations": { "allow": ["read"] }, "scopes": { "read": { "deny": ["__PRIVATE_EXAMPLE__"] } } }
```

Lists and searches leave these containers out, and `get` on an item inside them exits with code 4. Leave `scopes.read.allow` empty to mean "everything else".

## Limit how much one command may change

Set `limits.max_write_batch`. A command that would change more items than that exits with code 4 before it changes anything.

## Set up Claude Code

The plugin's hook already stops agents from editing the policy file with Claude's file tools. Two more settings make the policy hard to get around:

1. Print the recommended settings:

   ```sh
   __BIN__ policy --claude-settings
   ```

2. Merge the output into `~/.claude/settings.json`. It contains:
   - permission rules that allow read commands, ask before every write command, and deny reading or editing `~/.config/agent-cli`
   - a `sandbox` block that turns on the Bash sandbox and runs only `__BIN__` outside it

Inside the sandbox an agent cannot send Apple Events, open network connections or write outside the project, so `__BIN__` and its policy are the only way to reach your data. If you use several agent-cli tools, combine their `excludedCommands` and permission lists into one block.

If you use another agent (Codex, Cursor, Gemini CLI), the policy file still applies, because the binary enforces it. Only the hook and the settings above are specific to Claude Code.

## If a command fails

| Exit | What happened | What to do |
|---|---|---|
| 4 | The policy does not allow the operation or the container, or the policy file is invalid | Run `__BIN__ policy`. An `error` field means the file was rejected. |
| 5 | The command would write, but `--confirm` was missing | The plan is on stdout. Run the command again with `--confirm` if it is what you want. |
| 6 | __PERMISSION_HINT__ | See the [README](../../README.md). |
