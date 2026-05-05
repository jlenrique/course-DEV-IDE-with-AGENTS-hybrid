# Codex dev-story prompt — Story 7c.5.G2C (G2C DecisionCard Extend-and-Audit; dual-gate-cross-agent-CONTRACT-EVOLUTION; standard T11)

**Cycle:** Claude spec (lookahead_tier=2) → Codex T0-T1 (frozen-hash pre-check + contract-diff + backward-consumer audit) → **PRE-T2 CROSS-AGENT REVIEW CHECKPOINT (Claude)** → Codex T2-T10 → drops `_codex-handoff/7c-5-g2c.ready-for-review.md` → Claude T11 standard → commit + flip done.
**Wave:** 2 — slot 10 (second per-gate extend-and-audit; G2C pre-composition QA migration).
**Pre-authored:** 2026-05-05.
**Dispatch state:** **HELD until G1 closes** (serial dispatch chain). AMELIA-P2 freshness check at dispatch-time.

**Special downstream impact:** This story's close is the trigger for AMELIA-P3 staggering on 4 Wave-3 stories (7c.9 / 7c.10 / 7c.11 / 7c.12; all G2C-aliased). Plan their dispatch sequence (≥30 min apart) ahead of G2C close.

---

```
Run bmad-dev-story on Story 7c.5.G2C (Slab 7c Wave 2 slot 10; dual-gate-cross-agent-CONTRACT-EVOLUTION; extend-and-audit; standard T11; SERIAL dispatch only).

Spec: `_bmad-output/implementation-artifacts/migration-7c-5-g2c-decision-card-extend-and-audit.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T0-T10 task structure with PRE-T2 CROSS-AGENT REVIEW CHECKPOINT).
2. **`_bmad-output/implementation-artifacts/migration-7c-5-g1-decision-card-extend-and-audit.md`** (predecessor extend-and-audit canonical pattern).
3. **`_bmad-output/implementation-artifacts/migration-7c-5-g1-contract-diff.md`** (canonical contract-diff structure to mirror).
4. **`_bmad-output/implementation-artifacts/migration-7c-5-g1-backward-consumer-audit.md`** (canonical audit per-call-site verdict shape).
5. **`_bmad-output/implementation-artifacts/7c-5-g1-t1-cross-agent-review-2026-05-05.md`** (canonical T1 review verdict; documents 2-class-regime compatibility surfaces already updated by G1 — your audit just verifies G2C is recognized).
6. `_bmad-output/implementation-artifacts/7c-5-g1-code-review-2026-05-NN.md` (G1 T11 verdict — once landed; document any patches affecting G2C).
7. `app/models/decision_cards/_base.py` (canonical `DecisionCardBase`).
8. `app/models/decision_cards/g2c.py` (LEGACY pre-extension; pre-extension SHA256 = `237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a`).
9. **`app/models/decision_cards/g1.py`** (POST-G1-close MIGRATED canonical extend-and-audit body; mirror its structure for G2C).
10. `app/models/decision_cards/g2a.py` (canonical fresh-author pattern; UUID4 + strip-then-non-empty validators).
11. `app/parity/contracts/tw_7c_3_firing.py` + `tests/structural/test_tw_7c_3_firing_spec_single_source.py`.
12. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G2C = pre-composition QA gate).
13. `docs/dev-guide/pydantic-v2-schema-checklist.md`.
14. Governance JSON `7c-5-g2c` (extend_and_audit_t1_deliverables binding=hard; downstream_dispatch_staggering_keyed for 7c.9/10/11/12).

## T0 PRE-T1 hard checkpoints (HALT-AND-SURFACE)

- 7c.4b done; G0/G2A/G5/G6 done; G1 done (committed; T11 PASS).
- `DecisionCardBase` + `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` importable.
- `app/models/decision_cards/_frozen_hashes.py` exists + contains `g2c` key with value `237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a` (landed at G1 close).
- 2-class-regime compatibility validators (compiler.py + dotted-ref-test + resume_api.py) already accept BOTH legacy `DecisionCard` AND new `DecisionCardBase` per G1 close. Verify post-G1-close state.
- Class-conformance baseline at T1: record observed (likely 16 if G1 closed; +1 increment expected for G2C).
- Broad-regression baseline: re-run at T1; record for T9 R3 delta.

## T0 — Frozen-hash pre-check (lighter than G1 because file already exists)

```bash
.venv/Scripts/python.exe -c "import hashlib; print(hashlib.sha256(open('app/models/decision_cards/g2c.py', 'rb').read()).hexdigest())"
.venv/Scripts/python.exe -c "from app.models.decision_cards._frozen_hashes import FROZEN_AT_SHIP_HASHES; print(FROZEN_AT_SHIP_HASHES['g2c'])"
```

Both MUST equal `237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a`. Mismatch → HALT-AND-SURFACE.

## T1 — Contract-diff + backward-consumer audit

Author both artifacts per spec AC-A. Mirror G1 structure exactly (the G1 contract-diff is the canonical reference). G2C-specific differences:
- Legacy G2CCard fields: `readiness_status: Literal["ready", "blocked"]`, `blocking_issues: list[str]`, `ready_nodes: list[str]` (preserve all three).
- **NEW field added:** `gate_focus: Literal["pre_composition_qa"]` — legacy G2CCard has NO gate_focus (unlike G1); spec contract-diff §4 must explicitly mark this as ADD.
- 2-class-regime compatibility: G1 already widened compiler.py + dotted-ref-test (+ possibly resume_api.py) to accept both regimes. G2C audit verifies G2CCard inherits-via-DecisionCardBase under those wider validators.

After both artifacts authored, drop `_codex-handoff/7c-5-g2c.t1-ready.md` notice. **HALT and await cross-agent T1 review verdict** at `_bmad-output/implementation-artifacts/7c-5-g2c-t1-cross-agent-review-2026-05-NN.md`.

## CROSS-AGENT T1 REVIEW CHECKPOINT (binding HALT)

Codex MUST NOT proceed to T2 until cross-agent reviewer drops PASS verdict.

## T2-T9 — Body extension + verification battery (POST-T1-PASS only)

T2: AMELIA-P4 verification + G2CCard rewrite. Inheritance change `DecisionCard` → `DecisionCardBase`. Re-declare per G2A canonical: card_id (UUID4), trial_id (UUID4), gate_id (Literal["G2C"]), created_at, verb, schema_version (Literal["v1"]). Preserve gate-specific: readiness_status (Literal["ready", "blocked"]), blocking_issues (list[str]), ready_nodes (list[str]). ADD `gate_focus: Literal["pre_composition_qa"]`. Drop legacy DecisionCard fields per AC-A contract-diff verdicts.

T3: Regenerate `app/models/decision_cards/schema/g2c.v1.schema.json` via Python file-write (NOT shell `>` redirection — see anti-pattern A18 in `docs/dev-guide/specialist-anti-patterns.md`; PowerShell `>` emits a UTF-8 BOM that breaks byte-for-byte schema-match in T6).

Canonical command (use this exact form):

```bash
.venv/Scripts/python.exe -c "from pathlib import Path; from app.models.decision_cards.g2c import G2CCard; import json; Path('app/models/decision_cards/schema/g2c.v1.schema.json').write_text(json.dumps(G2CCard.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
```
T4: Author g2c_golden.json (gate_id="G2C", gate_focus="pre_composition_qa", readiness_status="ready", etc.).
T5: Author shape-pin (9-10 tests including closed-enum on readiness_status). **MANDATORY guardrail #1 self-grep at T5.2.**
T6: Run R3 verification battery.

## PARALLEL-DISPATCH GUARDRAILS (binding even under serial dispatch — harvested from G0+G2A 2026-05-05 dual-Codex run)

(Same six rules as G1 prompt; #3 informational under serial dispatch.)

1. **AMEND-7d-i AST-scan compliance — MANDATORY T5.2 self-grep.** ZERO matches for `FOUR_FILE_GLOBS` / `all_four_present` outside bare `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` import lines.
2. **Pattern-replication discipline — read canonical sibling.** When in doubt, prefer reading post-G1-close `g1.py` (canonical extend-and-audit body) + `g2a.py` (canonical fresh-author shape) over re-interpreting spec.
3. **Shared-file integration ordering** (informational under serial dispatch). `__init__.py` flat-export already extended through G6; G2C just adds another union member. No coordination needed under serial dispatch.
4. **Pattern-parity ratchet (cosmetic — but apply at T2).** UUID4 typing + strip-then-non-empty validators on any non-empty-string field. (G2C has no string fields requiring strip-then-check; readiness_status is closed Literal; blocking_issues + ready_nodes are list[str] with default empty.)
5. **Class-conformance baseline arithmetic.** Under serial dispatch, +1 exactly. T1 records observed (likely 16 if G1 closed); T6.5 verifies T1-baseline + 1.
6. **Broad-regression baseline shift with per-failure attribution.** At T1, record post-G1-close baseline. At T9, delta ≤ 0; ≥1 new failure attributable to G2C is HALT.

## Files in scope

**New (4 files):**
- `_bmad-output/implementation-artifacts/migration-7c-5-g2c-contract-diff.md`
- `_bmad-output/implementation-artifacts/migration-7c-5-g2c-backward-consumer-audit.md`
- `tests/parity/test_decision_card_g2c_shape.py`
- `tests/fixtures/decision_cards/g2c_golden.json`

**Modified (3 files):**
- `app/models/decision_cards/g2c.py` — REWRITTEN
- `app/models/decision_cards/schema/g2c.v1.schema.json` — REGENERATED
- `app/models/decision_cards/__init__.py` — flat-export verified post-G6

**Codex-handoff dropbox files (2):**
- `_codex-handoff/7c-5-g2c.t1-ready.md` — PRE-T2 trigger
- `_codex-handoff/7c-5-g2c.ready-for-review.md` — POST-T9 trigger

**Do NOT modify:**
- 7c.4b deliverables (read-only).
- Sibling G0/G2A/G5/G6 cards or G1 migrated card (read-only post-close).
- Legacy `app/models/decision_cards/base.py:DecisionCard` (still used by G3/G4 until their own stories).
- Legacy G3/G4 cards (separate stories).
- 2-class-regime compatibility validators (already updated by G1 — verify accept G2C; do NOT re-edit unless audit reveals need).
- C4/C5/C6 contracts.
- `_frozen_hashes.py` (already populated).
- `scripts/utilities/validate_parity_test_class_conformance.py` (already extended).

## Critical implementation notes

- **2-class regime continues:** G2C migrates to `DecisionCardBase`; G3/G4 stay on legacy `DecisionCard` until their own extend-and-audit stories.
- **Frozen-hash AMELIA-P4 binding** at T2 start.
- **CROSS-AGENT T1 REVIEW BINDING HALT** before T2.
- **K-target 1.4× ≈ 350 LOC ceiling.**
- **R-tier R3** at T9.
- **T11 standard tier.**

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_decision_card_g2c_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/parity/ tests/parametrized_harness/ tests/unit/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/structural/test_tw_7c_3_firing_spec_single_source.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g2c-decision-card-extend-and-audit.md
.venv/Scripts/python.exe -m ruff check app/models/decision_cards/g2c.py tests/parity/test_decision_card_g2c_shape.py app/models/decision_cards/__init__.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-5-g2c.ready-for-review.md`. Include: 4-file lockstep verification + frozen-hash AMELIA-P4 verdict + cross-agent T1 review link + backward-consumer audit verdict + class-conformance delta + AMEND-7d-i compliance evidence + pattern-parity-ratchet confirmation + 2-class-regime preservation + R3 broad-regression delta with per-failure attribution + Pydantic-v2 14-idiom checklist.

T11: Claude standard review. AC-A through E line-by-line; cross-agent T1 review cross-checked; backward-consumer audit re-verified; AMEND-7d-i AST-scan; Pydantic-v2 14-idiom; pattern-parity ratchets; 2-class-regime preservation. Verdict at `_bmad-output/implementation-artifacts/7c-5-g2c-code-review-2026-05-NN.md`.

## Boundary

HALT on:
- 7c.4b/G1/G0/G2A/G5/G6 not done.
- LOCKSTEP_CHECK / DecisionCardBase / legacy DecisionCard not importable.
- `_frozen_hashes.py` missing or G2C hash mismatch.
- Pre-T2 cross-agent T1 review NOT PASSed.
- AMELIA-P4 frozen-hash mismatch at T2 start.
- Any LOCKSTEP_CHECK re-derivation, FOUR_FILE_GLOBS import, or all_four_present reference in test body (guardrail #1).
- Class-conformance count ≠ T1-baseline + 1.
- Broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited.
- G2CCard still inheriting from legacy `base.py:DecisionCard`.
- Backward-consumer audit identifies field-access pattern change requiring update AND that change is neither co-committed nor explicitly deferred.
- Legacy `base.py:DecisionCard` accidentally removed (must remain for G3/G4).

DO NOT touch: 7c.4b deliverables; sibling deliverables; G3/G4 cards (separate stories); C4/C5/C6 contracts; class-conformance validator (already extended); _frozen_hashes.py (already populated).

DO NOT introduce: new third-party deps; defensive enum widening; golden fixtures with non-deterministic timestamps; concurrent dispatch with G3/G4 (serial only).
```

---

## Operator dispatch checklist

1. ☐ 7c.4b/G0/G2A/G5/G6 done.
2. ☐ G1 `done` (current cycle pending — HELD until then).
3. ☐ AMELIA-P2 freshness check.
4. ☐ Sandbox-AC validator PASS on spec.
5. ☐ Governance JSON entry current (extend_and_audit_t1_deliverables binding=hard).
6. ☐ Sprint-status: `migration-7c-5-g2c-decision-card-extend-and-audit: ready-for-dev`.
7. ☐ Confirm Codex understands SERIAL-DISPATCH constraint + PRE-T2 CROSS-AGENT T1 REVIEW CHECKPOINT.
8. ☐ Plan downstream dispatch sequence: at G2C close, 4 Wave-3 stories (7c.9/10/11/12) unblock; AMELIA-P3 staggering ≥30 min apart applies.
9. ☐ Dispatch G2C ALONE.

## Post-Codex-T1 cross-agent review-watch + Post-Codex-T10 dropbox-watch

(Same as G1 pattern: T1 cross-agent review (~25-35 min) → PASS unblocks T2 → Codex T2-T9 → T10 dropbox → Claude T11 standard (~25-35 min) → commit + flip done.)
