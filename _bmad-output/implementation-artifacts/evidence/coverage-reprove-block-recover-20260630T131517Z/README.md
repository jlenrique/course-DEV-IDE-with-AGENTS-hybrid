# Coverage interlock re-prove — BLOCK arm (REWIND-RECOVER)

- Verdict: **PASS**
- method: rewind-recover of a COPY of golden run 8d819b8d (golden untouched)
- copy trial_id: 1e385fd0-e230-417c-a824-8ea17c5a2744
- run_dir: C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid\state\config\runs\1e385fd0-e230-417c-a824-8ea17c5a2744
- re-entry: node 07D.5 (idx 29); dropped motion_planner@07D.5 empty-plan contribution
  so the fixed 0-credit motion floor re-fires -> kira (07E) clears -> reach G3.
- final_status: paused-at-error
- paused_error_tag: marcus.coverage.must-cover-uncovered
- error_pause node_id: 11
- total_seconds: 1144.0
- timeout patch: make_chat_model=True ChatOpenAI=True (per-request 900.0s, max_retries=0)
- ablation deck dropped: ['slide-01']
- ablation narration dropped: ['slide-01']
- missing+must_cover rows: 13
- mp3 files in run_dir: 0 (must be 0)
- no fresh gpt-5 extraction (g0-enrichment reused from copy)
- checks: {"status_is_paused_at_error": true, "error_tag_is_coverage": true, "receipt_exists": true, "has_missing_must_cover_row": true, "zero_mp3_audio": true, "zero_wav_audio": true, "no_walk_error_or_coverage_pause": true}

Gate sequence walked after recover: ['G3', 'G4']
