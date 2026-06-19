---
title: 'P2-2 — PNG-grounded PerceptionArtifact + standalone vision node'
type: 'feature'
created: '2026-06-19'
baseline_commit: '2063686'
status: 'ready-for-dev'
governance:
  workflow: 'bmad-create-story → NEW CYCLE Codex dispatch'
  gate_mode: 'dual'
  tier: 'Tier-3 (party green-light REQUIRED before dev)'
  cycle: 'NEW CYCLE — Claude pre-author → Codex T1-T10 → Claude T11'
  authority: 'beta-phase-1-closure-ratification-2026-06-19.md §7 (P2-2); epics-perception-reading-path-fidelity.md (Story P2-2)'
epic: 'P2 — Perception + Reading-Path Narrative-Grounding Restoration'
story_key: 'p2-2'
velocity:
  r_tier: 'R3'          # substrate-impacting: new manifest node + data-plane projection + schema family + provider seam
  t11_tier: 'cross-agent'  # T11 must run full battery incl. parity / integration-marcus / audit / lockstep / lint-imports
  files_touched: '~14-18 (model + emitted schema + 2 shape/lockstep tests + golden fixture + manifest + generator template + -gen witness + vision specialist pkg [act/provider/payload_contract] + _act.py flip + tripwire-replacement test + pyproject import contract + SCHEMA_CHANGELOG + TW-7c-4 allowlist)'
  lookahead_tier: '3'   # P2-3 (Pass-2 consumption) + P2-4 (reading-path) both build on this producer
context:
  - '{project-root}/_bmad-output/planning-artifacts/prd-perception-reading-path-fidelity.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics-perception-reading-path-fidelity.md'
  - '{project-root}/_bmad-output/planning-artifacts/beta-phase-1-closure-ratification-2026-06-19.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-p2-1-fidelity-detector-red-first.md'
  - '{project-root}/_bmad-output/planning-artifacts/deferred-inventory.md'
  - '{project-root}/docs/dev-guide/pipeline-manifest-regime.md'
  - '{project-root}/docs/dev-guide/pydantic-v2-schema-checklist.md'
  - '{project-root}/docs/dev-guide/scaffolds/schema-story/'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**The producer half.** P2-1 armed a deterministic fidelity detector that consumes a `PerceptionArtifact`, but the artifact is hand-authored fixture data and perception is **not wired into the production path** (the detector is dormant — `run_g5_checks` reports `status: unverified, reason: perception-not-wired`). P2-2 builds the **producer**: a standalone `vision` manifest node that perceives each rendered slide **PNG** into a per-slide-addressable `PerceptionArtifact` (with provenance + confidence/coverage), publishes it as the **authoritative production-envelope contribution**, and **wires it into the G5 path** so the detector runs on **real produced perception**. This **flips the P2-1 tripwire** (dormancy ends) and turns the detector **partly green** — real faithful slides pass; the real $5.2T defect now fails loud against a **produced** artifact (AC-12).

**This story does NOT repair Pass-2 grounding.** Irene Pass-2 still grounds on the brief (that is P2-3). Therefore a full production run may now **legitimately FAIL fidelity** — the detector finally sees the real defect against real perception. That honest-failure state is the **expected, correct** outcome at P2-2 close and is **not** a P2-2 bug.

## Boundaries & Constraints

**Always:** The vision node is the **sole owner** of the vision-provider dependency. `PerceptionArtifact` is extended **strictly additively** (Optional/defaulted only; P2-1 fixtures stay valid; `extra="forbid"` preserved). Perception is published via the manifest `dependency_projections` seam (run-dir disk copy is audit-only). Per-slide addressable by slide identity; uncovered slides carry an explicit `not-covered` state (never a missing key). Vision-step failures route per a seam taxonomy with attribution — **never** a silent fallback to the brief. Two-lane CI: the deterministic detector + schema tests stay **BLOCKING**; live/golden vision repeatability is **QUARANTINED** (non-blocking, alert-only).

**Ask First (party green-light items — see §Green-Light Questions):** SF-1 the manifest version axis (pack_version vs data_plane_vocabulary_version vs the `-gen` witness recipe); SF-3 provider seam (reuse legacy `bridge_utils.perceive` vs a new thin httpx client); SF-4 the shape-pin "stay green vs update-in-lockstep" resolution; SF-5 vision-node insertion point + pack-rendering classification.

**Never:** Do NOT rewire Pass-2 grounding (P2-3). Do NOT make a production run green by repairing narration (P2-3). Do NOT rename or make-required any P2-1 `PerceptionArtifact` field. Do NOT add the detector or vision failure tags to `_RETRYABLE_DISPATCH_TAGS` for the *detector* (the vision step MAY have its own bounded retry — distinct policy; see SF-6). Do NOT let Pass-2 or the detector import the vision provider (import-linter). Do NOT hand-edit the frozen v4.2 pack. Do NOT relitigate the P2-1 ratified decisions (Edge-1 dormant posture, money-normalization, idiom handling).

## Substrate Findings (grounded — Claude pre-author 2026-06-19, file:line)

### SF-0 — The P2-1 consumed contract (the additive base)
`app/models/perception/perception_artifact.py:13-39` — `PerceptionArtifact(BaseModel)` with `model_config = ConfigDict(extra="forbid", validate_assignment=True)`; fields: `confidence: Literal["HIGH","LOW"]`, `visual_elements`, `extracted_text`, `layout_description`, `slide_title`, `text_blocks`, `artifact_path`, `slide_id` (non-blank validator), `card_number`, `coverage: Literal["perceived","low-confidence","not-covered"]`. **P2-2 extends this module in place, additively.**

### SF-1 — Manifest versioning is DUAL-AXIS, and likely NOT a pack_version bump (refines binding inheritance #1)
The pipeline-manifest-regime + the manifest header carry two rulings that change the "pack-version bump" framing in the goal/inheritance #1:
- **Data-plane ruling (regime §"per-node dependencies edits are data-plane-only", 2026-06-12, lines 116-129; manifest header lines 30-42; `app/manifest/schema.py:339-349`):** adding a `dependency_projections` row is a **data-plane vocabulary change → bump `data_plane_vocabulary_version`** (currently `dp-v1.2` → `dp-v1.3`), **NOT `pack_version`**. "pack_version provably does not govern the data plane." The mandated vocabulary-version field now exists.
- **Determinism-witness split (regime §"determinism-witness split", Arc-1a 2026-06-18, lines 139-157):** a manifest **topology change** regenerates the `-gen` **determinism-target witness** and **keeps `pack_version` uniform** — "a topology refinement within a lineage is NOT a pack_version change"; the frozen `v4.2` mapping-axis pack is **never** regenerated in place. Registry of record: `state/config/frozen-pack-shas.json`.
- **Tension (THE #1 party decision):** a **net-new content-bearing `vision` node** is also a textbook Tier-2 "New pipeline step added" (regime lines 69-91, Scenario A lines 163-169) → which prescribes `v4.3` + a new generator sibling `scripts/generators/v43/`. **Reading A** (Tier-2 classic): mint v4.3. **Reading B** (Arc-1a topology-refinement): keep `pack_version: v4.2`, regenerate the `-gen` witness, bump `data_plane_vocabulary_version`. **Claude recommendation: Reading B** — frozen-at-ship requires v4.2 to stay byte-frozen regardless; the determinism-witness recipe (the newest doctrine) exists precisely to absorb topology changes without a version-line bump; minting a whole `v43/` generator sibling for one additive node is disproportionate. **Winston rules at green-light.**

### SF-2 — The G5 node + the tripwire flip (load-bearing)
- G5 node = manifest **node id `13`** "Quinn-R Pre-Composition QA", `gate_code: G5` (`state/config/pipeline-manifest.yaml:733-762`). Current `dependency_projections`: `slides`(gary), `narration_script`(irene), `segment_manifest_deltas`(irene), `narration_outputs`(elevenlabs).
- The dormant-skip branch: `app/specialists/quinn_r/_act.py:181-190` — `perception = payload.get("perception_artifacts"); if perception: detect_fidelity(...) else: {status:"unverified", reason:"perception-not-wired", ...}`. **Flip = delete the dormant `else` branch** (or make absent-perception a Class-A fail once wired); enforcement runs on the projected artifact.
- The tripwire test: `tests/specialists/quinn_r/test_fidelity_detector.py:182-202` asserts `"perception_artifacts" not in` each G5 node's `dependency_projections`. **Wiring the projection makes this FAIL by design** — P2-2 **deletes/replaces** it with a positive test asserting perception IS projected + enforced.
- **Consumer side already ready:** `app/specialists/quinn_r/payload_contract.py:28` — `perception_artifacts` is **already** in `CONSUMED_PAYLOAD_KEYS`, so the Ratchet-D manifest-contract test (`tests/contracts/test_manifest_payload_contracts.py`) passes the instant node 13 projects it. No consumer-contract edit needed.

### SF-3 — The projection mechanism (how perception reaches the payload)
`app/manifest/schema.py:125-135,219-239` — `dependency_projections: dict[str, ProjectionSpec]`; `ProjectionSpec = {from: <producer specialist id>, key: <producer output key>}`. `app/marcus/orchestrator/production_runner.py:1312-1313` — when a node has `dependency_projections`, the runner threads `projection_map` into the specialist invocation, resolving each producer output key onto the consumer input key. So wiring = add `perception_artifacts: {from: vision, key: perception_artifacts}` to node 13; the `vision` specialist must emit a contribution carrying `perception_artifacts`.

### SF-4 — Four-file lockstep + the shape-pin "stay green" tension
The schema-story scaffold (`docs/dev-guide/scaffolds/schema-story/`) gives the four-file pattern: model + emitted JSON Schema + shape-pin test + (here) golden fixture, plus `test_json_schema_parity` and a no-leak test. **Tension:** the P2-1 shape-pin (`tests/specialists/quinn_r/test_fidelity_detector.py:205-220`) asserts an **EXACT** `set(artifact.model_dump()) == {…}`. Adding **non-excluded** Optional fields (richer confidence/coverage) will break that exact-set assertion → the shape-pin test must be **updated in lockstep**. Provenance is `Field(exclude=True)+SkipJsonSchema` → absent from both `model_dump()` and the emitted JSON Schema → the lockstep test must assert the **deliberate model-vs-schema divergence** (provenance present on the model, absent from schema), NOT naive field-equality. **Resolution (party-confirm):** "P2-1 fixtures stay green" = P2-1 JSON fixtures still validate (additive Optional = backward-compatible); the shape-pin **test** is updated in lockstep (keeping the `extra="forbid"` + closed-enum-rejection assertions).

### SF-5 — Vision node placement + pack classification
Gary (node `07` "Gary Dispatch + Export", `pipeline-manifest.yaml:371-397`) produces `gary_slide_output` with per-slide `file_path` PNGs (`perception_contract.py:106-107` reads `file_path`). Irene Pass-2 (node `08`, lines 531-561) and Quinn-R G5 (node `13`) are downstream. **Insert `vision` after `07F`, before `08`** so P2-3 can later project perception into node 08 without moving the node. Classification: a node with `specialist_id` set is **pack-rendered** (`app/manifest/schema.py:430-497` — `is_orchestration_only` requires `specialist_id is None`), so the vision node renders a pack section → needs a generator template section → the `-gen` witness regenerates (SF-1 Reading B). **Party-confirm the insertion point + whether vision should be pack-rendered or a runtime-only node.**

### SF-6 — Provider seam + isolation
Legacy provider: `skills/sensory_bridges/scripts/bridge_utils.py::perceive` (used by `perception_contract.py:96-98` and `app/specialists/quinn_r/sensory_bridges_dispatch.py`). Binding inheritance #5/#7 prefers a **new thin pinned-endpoint httpx client** owned by the vision node (pinned model id + deterministic decode) over a vendor SDK or the legacy skill-tree bridge. Import-linter contract lives in `pyproject.toml:308-313` (P2-1's "fidelity_detector may not import sensory_bridges_dispatch"). **P2-2 adds a new forbidden contract:** the vision provider module is importable ONLY by the vision specialist; `app.specialists.irene.*` and `app.specialists.quinn_r.fidelity_detector` may import only `app.models.perception`. **Party-confirm reuse-legacy vs new-thin-client.** Note: the "no LLMs in critical path" rule (regime line 16) governs the **pack generator** (Jinja2), not runtime specialist nodes — the vision node calling a vision LLM at runtime is fine (like irene/gary).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Perceive a PNG | rendered slide PNG path | `PerceptionArtifact` (elements, positions, figures) per slide | provider raises → seam taxonomy |
| Multi-slide deck | N PNGs | N artifacts, per-slide-addressable by slide identity | — |
| Uncovered slide | a slide with no successful perception | explicit `coverage: not-covered` artifact (NEVER a missing key) | — |
| Provenance | each visual claim | `provenance ∈ {png-grounded, brief-expectation, not-covered}` (model field, schema-excluded) | — |
| Published authority | artifact emitted | projected to node 13 via `dependency_projections`; disk copy audit-only | — |
| Vision failure: raised/timeout | provider error | typed seam outcome + attribution; **no brief fallback** | `VisionSeamError` (tag) |
| Vision failure: low-confidence | provider returns LOW | artifact carries `confidence: LOW` / `coverage: low-confidence` → detector treats as non-conformance | not a silent pass |
| Vision failure: schema-invalid | provider returns malformed | tagged failure (ValidationError → typed) | never silent |
| Tripwire flip | node 13 projects `perception_artifacts` | old tripwire test FAILS → replaced by positive enforce test; `run_g5_checks` enforces | — |
| AC-12 real-defect | the **produced** $5.2T artifact + un-repaired narration | detector RED on the **real produced** artifact | `FidelityError` orphan/contradiction tag |
| Golden repeatability | identical PNG @ pinned model | artifact stable within comparator tolerances (bbox IoU≥θ, element Jaccard=1.0, text edit-dist≤d) | QUARANTINED lane |
| Determinism boundary | detector on produced artifact | detector still deterministic + no-retry (P2-1 invariant intact) | — |

## Code Map (exact edit sites — Codex fills bodies)

| # | Path | Change |
|---|------|--------|
| 1 | `app/models/perception/perception_artifact.py` | **Additive:** add `provenance` (`Field(exclude=True)+SkipJsonSchema`, closed enum), richer confidence/coverage (Optional/defaulted). No rename/required. Keep `extra="forbid"`. |
| 2 | `state/config/schemas/perception-artifact.schema.json` (NEW) | Emitted JSON Schema (provenance EXCLUDED). |
| 3 | `tests/.../test_perception_artifact_schema_parity.py` (NEW) | model↔schema parity asserting the deliberate provenance divergence (per scaffold `test_json_schema_parity`). |
| 4 | `tests/specialists/quinn_r/test_fidelity_detector.py:205-226` | **Update** shape-pin for new non-excluded fields; keep `extra=forbid` + enum-rejection pins. |
| 5 | `tests/fixtures/.../perception/golden/<slide>.json` (NEW) | Golden produced-artifact fixture(s). |
| 6 | `app/specialists/vision/__init__.py`, `_act.py`, `provider.py`, `payload_contract.py` (NEW pkg) | The standalone vision specialist: perceive PNGs → emit `perception_artifacts`; provider isolated in `provider.py`. |
| 7 | `state/config/pipeline-manifest.yaml` | Add `vision` node after `07F` (before `08`); add `perception_artifacts: {from: vision, key: perception_artifacts}` to node `13` `dependency_projections`; bump `data_plane_vocabulary_version` → `dp-v1.3`; (SF-1 Reading B) keep `pack_version: v4.2`. |
| 8 | `scripts/generators/v42/templates/sections/<vision>.md.j2` (NEW) + regenerate `-gen` witness | Pack section for the vision node; regenerate the determinism-target witness (NEVER touch frozen v4.2). |
| 9 | `app/specialists/quinn_r/_act.py:181-190` | **Flip** the dormant-skip branch to enforce (delete `perception-not-wired` dormant status). |
| 10 | `tests/specialists/quinn_r/test_fidelity_detector.py:182-202` | **Delete/replace** the tripwire test with a positive "perception IS projected + enforced" test. |
| 11 | `tests/.../test_ac12_detector_red_on_produced_artifact.py` (NEW) | AC-12: detector RED on the **real produced** $5.2T artifact. |
| 12 | `pyproject.toml` (`[tool.importlinter]`) | New forbidden contract: provider importable only by the vision specialist; irene + detector import only `app.models.perception`. |
| 13 | `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` | Schema-version entry for the additive extension. |
| 14 | `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py` | Extend the TW-7c-4 allowlist for P2-2 paths. |
| 15 | golden/canary | Silent-drift canary (out-of-CI, non-blocking) re-runs the golden image + diffs per comparator table. |

## Tasks + Acceptance Criteria (dev-agent vs operator-gated; sandbox-clean)

> **AC tagging:** `[dev]` = verified in-process by a shipped dep / offline fixture (sandbox-clean — NO operator CLIs). `[op]` = operator-gated; evidence pasted into Completion Notes once.

- **AC-1 [dev]** Given a rendered slide PNG, the vision node emits a `PerceptionArtifact` of perceived elements/positions/figures. (FR1) — verified offline against a recorded provider fixture.
- **AC-2 [dev]** Multi-slide → per-slide-addressable artifacts by slide identity; uncovered slides carry explicit `not-covered` (never a missing key). (FR2, FR4)
- **AC-3 [dev]** Each visual claim carries `provenance ∈ {png-grounded, brief-expectation, not-covered}` + a confidence/coverage state. (FR3, FR4)
- **AC-4 [dev]** The artifact is published as the authoritative envelope contribution via `dependency_projections` (node 13 receives it through the runner's `projection_map`); any disk copy is audit-only. (FR5)
- **AC-5 [dev]** Vision-step failure (raised/timeout, low-confidence, schema-invalid) routes per the seam taxonomy with attribution — never a silent brief fallback. (FR6, NFR4)
- **AC-6 [dev]** Emitted JSON Schema EXCLUDES `provenance` (`Field(exclude=True)+SkipJsonSchema`); confidence/coverage are closed-enum triple-layer-red-rejected; the four-file lockstep test asserts the deliberate model-vs-schema divergence (not naive equality). (NFR9)
- **AC-7 [dev]** P2-1 fixtures still validate AND the P2-1 shape-pin test (updated in lockstep) stays green — proving strictly-additive extension. (binding #2)
- **AC-8 [dev]** TRIPWIRE FLIP: node 13 projects `perception_artifacts`; `run_g5_checks` enforces (dormant branch deleted); the old tripwire test is replaced by a positive enforce test. (binding #3)
- **AC-9 [dev]** AC-12: the detector is RED on the **real produced** `PerceptionArtifact` for the $5.2T slide (offline fixture of a produced artifact), and GREEN on real faithful slides. (binding #8)
- **AC-10 [dev]** Import-linter: the vision provider is imported ONLY by the vision specialist; irene + `fidelity_detector` import only `app.models.perception`; `lint-imports` kept/0-broken. (NFR8)
- **AC-11 [dev]** Pipeline lockstep `check_pipeline_manifest_lockstep.py` exit 0 (incl. determinism witness check 9 + frozen-SHA check 10); `data_plane_vocabulary_version` bumped; (SF-1 Reading B, if ratified) `pack_version` unchanged. (binding #1)
- **AC-12 [dev]** Two-lane CI: deterministic detector + schema/parity tests are BLOCKING; the live/golden vision repeatability test is QUARANTINED (marker), non-blocking. (binding #6)
- **AC-13 [dev]** Golden-image repeatability: identical PNG @ pinned model id → artifact stable within comparator tolerances (bbox IoU≥θ, element Jaccard=1.0, text edit-dist≤d). Runs offline against a recorded fixture (no skip). (NFR2)
- **AC-14-A [dev]** Live vision round-trip invokes the provider IN-PROCESS via a shipped dep (thin pinned-endpoint httpx client preferred) with `pytest.skip` when the key/service is unreachable. (NFR5, sandbox-AC)
- **AC-14-B [op]** Operator runs one live vision round-trip against the real provider; pastes the produced artifact + cost/latency observation into Completion Notes. (NFR5)
- **AC-15 [dev]** Silent-drift canary (out-of-CI, non-blocking) re-runs the golden image, diffs per the comparator table, alerts on drift even under an unchanged model id. (FR23, NFR7)
- **AC-16 [dev]** TW-7c-4 audit allowlist extended for P2-2 paths; `tests/audit/` green.

## Verification Gates (all green before T11 close; run by Claude T11, NOT trusted from the handoff)

- New P2-2 suite + full `tests/specialists/quinn_r/` + `tests/parity/` + audio + `tests/contracts/test_specialist_error_taxonomy.py` + TW-7c-4 pass.
- `tests/integration/marcus/` green (no new failures).
- Tripwire replaced by a positive enforce test; detector RED on the real produced $5.2T artifact (AC-9) + GREEN on faithful slides.
- P2-1 fixtures + (lockstep-updated) shape-pin green.
- `check_pipeline_manifest_lockstep.py` exit 0; `lint-imports` kept/0-broken (new provider-isolation contract); `ruff` clean on touched files.
- `data_plane_vocabulary_version` bumped; pack version axis per the ratified SF-1 reading; TW-7c-4 allowlist extended.
- Push ≥ once; do NOT merge to master (scoped branch).

## Binding Inheritances from the P2-1 Green-Light + T11 (encoded; do NOT relitigate)

1. **Tier-3 + manifest change → lockstep regime bites here.** Read `pipeline-manifest-regime.md` at Codex-T1. (Refined by SF-1: dual-axis versioning; party rules pack-version axis.)
2. **Strictly-additive `PerceptionArtifact`** — Optional/defaulted only; no rename/required; `extra="forbid"` kept; provenance `Field(exclude=True)+SkipJsonSchema`; four-file lockstep asserts the divergence. (SF-4)
3. **The tripwire flip** — wire node 13, flip `_act.py` to enforce, replace the tripwire test. (SF-2)
4. **One perception authority** — vision node sole provider owner; published via ProjectionSpec; per-slide addressable; uncovered = explicit `not-covered`; import-isolation. (SF-3, SF-6)
5. **Vision robustness** — pinned model id + deterministic decode + golden repeatability + silent-drift canary + seam failure taxonomy + a vision-step retry policy distinct from the detector's no-retry. (SF-6)
6. **Two-lane CI** — detector/schema BLOCKING; vision repeatability QUARANTINED. Never relax the detector gate to absorb vision flake.
7. **Sandbox-AC** — live round-trip in-process + `pytest.skip` on unreachable; golden offline (no skip); no operator CLIs in `[dev]` ACs; run `validate_migration_story_sandbox_acs.py` structurally before freeze.
8. **AC-12** — standing test: detector RED on the **real produced** artifact. (AC-9)
9. **DoD** — deferred-inventory `fidelity-metric-blind-to-perception-regression` STAYS OPEN (struck only at P2-3); P2-2 cross-trial harvest filed; sprint annotation added.

## Green-Light Questions (for the Tier-3 party round — T3)

- **Q1 (SF-1, Winston):** pack-version axis — Reading A (mint v4.3 + `v43/` generator sibling) vs Reading B (keep `pack_version: v4.2`, regenerate `-gen` witness, bump `data_plane_vocabulary_version` → dp-v1.3)? *Claude rec: B.*
- **Q2 (SF-3/SF-6, Winston/Amelia):** provider seam — reuse legacy `bridge_utils.perceive` vs a new thin pinned-endpoint httpx client owned by the vision node? *Claude rec: new thin client (isolation + pinned model id).*
- **Q3 (SF-4, Murat):** ratify "P2-1 fixtures stay green; shape-pin TEST updated in lockstep" + the divergence-assertion form.
- **Q4 (SF-5, Winston):** vision node insertion (after 07F, before 08) + pack-rendered vs runtime-only classification.
- **Q5 (Murat):** comparator tolerances (θ for bbox IoU, edit-distance d) — concrete defaults vs "finalize in Codex-T1 with a placeholder + held-out calibration."
- **Q6 (Amelia/Murat):** the vision-step retry policy (bounded retry count + which tags) — distinct from the detector's no-retry; must not be added to `_RETRYABLE_DISPATCH_TAGS` for the *detector*.
- **Q7 (Mary/John):** does P2-2 close leaving a **legitimately red** real run satisfy the DoD, given the grounding-leg entry stays open until P2-3?

</frozen-after-approval>

## §Tier-3 Green-Light Disposition

> **Status: GREEN-LIGHTED — consensus 5/5 GREEN-WITH-AMENDMENTS, zero blocks, no impasse.** Spawned party round 2026-06-19 (real subagents): Winston (architect), John (PM), Murat (test architect), Mary (analyst), Amelia (dev). Frontmatter flipped `status: ready-for-dev`. The amendments below are **BINDING on Codex** and, where they extend an AC in the frozen Intent block, are authoritative (the green-light is the renegotiation step). The Codex dev prompt (T4) encodes each concretely.

### Verdicts (per voice)
| Voice | Verdict | Owned questions |
|---|---|---|
| 🏗️ Winston | GREEN-WITH-AMENDMENTS | Q1, Q2, Q4 |
| 📋 John | GREEN-WITH-AMENDMENTS | Q7 + tiebreaker |
| 🧪 Murat | GREEN-WITH-AMENDMENTS | Q3, Q5, Q6 |
| 🔍 Mary | GREEN-WITH-AMENDMENTS | Q7, traceability, forward-consequence |
| 💻 Amelia | GREEN-WITH-AMENDMENTS | Q2, Q6, buildability |

### Green-Light Question rulings
- **Q1 (pack-version axis) → RATIFIED Reading B.** No `v4.3`, no `v43/` generator sibling. Bump `data_plane_vocabulary_version` `dp-v1.2 → dp-v1.3` (data-plane ruling) + regenerate the `-gen` determinism witness (topology refinement); frozen v4.2 untouched. **[W-A1, binding]** The spec/Codex prompt MUST write the discriminator: *"Scenario A does not fire — `PerceptionArtifact` is an internal envelope contribution consumed by the detector, NOT a learner-facing pack-lineage content deliverable; therefore a new content node here is a topology refinement within the v4.2 lineage, not a new pack family."*
- **Q2 (provider seam) → RATIFIED new thin pinned-endpoint httpx client** (not legacy `bridge_utils.perceive`). **[W-A2]** pinned model id + decode params live as **governed config data** (manifest/config), not hardcoded; the determinism witness covers the decode path. **[AM-1]** the provider RESPONSE contract is a Pydantic model in the vision `payload_contract.py`; the golden fixture is a serialization of that model. **[AM-2]** the thin client carries **NO retry** — raises typed `VisionProviderError` / `VisionProviderTimeout` only. **[AM-5]** the spec names the endpoint env var + pinned endpoint/model id.
- **Q3 (shape-pin lockstep) → SOUND.** **[M-1]** shape-pin stays exact `==` against an explicitly enumerated set — NO subset/superset operators; `extra="forbid"` + closed-enum triple-layer-red-rejection carry forward verbatim. **[M-2]** the model↔schema divergence test asserts BOTH sides (provenance present-on-model AND absent-from-emitted-schema), not absence-only.
- **Q4 (placement + classification) → placement RATIFIED (after `07F`, before `08`).** Classification **RESOLVED BY ORCHESTRATOR SYNTHESIS of W-A4 + AM-4: vision is a normal pack-rendered house-scaffold specialist node** (like gary/irene). Rationale satisfying both voices: W-A1 already decoupled pack-rendering from version-bumping (rendering a section = `-gen` witness regen, not v4.3), and a specialist_id-bearing producer that also renders a section is precisely how every existing node works — so there is no new "overload smell" and no new substrate predicate is introduced. **[AM-4, binding]** vision conforms to the **house specialist scaffold** (`model_config` + node-conformance), **reference specialist = `quinn_r`**, with `provider.py` / `payload_contract.py` as additions, not replacements. The Code Map's 3-file sketch is superseded by full-scaffold conformance.
- **Q5 (comparator tolerances) → PLACEHOLDER-WITH-CALIBRATION (anti-vacuity gated).** **[M-3]** AC-13 ships placeholder θ/d at Codex-T1, but calibration is a **BLOCKING sub-task** against a held-out labeled set (identical-PNG pass cases + ≥1 perturbed pair). **[M-4]** AC-13 requires a **negative control**: a perturbed pair MUST return not-stable at the shipped tolerance (proves the comparator can fail). Tolerances live in one named constants block.
- **Q6 (vision retry vs detector no-retry) → SOUND.** **[M-5, binding, BLOCKING-lane]** a standing test asserts the detector tag is NOT in `_RETRYABLE_DISPATCH_TAGS`. **[AM-3]** vision-step retry = bounded 2-attempt (1 retry), **transport-only** (timeout / 5xx); explicit **no-retry on 4xx** AND **no-retry on a successful-but-low-fidelity response**, each with its own test. Principle: *"retry budget applies to artifact PRODUCTION (transport), not artifact QUALITY (fidelity)."*
- **Q7 (legitimately-RED close) → RATIFIED satisfies DoD** (John + Mary). The RED run is the story *working* (PRD primary criterion "no silent confident-wrong output"); a green run over un-repaired narration would be the actual violation. `fidelity-metric-blind-to-perception-regression` STAYS OPEN through P2-3.

### New binding ACs / DoD additions
- **AC-17 [op-gated default + dev-tested] — J1 fidelity-gate override (mandatory).** Ship a **default-ENFORCE**, opt-in override (e.g. `FIDELITY_GATE=warn`) that downgrades the G5 block to a loud, recorded **WARN** so mechanics-only trials can complete. Requirements: default is enforce (override is opt-in, never silent); when engaged it emits a conspicuous artifact annotation **"fidelity gate OVERRIDDEN by operator — narration unverified"** (an overridden run can NEVER be mistaken for a clean pass); documented in completion notes + sprint annotation with an explicit "reconsider/remove at P2-3 close" note. A dev test asserts enforce-by-default + warn-when-set + the annotation is present.
- **AC-18 (= M-6, binding) — tripwire replacement is ONE two-sided enforcement test:** RED on the real produced $5.2T artifact (AC-9) AND GREEN on faithful slides; the old tripwire is **deleted, not skipped/commented**. (Subsumes John J2's positive+negative requirement.)
- **DoD [Mary-A1, binding]:** the legitimately-RED real-run state is **annotated at P2-2 close** — a one-line sprint/handoff note: *"real-run fidelity RED is the EXPECTED P2-2 outcome; root-cause repair lands at P2-3; deferred entry stays open."*
- **[John-J3, boundary guard]:** confirm no AC verb touches narration *repair*/generation — perceive / compare / gate / annotate only. Anything that repairs is P2-3.
- **[Mary-A2, minor]:** FR-coverage claim notes AC-9 **exercises FR10/FR11** at the producer→detector wiring seam (P2-1-owned, re-validated here).
- **[Mary-A3, confirm]:** the additive-schema posture (binding #2) MUST leave room for P2-4 to add `reading_path` as another Optional field later **without a second topology change** — Codex keeps the model open to that.

### Consensus
**GREEN-LIGHTED for dev.** No impasse; the only cross-voice divergence (W-A4 vs AM-4) was resolved by orchestrator synthesis above, consistent with both voices' deeper rationale. Codex proceeds under the binding amendments. Impasse chain (Quinn → John → operator) was NOT triggered.

## §T11 Review & Close

> **Status: PENDING** — filled by Claude T11 after Codex T1-T10. bmad-code-review 3-lane (Blind/Edge/Auditor) on the real code; full battery run locally; tripwire-flip + additive-schema-keeps-P2-1-green verified; commit + flip P2-2 done; push.
