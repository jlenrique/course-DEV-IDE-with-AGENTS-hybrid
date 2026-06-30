# Coverage interlock re-prove — COVERED arm (REWIND-RECOVER, NO ablation)

- Verdict: **PASS**  (bar: NON-VACUOUS receipt with >=1 genuinely-joined-COVERED must-cover point)
- method: rewind-recover of a COPY of golden run 8d819b8d (golden untouched)
- copy trial_id: a62187ec-e1bd-40fe-a656-d51dd170aba7
- run_dir: C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid\state\config\runs\a62187ec-e1bd-40fe-a656-d51dd170aba7
- figure-token fix in tree: 5ba2716d
- re-entry: node 07D.5 (idx 29); dropped motion_planner@07D.5 empty-plan contribution
  so the fixed 0-credit motion floor re-fires -> kira (07E) clears -> reach G3 -> DERIVE.
- NO ablation (covered arm).
- final_status: paused-at-error
- paused_error_tag: marcus.coverage.must-cover-uncovered
- total_seconds: 1157.0
- no fresh gpt-5 extraction (g0-enrichment reused from copy)

## Receipt breakdown
- rows: 13
- coverage_status counts: {"missing": 12, "covered_on_slide": 1}
- vouch_level counts: {"not_assessed": 13}
- joined-covered rows (anchor_resolved AND status in {both,covered_on_slide,covered_in_narration}): 1
- missing + must_cover rows: 12

## Gate outcome
- BLOCK (>=1 must-cover figure dropped -> blocked before enrique/audio)
- gate blocked on coverage: True
- real-audio mp3 (>0 bytes): 0

## Checks
{
  "receipt_exists": true,
  "receipt_non_vacuous_n_rows>0": true,
  "has_joined_covered_row": true,
  "no_walk_error": true
}

Gate sequence walked after recover: ['G3', 'G4']
