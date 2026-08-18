---
name: fairmat-dev
description: Use when working in the Fairmat dev_distro repository, especially for NOMAD workspace packages, plugin development, local developer workflows, root Poe tasks, and repo-specific validation steps.
---

# Fairmat Dev

Use this skill for changes in this repository when repo-specific structure or workflows matter.

## When to use

- Changes under `packages/*`, `ui/`, `scripts/`, or root project configuration
- Work involving NOMAD plugins, actions, parsers, package wiring, or local development tasks
- Work involving NOMAD metainfo traversal, serialized archive flattening, or Parquet export behavior
- Requests that need repo-specific validation commands instead of generic Python advice

## Workflow

1. Read `AGENTS.md` at the repo root, then follow any deeper `AGENTS.md` files in the touched subtree.
2. For work in a plugin submodule, check for `.codex/ARCHITECTURE.md` under that submodule and read it before investigating or editing.
3. Inspect the affected package or app before editing shared code.
4. Prefer existing root Poe tasks and `uv` workspace commands over ad hoc alternatives.
5. Keep changes scoped to the touched package unless a cross-package change is necessary.
6. Run the narrowest validation that covers the behavior you changed.

## References

- Read `references/repo-layout.md` for the workspace structure and common edit boundaries.
- Read `references/testing.md` before choosing validation commands for a change.
- Read `references/nomad-metainfo-traversal.md` when working on NOMAD metainfo traversal, `m_def` resolution, or archive-to-tabular export logic.
