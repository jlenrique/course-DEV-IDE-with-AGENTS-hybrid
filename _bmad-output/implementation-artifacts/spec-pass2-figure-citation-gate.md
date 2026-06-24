# Spec — Pass-2 Chosen-Variant Figure-Citation Gate (fix `pass2-narration-must-ground-to-chosen-variant-figures`, option (a))

**Status:** ✅ DONE — Codex T1–T10 → Claude T11 → party-mode CLOSE 3/3 (Murat/Winston/Amelia, no impasse) 2026-06-24. Fix (a) landed; the live N≥15 0-contradiction experiment remains the pre-B-heavy-trial gate (deferred-inventory). 4 non-blocking rider follow-ons filed.
**Story key:** `pass2-figure-citation-gate`
**Author:** Claude (pre-author), 2026-06-24
**Party-mode authority:** disposition recorded in `deferred-inventory.md` (Murat/Winston/Amelia/Mary, CONSENSUS green-with-named-dissent 2026-06-24).
**Velocity tags:** `r_tier=R2` · `t11_tier=standard` · `lookahead_tier=1` · `files_touched≈5`
**Gate mode:** single-gate (focused fidelity-hardening; touches NO block-mode trigger path → no pack/manifest regen).

---

## 0. T1 Readings (dev agent reads BEFORE any code)

- `app/specialists/quinn_r/fidelity_detector.py` — the **load-bearing G5 detector**. `detect_fidelity` line 90 already enforces `narration_figures ⊆ perceived_figures` per slide via `_figures()` over the **chosen variant's** perception artifact. The figure tokens (`_FIGURE_RE`, `_figures`, `_normalize_figure`) are the SHARED truth this story extracts. **G5 is correct; do NOT relax it.**
- `app/specialists/irene/graph.py` — `_act_pass_2` (line 743), `_assemble_pass_2_prompt` (565), `_payload_section_for_prompt` (333) + `_redact_unverified_payload` (354), `_slide_roster` (145) + `_perception_artifacts_by_slide` (213), `_visual_authority_for_slide` (263), the existing deterministic post-checks `_assert_narration_joins_roster` + `_assert_reading_path_conformance` (called at 780–781).
- `app/marcus/orchestrator/production_runner.py` lines 1245–1257 — `_RETRYABLE_DISPATCH_TAGS` + the comment that explicitly warns the net is for VARIANCE, not deterministic defects. **This is why option (b) is OUT of scope here.**
- `docs/dev-guide/dev-agent-anti-patterns.md` (H1–H4 believed-green family) + `docs/dev-guide/pydantic-v2-schema-checklist.md` (if any model touched — none expected).
- `tests/specialists/quinn_r/test_fidelity_detector.py`, `tests/specialists/quinn_r/test_quinn_r_g5_perception_enforcement.py`, `tests/specialists/irene/test_irene_pass2_perceived_visual_authority.py`, `tests/specialists/irene/test_irene_pass2_grounding_fail_loud.py` — the fixture/assertion style to mirror.

## 1. Problem (the filed caveat)

Genuine per-slide A/B variant selection ships. Variant **A** renders quantitative content as DATA CHARTS (figures present in the rendered PNG → present in the chosen-variant `PerceptionArtifact`). Variant **B**'s blueprint/lineArt aesthetic re-renders the SAME content as PROSE (figures ABSENT from B's perception). The G5 detector requires `narration_figures ⊆ perceived_figures`. So when **B is the picked variant for a figure-bearing slide**, Irene Pass-2 must ground to B's figure-FREE perception and NOT cite the source figure. She did reliably on the 2nd live mirror run but NOT its first attempt (cited "18%" → `quinn_r.g5.fidelity-figure-contradiction` error-pause). **RED witness: run `8553ab38`.** The pass is partly grounding VARIANCE, not a deterministic guarantee.

**Likely contributing root cause (the dev agent MUST verify, do not assume):** `_payload_section_for_prompt` redacts brief visual content only for **UNVERIFIED** slides (`_redact_unverified_payload`). For a **verified B slide**, the source figure (e.g. "18%") still sits in the demoted `## Envelope payload` tail (from `gary_slide_output`/`slide_briefs`), so the model can ground on a figure absent from the chosen variant's perception. The perceived-authority block for B is figure-free, but the brief figure is still in the prompt → leak. This is the sibling of the struck [[pass2-envelope-payload-brief-unframed-in-prompt-tail]] (which closed the UNVERIFIED case only).

## 2. Fix — option (a): a deterministic chosen-variant figure-citation gate

Two complementary deterministic mechanisms, both reusing ONE shared figure-extractor (no drift with G5). This GATES THE CITATION SET, never the prose/paraphrase (Amelia's named dissent honored: paraphrase that cites no raw figure has an empty figure-set → trivially a subset → never false-fails).

**(a.1) Input-side prevention (the ratchet at the neck — Winston).** Extend the Pass-2 payload redaction so that, for EVERY slide (not just UNVERIFIED), figure tokens present in the demoted brief/`gary_slide_output`/`slide_briefs` but **absent from that slide's chosen-variant perceived-figure set** are redacted from the assembled prompt's envelope-payload tail. Legitimate perceived figures (A slides) are untouched — they live in the perceived-authority block, which is never redacted. Removes the leak SOURCE.

**(a.2) Output-side fail-loud post-check (the backstop — mirrors G5, at the source specialist).** Add `_assert_figure_citations_within_perceived(parsed, slide_roster, perception_by_slide)` in `_act_pass_2` immediately after `_assert_reading_path_conformance` (line 781). For each narration segment, using the SHARED extractor: `offending = narration_figures - perceived_figures(slide_id)`. If non-empty → raise a tagged `IreneActError`/`Pass2GroundingError` with tag **`irene.pass2.figure-contradiction`**, scope `narration`, naming the offending figures + slide_id. Caught BEFORE G5, at Irene.

**Shared extractor (a.3 — no-drift requirement).** Extract `_FIGURE_RE`, `_figures`, `_normalize_figure` from `quinn_r/fidelity_detector.py` into a NEUTRAL shared module (recommend `app/specialists/_shared/figure_tokens.py`; confirm import-linter clean — no contract forbids `app.specialists.quinn_r` or `app.specialists.irene` importing a neutral `app.specialists._shared`). G5 re-points its imports to the shared module **behavior-preserving** (existing quinn_r figure tests stay byte-green). Irene's gate imports the SAME functions → Irene's gate and G5 can never disagree on "what is a figure."

### Explicitly OUT of scope (deferred, per party consensus)
- **(b)** Adding `irene.pass2.figure-contradiction` (or `quinn_r.g5.fidelity-figure-contradiction`) to `_RETRYABLE_DISPATCH_TAGS`. **Deferred** pending the discriminating experiment (§5). Until then a residual contradiction is a loud, recoverable error-pause (Murat: "ship loud"). When/if added later it MUST be counted/logged/bounded (never silent).
- **(c)** Treatment-template policy (figure-bearing slides offer figure-preserving variants only) — product/scope decision, party-gated, separate story.
- **No change to the G5 detector's enforcement** (only the behavior-preserving extractor refactor).

## 3. Acceptance Criteria

- **AC-1 (RED-first, the witness).** A RED-first test reproduces the `8553ab38` scenario: a **verified** slide whose chosen-variant `PerceptionArtifact` is figure-free, with a brief carrying a figure (e.g. `18%`), and a narration segment citing `18%`. PRE-fix: the test proves the figure reaches Irene's prompt tail AND/OR a citing narration passes Irene's post-checks (i.e. only G5 would catch it). POST-fix: (a.1) the figure is absent from the assembled prompt for that slide, and (a.2) a narration citing `18%` raises `irene.pass2.figure-contradiction`. Use a REAL recorded figure-free perception shape (no fabricated API mock).
- **AC-2 (input-side redaction).** `_assemble_pass_2_prompt` output contains NO brief figure token absent from a slide's chosen-variant perceived-figure set, for verified AND unverified slides. Perceived figures (A-slide case) remain present. Pinned by a test asserting presence/absence per slide.
- **AC-3 (output-side post-check).** `_assert_figure_citations_within_perceived` raises `irene.pass2.figure-contradiction` (scope=narration, names offending figures+slide_id) when a segment cites a figure outside the chosen-variant perceived set; passes silently when citations ⊆ perceived OR when the segment cites no figures (paraphrase). Boundary tests: bare `$5` vs `$5 trillion` not conflated (reuse the shared normalizer's existing magnitude discipline); `%`/`x` tokens handled.
- **AC-4 (no false-fail on legitimate latitude — Amelia).** A narration that conceptually describes the trend WITHOUT citing a raw figure (e.g. "burnout keeps climbing") passes the gate even on a figure-free B slide. A narration citing a figure that IS in the chosen-variant perception (A slide) passes.
- **AC-5 (shared extractor / no drift).** G5's figure-extraction behavior is byte-identical pre/post refactor (existing `test_fidelity_detector.py` + `test_quinn_r_g5_perception_enforcement.py` stay green unchanged). Irene's gate and G5 import the same `figure_tokens` functions. A test asserts the two produce identical figure-sets on a shared sample.
- **AC-6 (no-regression).** Full Irene suite + quinn_r suite green; `lint-imports` clean (15 kept / 0 broken — confirm the new shared module introduces no broken contract); `ruff` clean on touched files. No block-mode trigger path touched → no pack/manifest regen, no lockstep run required (assert via diff: none of `state/config/pipeline-manifest.yaml`, `*workflow_runner.py`, `run_hud.py`, `progress_map.py`, v4.2 pack, generators/v42 in the change set).
- **AC-7 (cache/byte-stability).** The Pass-2 prompt remains deterministic (no datetime/UUID/random). If the NFR-I6 byte-stability fixture for the assembled prompt exists, re-pin it deliberately with a one-line note (the redaction changes prompt bytes by design for figure-leak slides).

## 4. Build contract / sequencing

1. Extract `figure_tokens` shared module; re-point G5 (behavior-preserving) → run quinn_r tests GREEN (AC-5).
2. RED-first: write AC-1 failing test against current substrate → confirm it RED.
3. Implement (a.2) output-side post-check in `_act_pass_2` → AC-1/AC-3/AC-4 green.
4. Implement (a.1) input-side redaction extension in `_payload_section_for_prompt`/`_redact_unverified_payload` (generalize from UNVERIFIED-only to figure-leak-aware) → AC-1/AC-2 green.
5. Full battery + lint-imports + ruff (AC-6); re-pin byte-stability if needed (AC-7).
6. **Codex self-review (T10):** baseline-diff attestation MANDATORY (per Mary's NEW CYCLE rule) — confirm the failing tests pre-existed the fix and the quinn_r suite is unchanged-green.

## 5. T11 + pre-B-heavy-trial validation (Claude, NOT Codex)

- **T11:** `bmad-code-review` (3-layer) + reproduce the full deterministic battery + party-mode CLOSE + commit + flip done + push.
- **Discriminating experiment (the party's binding pre-B-heavy-trial gate — Murat+Mary):** before any B-heavy/2-variant non-demo trial, run **N≥10–15 forced B-on-figure-bearing-slide live runs** on the current substrate, inspecting Pass-2's context (is the source figure in the prompt on RED draws?) and counting the post-(a) figure-contradiction rate. **Exit = 0 contradictions across ≥15 post-(a) forced runs** (Mary). If a low irreducible floor remains → reactivate option (b) as a counted/bounded net. This experiment is a SEPARATE live-validation leg (Claude may run it via a fresh independent subagent under the strict validity protocol; first-run-stands; no retry-to-green); it is NOT part of Codex's T1–T10 unit work.
- **Not a blocker for the next SINGLE-variant trial** — carry forward as the named/bounded/witnessed/triggered risk already filed.

## 6. Hard fences

- No mocks (RED-first fixtures use REAL recorded perception/narration shapes; no fabricated API substrate). The G5 detector is untouched in enforcement. No `--no-verify`, no force-push. Additive non-regression: P2-1/2/3/4a stay green. RED-first against `8553ab38` is MANDATORY. Baseline-diff attestation in the Codex handoff.
