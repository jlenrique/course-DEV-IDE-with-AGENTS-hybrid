# Codex Dev Prompt — P2-3 (Pass-2 consumes perceived visuals — the regression fix)

**Story:** `p2-3-pass2-consumes-perceived-visuals` · **Branch:** `fidelity-perception-arc-2026-06-19` · **Baseline:** P2-2 closed at `3a0ad22`.
**Cycle:** NEW CYCLE — you run T1–T10 (dev + tests), then Claude runs T11 (review/commit/close). **Read first:** the spec `spec-p2-3-pass2-consumes-perceived-visuals.md` (frozen Intent + ACs + §Tier-3 Green-Light Disposition with binding amendments A1–A9), and `docs/dev-guide/pipeline-manifest-regime.md` at T1 (pipeline-lockstep applies — manifest + `-gen` pack are touched).

## The fix in one sentence
Make Irene's Pass-2 narration ground on the **perceived `PerceptionArtifact`** (rich model, vision-produced) as the **sole visual authority**, demoting Gary's brief (`visual_description`) and Vera to a subordinate "expected (may be stale)" signal — so slide-01 narrates **$4.5T (rendered)**, not **$5.2T (brief)**, and the P2-1 detector goes regression-green.

## Edit sites (verified at 3a0ad22)
1. **`state/config/pipeline-manifest.yaml:571-583`** — node `08` (irene Pass-2) `dependency_projections`: ADD `perception_artifacts: {from: vision, key: perception_artifacts}`. Bump `data_plane_vocabulary_version` `dp-v1.3 → dp-v1.4`; regenerate the `-gen` witness (`docs/workflow/production-prompt-pack-v4.2-gen-...md`); `pack_version` stays `v4.2` (no v4.3). Lockstep L1 must exit 0; frozen-pack-SHA unchanged.
2. **`app/specialists/irene/graph.py`** — `_act_pass_2` (395-453): read `perception_artifacts` off the envelope payload. `_slide_roster` (97-131) / new helper: build the **visual authority** from perceived elements (`visual_elements`, `extracted_text`, perceived figures, `layout_description`) of the RICH `app/models/perception` model. `_assemble_pass_2_prompt` (228-280): present perceived elements as THE authority under an explicit delimited region; put brief/Vera ONLY in a subordinate demoted region.
3. **`app/specialists/irene/authoring/pass_2_template.py`** — the minimal `PerceptionArtifact` here is NOT the grounding source (A1). Populate it FROM the rich model at the envelope boundary, or leave it untouched; add a module docstring naming the rich model as sole upstream + a field-compatibility contract test (A1). Add a **decoy note** at the wiring site (A2).

## Binding amendments (T11 re-fails without these)
- **A1 (rich-model authority):** runtime grounds on `app/models/perception/perception_artifact.py::PerceptionArtifact`. NEVER ground on the minimal authoring-envelope model (it is field-poor and silently reverts to brief). Contract test: every field the authoring-envelope model reads must be populated-from/type-compatible-with the rich model; fail loud if the rich model drops it.
- **A2 (fork filing — BLOCKING):** the deferred-inventory entry `perception-artifact-two-model-fork` is filed (cleanup direction + "direction may flip" caveat); add the in-code decoy note. (Claude filed the inventory entry at spec close; you add the code-site note.)
- **A3 (anti-vacuity test gate — non-negotiable):**
  - **Contradiction fixture** mandatory: perceived `$4.5T` + photo/bar vs brief `$5.2T` + "line+bars" (they MUST disagree on a load-bearing figure AND chart type).
  - **Assert by section/region:** the assembler emits a structural delimiter separating an authority region from a demoted region. Tests assert: authority region CONTAINS the perceived figure (`$4.5T`) + perceived chart type AND **EXCLUDES** `$5.2T`/"line+bars"; brief content appears ONLY in the demoted region, explicitly labeled subordinate. A presence-grep for `$4.5T` alone is REJECTED.
  - **Two mutation runs, evidence in Completion Notes:** **M1** revert grounding to the brief → authority carries `$5.2T` → test RED. **M2** collapse the authority/demoted partition into one flat blob → positional assertion can't locate `$4.5T` as authority → test RED. If either mutation stays green, the test is vacuous.
- **A4 (detector-as-judge):** AC-4's pass criterion is the **P2-1 fidelity detector returning clean** on the Pass-2 output, NOT a string match. At T1, confirm the P2-1 detector is **headlessly invokable** on Pass-2 narration; if it is not, STOP and surface it as a blocker (do not work around it at T11).
- **A5 (RED-first):** commit a regression test reproducing the `$5.2T line+bars` hallucination vs the `$4.5T`+photo perceived slide — RED pre-fix, GREEN post-fix. Name a **held-out** seed-contradicted slide (not tuned against) for the anti-overfit leg.
- **A6 (STRIKE gate):** the grounding-leg deferred entry is struck only on (a) detector-GREEN across the full frozen corpus, (b) detector-GREEN on ≥1 held-out slide, (c) a cited reproduced pre-fix RED baseline. (Claude does the strike at T11; you provide the evidence.)
- **A7 (baseline-diff attestation — carry P2-2 Category-F forward):** paste pre-fix RED + post-fix GREEN detector output for the same corpus into Completion Notes, plus an explicit attestation: "the green assertion is bound to perceived/rendered-PNG elements, not the brief." Any test you label "pre-existing failure" needs clean-HEAD (`4455c04`/`3a0ad22`) evidence.
- **A8 (NFR-I6 cache-prefix):** the prompt body changes, so the cache-prefix shifts ONCE — re-pin the named stability fixture deliberately with a one-line rationale (never `xfail`/skip). Preserve: canonical sorted-keys JSON for injected perception (match the existing pinned `json.dumps(..., sort_keys=True, ensure_ascii=True, separators=(",",":"))` signature); deterministic perceived-element ordering by a stable key; inject the authority block at a FIXED seam; no incidental reformatting of pinned text.
- **A9 (D3 deferral):** `perception_source=slide_id` stays; do NOT promote to element-reference (P2-4).

## D2 — not-covered / low-confidence (no silent brief-fallback)
Per-slide, perception is either authoritative (covered + above confidence threshold) OR routes to an explicit detector-visible **"UNVERIFIED — no perceived authority"** token. The brief NEVER occupies the authority position. No third "blend with brief" mode. Record each grounding decision's source (`perceived-high | perceived-low | unverified`). Test: a slide with no perception artifact → the detector fires (or the abstention token is asserted present), NOT a brief-grounded `$5.2T`.

## Scope fence (AC-7)
P2-1 detector unchanged + stays green; P2-2 schema unchanged; NO `reading_path`/scan-order (P2-4); `_assert_narration_joins_roster` slide_id join preserved.

## Verification battery (T1–T10)
Focused irene suite + new grounding/mutation tests green; P2-1 detector suite green; manifest-payload contract pins the new projection edge; lockstep L1 exit 0; frozen-pack-SHA unchanged; lint-imports 0-broken; ruff clean; sandbox-AC validator PASS; `git diff --check` clean. Re-pin the cache-prefix stability fixture deliberately. Completion Notes carry: the A3 mutation table, the A7 baseline-diff attestation, and the A4 headless-detector confirmation.
