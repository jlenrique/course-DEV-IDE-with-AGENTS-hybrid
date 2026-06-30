# Story enhanced-vo.1: directed-voice role→slide identity linkage (Slice 0)

Status: done

<!-- Epic: enhanced-vo (Enhanced VO Generation — directed voice made REAL, v3 text-driven). Story key: enhanced-vo-1-role-slide-linkage. Party GREEN-LIGHT CONSENSUS 2026-06-29 (Dr. Quinn). SSOT: _bmad-output/planning-artifacts/enhanced-vo-party-consensus-2026-06-29.md. This is the SLICE-0 SEAM and GATES Story B (enhanced-vo-2-v3-provider-text-compiler). ZERO live TTS spend in this story. -->

## Story

As the directed-voice pipeline,
I want each narration segment to carry a **stable `slide_key`** emitted from Irene's clustering output, and the role→slide linkage to be a **deterministic identity join on that key** (not a fragile source/final ordinal comparison),
so that a per-segment voice direction **FIRES on real clustered Gary decks** instead of failing open to neutral — making Story B's v3 expressive compiler act on the correct slide.

## Why this story exists (the residual it fixes)

On real clustered decks the role→slide read **fails open to neutral**: a 6-source-slide deck becomes `slide-01..slide-11`, so the source-ordinal set and the final-ordinal set diverge and the EDGE-1 guard returns `None` (no seed). This is the `p5-s2-role-seed-robust-source-to-final-slide-linkage` deferred item. A failed join silently corrupts every downstream channel, so it must fail **offline, loudly, first**. Story B must not open until this is green.

## Acceptance Criteria

**AC-A1 — `slide_key` emitted as DATA on the manifest at Irene's clustering output.**
- A new field `slide_key: str | None = None` is declared on `SegmentManifestSegment` (`app/specialists/irene/authoring/pass_2_template.py:214`; the model is `extra="forbid"`, so it MUST be a declared field, not an extra) and added to `state/config/schemas/segment-manifest.schema.json`. Backward compatibility: legacy manifests may parse without `slide_key`; newly emitted Story-A Pass-2 deltas MUST populate a non-empty `slide_key`, and Story-A join paths MUST fail loud if it is absent.
- `slide_key` is populated on every Pass-2 delta emitted by `_act_pass_2` (`app/specialists/irene/graph.py:1162`) into `segment_manifest_deltas` in `cache_state.cache_prefix`.
- `slide_key` derives from the **source-slide identity that Irene HOLDS at clustering**, NOT from the final slide ordinal. Authoritative derivation for the real clustered fixture is: final `slide_id` -> Gary/slide brief `source_ref` -> Pass-1 `plan_units.unit_id` -> source head (`parent_slide_id` for interstitials, otherwise the unit itself) -> stable source-slide ordinal/key. It crosses as a serialized value on the deltas — **no consumer imports clustering/authoring code** (import-linter Contract M3: `app.specialists` may not import `app.marcus` facade/intake/orchestrator; the orchestrator-side consumer reads `slide_key` as data).

**AC-A2 — Deterministic source→final slide-map fixture on a REAL clustered Gary deck.**
- A committed fixture captures, from a real clustered deck (recommended source: trial `c2c6dcbf-5734-42d0-b525-2ea3212aa3f0` — `runs/c2c6dcbf-.../irene-pass1.md` shows `c-u01..c-u04` clustering; `state/config/runs/c2c6dcbf-.../exports/segment-manifest-storyboard-b.yaml` has the 13 final segments where the ordinal join fails open in the wild), the mapping `{source_slide_identity → final segment slide_key → final slide_id/ordinal}`.
- The fixture is the deterministic pin for the join: given the fixture, the identity join resolves every role-bearing source slide to exactly one final segment.

**AC-A3 — Identity join via `slide_key` — RED-first, build-breaking, no fuzzy-ordinal fallback.**
- The role→slide linkage resolves by **`slide_key` identity**, replacing the ordinal-set comparison in BOTH sides of the current fail-open join:
  - specialist side: `_role_derived_seeds_for_deltas` + `_slide_id_ordinal` (`app/specialists/irene/graph.py:1085-1159`; EDGE-1 fail-open guard at `:1146-1152`), consumed by `_attach_voice_direction` (`:1025-1075`);
  - orchestrator side: `slide_ordinal_from_locator` / `source_slide_ordinals` / `project_role_derived_voice_by_slide` (`app/marcus/orchestrator/enrichment_consumption.py:144-255`).
- A RED-first test on the `c2c6dcbf`-shaped clustered deck asserts: the OLD ordinal join FAILS OPEN (returns `None`/no seed) on that deck, AND the NEW `slide_key` identity join FIRES (emits the correct seed on the correct final segment). No fuzzy/ordinal fallback path is reachable when `slide_key` is present; absence of `slide_key` fails loud (build-breaking), it does not silently fall back to ordinal matching.

**AC-A4 — Stability-across-re-clustering.**
- The same source slide yields the **same `slide_key`** across two independent clustering runs (or two fixtures of the same source). Pinned by a test asserting key stability. `slide_key` is deterministic from source identity — never a UUID/random value and never the final ordinal (which varies with clustering).

**AC-A5 — Carry-survival (the frozen-neck gotcha).**
- `slide_key` must reach the join consumer. Per the known carry gap, `join_narration_segments` (`app/specialists/narration_join.py:39-53`, frozen policy) drops non-core fields, and cluster labels are re-attached only at the export projection (`app/marcus/orchestrator/storyboard_publisher.py:141-147`). Verify `slide_key` survives to every consumer that performs the join: it rides the `segment_manifest_deltas` blob (read by `decode_envelope_payload`, `app/specialists/enrique/_act.py:78-91`, and the seed join which runs on deltas BEFORE the frozen neck). If any join consumer reads a post-`join_narration_segments` row, `slide_key` MUST be re-projected at export following the `cluster_id` precedent — assert it does not silently drop to `None` (mirror `tests/integration/marcus/test_storyboard_publisher_cluster_carry.py`).

**AC-A6 — v2 byte-identical / no behavior change off the directed path.**
- With directed voice OFF, deck/narration output is byte-identical (the existing flag idiom). `slide_key` is additive; non-directed runs ignore it. No live TTS spend anywhere in this story.

## Tasks / Subtasks

- [x] T1 Readiness (AC: all) — read the SSOT consensus record + this story; confirm block-mode NOT triggered (a pure data-field add on deltas/schema/model does NOT touch `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`; only an edit to `pipeline-manifest.yaml` itself would — see Dev Notes §8). If you end up adding a node/edge, read `docs/dev-guide/pipeline-manifest-regime.md` first.
- [x] T2 RED fixture (AC: A2) — build the deterministic source→final slide-map fixture from the real `c2c6dcbf` clustered deck (source identities ↔ final `slide_key` ↔ final slide_id/ordinal). Capture a paired clustered-vs-flat case if useful (`_bmad-output/test-artifacts/cluster-tolerance-test/` has a ready pair).
- [x] T3 RED join test (AC: A3) — assert OLD ordinal join fails open on the clustered fixture; assert NEW identity join fires. Build-breaking.
- [x] T4 Declare `slide_key` (AC: A1) — add optional/backward-compatible field to `SegmentManifestSegment` (pass_2_template.py:214) + `segment-manifest.schema.json`; populate every newly emitted Story-A Pass-2 delta in `_act_pass_2` from the final slide's `source_ref` -> Pass-1 `plan_units` -> source-head identity.
- [x] T5 Identity join (AC: A3) — rewrite the role→slide linkage on both sides (graph.py:1094-1159 + enrichment_consumption.py:144-255) to key on `slide_key`; remove the ordinal fail-open path; fail loud if `slide_key` missing.
- [x] T6 Stability test (AC: A4) — same source slide → same key across two clustering runs/fixtures.
- [x] T7 Carry-survival test (AC: A5) — `slide_key` reaches every join consumer; re-project at export if any consumer reads a post-join row.
- [x] T8 Regression (AC: A6) — directed-OFF byte-identical; full irene/enrique/storyboard suites green; ruff + import-linter (only the pre-existing C3 break permitted).

## Dev Notes

### Architecture / source tree (verified file:line)
- **Pass-2 emission (where slide_key lands on deltas):** `_act_pass_2` `app/specialists/irene/graph.py:1162` → serializes `narration_script` + `segment_manifest_deltas` to `cache_state.cache_prefix` (`:1216-1227`). Post-pipeline already runs `backfill_delta_ids` (:1202), `backfill_delta_perception_sources` (:1206), join/figure asserts (:1207-1209), `_attach_voice_direction` (:1215).
- **Pass-1 source identity lineage:** `app/specialists/irene_pass1/_act.py:170-346` — plan_units carry `cluster_id` (`c-uNN`), `cluster_role`, `cluster_position`, `parent_slide_id`, `narrative_arc`. The basis for `slide_key` is the source-head identity: for a head unit, the unit id itself; for an interstitial unit, its `parent_slide_id`. The real fixture pins the path as final slide `source_ref` -> plan unit -> source head -> stable source-slide ordinal/key.
- **Segment-manifest contract:** Pydantic `SegmentManifestSegment` `app/specialists/irene/authoring/pass_2_template.py:214` (`_StrictModel`, `extra="forbid"`, :63-64) → wrapped by `SegmentManifest` (:238) in `IrenePass2AuthoringEnvelope.segment_manifest` (:251). JSON-schema `state/config/schemas/segment-manifest.schema.json` (additive-tolerant). Export `_write_segment_manifest_for_b` `app/marcus/orchestrator/storyboard_publisher.py:87` → `exports/segment-manifest-storyboard-b.yaml`.
- **cache_prefix read pattern to mirror:** enrique `decode_envelope_payload` `app/specialists/enrique/_act.py:78-91` reads `segment_manifest_deltas` from `cache_prefix` (NOT `contributions[]`); irene's own `_decode_envelope_payload` `graph.py:965-973`. A `slide_key` on the deltas arrives at enrique for free.

### The fragile join being replaced (both sides)
- Specialist: `_slide_id_ordinal` `graph.py:1085-1091`; `_role_derived_seeds_for_deltas` `:1094-1159` with fail-open guard `if not source_set or source_set != final_ordinals: return None` (`:1146-1152`); consumer `_attach_voice_direction` `:1025-1075`.
- Orchestrator: `_SLIDE_LOCATOR_RE` + `slide_ordinal_from_locator` `enrichment_consumption.py:144-158`; `source_slide_ordinals` `:161-183`; `project_role_derived_voice_by_slide` `:186-255`; role table `PEDAGOGICAL_ROLE_TO_VOICE` `:85-92` (import-time exhaustiveness guard `:100-105`).
- Downstream TTS mapper (NOT ordinal; context only): `app/specialists/_shared/voice_direction_map.py:255,281`.

### The carry gotcha (precedent for AC-A5)
- Frozen neck drops non-core fields: `app/specialists/narration_join.py:39-53`.
- Cluster labels re-attached at export projection: `storyboard_publisher.py:141-147` (+ `cluster_arc_by_id` from Pass-1 at `:176-205`). Follow this precedent if `slide_key` must survive past the neck.
- Witness/test of the gap: `tests/integration/marcus/test_storyboard_publisher_cluster_carry.py` (cites the real `c2c6dcbf` checkpoint). Live evidence: `state/config/runs/c2c6dcbf-.../exports/segment-manifest-storyboard-b.yaml` carries NO cluster labels though `runs/c2c6dcbf-.../irene-pass1.md` shows the deck IS clustered.

### Testing standards
- RED-first (red→green→refactor). NO mocks for any real-data assertion; use the real `c2c6dcbf` artifacts. Run via `.venv/Scripts/python.exe`, `PYTHONIOENCODING=utf-8`. Most-relevant existing tests to extend/mirror: `tests/specialists/irene/test_role_derived_seed_wiring.py`, `tests/marcus/orchestrator/test_enrichment_consumption.py`, `tests/integration/marcus/test_storyboard_publisher_cluster_carry.py`, `tests/specialists/irene/test_pass2_delta_id_backfill.py`. Golden: `tests/fixtures/specialists/irene/pass_2_template_golden.json`. Paired clustered/flat substrate: `_bmad-output/test-artifacts/cluster-tolerance-test/{cluster-bundle,flat-bundle}/segment-manifest.yaml`.

### Project Structure Notes
- M3 import-linter fence holds: `slide_key` is data on the deltas/manifest; the orchestrator-side consumer (`app/marcus/orchestrator/enrichment_consumption.py`) reads it as a value, never importing `app.specialists.irene` authoring/clustering code, and the specialist side never imports `app.marcus`.
- Schema additive: `SegmentManifestSegment` field add + schema fragment is additive (dev-agent authority, no contract version bump) provided directed-OFF output stays byte-identical (AC-A6) — pin that.

### §8 Pipeline-manifest block-mode — NOT triggered
- `state/config/pipeline-manifest.yaml:60-85` `block_mode_trigger_paths` does NOT list `irene/graph.py`, `pass_2_template.py`, `segment-manifest.schema.json`, `enrichment_consumption.py`, `storyboard_publisher.py`, or `narration_join.py`. Block-mode + the T1 regime read are triggered ONLY if the story edits `pipeline-manifest.yaml` itself (e.g. to add a node/edge). A pure data-field addition does not trip it.

### ⚠️ Verified implementation findings (2026-06-29 dev-design pass — READ FIRST)

These were confirmed against the live tree and change the *internals* of how `slide_key` is sourced (the ACs stand; the mechanism is sharper):

1. **`parent_slide_id` does NOT flow directly into Pass-2 deltas.** It lives on Pass-1 plan_units, and only on interstitials (heads ARE the parent) — `app/specialists/irene_pass1/_act.py:345-372`. So `slide_key` cannot be read directly from `parent_slide_id` at the Pass-2 emit point.
2. **The source-slide lineage is broken at the Gary render boundary.** Pass-2's roster is `gary_slide_output` (`_slide_roster`, `app/specialists/irene/graph.py:151-200`), whose rows carry only the FINAL `slide_id` (`slide-NN`) + visual_description — no source/cluster provenance. This is the deeper root cause of the fail-open: the final deck genuinely does not carry which source slide each final slide came from.
3. **`cluster_id` IS a declared field on `SegmentManifestSegment` and reaches the Pass-2 deltas** (`pass_2_template.py:227-230`; confirmed by the cluster-carry witness in §5), but it is not sufficient by itself to recover the exact source-head key in all paths. The authoritative real-deck fixture (`tests/fixtures/specialists/irene/c2c6dcbf_source_to_final_slide_map.json`) pins the derivation as: final slide `source_ref` -> Pass-1 `plan_units.unit_id` -> source head (`parent_slide_id` for interstitials, otherwise the unit id) -> stable `slide_key`. `cluster_id` remains corroborating lineage/context, not the only derivation input.
4. **Implication for scope:** establishing `slide_key` requires tracing the Pass-1→Gary→Pass-2 lineage through the source-ref/plan-unit path rather than adding a field from a final ordinal. This is still Slice-0 / ZERO live spend, but it is a lineage-threading change across the clustering seam — dev MUST trace where `source_ref`, `cluster_id`, and any backfilled fields are populated before choosing the final implementation, and a brief Winston (architect) confirm on the source-ref/plan-unit derivation is advised before code lands in the proven Pass-1/Pass-2 substrate.

## Out of scope (Story B — enhanced-vo-2-v3-provider-text-compiler)
- The v3 provider-text compiler, the four text channels (canonical/provider/display/captions), captions zero-tag-leak gates, the eleven_v3 tag allowlist, receipts/skip-if-exists changes, any live ElevenLabs synthesis, and the Descript-final A/B. This story ONLY makes the role→slide join reliable so Story B's compiler acts on the correct slide. Do NOT add `rhetorical_role`, `render_strategy:v3`, or any compiler here.

## References
- [Source: _bmad-output/planning-artifacts/enhanced-vo-party-consensus-2026-06-29.md] — green-light consensus + binding amendments (Story A AC-A1..A4, Winston M3 pre-condition, Amelia field-pin list, Murat build-breaking RED).
- [Source: _bmad-output/implementation-artifacts/claude-code-brief-enhanced-vo-v3-generation-2026-06-29.md] — Marcus brief (§7 cluster/lesson-plan integration, the practical path).
- [Source: _bmad-output/planning-artifacts/p5-directed-voice-arc-strawman-2026-06-27.md §S] — the `p5-s2-role-seed-robust-source-to-final-slide-linkage` deferred item this story discharges.
- [Source: app/specialists/irene/graph.py:1085-1159, :1025-1075, :1162-1227] ; [app/marcus/orchestrator/enrichment_consumption.py:85-255] ; [app/specialists/irene/authoring/pass_2_template.py:214-251] ; [app/specialists/enrique/_act.py:78-91] ; [app/specialists/narration_join.py:39-53] ; [app/marcus/orchestrator/storyboard_publisher.py:87,141-205].

## Dev Agent Record
### Agent Model Used
Claude Code BMAD dev lane; Codex independent review/hygiene lane.

### Debug Log References
- Local close commit: `d4455e4f feat(irene): enhanced-vo-1 slide_key role->slide identity join (Slice 0)`.
- Sprint status close record: `_bmad-output/implementation-artifacts/sprint-status.yaml` entry `enhanced-vo-1-role-slide-linkage: done`.
- Review-lane verification: `107 passed` for the focused Story A bundle; ruff clean on touched Story A files.

### Completion Notes List
- `slide_key` is now emitted as data on the manifest/deltas and used for role-to-slide identity joins.
- The old clustered-deck ordinal fail-open path is replaced by fail-loud identity linkage; no fuzzy ordinal fallback is accepted when `slide_key` is required.
- The real `c2c6dcbf` clustered deck fixture pins source-to-final lineage and stability.
- Story B concerns stayed out of this slice: no provider-text compiler, live v3 synthesis, `rhetorical_role`, caption tag-leak gate, or Descript A/B landed here.

### File List
- `app/specialists/irene/graph.py`
- `app/specialists/irene/authoring/pass_2_template.py`
- `app/marcus/orchestrator/enrichment_consumption.py`
- `app/marcus/orchestrator/production_runner.py`
- `app/marcus/orchestrator/storyboard_publisher.py`
- `schema/irene_pass_2_authoring.v1.schema.json`
- `state/config/schemas/segment-manifest.schema.json`
- `tests/fixtures/specialists/irene/c2c6dcbf_source_to_final_slide_map.json`
- `tests/specialists/irene/test_slide_key_identity_join.py`
- `tests/specialists/irene/test_role_derived_seed_wiring.py`
- `tests/integration/marcus/test_storyboard_publisher_cluster_carry.py`
- `tests/integration/marcus/test_package_builders.py`
