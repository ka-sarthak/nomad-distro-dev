# Repository Layout

## Workspace

- The root `pyproject.toml` defines a `uv` workspace with members from `packages/*` and `ui/infra`.
- Root dependencies assemble a local development distribution of NOMAD and related plugins.

## Main Areas

- `packages/`: Python packages and plugins, each with its own `pyproject.toml`
- `ui/`: frontend and related UI infrastructure
- `scripts/`: repo-level helper scripts
- `testing/`: shared testing utilities and fixtures
- `run/`: local runtime helpers

## Edit Boundaries

- Prefer package-local edits for code under `packages/<name>/`.
- Be careful with root `pyproject.toml`, `uv.lock`, and shared tasks because they affect the whole workspace.
- Check for nested `AGENTS.md` files before changing code in a subtree with its own conventions.
