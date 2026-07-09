# Spec: Crossroads Classic preserve sibling (no ad-hoc edit of approved guides)

**Status:** done  
**Workflow:** `bmad-quick-dev`  
**Operator correction:** 2026-07-09 — never mutate a completed/approved registry guide ad hoc  
**Supersedes:** earlier party-A proposal to flip classic in place (reverted)

## Goal

Meet Fidelity L1 / source-numeral retention by **copying** `hil-2026-apc-crossroads-classic`
into a named sibling that differs **only** in `text_content.mode: preserve` (amount null).
The approved classic `condense` record stays frozen.

## Acceptance Criteria

1. **Given** `hil-2026-apc-crossroads-classic`, **when** resolved, **then** `text_mode=condense`
   and `amount` present (minimal) — unchanged from the approved record.
2. **Given** `hil-2026-apc-crossroads-classic-preserve`, **when** resolved, **then**
   `text_mode=preserve`, amount absent, and theme/image_model/style_preset/dimensions match classic.
3. **Given** `validate_gamma_style_guides.py`, **when** run offline, **then** PASS.
4. Part-4 AFK HIL re-proof picks the **preserve sibling**, not classic.

## Tasks

1. Restore classic to approved condense record.
2. Add `hil-2026-apc-crossroads-classic-preserve` sibling.
3. Pin regression tests (classic stays condense; sibling is preserve + visual parity).
4. Point terminal-walk driver `GUIDE` at the sibling for Irene re-proof.
