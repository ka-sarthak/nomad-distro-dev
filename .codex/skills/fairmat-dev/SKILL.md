---
name: fairmat-dev
description: Use when working in the Fairmat dev_distro repository, especially for NOMAD workspace packages, plugin development, local developer workflows, root Poe tasks, and repo-specific validation steps.
---

# Fairmat Dev

Use this skill for changes in this repository when repo-specific structure or workflows matter.

## When to use

- Changes under `packages/*`, `ui/`, `scripts/`, or root project configuration
- Work involving NOMAD plugins, actions, parsers, package wiring, or local development tasks
- Requests that need repo-specific validation commands instead of generic Python advice

## Workflow

1. Read `AGENTS.md` at the repo root, then follow any deeper `AGENTS.md` files in the touched subtree.
2. Inspect the affected package or app before editing shared code.
3. Prefer existing root Poe tasks and `uv` workspace commands over ad hoc alternatives.
4. Keep changes scoped to the touched package unless a cross-package change is necessary.
5. Run the narrowest validation that covers the behavior you changed.

## References

- Read `references/repo-layout.md` for the workspace structure and common edit boundaries.
- Read `references/testing.md` before choosing validation commands for a change.
