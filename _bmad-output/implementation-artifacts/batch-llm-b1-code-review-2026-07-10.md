# Code review — batch-llm-b1-runtime-adapter (2026-07-10)

**Gate:** single-gate `bmad-code-review`  
**Layers:** Blind Hunter | Edge Case Hunter | Acceptance Auditor (independent subagents)  
**PM path check:** John GO-WITH-AMENDMENTS on B1→B2→B6-land sequence

## Layer verdicts

| Layer | Verdict |
| --- | --- |
| Blind Hunter | PASS-WITH-FIXES |
| Edge Case Hunter | PASS-WITH-FIXES |
| Acceptance Auditor | PASS |

## MUST-FIX folded

1. Empty `batch_id` → fail-loud `llm_batch.submit.missing-id` before receipt write
2. `join_completed_output` merges `error_file_id` rows with output rows
3. AST anti-`batch_completion` asserts Call + Attribute hits
4. Duplicate `custom_id` → `llm_batch.join.duplicate-custom-id`
5. Non-numeric `status_code` → row failed (no join abort)
6. Missing `custom_id` → fail-loud (no silent drop)
7. `_coerce_file_bytes` handles `str` from `.read()`

## Post-fix validation

`pytest tests/runtime/llm_batch/ -q` → **29 passed**; ruff clean.

## Final gate verdict

**CLOSE B1 as done** (scaffold claim fence intact).

## John sequence (binding for next)

B1 done → create-story B2 (OFF non-interference MUST) → B6-land (default realtime; T7) → B3+B4 only before B6-promote. Party not required again for B6-land done-bar; party/Murat before promote.
