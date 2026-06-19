# Codex dev-story prompt — P2-2 (PNG-grounded PerceptionArtifact + standalone vision node)

**Cycle:** Claude spec (Tier-3 party green-lit 2026-06-19, AMENDMENTS LOCKED) → Codex T1-T9 + T10 self-review → Codex handoff at `_bmad-output/implementation-artifacts/_codex-handoff/p2-2-perception-artifact-vision-node.ready-for-review.md` → Claude T11 `bmad-code-review` → Claude commit + flip done.
**Epic:** P2 (Perception + Reading-Path Narrative-Grounding Restoration). **Story:** P2-2. **Gate-mode:** dual. **Tier:** Tier-3 (party green-light DONE — see spec §Tier-3 Green-Light Disposition).
**Authority:** `beta-phase-1-closure-ratification-2026-06-19.md §7`; `epics-perception-reading-path-fidelity.md` (Story P2-2).
**Dispatch ordering:** P2-2 follows the CLOSED P2-1 (`43581d2`). It builds the producer + wires perception into G5; it does NOT repair Pass-2 grounding (P2-3). A real run may now legitimately FAIL fidelity — that is the EXPECTED P2-2 close state, not a bug.

---

```
Run bmad-dev-story on Story P2-2 (Epic P2; dual-gate; PNG-grounded PerceptionArtifact + standalone vision node).

Spec: `_bmad-output/implementation-artifacts/spec-p2-2-perception-artifact-vision-node.md`
The spec's <frozen-after-approval> Intent/Boundaries/Substrate/Code-Map/ACs AND the §Tier-3 Green-Light Disposition are CONTRACT. The design is LOCKED by a unanimous 5/5 party green-light — do NOT re-litigate the version axis, the provider seam, the node placement/classification, the scaffold shape, or the tripwire-flip. Honor every binding amendment (W-A1, W-A2, AM-1, AM-2, AM-3, AM-4, AM-5, M-1..M-6, J1/AC-17, J3, Mary-A1/A2/A3) verbatim.

## Required reading (T1, before any code)
1. The spec (whole file) — ESPECIALLY §Tier-3 Green-Light Disposition (the binding amendments) and §Substrate Findings (file:line edit sites).
2. `docs/dev-guide/pipeline-manifest-regime.md` — the WHOLE pack-versioning + determinism-witness-split policy. THIS STORY TOUCHES `state/config/pipeline-manifest.yaml` (a block_mode_trigger_path) → full L1 lockstep regime applies.
3. `docs/dev-guide/pydantic-v2-schema-checklist.md` + `docs/dev-guide/scaffolds/schema-story/` (model + emitted-schema + parity-test + shape-pin pattern).
4. `app/models/perception/perception_artifact.py` — the P2-1 contract you extend STRICTLY ADDITIVELY.
5. `app/specialists/quinn_r/_act.py:150-196` (`run_g5_checks` — the dormant-skip branch at 181-190 is the flip site) + `app/specialists/quinn_r/payload_contract.py:16-36` (note `perception_artifacts` is ALREADY a consumed key).
6. `tests/specialists/quinn_r/test_fidelity_detector.py:182-202` (the tripwire test to replace) + `:205-226` (the shape-pin to update in lockstep).
7. `state/config/pipeline-manifest.yaml` — header lines 24-56 (pack_version, data_plane_vocabulary_version, block_mode_trigger_paths), node `07` (gary, lines 371-397), node `08` (irene, 531-561), node `13` (G5/quinn-r, 733-762).
8. `app/manifest/schema.py` — `NodeSpec` / `ProjectionSpec` (125-239) + the pack-classification predicates (430-497); `app/marcus/orchestrator/production_runner.py:1312-1336` (how `dependency_projections` → `projection_map` reaches the specialist).
9. A REFERENCE specialist to copy the house scaffold from: `app/specialists/quinn_r/` (AM-4 names quinn_r as the scaffold reference) — mirror its `model_config` + node-conformance shape.
10. `skills/sensory_bridges/scripts/bridge_utils.py::perceive` — for reference ONLY (the legacy shape); you are NOT reusing it (W-Q2 ratified a new thin client).

## T1 hard checkpoints
- Baseline commit (spec frontmatter `baseline_commit`) is an ancestor of HEAD; branch `fidelity-perception-arc-2026-06-19`.
- Run `scripts/utilities/check_pipeline_manifest_lockstep.py` and CONFIRM exit 0 BEFORE any edit (capture the baseline trace). You will re-run it after; it must STILL be exit 0 (incl. determinism-witness check 9 + frozen-SHA check 10).
- Confirm `perception_artifacts` IS in `app/specialists/quinn_r/payload_contract.py` `CONSUMED_PAYLOAD_KEYS` (it is — no consumer-contract edit needed; the Ratchet-D test passes once node 13 projects it).
- Confirm `_RETRYABLE_DISPATCH_TAGS` (`production_runner.py`) is allowlist-based; you will NOT add the detector tag (M-5).
- Identify the frozen v4.2 pack + the `-gen` determinism-target witness from `state/config/frozen-pack-shas.json`. You regenerate the `-gen` WITNESS; you NEVER touch the frozen v4.2 pack.

## Version governance (W-A1 — WRITE THIS RATIONALE; do not relitigate)
- **NO `v4.3`, NO `scripts/generators/v43/` sibling.** Scenario A ("new pipeline step → mint v4.3") DOES NOT FIRE here. Discriminator (record it in the manifest rationale + your handoff): *"`PerceptionArtifact` is an internal envelope contribution consumed by the detector, NOT a learner-facing pack-lineage content deliverable; a new content node here is a topology refinement WITHIN the v4.2 lineage, not a new pack family."*
- Keep `pack_version: "v4.2"` UNIFORM (do not half-flip node pack_version — the single-value filter would drop the node).
- BUMP `data_plane_vocabulary_version` `dp-v1.2 → dp-v1.3` (the new `dependency_projections` row is a data-plane vocabulary change). This bump is GOVERNANCE-RATIFIED by the green-light — do NOT open a separate consensus gate mid-dev (AM-5).
- Regenerate the `-gen` determinism witness via the v42 generator after the manifest edit; commit manifest + template + regenerated witness as ONE logical change.

## Files in scope
**New:**
- `app/specialists/vision/` — full HOUSE SCAFFOLD specialist (AM-4: mirror `quinn_r`'s `model_config` + node-conformance): `__init__.py`, `_act.py` (perceive each `gary_slide_output` PNG → emit `perception_artifacts`), `provider.py` (the thin pinned-endpoint httpx client — AM-2: NO retry, raises typed `VisionProviderError`/`VisionProviderTimeout`), `payload_contract.py` (CONSUMED keys + the provider RESPONSE Pydantic model per AM-1), plus the `model_config.yaml` the scaffold requires.
- `state/config/schemas/perception-artifact.schema.json` (emitted JSON Schema — provenance EXCLUDED).
- `scripts/generators/v42/templates/sections/<vision-anchor>.md.j2` (pack section for the vision node).
- `tests/.../test_perception_artifact_schema_parity.py` (M-2: BOTH-sides divergence — provenance present-on-model AND absent-from-schema).
- `tests/fixtures/.../perception/golden/<slide>.json` (golden produced-artifact fixture = serialization of the AM-1 response model) + the recorded provider fixture for offline AC-1/AC-13.
- `tests/.../test_ac12_detector_red_on_produced_artifact.py` (AC-9: detector RED on the real PRODUCED $5.2T artifact, GREEN on faithful slides — this IS the AC-18 two-sided enforcement test, M-6).
- A test asserting the detector tag is NOT in `_RETRYABLE_DISPATCH_TAGS` (M-5, BLOCKING lane).
- A QUARANTINED golden-image repeatability test (AC-13) + its negative control (M-4) + the silent-drift canary (AC-15, out-of-CI).
**Modified:**
- `app/models/perception/perception_artifact.py` — ADDITIVE only: `provenance` (`Field(exclude=True)+SkipJsonSchema`, closed enum `png-grounded|brief-expectation|not-covered`), richer confidence/coverage (Optional/defaulted). KEEP `extra="forbid"`. NO rename/required. Keep the model OPEN so P2-4 can add `reading_path` later without a topology change (Mary-A3).
- `state/config/pipeline-manifest.yaml` — add the `vision` node after `07F` (before `08`); add `perception_artifacts: {from: vision, key: perception_artifacts}` to node `13` `dependency_projections`; bump `data_plane_vocabulary_version` → `dp-v1.3`.
- `app/specialists/quinn_r/_act.py:181-190` — DELETE the dormant `perception-not-wired` else-branch; `run_g5_checks` now ENFORCES via `detect_fidelity` on the projected artifact. Implement AC-17 here: a `FIDELITY_GATE=warn` override downgrades the Class-A block to a recorded WARN + the "OVERRIDDEN — narration unverified" annotation; DEFAULT is enforce.
- `tests/specialists/quinn_r/test_fidelity_detector.py` — UPDATE the shape-pin (M-1: stays exact `==` on an enumerated set; keep `extra=forbid` + closed-enum rejection verbatim); DELETE the tripwire test (`:182-202`) and replace with the positive enforce test (AC-18/M-6 — delete, do NOT skip/comment).
- `pyproject.toml` (`[tool.importlinter]`) — new forbidden contract: the vision provider module is importable ONLY by the vision specialist; `app.specialists.irene.*` and `app.specialists.quinn_r.fidelity_detector` import only `app.models.perception`.
- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` — additive schema-version entry.
- `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py` — extend the allowlist for P2-2 paths.
- `docs/trials/cross-trial-learnings.md` — P2-2 DoD harvest.
**Do NOT modify / do NOT do:**
- Frozen v4.2 pack (`docs/workflow/production-prompt-pack-v4.2-…md`) — regenerate the `-gen` WITNESS only.
- `_RETRYABLE_DISPATCH_TAGS` — do not add the detector tag (M-5).
- Irene Pass-2 grounding (`irene/graph.py`, `pass_2_template.py`) — that is P2-3. NO AC verb may REPAIR/generate narration (John-J3): perceive / compare / gate / annotate only.
- The grounding-leg deferred-inventory entry `fidelity-metric-blind-to-perception-regression` — do NOT strike it (struck at P2-3).
- Do NOT mint v4.3 or a v43/ generator sibling (W-A1).

## Critical implementation notes (amendment-locked)
- **AM-4 scaffold (BLOCKING):** `app/specialists/vision/` conforms to the house specialist scaffold — copy `quinn_r`'s `model_config` + node-conformance; `provider.py`/`payload_contract.py` are ADDITIONS. The Code Map's 3-file sketch is superseded by full-scaffold conformance. If scaffold conformance and the spec conflict, scaffold conformance wins (this is the gap that would otherwise bounce at T11).
- **AM-1/AM-2 provider:** `provider.py` = one thin httpx client: POST PNG bytes to the pinned endpoint (env var + pinned model/endpoint id NAMED in the spec/config — AM-5), parse the pinned response into a Pydantic model (in `payload_contract.py`), raise typed `VisionProviderError`(5xx/4xx) / `VisionProviderTimeout` on failure. NO retry in the client. The golden fixture is a serialization of that response model (offline AC-1/AC-13 and the live AC-14-A must not diverge).
- **W-A2 governed decode:** the pinned model id + deterministic decode params (temp 0 / greedy, fixed max-tokens, no sampling) live as CONFIG DATA (manifest/`model_config.yaml`), not hardcoded in the client; the determinism witness/golden test covers the decode path.
- **AM-3 vision retry (node-level):** bounded 2-attempt (1 retry), TRANSPORT-ONLY — retry on `VisionProviderTimeout` + 5xx-mapped `VisionProviderError`; NO retry on 4xx; NO retry on a successful-but-low-fidelity response (that becomes a `coverage: low-confidence`/`not-covered` artifact the detector then handles). Principle: *retry budget = artifact PRODUCTION (transport), never artifact QUALITY (fidelity)*. Test the no-retry-on-4xx AND no-retry-on-low-fidelity branches explicitly.
- **SF-3 wiring (the tripwire flip):** add the projection row to node 13; the runner threads `projection_map` so `payload["perception_artifacts"]` is populated; `run_g5_checks` calls `detect_fidelity(segments, perception)`. Per-slide-addressable by slide identity; an uncovered slide gets an explicit `coverage: not-covered` artifact, NEVER a missing key.
- **M-1/M-2 schema lockstep (four files):** model + emitted JSON Schema + shape-pin test + golden fixture move together. Shape-pin stays exact `==` (no subset). Parity/divergence test asserts BOTH: provenance IS on the model, provenance is NOT in the emitted schema. P2-1 JSON fixtures must STILL validate (additive = backward-compatible) — prove it.
- **M-3/M-4 tolerances (AC-13):** placeholder θ (bbox IoU) / d (edit-distance) at T1, but calibration is a BLOCKING sub-task against a held-out labeled set (identical-PNG pass cases + ≥1 perturbed pair). Negative control: a perturbed pair MUST return not-stable at the shipped tolerance. `element-set Jaccard == 1.0` (exact). Tolerances in ONE named constants block. AC-13 is QUARANTINED (non-blocking marker) but must not be vacuous.
- **AC-17 override (J1):** DEFAULT enforce; `FIDELITY_GATE=warn` (or equivalent) downgrades to a recorded WARN + a conspicuous artifact annotation "fidelity gate OVERRIDDEN by operator — narration unverified". An overridden run can NEVER read as a clean pass. Document it in the handoff + note "reconsider/remove at P2-3 close". Dev test: enforce-by-default + warn-when-set + annotation present.
- **Two-lane CI (binding #6):** the detector + schema/parity/shape-pin/M-5 tests are BLOCKING; the live (AC-14-A `pytest.skip` on unreachable) + golden-repeatability (AC-13) + canary (AC-15) tests are QUARANTINED (marker), non-blocking. NEVER relax the detector gate to absorb vision flake.

## Verification (T9 self-G6 — run the FULL battery, do not trust a partial list)
- `pytest tests/specialists/quinn_r/ -q` — tripwire replaced by the two-sided enforce test (RED on produced $5.2T, GREEN on faithful); shape-pin updated + green; M-5 no-retry guard green.
- `pytest tests/ -q` incl. `tests/parity/`, `tests/integration/marcus/`, `tests/audit/`, `tests/contracts/` — no new failures (the pre-existing `tests/contracts` repo-drift failures noted in the P2-1 handoff are out of scope; confirm you add none).
- New: schema parity (M-2), AC-12 produced-artifact RED (AC-9), AC-13 repeatability + negative control (QUARANTINED), AC-17 override.
- `check_pipeline_manifest_lockstep.py` → exit 0 (witness check 9 + frozen-SHA check 10 green); `data_plane_vocabulary_version` = dp-v1.3; `pack_version` unchanged.
- `lint-imports` → kept/0-broken (new provider-isolation contract). `ruff check` clean on touched files.
- Structurally re-run `scripts/utilities/validate_migration_story_sandbox_acs.py` reasoning over the AC blocks: live round-trip is `[op]`/in-process-with-skip; no operator CLIs in `[dev]` ACs.

## T10 ready-for-review handoff
Record at `_bmad-output/implementation-artifacts/_codex-handoff/p2-2-perception-artifact-vision-node.ready-for-review.md`: each new/changed test's intent + result; the tripwire-flip evidence (old test deleted; new two-sided enforce test passes RED+GREEN); proof P2-1 fixtures still validate + shape-pin green (additive proven); the version-governance summary (no v4.3; dp-v1.3; witness regenerated; frozen v4.2 untouched + SHA intact); lint-imports kept/0; lockstep exit 0; the AC-17 override behavior + annotation; the AC-13 calibration result (θ/d + negative-control proof); the AC-14-B operator live-round-trip item flagged as pending operator evidence; and an explicit statement that NO narration was repaired and the suite did NOT make a run green by repair (a legitimately-RED real run is the expected P2-2 state).

## Cycle-close discipline (Claude T11)
Claude T11 = `bmad-code-review` (3-lane Blind/Edge/Auditor) on the real code + FULL battery locally + verify the tripwire flip + additive-schema-keeps-P2-1-green + commit + flip P2-2 done + the P2-2 DoD harvest (cross-trial entry; grounding-leg inventory entry STAYS OPEN) + the Mary-A1 "RED-run is expected" sprint/handoff annotation + push (no master merge). After P2-2 closes, dispatch P2-3 (Pass-2 consumes perceived visuals — the regression fix) via a fresh NEW CYCLE.
```

---

**Authored 2026-06-19 by Claude orchestrator after the P2-2 Tier-3 party green-light (5/5 GREEN-WITH-AMENDMENTS). Companion to `spec-p2-2-perception-artifact-vision-node.md` (status: ready-for-dev). This is the Codex-side T5 driver — Codex ingests this + the spec and begins dev with zero further questions.**
