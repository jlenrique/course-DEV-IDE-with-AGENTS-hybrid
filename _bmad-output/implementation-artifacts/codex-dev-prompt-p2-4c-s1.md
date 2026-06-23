# Codex Dev Prompt — P2-4c **S1** (deterministic geometry + additive tuple schema)

**Cycle:** NEW CYCLE — you (Codex) run T1–T10 + a T10 self-review and return a handoff; Claude runs T11 (battery + 3-layer `bmad-code-review` + party CLOSE + commit + flip done). **Do NOT commit or flip status** — leave the tree for T11.
**Story:** P2-4c S1 (first RED slice; deterministic geometry, **NO LLM, NO perceiver-contract change**). **Class S.** Branch `fidelity-perception-arc-2026-06-19`.
**Authority (read first, in order):** `spec-p2-4c-reading-path-tuple-refactor.md` (§0 v1.1 amendments [BINDING], §4 S1 ACs, §7 conformance, §9 build contract) · `reading-path-patterns-catalog.md` v1.1 (§2 AXES 1/3/5, §4, §11 D1–D3) · `docs/dev-guide/pipeline-manifest-regime.md` (this diff touches `block_mode_trigger_paths`) · `docs/dev-guide/pydantic-v2-schema-checklist.md`.

## Scope = S1 ONLY
Deterministic geometry classification + the additive tuple schema + the pinned derivation + the 4-file lockstep regen. **Per-element image-role tier emission is S2; gpt-5.5 escalation + oppositional `two_pane` upgrade + `callout_intent` *labeling* are S3.** S1 only ADDS the optional fields (incl. nullable `callout_intent`) and populates the geometry-derivable axes.

## Files in scope
- `app/models/perception/perception_artifact.py` — enum widen + new optional fields (AC-S1-1, AC-S1-2).
- `scripts/utilities/reading_path_classifier.py` — geometry → tuple; tightened `_looks_z`; z demoted; default counter; D3 permutability downgrade (AC-S1-4, AC-S1-7).
- NEW `scripts/utilities/reading_path_derivation.py` (or a clearly-named module) — `derive_primary_name(macro_layout, text_substructure) -> ReadingPath` (AC-S1-3).
- The 4-file lockstep set (parity, AC-S1-6): `state/config/reading-path-patterns.yaml` · `scripts/validators/pass_2_emission_lint.py` (READING_PATH_PATTERNS) · `state/config/schemas/segment-manifest.schema.json` (enum) · (classifier above).
- `state/config/pipeline-manifest.yaml` — `data_plane_vocabulary_version: dp-v1.5 → dp-v1.6` + changelog entry (AC-S1-6).
- `-gen` determinism witness — regenerate via `scripts/generators/v42/render.py`; refresh the Check-9 SHA in `scripts/utilities/check_pipeline_manifest_lockstep.py` if it pins one.
- Tests under `tests/` (new RED-first fixtures + updates to the 3 existing reading-path test files).

## DO NOT MODIFY
- `app/specialists/vision/_act.py` / `provider.py` / `payload_contract.py` (S2 territory — perceiver contract unchanged in S1).
- `app/specialists/irene/graph.py` reading-path verify-node logic (consume the new fields read-only if needed; no behavior change in S1).
- Any P2-4a test assertion except to reflect the **derived** primary name (see AC-S1-5). Never weaken a red-rejection.

## Tasks (T1–T10)
**T1 — readings + baseline.** Read the authority docs. Capture a clean-HEAD baseline (`git stash` check) so any "pre-existing" claim in your handoff carries pasted clean-HEAD evidence (baseline-diff attestation — mandatory).

**T2 — schema (additive, pydantic-v2 checklist).**
- AC-S1-1: WIDEN the `ReadingPath` Literal to ADD the v1.1 primary names: `split_image_text`, `two_up_comparison`, `multi_column` (already present), `text_hero_divider`, `enumerated_process`, `top_down` (present), `center_out` (present), `diagram_driven`. **Keep ALL existing values** (`z_pattern`, `f_pattern`, `grid_quadrant`, `sequence_numbered`) — no value removed (additive; z_pattern/f_pattern retained as demoted/deprecated-but-mapped; `sequence_numbered` is the deprecated alias of `enumerated_process`, `grid_quadrant` of `card_grid`-routes-to-`top_down`).
- AC-S1-2: ADD optional/nullable sibling fields: `macro_layout: MacroLayout | None`, `image_roles: list[ImageRoleTier] | None` (tiers `"1"|"2"|"2_5"|"3"|"4"` — define the type; leave UNPOPULATED in S1, S2 fills), `text_substructure: TextSubstructure | None`, `narration_cadence: NarrationCadence | None`, `callout_intent: CalloutIntent | None` (Literal `invite_response|challenge_quiz|directive_cta`, nullable default — STUB, S3 populates). Closed Literals; `validate_assignment=True`; triple-layer red-rejection on each closed enum.

**T3 — derivation module (AC-S1-3).** `derive_primary_name(macro_layout, text_substructure) -> ReadingPath`, pure function, one module. `with_classified_reading_path` sets `reading_path` via this function. Add a dedicated **shape-pin test** so the projection can't drift.

**T4 — geometry → tuple (AC-S1-4, D1, D3).**
- Populate `macro_layout`, `text_substructure`, `narration_cadence` deterministically from perceived bboxes/kinds.
- **Tighten `_looks_z`** so it no longer fires on focal/visual-hero/peer-grid slides; **z_pattern is DEMOTED** — never emit it as a `macro_layout` (it may persist only as an optional cadence-flag when tier-1 hero elements sit at diagonal extremes).
- **D1:** detect side-by-side coordinate columns as `multi_column` (N≥2). Do NOT emit `two_pane` from geometry (oppositional upgrade is S3). An opposition lexicon (vs/versus/before/after/pro/con/✓✗/"Option A|B") may set an **escalation FLAG** but must NOT set `two_pane` in S1.
- **D3 (permutability):** `enumerated_process` ONLY when order is load-bearing (transform-sequence: arrow/flow glyphs OR transform-verb lexicon "becomes/then/feeds/produces/launch→iterate"). Numbered items that are layout-peers with no connective → **downgrade to `peer_boxes`**. Numerals alone NEVER set `enumerated_process` (kills the `_has_ordinal` over-trigger).

**T5 — default-degradation counter (AC-S1-7).** Emit a counted/observable artifact per classify-batch of `top_down`/DEFAULT emissions with a ceiling assertion (DEFAULT ≤ 25%). Not a log line — a returned/recorded value a test can assert.

**T6 — lockstep parity + dp bump (AC-S1-6).** Propagate the widened value-set across all 4 lockstep files; update `test_reading_path_parity.py` to the new set; bump `dp-v1.5 → dp-v1.6` + changelog; regenerate the `-gen` witness; refresh Check-9 SHA. `check_pipeline_manifest_lockstep.py` must exit 0. The "rejects out-of-vocab" test must still reject a genuinely-unknown token (e.g. `triptych`).

**T7 — RED-first fixtures (write FAILING first, then green).** Per spec §4 S1 fixtures:
1. default-degradation over-default batch → ceiling FAILS first.
2. `diagram_driven` foreground-gate negative control (decorative/background image → NOT diagram_driven).
3. `kind:diagram` ≠ instructional trap (kind:diagram but illustrative → NOT diagram_driven).
4. tightened-`_looks_z` regression (a known v0 z false-positive focal-hero slide → now `split_image_text`/non-z).
5. additive non-regression (the P2-4a `z_pattern` fixture still resolves to a stable derived primary name via the alias map — no value silently dropped).
6. **D3 permutability pair:** one true transform-sequence → `enumerated_process`; one numbered summary list → `peer_boxes` (split on permutability, not numerals).
7. **D1:** a 2-wide coordinate-peer slide → `multi_column` (not two_pane); confirm `multi_column` is a normally-emitted, counted value (un-quarantined).
PLUS fold-in regression fixtures for the two deferred slivers: `vision-perceiver-empty-visual-elements-degradation` (HIGH/perceived + empty visual_elements → controlled degradation, not an uncaught raise) and `reading-path-bbox-out-of-range-bucketing` (cx>1.0 / x1>x2 → clamp/normalize or assert-on-bucket, no skew). Cite both deferred-inventory entries.

**T8 — additive non-regression (AC-S1-5).** Run the existing reading-path tests; update ONLY to reflect the derived primary name (never weaken a red-rejection). P2-4a stays green.

**T9 — full battery.** Reading-path tests (parity/classifier/conformance) · `check_pipeline_manifest_lockstep.py` (exit 0) · ruff · lint-imports · `git diff --check`. No mocks on any production path.

**T10 — self-review + handoff.** Write `_codex-handoff/p2-4c-s1-ready-for-review.md`: per-AC evidence, the RED→green transcript for each fixture, the baseline-diff attestation (clean-HEAD evidence for any "pre-existing" claim), the dp-v1.6 + `-gen` regen evidence + Check-9 SHA, and a LOC/diff summary. Flag any deviation explicitly.

## Pass-bar (Claude T11 will verify)
Additive: P2-4a green; no enum value removed; JSON-schema enum widened not narrowed. All 7 RED-first fixtures + the 2 fold-in fixtures land RED-then-green. Lockstep exit 0 + dp-v1.6 + `-gen` regenerated + Check-9 refreshed. `callout_intent` present but nullable + unpopulated by S1 (S3 fills); `image_roles` present but unpopulated (S2 fills). Derivation shape-pin test green. No production-path mocks/fixtures. Baseline-diff attestation provided.
