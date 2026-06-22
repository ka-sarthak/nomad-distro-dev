# AGENTS.md

## Scope

- This file applies to the whole `dev_distro` repository unless a deeper `AGENTS.md` overrides it for a subtree.
- Follow nested guidance in `ui/AGENTS.md` and `packages/nomad-FAIR/AGENTS.md` when working in those areas.

## Repository Layout

- The repo is a `uv` workspace rooted at `pyproject.toml` with Python packages under `packages/*` and UI-related code under `ui/`.
- Treat packages as independently owned modules where possible; keep changes scoped to the touched package unless a repo-wide refactor is clearly required.
- Preserve existing `pyproject.toml` dependency boundaries and extras when editing package configuration.

## Development Workflow

- Prefer `rg` for code search and inspect the target package before editing shared code.
- For Python changes, run the narrowest relevant checks first, then broaden only if the change crosses package boundaries.
- Use `uv` and existing Poe tasks from the root `pyproject.toml` instead of inventing parallel commands when an existing task already fits.

## Validation

- Use `poe lint` for repo-wide Ruff validation when a change spans multiple Python packages.
- For package-local changes, prefer targeted tests or commands scoped to the affected package before running repo-wide checks.
- If a change affects NOMAD actions, workflows, or model schemas, verify both the Python module and any touched package configuration.

## Configuration

- Keep local-development assumptions aligned with `nomad.yaml`, root Poe tasks, and workspace dependencies.
- Avoid changing lockfiles, global tooling versions, or shared development tasks unless the task actually requires it.
