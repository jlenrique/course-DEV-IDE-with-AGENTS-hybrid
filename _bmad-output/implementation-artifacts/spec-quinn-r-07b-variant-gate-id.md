# Spec — Node 07B Quinn-R variant gate_id resolution (Trial-4 finding T4-F4)

**Date:** 2026-06-19 · **Branch:** `trial/4-2026-06-12` · **Mode:** quick-dev (Claude-direct) + 3-lane self-review
**Surfaced by:** Trial 4 (`d7ad4dac-…`) — after the Gamma fix cleared Gary, the walk reached node 07B and crashed: `ModeMismatchError: unknown Quinn-R gate_id/gate_phase: ''`.

## Problem
Quinn-R's `_act._mode` selects its body (`variant`/`pre`/`g5`/…) from `payload["gate_id"]`, which the runner derives from the dispatching node's `gate_code` (`_runner_payload_for_specialist`). **Arc-1a (2026-06-18)** moved `gate_code: "G2B"` off the Quinn-R evaluation node `07B` onto the new content-free `07B-gate` node (to wake G2B pack-neutrally). That left node 07B with **no gate_code** → empty gate_id → `ModeMismatchError('')`. Because `ModeMismatchError(ValueError)` is outside `SpecialistDispatchError`, it **crashed** the trial rather than error-pausing. Offline tests never dispatched node 07B live, so the gap was invisible (the woken-gate structural guard only checked template+shim existence).

## Fix (`app/marcus/orchestrator/production_runner.py`)
New `_effective_quinn_r_gate_code(node, manifest)`:
- returns `node.gate_code` when the node still owns one (e.g. 07C/G2C — unchanged), else
- resolves it from the **content-free** woken gate (`specialist_id is None`, has `gate_code`) whose `insertion_after == node.id`.

Discriminator note: both `07B-gate` (G2B) AND `07C` (G2C) declare `insertion_after: "07B"`. The `specialist_id is None` test selects the content-free gate (`07B-gate`), never the sibling content gate (`07C`).

`manifest` is threaded into the shared `_dispatch_specialist_at_node` (both start + resume walkers), and the quinn-r gate_code is resolved via the helper instead of bare `node.gate_code`.

## Blast radius
Strictly additive: only nodes with an empty `gate_code` that have a following content-free gate receive a newly-resolved code. Nodes with their own gate_code are unchanged. Non-quinn-r specialists ignore gate_code (e.g. elevenlabs node 11 → G4A is computed but unused). **Not a manifest edit** → not a `block_mode_trigger_paths` change.

## Non-goals / deferred
- **`ModeMismatchError` → recoverable family** (so a mode-miss error-pauses instead of crashing): deferred — changes the quinn_r exception hierarchy (ValueError→SpecialistDispatchError); risk of test ripple. Filed as a harvest follow-on.

## Validation
- ruff clean; lint-imports 13 kept.
- New `tests/unit/marcus/orchestrator/test_quinn_r_variant_gate_code.py` (3 tests: 07B→G2B via content-free gate; 07C→G2C unchanged; no sibling-borrow of 07C).
- `tests/integration/marcus/` + `tests/specialists/quinn_r/` + `tests/specialists/gary/` = 303 passed / 1 skipped.

## 3-lane self-review
- **Blind:** discriminator pins the content-free gate; manifest threaded to both walkers (both in scope).
- **Edge:** no-following-gate → None (preserves prior behavior); multi-gate → content-free wins.
- **Acceptance:** 07B resolves variant mode; 07C preserved; governance-light (no manifest touch).
