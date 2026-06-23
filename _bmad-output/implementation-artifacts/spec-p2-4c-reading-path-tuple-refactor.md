# Spec — P2-4c: Reading-Path Tuple Refactor (additive, hybrid-(c) classifier)

**Status:** **S1 DONE** (2026-06-23 — Codex T1–T10 → hand-back → remediation → Claude re-T11 → party-mode 5/5 CLOSE). S2/S3 `ready-for-dev` (gaps G1/G2/G3 resolved; Codex prompts authored).
**Story family:** P2-4 (P2-4a machinery DONE `38f2ba8`; **P2-4c = this** tuple refactor; P2-4b calibration is OPERATOR-GATED and **re-sequences AFTER P2-4c** — it calibrates the refactored classifier).
**Branch:** `fidelity-perception-arc-2026-06-19`. **Class:** S (substrate). **Dev:** **Codex** (NEW CYCLE: Codex T1–T10 + Claude T11 review/close), per the v7 session directive (supersedes the earlier "NO Codex" note).
**Authority:** `reading-path-patterns-catalog.md` v1 (party-ratified GREEN-WITH-AMENDMENTS 2026-06-22, amendments A1–A10) + `reading-path-patterns-design-decisions-2026-06-21.md`.
**T1 readings (mandatory before code):** `docs/dev-guide/pipeline-manifest-regime.md` (this diff touches `block_mode_trigger_paths`); `docs/dev-guide/pydantic-v2-schema-checklist.md` (schema-shape); `docs/dev-guide/dev-agent-anti-patterns.md`; the catalog v1 §9 build contract.

---

## 0. v1.1 AMENDMENTS — held-out round + D1–D3 (operator-ratified 2026-06-22; supersede where they conflict)
The catalog advanced to **v1.1** after the held-out confirm/deny round (12/14 confirmed; A6 primary-key top-1 **13/14 = 0.93** PASS; diagram_driven gate held). A 6/6 consensus round (no impasse) + operator ratification adopted three decisions that amend this spec:
- **D1 — `multi_column` = N≥2 coordinate peers** (was N≥3); `two_pane`/`two_up_comparison` reserved for **oppositional** with an **explicit-cue discriminator** (vs/before-after/pro-con/✓✗/Option A|B). **S1 geometry emits `multi_column`; the oppositional upgrade is an S3 call** (the cue may flag, never set). `multi_column` **EXITS the quarantine** (now N≥4) — it counts toward the top-1 denominator (held-out 17_ stays scored). Resolves Gap **G1** (peer-vs-oppositional = explicit-cue → S3).
- **D2 — new orthogonal `callout_intent` axis** (speech-act): a **separate OPTIONAL sibling field** (`callout_intent: Optional[CalloutIntent]`), OUTSIDE the tuple→primary-name derivation (Winston). Seeded values `{invite_response, challenge_quiz, directive_cta}` (provisional; `takeaway_imperative`+`contact` are harvest hypotheses, not in the frozen enum; `inform`/null = default). **LLM-resident in the existing S3 call** as an added structured-output key (no new round-trip, no new sub-story; deterministic regex pre-flags only). **EXCLUDED from primary-key + full-tuple top-1; reported as a probationary per-axis vector** gated on a **double-labeled agreement ≥0.80 / κ≥0.6** RED-first floor. The VO directness mandate is a *generation* directive, tested separately.
- **D3 — `enumerated_process` = transform-sequence (PERMUTABILITY test)**; numbered summary lists → `peer_boxes`. Discriminator = order-dependence, NOT numerals. **S1 conservatively downgrades** numbered peers to `peer_boxes`; S3 confirms genuine process. RED-first permutability fixture pair.
- **Build sequencing (Winston):** D1+D3 are zero-schema-diff derivation refinements — land them as ONE derivation-module change with a single shape-pin re-baseline. D2 adds one optional field (additive dp-v1.6). Back-check (Mary): original `enumerated_process` exemplars still pass; `peer_boxes` clears its floor after absorbing lists; reviewed-26 `multi_column` are genuine peers.

## 1. Intent (frozen)
Refactor the P2-4a reading-path classifier from a **flat closed 7-enum** into the party-ratified **compositional tuple** `{macro_layout × image_role(per-element) × text_substructure × narration_cadence}`, **ADDITIVELY** — `reading_path` stays a closed enum (the derived primary name); the tuple lands as optional sibling fields. Fix the `_looks_z` over-claim (v0: 43/54, 24 false-positives). Keep P2-4a green. Bump `data_plane_vocabulary_version` dp-v1.5 → dp-v1.6 (additive; pack stays v4.2). Party consensus on the dp bump is RECORDED (catalog §10 A1) — the pre-dev pipeline-regime gate is satisfied.

## 2. Substrate edit sites (grounded; file:line)
- **Enum + schema:** `app/models/perception/perception_artifact.py:13-21` (`ReadingPath` Literal, 7 values) + `:52-55` (Field). **ADD** sibling optional fields here (see §4 S1-AC2).
- **Classifier:** `scripts/utilities/reading_path_classifier.py` — entry points `classify_reading_path`:126, `ordered_element_keys_for_reading_path`:153, `with_classified_reading_path`:179; predicates `_looks_z`:272, `_looks_f_pattern`:287, `_looks_like_grid`:260, `_looks_center_out`:266, `_looks_multi_column`:278, `_has_ordinal`:256; default `top_down`:150; `READING_PATH_PATTERNS`:11-19; `CADENCE_TOKENS`:33-88.
- **Vision integration:** `app/specialists/vision/_act.py:112-138` (`with_classified_reading_path` call + fail-loud tag `vision.reading-path.unclassifiable`).
- **Irene verify-node:** `app/specialists/irene/graph.py:398-437` (`_assert_reading_path_conformance`, `Pass2ReadingPathError`).
- **Reading-path 4-file lockstep** (all in `block_mode_trigger_paths`, parity-pinned by `tests/contracts/test_reading_path_parity.py`):
  1. registry `state/config/reading-path-patterns.yaml`
  2. classifier `scripts/utilities/reading_path_classifier.py:11-19`
  3. lint `scripts/validators/pass_2_emission_lint.py:12-20`
  4. schema `state/config/schemas/segment-manifest.schema.json:23-31`
  (+ grammar-riders doc parity source `skills/bmad-agent-content-creator/references/pass-2-grammar-riders-examples.md`)
- **Manifest:** `state/config/pipeline-manifest.yaml:54` (`dp-v1.5`) + changelog `:35-53` + `-gen` witness via `scripts/generators/v42/render.py` (Check-9 SHA in `scripts/utilities/check_pipeline_manifest_lockstep.py`).

## 3. Build split (party A8) — 3 stories
- **S1 — deterministic geometry + additive schema + derivation** (NO LLM, no perceiver-contract change). **This spec's ready-for-dev scope. First RED slice.**
- **S2 — per-element image-role tier emission** (perceiver contract: emit tier {1,2,2.5,3,4}, not just `kind`). Gated on §Gaps G2.
- **S3 — gpt-5.5 ambiguity-escalation arbitration** (≥gpt-5.5 floor, no downgrade; recorded-real behind a parse seam, never a production-path fixture). Gated on §Gaps G1+G3.

---

## 4. S1 — Acceptance Criteria (frozen, RED-first)
**AC-S1-1 — additive enum value-set.** `ReadingPath` Literal updated to the catalog v1 admitted set as the **derived primary names**: `split_image_text`, `two_up_comparison`, `multi_column`, `text_hero_divider`, `enumerated_process`, `top_down`, `center_out`, `diagram_driven`. **No value removed** (`z_pattern`, `f_pattern`, `grid_quadrant`, `sequence_numbered` retained as deprecated-but-mapped aliases → see AC-S1-5). Pure value-set widening + alias mapping; field shape unchanged.

**AC-S1-2 — additive tuple sibling fields** on `PerceptionArtifact` (`app/models/perception/perception_artifact.py`), all **optional/nullable** (additive non-breaking; pydantic-v2 checklist applies):
- `macro_layout: MacroLayout | None` — Literal {`split_image_text`,`text_hero_divider`,`multi_column`,`two_pane`,`card_grid`,`single_text_block`}.
- `image_roles: list[ImageRoleTier] | None` — per-element tiers {`1`,`2`,`2_5`,`3`,`4`} (string keys; `2_5` = evidentiary, party A4).
- `text_substructure: TextSubstructure | None` — {`enumerated_process`,`peer_boxes`,`comparison_pair`,`dense_exposition`,`hero_message`}.
- `narration_cadence: NarrationCadence | None` — {`sparse_slow`,`moderate`,`dense`}.
- `reading_path` (existing) becomes the **derived** primary name (see AC-S1-3).

**AC-S1-3 — pinned derivation module (A1 invariant).** A single pure function `derive_primary_name(macro_layout, text_substructure) -> ReadingPath` lives in ONE module with its own **shape-pin test**. `with_classified_reading_path` sets `reading_path` via this function. The projection cannot drift from the tuple silently.

**AC-S1-4 — geometry detects macro_layout + tightened `_looks_z`.** Deterministic geometry (no LLM) populates `macro_layout`, `text_substructure`, `narration_cadence` from the perceived bboxes/kinds. `_looks_z` is tightened so it no longer fires on focal/visual-hero/peer-grid slides (the v0 24 false-positives). **`z_pattern` is DEMOTED** (A2): never emitted as a `macro_layout`; survives only as an optional `narration_cadence`-adjacent flag when tier-1 hero elements sit at diagonal extremes with nothing competing.

**AC-S1-5 — additive non-regression (P2-4a stays GREEN).** Existing `tests/contracts/test_reading_path_parity.py`, `tests/specialists/vision/test_reading_path_classifier.py`, `tests/specialists/irene/test_irene_reading_path_conformance.py` either stay green unmodified OR are updated only to reflect the **derived** primary name (deprecated aliases map to a stable primary name; the JSON-schema enum is WIDENED not narrowed → the "rejects out-of-vocab" test still rejects a genuinely-unknown token like `triptych`). No existing red-rejection weakened.

**AC-S1-6 — 4-file lockstep parity holds.** Registry YAML + classifier tuple + lint + segment-manifest schema all carry the widened value-set; `test_reading_path_pattern_lockstep` updated to the new set and GREEN. `dp-v1.5 → dp-v1.6` in `pipeline-manifest.yaml:54` + changelog entry; `-gen` determinism witness regenerated; Check-9 SHA refreshed. Pack stays v4.2.

**AC-S1-7 — default-degradation counter + ceiling (RED-first; party A7-1).** `top_down`/DEFAULT emission is **counted + reported** per classify-batch as an emitted artifact (not a log line), with a ceiling assertion (**DEFAULT ≤ 25%** of slides over a batch). A classifier that routes everything to DEFAULT must FAIL this test.

**AC-S1-8 — `multi_column` D1 un-quarantine attestation.** Superseding the older A3 quarantine, operator-ratified D1 generalizes `multi_column` to N≥2 coordinate peers and confirms N≥4 evidence; `multi_column` is emittable and counted in the top-1 denominator. S1 only sets an oppositional-cue side-channel flag for S3; it does not upgrade `multi_column` to `two_pane`/`two_up_comparison`.

**AC-S1-9 — fail-loud preserved.** `with_classified_reading_path` still raises `ReadingPathClassificationError` → `vision.reading-path.unclassifiable` when perceived geometry is absent (the P2-4a contract at `_act.py:120-130` and the non-numeric-bbox controlled-skip at classifier tests are preserved).

### S1 RED-first fixtures (party A7 — non-negotiable, land RED before GREEN)
1. **Default-degradation:** a batch fixture seeded to over-default → DEFAULT-ceiling assertion FAILS first, passes after the ceiling logic. (A7-1)
2. **`diagram_driven` foreground-gate negative control:** decorative/background image (not foreground+opaque+load-bearing) → assert NOT `diagram_driven` (assert `top_down`/`split_image_text`). (A7-2)
3. **`kind:diagram` ≠ instructional trap:** element `kind:diagram` but illustrative → assert NOT `diagram_driven` (the exact 26-slide finding; standing negative control). (A7-3)
4. **`multi_column` quarantine:** assert excluded from top-1 denominator until the evidence flag flips, in code. (A7-4 / A3)
5. **Tightened-`_looks_z` regression:** a known v0 z false-positive fixture (focal-hero slide) → now classifies `split_image_text` (or `image`-role-driven), NOT z. (AC-S1-4)
6. **Additive non-regression:** the P2-4a `z_pattern` fixture still resolves to a stable derived primary name via the alias map (proves no value silently dropped). (AC-S1-5)

---

## 5. S2 / S3 — scoped (NOT ready-for-dev; gated on §Gaps)
- **S2 (image-role tier emission):** perceiver emits a per-element tier {1,2,2.5,3,4}. Gated on **G2** (tier-assignment rubric). Carries the tier-2.5 evidentiary band as `provisional, validate at P2-4b`.
- **S3 (gpt-5.5 escalation arbitration):** escalates ONLY on the **G3** ambiguity predicate; returns the tuple + cited near-misses; ≥gpt-5.5 floor (catalog §8, no downgrade). Parse seam only; recorded-real responses never a production-path fixture. RED test: malformed/empty escalation → degrade-to-DEFAULT-counted, never crash/mislabel (A7-5).

## 6. Gaps — ALL RESOLVED (party-mode 2026-06-22; see `reading-path-gap-resolution-G2-G3-2026-06-22.md`)
- **G1 — peer vs oppositional → RESOLVED (D1):** explicit-cue discriminator (vs/before-after/pro-con/✓✗/Option A|B); S1 emits `multi_column`, S3 upgrades to `two_pane` on the cue. Cue may flag, never set, in S1.
- **G2 — image-role tier → RESOLVED:** perceiver-primary (`role_tier` on the existing call, rubric inlined) + deterministic geometry gate/backfill (tier-4 size-lock; tier-3 ruled out when `internal_label_count==0`; Amelia prior table backfill). Scored tiers {1,2,4}; 2.5→2 fold; tier-3 quarantined; κ≥0.6 + confusion-matrix gate; provenance metadata. → **`codex-dev-prompt-p2-4c-s2.md`**.
- **G3 — escalation predicate → RESOLVED:** inline-catalog default (no third call) + a triggered single ≥gpt-5.5 tuple-delta call on `escalate = macro_margin<θ ∨ opposition-cue ∨ callout-present ∨ numbered-without-transform-verb ∨ low-conf-role ∨ tuple-disagreement ∨ low-confidence ∨ 2.5/3-candidate-hit`; `escalation_ledger` observable; paired over-(≤20%)/zero-escalation tripwires; retry-to-green fence (upstream-frozen, single-shot, call-count assertion); permissive-start, calibrate after Trial-1. → **`codex-dev-prompt-p2-4c-s3.md`**.

## 7. Conformance-measurement contract (party A6 — binding, consumed by P2-4b)
- **Top-1 ≥0.85 = STRICT exact match on primary key `{macro_layout × image_role}`** (no partial credit).
- `text_substructure` + `narration_cadence` reported as a **separate per-axis conformance vector** (never folded into top-1) — absorbs John's A10 (secondary axes do not gate the headline metric).
- **≥80% conformance = full-tuple exact** across all axes.
- Per-axis confusion matrix emitted as an artifact.
- ~~`multi_column` excluded from top-1 denominator until N≥4 (A3).~~ **D1: `multi_column` now N≥4 → EXITS quarantine; it COUNTS toward the top-1 denominator (held-out 17_ stays scored — no metric laundering).**
- **`callout_intent` (D2) is EXCLUDED from the primary-key AND full-tuple top-1** — reported as a **probationary separate per-axis vector**; it may influence NO scored number until a **double-labeled agreement ≥0.80 / κ≥0.6** floor is cleared (RED-first test pins the floor on double-labeled data; if it fails, collapse the value-set before shipping).
- **Contamination check:** record per held-out slide whether its gold label invokes a gated/retired pattern; ≥2 of 14 ⇒ retirement overfit, 0.85 contaminated (recorded observable).

## 8. Governance + verification
- **Pipeline-lockstep regime:** diff touches `block_mode_trigger_paths` (manifest + reading-path 4-file set + pack `-gen` witness) → Cora block-mode hook applies; run `scripts/utilities/check_pipeline_manifest_lockstep.py`. dp-v1.6 = additive vocab bump within v4.2 (same tier as dp-v1.5); party consensus recorded (catalog §10 A1).
- **Verification battery (S1 close):** the 6 RED-first fixtures GREEN; `test_reading_path_parity` GREEN on the widened set; vision + irene reading-path tests GREEN; lockstep L1 exit 0; ruff; lint-imports; `git diff --check`. No mocks on the production path.
- **Close gate:** `bmad-code-review` (3-layer) before flipping S1 done; additive-non-regression attestation (P2-4a fixtures green). Schema-shape discipline per the pydantic-v2 checklist (validate_assignment, closed Literals, triple-layer red-rejection on the closed enum).

## 9. Open decisions for the dev-open party (not blocking S1)
- Confirm the deprecated-alias mapping table (`z_pattern`→? , `f_pattern`→? , `grid_quadrant`→`multi_column`?, `sequence_numbered`→`enumerated_process`) — propose in S1 dev, ratify at the S1 close party.
- G1/G2/G3 resolutions ratify at the S2/S3-open party.
