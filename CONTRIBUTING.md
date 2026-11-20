# Contributing to agent-cli-plugins

[AGENTS.md](AGENTS.md) describes the layout of this repository.

Shared Go code lives in `scaffold/go`. It uses only the standard library and comes with tests, fuzz targets and golden files; `make test` must pass. After a change, render it into every CLI repository with `python3 scaffold/render.py ../<repo>` and open a pull request there as well.

The tool skills live in each CLI repository under `plugin/skills/<tool>`. `make references` copies their reference sections into the shared skill here.

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/), and `lefthook install` sets up the git hooks that check them. Examples, fixtures and issues must not contain real personal data.
