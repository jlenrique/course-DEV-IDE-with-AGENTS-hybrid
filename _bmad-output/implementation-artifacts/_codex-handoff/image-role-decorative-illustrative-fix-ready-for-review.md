# Image Role Decorative/Illustrative Fix Ready for Review

Date: 2026-06-23

## Scope

Executed the canonical image-role decorative-vs-illustrative remediation for the LLM-primary reading-path classifier.

Canonical instruction source:

- `_bmad-output/implementation-artifacts/codex-dev-prompt-image-role-decorative-illustrative-fix.md`

## Implementation Summary

- Tightened the LLM-primary prompt rubric for image_role tier 1 vs tier 2:
  - Tier 1 is decorative/evocative, including rich prominent full-bleed photos or illustrations when they have no internal labels/text, are not technical/instructional, and slide text does not depend on them.
  - Tier 2 is illustrative only when the slide text explicitly depends on what the image depicts, names it, compares against it, or the image visibly substantiates the claim.
  - Tier 3 and tier 4 remain instructional and pointer/iconographic respectively.
  - If uncertain between tier 1 and tier 2, the prompt now directs the model to choose tier 1.
  - When any image element exists, the prompt tells the model not to return null image_role.
- Added dominant-image fallback:
  - If the LLM returns null image_role and at least one image-like element exists, the classifier assigns `dominant_image_role` from the largest image element's existing tier.
- Added deterministic decorative boundary:
  - If the LLM returns tier 2 or 2_5 for the dominant role, a plain photo/illustration with no internal labels and no caption is demoted to tier 1.
  - Charts, tables, diagrams, small icons, logos, and captioned evidence retain their stronger roles.
- Added focused tests for:
  - Prompt rubric language.
  - Null image_role fallback to largest image tier.
  - Plain mood photo demotion from tier 2 to tier 1.
  - Captioned chart retention of tier 2_5.

## Measurement

Subject: `llm-primary reading-path classifier`

Substrate: `frozen fresh@2026-06-23 role_tier-aware perceptions`

Gold SHA256:

- `56473484F1D296C04D5A569865B8C6D5EE296FB55AB0AC193BAF6B9EB3DE20A8`

Final live report:

- `_bmad-output/implementation-artifacts/reading-path-holdout-rescan-2026-06-23/llm-primary-reading-path-measurement.json`

Final report SHA256:

- `80F8141FB8B8ADB83B86F56D5147CFEED5942E6FC1281038386E9DDAC196A8C0`

## Before / After

Before, from the prior LLM-primary remediation report used as this cycle's baseline:

| Metric | Before |
| --- | ---: |
| primary-key top-1 | 0.500 |
| full-tuple | 0.357 |
| macro_layout | 0.857 |
| image_role | 0.643 |
| text_substructure | 0.929 |
| narration_cadence | 0.857 |
| degraded_rows | 0 |
| hard_blocks | 0 |

After, from the final live measurement:

| Metric | After |
| --- | ---: |
| classified_ok | 14/14 |
| scored_slides | 14/14 |
| primary-key top-1 | 0.714 |
| full-tuple | 0.429 |
| macro_layout | 0.857 |
| image_role | 0.857 |
| text_substructure | 0.929 |
| narration_cadence | 0.786 |
| degraded_rows | 0 |
| hard_blocks | 0 |

## Acceptance Status

- Met: image_role target `>= 0.85` with final `0.857`.
- Met: degraded rows remained `0`.
- Met: hard blocks remained `0`.
- Missed: primary-key target `>= 0.78`; final was `0.714`.
- Missed: overall `0.85` primary-key target remains unmet.
- Watch item: narration_cadence changed from `0.857` baseline to `0.786` on the final live run.

This remediation is ready for review, but it is not a full green acceptance pass because the primary-key target remains below threshold.

## Validation

Ruff:

```powershell
.venv\Scripts\python.exe -m ruff check scripts\utilities\reading_path_classifier.py tests\specialists\vision\test_reading_path_classifier.py
```

Result:

- All checks passed.

Focused tests:

```powershell
.venv\Scripts\python.exe -m pytest tests\specialists\vision\test_reading_path_classifier.py tests\specialists\vision\test_image_role_tiers.py tests\analysis\test_reading_path_p2_4b_run.py tests\analysis\test_reading_path_p2_4b_score.py
```

Result:

- 70 passed.

Live measurement:

```powershell
.venv\Scripts\python.exe scripts\analysis\reading_path_p2_4b_measure_fresh.py
```

Result:

- Classified 14/14.
- Scored 14/14.
- `primary_key_top1 = 0.714`.
- `image_role = 0.857`.
- `degraded_rows = 0`.
- `hard_blocks = 0`.

## Baseline-Diff Attestation

- No slide-id special casing was added.
- No gold keyed lookup was added.
- No prompt pack or manifest edits were made for this remediation.
- The frozen gold file was not modified.
- Existing dirty worktree state from earlier LLM-primary remediation was preserved.
- `claude-goal.txt` was already dirty before this remediation and was not touched.
