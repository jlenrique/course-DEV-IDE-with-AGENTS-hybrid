# Codex Dev Prompt — Pass-2 Chosen-Variant Figure-Citation Gate (`pass2-figure-citation-gate`)

**Cycle:** NEW CYCLE — you (Codex) run **T1–T10** (implement + self-review). Claude runs **T11** (bmad-code-review + party CLOSE + commit + flip done). Do NOT flip story status, do NOT commit final — hand back a review doc.
**Spec (authoritative):** `_bmad-output/implementation-artifacts/spec-pass2-figure-citation-gate.md`. Read it fully first; this prompt is the operational driver.
**Branch:** `fidelity-perception-arc-2026-06-19` (work in place; the worktree has by-design untracked `runs/<uuid>/` + a modified `claude-goal.txt` — DO NOT touch or revert those; they are ambient, not yours).
**Tooling:** `./.venv/Scripts/python.exe`, `./.venv/Scripts/ruff.exe`, `./.venv/Scripts/lint-imports.exe`, `pytest`. Run freely. No `--no-verify`, no force-push, no mocks.

---

## Mission (one sentence)

Stop Irene Pass-2 from citing figures that are absent from the **chosen variant's** rendered perception (the variant-B figure-as-prose case), via a deterministic figure-citation gate that shares ONE figure-extractor with the load-bearing G5 detector — **without relaxing G5**.

## Why (the bug, concretely)

Per-slide A/B variant selection ships. Variant B's blueprint aesthetic re-renders quantitative content as PROSE, so B's `PerceptionArtifact` has NO figures. The G5 fidelity detector (`app/specialists/quinn_r/fidelity_detector.py:90`) correctly fails when `narration_figures ⊄ perceived_figures`. When B is picked for a figure-bearing slide, Irene sometimes still cites the source figure (RED witness: run `8553ab38` cited "18%" → `quinn_r.g5.fidelity-figure-contradiction` error-pause). **Likely leak (VERIFY, don't assume):** `_payload_section_for_prompt` (`app/specialists/irene/graph.py:333`) redacts brief visual content only for UNVERIFIED slides — so for a verified B slide the source figure is still in the `## Envelope payload` prompt tail (from `gary_slide_output`/`slide_briefs`), where the model can grab it.

## Substrate map (exact refs)

- `app/specialists/quinn_r/fidelity_detector.py` — `_FIGURE_RE` (18), `_figures` (178), `_normalize_figure` (182), used by `detect_fidelity` (54) at line 90. **EXTRACT these three into a shared module; G5 re-imports them behavior-preserving.**
- `app/specialists/irene/graph.py` — `_act_pass_2` (743; post-checks called at 780–781), `_assemble_pass_2_prompt` (565), `_payload_section_for_prompt` (333), `_redact_unverified_payload` (354), `_slide_roster` (145), `_perception_artifacts_by_slide` (213), `_visual_authority_for_slide` (263). Existing tagged-error pattern: `Pass2GroundingError(..., tag="irene.pass2.X")`.
- `app/marcus/orchestrator/production_runner.py:1248` — `_RETRYABLE_DISPATCH_TAGS`. **DO NOT add any tag here** (option (b) is deferred; its own comment warns the net is for variance, not deterministic defects).
- Import contracts: `pyproject.toml [tool.importlinter]`. No contract forbids `app.specialists.{quinn_r,irene}` importing a neutral `app.specialists._shared`. Confirm `lint-imports` stays **15 kept / 0 broken** after adding the shared module.

## Build sequence (RED-first; follow in order)

**T1 — read.** The T1 readings in the spec §0. Confirm the leak hypothesis by printing the assembled Pass-2 prompt for a verified figure-free slide and grepping for the brief figure.

**T2 — shared extractor (no-drift).** Create `app/specialists/_shared/figure_tokens.py` (new package + `__init__.py` if needed) containing `FIGURE_RE`, `figures(text) -> set[str]`, `normalize_figure(str) -> str` — moved verbatim from `fidelity_detector.py` (preserve the bare-`$5` vs `$5 trillion` magnitude discipline + `%`/`x` handling EXACTLY). Re-point `fidelity_detector.py` to import them. **Run `pytest tests/specialists/quinn_r -q -p no:randomly` → MUST stay green unchanged (AC-5).** `lint-imports` clean.

**T3 — RED-first witness test (AC-1).** Add `tests/specialists/irene/test_pass2_figure_citation_gate.py`. Build a REAL-shaped fixture: a verified (`coverage="perceived"`, `confidence="HIGH"`) figure-free `PerceptionArtifact` for a slide, an envelope payload whose `gary_slide_output`/`slide_briefs` carry `18%`, and a narration segment citing `18%`. Assert the PRE-fix failure mode (figure present in assembled prompt tail; citing narration NOT caught by Irene's current post-checks). Run → confirm RED.

**T4 — output-side post-check (a.2 / AC-3/AC-4).** Add `_assert_figure_citations_within_perceived(parsed, slide_roster, perception_by_slide)` and call it in `_act_pass_2` right after `_assert_reading_path_conformance` (line 781). Per segment: `offending = figures(narration_text) - figures_of(chosen_variant_perception[slide_id])`; if non-empty raise `Pass2GroundingError(f"slide {sid} narration cites figures absent from chosen-variant perception: {sorted(offending)}", tag="irene.pass2.figure-contradiction")` (scope narration). Use the perceived-figure set derived from the SAME perception the roster/authority block uses. Passes when citations ⊆ perceived OR no figures cited (paraphrase — AC-4). Green AC-3/AC-4.

**T5 — input-side redaction (a.1 / AC-2).** Generalize `_payload_section_for_prompt`/`_redact_unverified_payload`: for EVERY slide, strip from the brief/`gary_slide_output`/`slide_briefs` rows any figure token (via `figure_tokens.figures`) NOT in that slide's chosen-variant perceived-figure set. Leave perceived figures intact (A slides untouched). Keep the existing UNVERIFIED full-redaction behavior as a superset. Green AC-1 (full)/AC-2.

**T6 — regression + hygiene (AC-6/AC-7).** Full `pytest tests/specialists/irene tests/specialists/quinn_r -q -p no:randomly`; `ruff` clean on touched files; `lint-imports` 15/0. If a Pass-2 prompt byte-stability fixture (NFR-I6) exists, re-pin it deliberately with a one-line code comment (redaction changes prompt bytes for figure-leak slides by design — AC-7). Confirm via `git diff --name-only` that NO block-mode trigger path is touched (no pipeline-manifest, workflow_runner.py, run_hud.py, progress_map.py, v4.2 pack, generators/v42).

**T7–T9 — harden.** Edge cases: multiple figures per segment; `$`/`%`/`x` mix; a slide with NO perception artifact (must still behave per existing UNVERIFIED path); empty narration; A-slide-with-figures passes untouched. Ensure the gate keys on the chosen variant's perception (post per-slide selection), not the brief.

**T10 — self-review + handoff.** Write `_bmad-output/implementation-artifacts/_codex-handoff/pass2-figure-citation-gate-ready-for-review.md` containing: per-AC evidence; the exact RED→GREEN diff for AC-1; **baseline-diff attestation** (quinn_r suite byte-unchanged green; the AC-1 test was RED pre-fix); full-battery output; `lint-imports`/`ruff` results; the re-pinned byte-stability note if any; and a confirmation that `_RETRYABLE_DISPATCH_TAGS` and all block-mode trigger paths are UNTOUCHED. List any judgment calls for Claude's T11.

## Hard fences

- **Do NOT relax or alter G5 enforcement** — only the behavior-preserving extractor refactor touches `fidelity_detector.py`.
- **Do NOT add anything to `_RETRYABLE_DISPATCH_TAGS`** (option (b) is deferred pending a live experiment).
- No mocks; RED-first fixtures use real-shaped recorded perception/narration. No `--no-verify`, no force-push, no story-status flip, no final commit (Claude T11 owns those). Additive non-regression: P2-1/2/3/4a + reading-path + per-slide-variant suites stay green.
- If you discover the leak hypothesis is WRONG (figure not in prompt; failure is pure sampling variance), STOP and surface it in the handoff doc — do not silently re-scope; the output-side post-check (a.2) still ships, but flag that (a.1) may be a no-op and the experiment (Claude T11/§5) becomes load-bearing.
