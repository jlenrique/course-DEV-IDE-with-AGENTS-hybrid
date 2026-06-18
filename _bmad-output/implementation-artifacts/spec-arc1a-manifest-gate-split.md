---
title: 'Arc 1a — manifest topology split: decompose co-located voice/variant HIL gates into [content specialist] + [folded content-free gate node]'
type: 'feature'
created: '2026-06-18'
status: 'ready-for-dev'
baseline_commit: 'af7a8af'
pack_tier: 'Tier-2 (pipeline structural shape) — party-RATIFIED 2026-06-18 (Winston/Amelia/Murat unanimous RATIFY-WITH-CONDITION; D2 PM-tiebreaker design)'
routing: 'Claude-direct per operator standing autonomous directive (supersedes the NEW-CYCLE Codex hand-off default for this session); same rigor — party-ratified spec + 3-lane bmad-code-review.'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-arc1-fold-semantics-pause-topology.md (D2 resolution + chain trail)'
  - '{project-root}/_bmad-output/planning-artifacts/trial-4-scope-plan.md'
  - '{project-root}/docs/dev-guide/pipeline-manifest-regime.md (Tier-2 governance — READ AT T1)'
  - '{project-root}/state/config/pipeline-manifest.yaml'
  - '{project-root}/app/manifest/{schema,compiler}.py'
  - '{project-root}/scripts/generators/v42/manifest.py + app/manifest/schema.py::is_orchestration_only'
---

<frozen-after-approval reason="human-owned intent — party-ratified; do not modify unless renegotiated">

## Intent
Restructure the pipeline manifest so each **co-located** voice/variant HIL gate is decomposed into two nodes, conforming them to the surfaced-gate pattern G1/G2C/G3/G4 already follow (a content-free gate node positioned AFTER the content it gates). This is the keystone enabling Arc 1b (membership-only wake) and the trial-4 genuine variant/voice pauses. **Default (folded) behavior is byte-identical to today — this arc changes NOTHING observable in the folded default.** Wake is Arc 1b.

The three co-located gates (gate_code currently ON the content-producing specialist node — the root cause of the pre-content-pause bug):
- node `11` = `elevenlabs` (voice) carries `gate_code: G4A`, `fold_with: G4`
- node `11B` = `elevenlabs` (voice) carries `gate_code: G4B`, `fold_with: G4`
- node `07B` = `quinn-r` (variant) carries `gate_code: G2B`, `fold_with: G2C`

After split, each becomes: **[content specialist node, gate_code REMOVED]** → (new edge) → **[separate content-free gate node carrying the gate_code + fold_with, FOLDED/no-op by default]**.

## Decision provenance
D2 impasse (un-fold-on-wake vs deferred-pause) → impasse-resolution chain: Dr. Quinn "membership-only wake" synthesis REFUTED by code verification (gates co-located on content nodes; `_production_gate_node` is content-free + suppresses the specialist) → **John PM tiebreaker (binding): path (i) topology split → membership wake; (ii) rejected (Winston firewall).** This spec is Arc 1a (the split). Arc 1b (wake) is a separate spec, opens only AFTER 1a ships folded-verified.

## Acceptance contract (party-ratified conditions — ALL binding)

**Design / structure**
- A1. Each of the 3 co-located gates decomposed into [content specialist, gate_code+fold_with REMOVED] → [new content-free gate node carrying gate_code+fold_with], with the gate node folded by default (NOT in `production_gate_ids`).
- A2. **Positional pin — STRUCTURAL over the manifest graph (Murat A; his escalation-closing pin):** assert "for EVERY node carrying a gate_code: (i) it is content-free (specialist_id is None), AND (ii) its sole immediate predecessor is a content-producing specialist node." NOT enumerated over today's 3 pairs — must be a graph-wide invariant so it cannot rot when a 4th gate is added.
- A3. **Edge rewiring total + acyclic (Winston C2):** manifest-load assertion — every edge formerly terminating at the fused node now terminates at the content node; every edge formerly originating there now originates at the gate node; no edge skips the gate node; no orphaned/dangling edge to the old fused identity; no new cycle.
- A4. **Single-gate_code ownership (Amelia 2c):** each gate_code lives on exactly one node (the new gate node); the content node no longer carries it — no duplication, no orphan.

**Folded-equivalence (the master safety net)**
- A5. **Equivalence ORACLE explicitly defined (Winston C1 + Murat C — non-negotiable):** folded-run equivalence is over the **content/decision plane** — specialist outputs, gate decisions, pause/no-pause control flow, artifact payloads — which MUST be byte-identical pre/post-1a. An **enumerated, frozen expected-delta set** (node-count-derived fields, HUD/topology rendering, per-node structural telemetry) is the ONLY permitted difference. Either (a) enumerate+freeze the expected-delta set alongside the golden, OR (b) pin "folded gate nodes are TELEMETRY-SILENT" (zero emission) and then full-surface byte-identity holds. Pick one and pin it; do NOT leave "byte-identical" ambiguous.
- A6. **Folded-equivalence golden + kill-the-mutant (Murat B):** freeze a pre-split folded-run trace (content/decision plane) on disk; post-split folded run matches. Demonstrate the mutant: a gate node that mutates state / emits an event / reorders / sets pause=true MUST red the golden — run and show, don't assert.
- A7. **Compiled gate-id set byte-identical pre/post-1a (Amelia):** pin `production_gate_ids(manifest)` unchanged after the split (proves the folded gate node is auto-excluded; no compiler change in 1a).
- A8. **Inert-when-folded anti-goal (Amelia 3):** the gate node ships no-op when folded — no membership entry, no wake registration, no gate-count tally participation, no new receipt/state key. Any such wiring is Arc 1b. Stated as an explicit anti-goal so the implementer does not gold-plate.

**Live-pause proof (so invariant 3 ships pinned, not theoretical)**
- A9. **Forced-membership replay fixture (Murat D):** a 1a-suite fixture that flips ONE gate folded→pause via `production_gate_ids` membership and asserts the run PAUSES AT the content-free gate node (after its content node ran). Proves the single-control-plane invariant is LIVE before Arc 1b. (Does not wake by default; a test-only forced membership.)
- A10. **Single-control-plane invariant (Winston firewall as a test):** assert the ONLY mechanism converting a folded gate to a pause is `production_gate_ids` membership; no runtime pause-branch keys on co-location / already-ran.

**Per-slide + consumers**
- A11. **Per-slide cardinality (Winston C3 + Amelia 1 — highest-risk spot):** if the content nodes are per-slide-subgraph-instantiated, the new gate node is instantiated at the SAME per-slide cardinality, inside the same subgraph scope. The folded-equivalence test MUST exercise a MULTI-slide run, not a single-slide degenerate case.
- A12. **Downstream consumer inventory (Winston C4 — non-negotiable):** confirm HUD (`run_hud.py`), `progress_map.py`, and the L1 lockstep check key off `gate_code`/`production_gate_ids` membership (semantic), NOT node position/count (structural). Any structural consumer is patched in the SAME lockstep batch. (Finding so far: L1 + generator consume `is_orchestration_only`, which is gate-aware; HUD/progress_map to confirm at T1.)

**Governance**
- A13. **Generator disposition resolved at T1 (Amelia 1 — her hard line):** `is_orchestration_only` = `specialist_id is None AND gate is False AND hud_tracked is False` → the new gate node (gate=True) is NOT orchestration-only, so it routes through the generator's `if step.gate:` path (manifest.py:83). T1 MUST confirm that path renders a `specialist_id=None` content-free gate cleanly (no crash / malformed section). If it requires a content section, add a minimal content-free-gate branch (widens bump → generator enters frozen-at-ship discipline; record it). State "generator untouched" vs "generator gains a branch" explicitly.
- A14. **Tier-2 pack bump + frozen prior pack (Winston C5):** bump the pack version per the lockstep regime; retain the frozen prior-version pack on disk for audit. 1a ships + A5/A6/A9 green BEFORE Arc 1b opens (enforced ordering).

## T1 readings (mandatory before code)
- `docs/dev-guide/pipeline-manifest-regime.md` (Tier-2 governance + pack-version policy).
- `state/config/pipeline-manifest.yaml` edge/dependency/projection-key + per-slide-subgraph schema around nodes 07/07B/07C, 10/11/11B.
- `scripts/generators/v42/manifest.py` `if step.gate:` path + `is_orchestration_only` (A13).
- `app/manifest/compiler.py::production_gate_ids` (confirm folded auto-exclusion holds → A7).
- HUD/progress_map gate-topology consumption (A12).

## Boundaries
**Always:** folded default byte-identical (content/decision plane); gate node inert when folded; structural positional pin; multi-slide equivalence test. **Never:** no wake/membership change (that's 1b); no runtime pause-branch; no gate_code on a content-producing node; no gold-plating the gate node.

## Verification
- `.\.venv\Scripts\python.exe -m pytest tests/unit/manifest/ tests/integration/marcus/ tests/generators/ -q`
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` (Tier-2 — expect the pack-version-bump lockstep to engage)
- `.\.venv\Scripts\lint-imports.exe` · `.\.venv\Scripts\ruff.exe check <touched>`

## T1 FINDINGS (resolved this session — derived from code reads)
**A13 generator disposition — RESOLVED: the bump WIDENS into the generator/pack (Amelia's flagged case).** `pack.md.j2` renders every step via `{% include step.template_name %}`; `is_orchestration_only` = `specialist_id is None AND gate is False AND hud_tracked is False`, so a `gate=True` content-free node is NOT skipped and DOES need a section template (a missing one crashes the renderer — the documented renderer/L1 failure mode). Splitting one node into [content] + [gate] therefore requires a template/anchor disposition for BOTH nodes. → Arc-1a is NOT a pure data bump; it touches the v4.2 generator/pack (frozen-at-ship discipline). Recommended disposition: the new gate node inherits the original `pack_section_anchor` + section template (it IS the operator-facing gate section); the content node either reuses an orchestration-style minimal template or is classified to render as the upstream content step — confirm against the section templates at implementation.

## A13 — PROVEN via live lockstep FAIL (2026-06-18, dry-run attempt, then reverted to green)
Applied the G2B split to the working tree (07B→content + new `07B-gate` folded node + edge reroute 7.5→07B→07B-gate→07C) and ran `check_pipeline_manifest_lockstep.py`. Result: **FAIL** — L1 check 1 (set-equality), check 2 (order-equality), check 3 (name-equality: `07B` label changed) all RED; gate-bitmap/insertion/emission/schema/event checks PASS. Reverted the manifest to green (this was a diagnostic dry-run, not a landing).
**Proven requirement (the coupled work, no longer just predicted):** the manifest split CANNOT land alone — it requires, atomically, in the same change:
1. A **folded-gate skip-classification** used CONSISTENTLY by BOTH the generator step-shaping (`_orchestration_only_ids` / step rendering) AND the L1 lockstep check, so a FOLDED gate node (gate=True + fold_with set) is excluded from the manifest↔HUD↔pack set/order/name projections (so check 1/2 pass + folded-equivalence A5 holds — the folded pack stays byte-identical).
2. **Pack/HUD regeneration** to absorb any content-node label change (check 3) — or keep the content node's label unchanged to avoid churn.
3. The **Tier-2 pack-version bump** + frozen prior pack (A14).
This is a coupled, build-gating, multi-surface change (manifest + generator + L1 + regeneration) — a dedicated dev cycle (Codex per party, or a fresh focused session), NOT a context-tail improvisation. The manifest-edit mechanics below are validated (they apply cleanly); the generator/L1 skip + regen is the remaining coupled work.

## Implementation execution plan (mechanical — derived T1; edges are explicit `{from,to}` pairs)
Structure facts: 07B/11/11B are SINGLE manifest nodes (per-slide fan-out is handled by the `per-slide-subgraph` node id `0.6`, NOT by replicating these nodes — so per-slide cardinality is verified by a multi-slide run [A11], not by manifest replication). Ordering uses explicit edges + `insertion_after` + `sub_phase_of`.

**G2B split (node 07B = quinn-r variant eval):**
- 07B content node: KEEP specialist_id quinn-r, scaffold_node act, `dependency_projections` (slides←gary), sub_phase_of "07", insertion_after "7.5"; REMOVE gate_code+fold_with; gate→false.
- NEW `07B-gate`: content-free (specialist_id null), gate true, gate_code G2B, fold_with G2C, sub_phase_of "07", insertion_after "07B", hud_tracked true, pack_section_anchor "7B)" (inherits the gate section).
- Edges: `{from:"7.5",to:"07B"}` (keep) · CHANGE `{from:"07B",to:"07C"}` → `{from:"07B",to:"07B-gate"}` + `{from:"07B-gate",to:"07C"}`.

**G4A/G4B split (nodes 11/11B = elevenlabs voice):** mirror — 11 content (specialist elevenlabs, insertion_after "10", gate_code removed) → NEW `11-gate` (G4A, fold_with G4, insertion_after "11"); 11B content (insertion_after "11", sub_phase_of "11", gate_code removed) → NEW `11B-gate` (G4B, fold_with G4, insertion_after "11B", sub_phase_of "11"). Reroute the 10→11→11B→12 edge chain through the two new gate nodes (confirm the exact G4-region edges at implementation — same reroute pattern as G2B).

**Then:** A2 structural positional pin; A6 folded-equivalence golden (content/decision-plane oracle per A5) + kill-the-mutant; A7 `production_gate_ids` byte-identical; A9 forced-membership fixture; A11 multi-slide equivalence; A12 consumer inventory; generator template disposition (A13); A14 pack-version bump + frozen prior pack.

## Spec Change Log
**2026-06-18 — authored ready-for-dev** after unanimous Tier-2 pack-bump ratification (Winston C1–C5; Murat A–D incl. escalation-resolving structural positional pin; Amelia 1–3 incl. generator-disposition hard line). Consolidated as acceptance items A1–A14. Routing: Claude-direct (operator autonomous directive) with party-ratified-spec + 3-lane-review rigor.
