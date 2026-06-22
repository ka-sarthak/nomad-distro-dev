# Validation Guide

## Default Approach

- Start with the smallest command that validates the changed behavior.
- Use repo-wide linting or broader tests only when the change spans packages or shared tooling.

## Common Commands

- `uv run poe lint`: repo-wide Ruff checks
- `uv run pytest <path>`: targeted Python tests for a package or module
- `uv run poe start`: local app workflow when changes affect integrated runtime behavior
- `uv run poe cpuworker`: action worker validation for CPU-backed action flows
- `uv run poe gui` or package-local UI commands: frontend validation when changes affect UI behavior

## Notes

- Prefer package-scoped test paths over full-suite runs unless the task requires broader regression coverage.
- If you change `pyproject.toml`, action wiring, or plugin registration, validate both code and configuration together.
