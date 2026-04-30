# Audra Sidecar Index

Internal-artifact auditor context and cross-session patterns for Audra.

## Current Status

- Initialized 2026-04-16 as part of dev-support agents build.
- Active use: Cora-route (primary), operator-direct (occasional), Marcus-route-via-Cora (when Marcus's External Specialist Agents table is updated to include Cora per Phase 5 of vision).
- Phase 2 (`dev_coherence_sweep.py` consolidated runner): planned, not yet shipped. Audra invokes structural-walk + per-check operations directly until Phase 2 lands.
- Phase 3 auxiliary check scripts: planned, not yet shipped.

## Active Invocation Context

- **Anchor:** (populated per invocation)
- **Scope:** (populated per invocation — since-handoff / full-repo / directory:<path>)
- **Workflow:** (populated per invocation — standard / motion / cluster / null)
- **Invocation source:** (populated per invocation — operator-direct / cora-route / marcus-route-via-cora)

## Operator Preferences

- **L2 check emphasis:** none set yet; all checks run at default priority
- **L2 check mute:** none

## Files

- `patterns.md` — durable cross-session learnings (drift velocity, brittle contracts, closure-gap classes)
- `chronology.md` — dated sweep log
- `access-boundaries.md` — read/write/deny zones

## Recent Sweep Summary

(Empty. Populate after first sweep.)
