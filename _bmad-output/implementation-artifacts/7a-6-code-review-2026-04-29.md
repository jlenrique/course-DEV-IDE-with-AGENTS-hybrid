# Story 7a.6 Code Review — Vocabulary Registry + Operator-Control Parity Table

**Reviewer:** Claude Opus 4.7 (final code-review under new cycle).
**Reviewed:** 2026-04-29 against working tree post-Codex T1-T10.
**Codex self-review:** `_bmad-output/implementation-artifacts/7a-6-codex-self-review-2026-04-29.md` (PASS-WITH-NOTES).

## Verdict

**PASS.** No PATCH items. 1 NOTE (spec-vs-implementation path; Codex deviation is structurally correct). Story is ready to flip done.

## Triage Summary

| Disposition | Count |
|---|---:|
| PATCH | 0 |
| DEFER | 0 |
| DISMISS | 1 |
| NOTE (acceptable Codex deviation) | 1 |

## Layer Findings

### Layer 1 — Blind Hunter

| ID | Severity | Disposition | Finding | Evidence |
|---|---|---|---|---|
| BH-1 | NOTE | ACCEPTABLE | Codex's vocabulary loader lives at `app/models/decision_cards/vocabulary.py` (a package module) instead of the spec's literal `app/models/decision_cards.py` (single file). | `app.models.decision_cards` already existed as a package with `g1.py`, `g2c.py`, `g3.py`, `g4.py`, `base.py`, `override_event.py`. The spec's single-file path would have collided. Codex made the right structural call: created the new module under the existing package, exported the new symbols (`SpecialistId`, `GateDecisionToken`, `GateDirectiveToken`, `EscapeCardOption`, `VocabularyDecisionCard`) from `app.models.decision_cards` package init for downstream consumers. **Documented in Codex self-review line 6-9.** |
| BH-2 | LOW | DISMISS | Codex notes a 7a.1 editor fallback test fails on environments without `vi` on PATH. | Same finding as 7a.2; out of 7a.6 scope. |

### Layer 2 — Edge Case Hunter

All edge cases per Codex self-review verified independently:
- Unknown decision/directive tokens → Pydantic ValidationError ✓
- Extra fields → ValidationError via `extra="forbid"` ✓
- Rationale <20 chars → ValidationError + JSON Schema `minLength: 20` ✓
- Glossary + JSON Schema sync checks operational ✓

### Layer 3 — Acceptance Auditor

All 10 ACs (A-J) PASS at acceptance-auditor layer per Codex self-review. Independently verified:

| AC | Verdict | Independent verification |
|---|---|---|
| A — Vocabulary registry artifact | PASS | `docs/conversational-gates/_registry/vocabulary.yaml` has 3 namespaces + schema_version "1.0". |
| B — Pydantic enum loader + four-file-lockstep | PASS | `vocabulary.py` + `decision_cards.schema.json` + golden fixture + shape-pin tests all present. |
| C — Operator-control parity table | PASS | `docs/operator/legacy-vs-langgraph-control-parity.md` has exactly 33 numbered rows + parity_test_id column. |
| D — Parity-test suite | PASS | `tests/parity/test_operator_control_parity.py` has exactly 33 `def test_row_NN_*` functions (verified via `grep -c "^def test_row_"`). |
| E — 11-specialist build assertion | PASS | Module-level `assert len(SpecialistId) == 11` at import time; verified via `python -c "from app.models.decision_cards.vocabulary import SpecialistId; print(len(list(SpecialistId)))"` → 11. |
| F — AST scan for ad-hoc tokens | PASS | `tests/structural/test_no_ad_hoc_vocabulary_tokens.py` exists; clean baseline + injected fake-token negative case both verified. |
| G — Auto-generated glossary | PASS | `docs/conversational-gates/_registry/glossary.md` auto-emitted; CI sync-check pinned. |
| H — Composition Spec §3.6/§11 | PASS | Additive only; no §11 trigger fires; no §10 entry needed. |
| I — N-item / anti-pattern trace | PASS | N1/N2/N4/N10 honored; N9 PASS-PENDING-OPERATOR. |
| J — D12 close protocol | HANDOFF-TO-CLAUDE | Claude executes the close steps. |

## Independent Verification Battery

```
.venv/Scripts/python.exe -m pytest tests/unit/models tests/parity tests/structural -q --tb=short
→ 287 passed, 19 skipped in 5.42s

.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
→ exit 0

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-6-vocabulary-registry-parity-table.md
→ PASS

.venv/Scripts/python.exe -c "from app.models.decision_cards.vocabulary import SpecialistId; print(len(list(SpecialistId)))"
→ 11

grep -c "^def test_row_" tests/parity/test_operator_control_parity.py
→ 33

grep -c "@pytest.mark.skip" tests/parity/test_operator_control_parity.py
→ 19 (placeholders awaiting Slab 7a/7b activations; expected per AC-7.6-D)
```

## Composition Spec §11 Trigger Check

**Verdict:** no trigger fires.

- No fan-out / parallel dispatch (Trigger 1 N/A).
- No partial state mid-execution (Trigger 2 N/A).
- No gate precedence promotion (Trigger 3 N/A).
- No adapter LOC change (Trigger 4 N/A).
- No new `_act` body category (Trigger 5 N/A).
- No §10 entry needed (vocabulary registry is data + Pydantic schema; not substrate evolution).

## Close Action

Claude flips `migration-7a-6-vocabulary-registry-parity-table` review → done in BOTH the spec file + sprint-status.yaml. No remediation cycle needed. Commit + continue.
