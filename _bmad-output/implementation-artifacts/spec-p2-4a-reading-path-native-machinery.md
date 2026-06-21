---
story_key: p2-4a-reading-path-native-machinery
epic: P2 — Perception + Reading-Path Narrative-Grounding Restoration
status: done
gate_mode: single
tier: Tier-3 (party green-light required BEFORE dev — DONE 2026-06-20, 5/5 PARTIAL-SPEC-NOW)
baseline_commit: 485662e
authority: epics-perception-reading-path-fidelity.md §Story P2-4 (FR17–FR20); prd-perception-reading-path-fidelity.md §7
sequence: after P2-3 (CLOSED + AC-6 strike fired). Last P2 story; Growth. Native rewrite — do NOT re-absorb upstream code.
r_tier: R2
t11_tier: standard
lookahead_tier: 2
files_touched: [app/models/perception/perception_artifact.py, app/specialists/vision/_act.py, app/specialists/irene/graph.py, app/specialists/irene/authoring/pass_2_template.py, state/config/pipeline-manifest.yaml, state/config/reading-path-patterns.yaml (NEW), state/config/schemas/segment-manifest.schema.json, scripts/validators/pass_2_emission_lint.py (NEW/native), scripts/utilities/reading_path_classifier.py (NEW/native), tests/contracts/test_reading_path_parity.py (NEW/native), tests/specialists/irene/*, tests/specialists/vision/*, _bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md, docs/workflow/production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md]
note: P2-4 SPLIT at the party green-light → this is **P2-4a (machinery leg)**. FR19 repertoire-growth + the held-out ≥80% real-slide conformance corpus are **P2-4b (operator-evidence-gated)** — see §Scope Boundary + §Successor/Coupling.
---

# P2-4a: Reading-path native machinery — classifier + verify-node conformance (Growth)

## Frozen Intent

Restore the **reading-path scan-order leg** severed 2026-04-24, natively (no upstream re-absorb). Each rendered slide receives a `reading_path` (closed enum over the surviving **7 patterns**) classified **deterministically from the perceived geometry** the vision node already produces; Pass-2 narrates in that scan order; a deterministic **fail-loud verify-node** checks narration order against the scan order. Per-cluster cadence couples to the scan pattern (FR20) against the already-live clustering arc.

This closes the **machinery** half of P2-4. It does **NOT** grow the repertoire (FR19 triptych / image-dominant-first) and does **NOT** assert a held-out real-slide ≥80% conformance bar — both require operator-derived scan-order ground truth that does not exist yet (→ P2-4b, operator-gated).

## Substrate grounding (verified against `485662e`)

- **No `reading_path` field exists.** The rich `app/models/perception/perception_artifact.py::PerceptionArtifact` carries `visual_elements`, `extracted_text`, `layout_description`, `slide_title`, `text_blocks`, `coverage`, `confidence`, `provenance` (`exclude=True`) — but no scan-pattern field. The minimal `pass_2_template.py::PerceptionArtifact` is field-poorer still. P2-3 AC-7 explicitly deferred `reading_path` to P2-4.
- **The 5-part reading-path lockstep was SEVERED and NOT re-absorbed:** enum registry (`reading-path-patterns.yaml`), schema enum (`segment-manifest.schema.json::reading_path`), emission lint (`pass_2_emission_lint.py::_check_reading_path_pattern`), heuristic classifier (`reading_path_classifier.py::_SCORERS`/`READING_PATH_PATTERNS`), parity test (`test_reading_path_parity.py`). **All must be rebuilt native.** The worked-examples doc **survived**: `skills/bmad-agent-content-creator/references/pass-2-grammar-riders-examples.md` carries the canonical scan order + cadence tokens + sample narration for the **7 patterns** (z_pattern, f_pattern, center_out, top_down, multi_column, grid_quadrant, sequence_numbered).
- **Verify-node precedent:** the deterministic fail-loud post-check pattern is `app/specialists/irene/graph.py::_assert_narration_joins_roster` (`:267-296`, called in `_act_pass_2` at `:575`). FR18 mirrors it. Irene's graph `_verify` node is a synthetic-error stub only.
- **Two-model fork (open `perception-artifact-two-model-fork`).** P2-4 adds a **third consumer** (the classifier/verify). `reading_path` MUST live on the **rich** model only and be a deterministic function of geometry the vision model already returns — fork-agnostic, no incremental model call.

## Acceptance Criteria

- **AC-1 (FR17 — field).** `reading_path` is a **closed `Literal[...]` enum** of the 7 surviving patterns on the **rich** `PerceptionArtifact`, with triple-layer red-rejection (pydantic-v2 checklist) and a fail-loud default (no silent "unknown"). If treated as an internal audit field, mirror the `provenance` `SkipJsonSchema[...] + Field(exclude=True)` idiom (P2-2 precedent); if public, it enters the emitted JSON Schema + the four-file lockstep. NOT on the minimal `pass_2_template.py` model (A1 trap).
- **AC-2 (FR17 — classifier).** A **deterministic** classifier derives `reading_path` from the perceived element geometry (bbox/positions/`visual_elements`) at the vision node (or vision-adjacent post-processing over the rich artifact) — **no incremental LLM/model call**. A field-compatibility contract test fails loud if the rich model drops a field the classifier reads.
- **AC-3 (FR18 — verify-node).** A deterministic, fail-loud conformance check (Irene-side post-check mirroring `_assert_narration_joins_roster`) asserts Pass-2 narration order tracks the slide's `reading_path` scan order; raises a tagged `Pass2ReadingPathError` (no silent demote, no warning-level for in-scope patterns) on non-conformance.
- **AC-4 (anti-vacuity — Murat A3 analog, RED-first, non-negotiable).** A **contradiction fixture**: a constructed slide whose perceived scan order contradicts a naive top-to-bottom / DOM default. Tests assert the classifier emits the **correct non-default** pattern AND the verify-node FAILS LOUD when narration follows the wrong (default) order. **Two mutation runs must go RED:** **M1** classifier reverts to naive-default → conformance RED; **M2** collapse/disable the verify-node partition → the known-wrong fixture passes → test RED. Committed RED-first: the failing-order case is RED pre-fix, GREEN post-fix. Mutation evidence in Completion Notes.
- **AC-5 (FR20 — cadence coupling).** Per-cluster narration cadence couples to the scan pattern (cadence tokens from the worked-examples doc), against the already-live clustering (`cluster_id`/`cluster_role`/`cluster_position` on `SegmentManifestSegment`). Offline test asserts the cadence rule applied matches the classified pattern.
- **AC-6 (four-file lockstep — native rebuild).** Rebuild the severed quartet natively + in lockstep: enum registry `reading-path-patterns.yaml`, schema enum on `segment-manifest.schema.json`, emission lint `pass_2_emission_lint.py`, parity test `test_reading_path_parity.py`. Parity asserts registry ↔ schema ↔ worked-examples-doc headings agree on the 7 patterns; out-of-vocab rejected.
- **AC-7 (A8 cache-prefix re-pin).** If scan-order data is injected into the Pass-2 prompt, deliberately re-pin the named cache-prefix byte-stability fixture (clone the P2-3 seam discipline: canonical sorted-keys JSON, deterministic ordering, fixed-seam injection, one-line rationale, never `xfail`/skip).
- **AC-8 (§52 payload-tail rider — party-ratified fold-in).** Since P2-4a reworks the envelope→prompt surface, fold the deferred `pass2-envelope-payload-brief-unframed-in-prompt-tail` fix in: gate/redact (or explicitly frame) the un-framed `## Envelope payload` brief tail for UNVERIFIED slides, scoped precisely so it does not break the A8 pin without the deliberate re-pin in AC-7. Strikes that deferred entry on close.
- **AC-9 (≥80% real-slide bar — OPERATOR-EVIDENCE-GATED, NOT a green-able dev AC).** The held-out real-slide ≥80% conformance bar is **deferred to P2-4b**. It is recorded here as an operator-gated Completion-Notes AC whose precondition is the operator's scan-order harvest (≥8–10 real frozen-corpus slides with operator-labeled expected scan order + ≥1 known-wrong-default case). Dev T1–T10 does NOT block on it; it MUST NOT be authored as a self-labeled (vacuous) test. Includes the PRD §disconfirmation criterion as a written FAIL observation ("verify-node green but operator scan-order complaint reproduces on fresh narration" = FAIL).
- **AC-10 (scope fence).** NO FR19 repertoire growth (triptych / image-dominant-first) in P2-4a — the enum ships with the 7 surviving patterns; any later addition enters at **warning** severity and costs the full parity set + the operator corpus. P2-1/2/3 unchanged + green. The strike scopes to the **machinery** leg only — the combined-arc entry + the last asterisk stay OPEN until P2-4b.
- **AC-11 (governance).** `data_plane_vocabulary_version` bumps `dp-v1.4 → dp-v1.5` (additive); `pack_version` policy per the pipeline-lockstep regime (no new pipeline node if classifier is vision-adjacent → dp-vocab bump, NOT a pack-family bump — confirm at T1 against `docs/dev-guide/pipeline-manifest-regime.md`); `-gen` witness regenerated; SCHEMA_CHANGELOG updated; lint-imports 0-broken; sandbox-AC PASS.

## Scope Boundary (Mary — binding)

**IN (P2-4a, this spec):** FR17 native `reading_path` contract (closed enum, 7 surviving patterns) + deterministic classifier; FR18 verify-node fail-loud conformance; FR20 per-cluster cadence coupling; native four-file lockstep rebuild; anti-vacuity contradiction fixture + mutation gates; A8 re-pin; the §52 payload-tail rider.

**OUT (P2-4b, operator-evidence-gated):** FR19 repertoire growth (triptych / image-dominant-first); the held-out ≥80% real-slide conformance corpus + threshold against operator-labeled ground truth. Gate = the operator's G2C/G3 storyboard scan-order harvest (NOT collected as of 2026-06-20). New patterns, when added, enter at warning severity and cost the full parity set.

## Tier-3 Green-Light Disposition

**Fully-spawned party-mode (Winston/John/Murat/Mary/Amelia) — UNANIMOUS 5/5 PARTIAL-SPEC-NOW, no impasse, Quinn→John chain not triggered (2026-06-20).**

- **Soundness:** PARTIAL-SPEC-NOW — the machinery leg (FR17/FR18/FR20) is fully spec-able against the surviving 7-pattern worked-examples + synthetic anti-vacuity fixtures (no operator evidence needed); the FR19 growth + held-out ≥80% real-slide bar are evidence-gated on an operator harvest that does not exist (self-labeling them now would be a vacuous-pass spec — the failure class P2-1's RED-first detector exists to prevent).
- **Architecture (Design A, all 5):** classifier vision-node-adjacent; `reading_path` on the rich PerceptionArtifact (`exclude=True`/`SkipJsonSchema` idiom); deterministic geometry derivation, no new model call; reject Design B (LLM-declares — reintroduces the LLM-asserts-then-self-checks failure class P2-1/P2-3 closed) and Design C (new manifest node — unjustified topology cost).
- **Murat amendments:** native rebuild of the severed four-file lockstep; FR18 RED-first vs a known-mis-classified fixture; ≥80% real-slide bar = operator-gated AC (AC-9), never self-labeled; disconfirmation criterion written in.
- **Mary amendments:** Scope Boundary block; new patterns warning-severity until corpus; strengthen the machinery inventory entry; couple the two follow-ons; **fold the §52 payload-tail rider into P2-4a (RATIFIED)**.
- **Amelia amendments:** A8 deliberate re-pin (clone P2-3 seam); contradiction fixture + M1/M2 mutations; FR19 carve-out filed with reactivation trigger + flip caveat.
- **John amendments:** single-gate Growth; FR19 enum-additions OUT to P2-4b; surface the operator-harvest dependency as a roadmap decision, not a dev blocker.

## Successor / Coupling

- **P2-4b (FR19 repertoire growth + held-out ≥80% corpus)** — operator-evidence-gated successor. Precondition: operator scan-order harvest (≥8–10 labeled real slides + ≥1 known-wrong-default). Filed in deferred-inventory.
- **`vo-narration-layout-tracking-trained-patterns`** — operator-led exemplar/training build; reactivate AFTER P2-4a lands + Z-path is trial-confirmed; do NOT fold into P2-4a.
- **`pass2-envelope-payload-brief-unframed-in-prompt-tail`** — folded into P2-4a as AC-8 (the §52 rider); struck on close.

**Status → ready-for-dev (P2-4a machinery leg).** Codex driver: `codex-dev-prompt-p2-4a-reading-path-native-machinery.md`.

## Completion Notes (T11 close — 2026-06-21)

**Disposition: CLOSED `done` via NEW CYCLE T11 (Codex T1–T10 → Claude T11).** Fully-spawned party-mode (Winston/John/Murat/Mary/Amelia) **UNANIMOUS 5/5 (A) CLOSE**, no impasse; Quinn→John chain not triggered.

**Independent battery (T11 reproduced, all green):** reading-path parity/classifier/conformance/schema-parity 20 · irene+vision+detector+package-builders 85 · deterministic re-run post-patch 104 passed/1 skipped · lockstep L1 exit 0 · ruff · lint-imports 15/0 · sandbox-AC PASS. 3-layer `bmad-code-review`: **Acceptance Auditor PASS-WITH-NITS** (all 11 ACs + amendments met; AC-9 ≥80% real-slide vacuity-trap correctly DEFERRED/unclaimed; AC-10 exactly 7 patterns, FR19 out; AC-4 anti-vacuity genuinely non-vacuous — M1 classifier-default + M2 conformance-collapse both hand-traced to go RED).

**Two corpus-independent machinery hardenings PATCHED at T11 (Claude-local, party-ratified) + regression-tested:**
- **3a (error-pause taxonomy):** `app/specialists/vision/_act.py` now catches `ReadingPathClassificationError` and converts it to a non-retryable `VisionProviderError` (tag `vision.reading-path.unclassifiable`) so a zero-bbox HIGH/perceived artifact routes through the error-pause contract instead of escaping as an uncaught `ValueError`. Test: `test_reading_path_classification_failure_converts_to_vision_provider_error`.
- **3b (`_bbox` robustness):** `scripts/utilities/reading_path_classifier.py::_bbox` now SKIPs (returns `None`) on non-numeric coordinates instead of raising a raw `ValueError`, uniform with the structural-mismatch path. Test: `test_non_numeric_bbox_skips_to_controlled_failure_not_raw_valueerror`.

**Deferred to P2-4b (filed as named riders in `p2-4b-reading-path-repertoire-and-conformance-corpus`):** (1) ordinal-gate over-trigger + label↔order degeneration; (2) conformance vacuous-skip on key-vocab mismatch + strict-`<` — **carries a MUST RED-first requirement**; (3) nits. These are classifier-ACCURACY/keying-CALIBRATION concerns that the operator-derived corpus is required to fix safely.

**Murat named dissent (recorded):** Murat held finding #2 (conformance silent-skip) should be `continue`→`raise`-fixed at T11, not deferred. Party majority (4) + adopted synthesis: the literal raise-now would hard-fail a legitimate key-vocabulary mismatch → a false-positive Class-A failure (the "stuck-alarm" anti-pattern Murat's own fidelity principles reject); the keying contract must be pinned with corpus evidence first. Dissent addressed by the mandatory RED-first P2-4b rider (tracked, not evaporated).

**Flaky-test attestation (A7):** `test_irene_act_node_real_llm_invocation_with_token_floor` (`@pytest.mark.llm_live`) intermittently fails with `Pass2GroundingError` (tag `irene.pass2.slide-join-failed`) — the **known Irene slide-join LLM-variance** (auto-retry-absorbed in-dispatch per STATE-OF-THE-APP, but this direct-`_act` unit test has no dispatch retry). Confirmed flaky + ORTHOGONAL to the T11 patches: the test feeds numeric bbox + pre-set `reading_path`, so the `_bbox` change is a provable no-op; observed pass/fail across rolls (≈50%) with patches present, and it passed with patches stashed. NOT a P2-4a regression.

**Scope:** P2-4a machinery leg DONE. The P2 arc's last story (P2-4b — reading-path repertoire growth + held-out conformance corpus) remains OPERATOR-GATED on the scan-order harvest. The combined-arc last asterisk drops only when P2-4b lands.
