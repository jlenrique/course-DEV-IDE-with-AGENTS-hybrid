# Marcus Sidecar Index

> **DEPRECATED (Epic 26, 2026-04-17):** This sidecar is superseded by `_bmad/memory/bmad-agent-marcus/`. Files remain for backward compatibility until Epic 27 cleanup. Active runtime callers (`scripts/state_management/init_state.py`, `tests/test_state_management.py`) still resolve this path. New writes should target the new sanctum.

This local sidecar (legacy) formerly stored Marcus session context and learned production patterns.

## Current Status

- Initialized to satisfy structural-walk runtime checks.
- Active use: tracked production orchestration and shift handoff continuity.

## Files

- `patterns.md` - durable workflow and routing learnings
- `chronology.md` - dated run/session milestones
- `access-boundaries.md` - read/write limits for this sidecar
