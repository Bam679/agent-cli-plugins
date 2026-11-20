# Contributing

This repo holds the shared core and the marketplace. See [AGENTS.md](AGENTS.md) for the layout.

- **Shared Go code** (`scaffold/go`): standard library only, with tests, fuzz targets and golden files. `make test` must stay green. Afterwards, render the change into every CLI repo (`python3 scaffold/render.py ../<repo>`) and open PRs there.
- **Skills:** the tool skills live in each CLI repo (`plugin/skills/<tool>`). `make references` copies them here.
- **Commits:** use [Conventional Commits](https://www.conventionalcommits.org/). Install hooks with `lefthook install`.
- No personal data in examples, fixtures or issues.
