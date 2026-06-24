# Pass2 figure citation gate ready for review

Date: 2026-06-24
Branch: `fidelity-perception-arc-2026-06-19`
Codex scope: T1-T10 only. No commit, no status flip.

Authority: `_bmad-output/implementation-artifacts/spec-pass2-figure-citation-gate.md`.

## Implementation summary

- Extracted Quinn-R's figure-token regex/normalizer into `app/specialists/_shared/figure_tokens.py`.
- Repointed Quinn-R G5 to the shared extractor without changing enforcement behavior.
- Added Irene Pass-2 prompt-side figure redaction:
  - verified slides keep only figures present in that slide's chosen-variant perceived authority;
  - unverified slides still get the existing full visual-row redaction;
  - stale figures are redacted from both the expected-plan region and the sorted envelope JSON tail.
- Added Irene output-side post-check `_assert_figure_citations_within_perceived(...)`, called after reading-path conformance and before output emission.
- Added tests for the `8553ab38`-class verified figure-free stale-brief leak, legitimate perceived figures, paraphrase latitude, `$5` vs `$5T` boundary discipline, and shared-extractor identity with G5.

## Baseline-diff attestation

- Opening worktree was dirty before Codex edits:
  - `claude-goal.txt`
  - `scripts/api_clients/__init__.py`
  - `skills/bmad-agent-desmond/scripts/refresh_descript_reference.py`
  - many untracked `runs/` artifacts plus Descript/variant-demo artifacts.
- Codex did not touch those unrelated files.
- Codex-owned changed paths:
  - `app/specialists/_shared/__init__.py`
  - `app/specialists/_shared/figure_tokens.py`
  - `app/specialists/irene/graph.py`
  - `app/specialists/quinn_r/fidelity_detector.py`
  - `tests/specialists/irene/test_irene_pass2_perceived_visual_authority.py`
  - this handoff file.
- The remaining Quinn-R full-suite failure is not in touched production/test paths:
  - `tests/specialists/quinn_r/test_fidelity_detector.py::test_perception_artifact_shape_pins_legacy_fields_and_coverage_enum`
  - Cause observed: `PerceptionArtifact.model_dump()` includes newer reading-path/image-role fields absent from that legacy pin.
  - Codex did not modify `app/models/perception/**` or `tests/specialists/quinn_r/test_fidelity_detector.py`.

## Validation

- Focused figure-gate battery:
  - `.\.venv\Scripts\python.exe -m pytest tests\specialists\irene\test_irene_pass2_perceived_visual_authority.py tests\specialists\irene\test_irene_pass2_grounding_fail_loud.py tests\specialists\quinn_r\test_quinn_r_g5_perception_enforcement.py tests\specialists\quinn_r\test_fidelity_detector.py -k "not perception_artifact_shape_pins_legacy_fields_and_coverage_enum"`
  - Result: `34 passed`.
- Full offline Irene suite:
  - `.\.venv\Scripts\python.exe -m pytest tests\specialists\irene -m "not llm_live"`
  - Result: `52 passed`.
- Full Irene suite including live tests:
  - `.\.venv\Scripts\python.exe -m pytest tests\specialists\irene`
  - Result: `52 passed, 1 failed`.
  - Failure: live LLM response omitted top-level `visual_references`, so existing `irene.pass2.slide-join-failed` fired before the new figure gate.
- Full Quinn-R suite:
  - `.\.venv\Scripts\python.exe -m pytest tests\specialists\quinn_r`
  - Result: `86 passed, 1 failed`.
  - Failure: ambient legacy `PerceptionArtifact` shape pin described above.
- Ruff:
  - `.\.venv\Scripts\ruff.exe check app\specialists\_shared\figure_tokens.py app\specialists\quinn_r\fidelity_detector.py app\specialists\irene\graph.py tests\specialists\irene\test_irene_pass2_perceived_visual_authority.py`
  - Result: `All checks passed!`
- Import-linter:
  - `.\.venv\Scripts\lint-imports.exe --config pyproject.toml`
  - Result: `15 kept, 0 broken`.
- Diff whitespace:
  - `git diff --check`
  - Result: exit 0; line-ending normalization warnings only.
- Block-mode trigger check:
  - Result: `NO_BLOCK_MODE_TRIGGER_PATHS_TOUCHED`.

## T11 notes

- No retryable dispatch tags were added; `irene.pass2.figure-contradiction` remains loud and deterministic.
- No G5 enforcement was relaxed.
- `uv run` is not usable in this worktree because editable build fails on flat-layout package discovery; `.venv` was used for verification.
