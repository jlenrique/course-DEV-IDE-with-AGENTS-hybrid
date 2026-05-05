# Codex dev-story prompt — Story 7c.5.G4 (G4 DecisionCard Extend-and-Audit; dual-gate-cross-agent-CONTRACT-EVOLUTION; standard T11)

**Cycle:** Claude spec (lookahead_tier=2) → Codex T0-T1 → **PRE-T2 CROSS-AGENT REVIEW CHECKPOINT (Claude)** → Codex T2-T10 → Claude T11 standard → commit + flip done.
**Wave:** 2 — slot 12 (fourth/final per-gate extend-and-audit; G4 fidelity gate migration). Closes 2-class-regime migration chain.
**Pre-authored:** 2026-05-05.
**Dispatch state:** **HELD until G3 closes** (serial dispatch chain G1→G2C→G3→G4) OR operator (E)-elasticity override authorizes earlier. AMELIA-P2 freshness check at dispatch-time.

**V6 + V7 amendments codified at `57b92b2` (BINDING):**
- V6 AMELIA-P5 DROP-row Heavy gate: contract-diff §2 MUST carry per-row `audit_method=heavy|light`; DROP rows REQUIRE `audit_method=heavy` with smoke-pass evidence.
- V7 wave_3_lookahead_policy: G4 close is the third P2-clean-×3 baseline cycle; after close, Wave-3 7c.6+ may elevate to N+3 cap if all 3 cycles held clean.

---

```
Run bmad-dev-story on Story 7c.5.G4 (Slab 7c Wave 2 slot 12; dual-gate-cross-agent-CONTRACT-EVOLUTION; extend-and-audit; standard T11; SERIAL dispatch only OR operator (E)-elasticity override).

Spec: `_bmad-output/implementation-artifacts/migration-7c-5-g4-decision-card-extend-and-audit.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T0-T10 task structure with PRE-T2 CROSS-AGENT REVIEW CHECKPOINT).
2. **`_bmad-output/implementation-artifacts/migration-7c-5-g1-decision-card-extend-and-audit.md`** (canonical extend-and-audit predecessor).
3. **`_bmad-output/implementation-artifacts/migration-7c-5-g2c-decision-card-extend-and-audit.md`** AND **`migration-7c-5-g3-decision-card-extend-and-audit.md`** (immediate predecessors; canonical V6 AMELIA-P5 application).
4. `_bmad-output/implementation-artifacts/migration-7c-5-{g1,g2c,g3}-contract-diff.md` (canonical contract-diff structures with audit_method qualifiers — mirror).
5. `_bmad-output/implementation-artifacts/migration-7c-5-{g1,g2c,g3}-backward-consumer-audit.md`.
6. `_bmad-output/implementation-artifacts/7c-5-{g1,g2c,g3}-t1-cross-agent-review-2026-05-05.md` (T1 review precedents — what passes; what gets flagged).
7. `_bmad-output/implementation-artifacts/7c-5-{g1,g2c,g3}-code-review-2026-05-NN.md` (T11 verdicts — document any patches affecting G4).
8. `app/models/decision_cards/_base.py` (canonical `DecisionCardBase`).
9. `app/models/decision_cards/g4.py` (LEGACY pre-extension; pre-extension SHA256 = `98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a`).
10. `app/models/decision_cards/g1.py` AND `g2c.py` AND `g3.py` (POST-close MIGRATED canonical extend-and-audit bodies).
11. `app/models/decision_cards/g2a.py` (canonical fresh-author shape).
12. `app/parity/contracts/tw_7c_3_firing.py` + `tests/structural/test_tw_7c_3_firing_spec_single_source.py`.
13. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G4 = fidelity gate per §1 family table).
14. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
15. `docs/dev-guide/pydantic-v2-schema-checklist.md`.
16. Governance JSON: `7c-5-g4` entry + `extend_and_audit_t1_audit_method` (V6) + `wave_3_lookahead_policy` (V7).

## T0 PRE-T1 hard checkpoints (HALT-AND-SURFACE)

- 7c.4b/G0/G2A/G5/G6/G1 done.
- G2C + G3 done (or operator (E)-elasticity override authorizing earlier dispatch).
- `DecisionCardBase` + `LOCKSTEP_CHECK` importable.
- `_frozen_hashes.py` exists + contains `g4` key with value `98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a`.
- 2-class-regime compatibility validators already updated (G1 close).
- Class-conformance baseline at T1: record observed (likely 18 if G1+G2C+G3 closed; +1 increment expected for G4 → final 19).
- Broad-regression baseline: re-run at T1.

## T0 — Frozen-hash pre-check

```bash
.venv/Scripts/python.exe -c "import hashlib; print(hashlib.sha256(open('app/models/decision_cards/g4.py', 'rb').read()).hexdigest())"
.venv/Scripts/python.exe -c "from app.models.decision_cards._frozen_hashes import FROZEN_AT_SHIP_HASHES; print(FROZEN_AT_SHIP_HASHES['g4'])"
```

Both MUST equal `98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a`. Mismatch → HALT.

## T1 — Contract-diff + backward-consumer audit + AMELIA-P5 DROP-row Heavy gate

Author per spec AC-A. Mirror G1+G2C+G3 structure. G4-specific:
- Legacy G4Card fields: `final_status: Literal["completed", "partial", "failed"]` (preserve closed 3-value Literal), `artifact_paths: list[str]` (default empty list), `outcome_summary: str` (mirror with strip-then-non-empty per G2A pattern).
- **NEW field added:** `gate_focus: Literal["fidelity_gate"]` per ADR 0002.
- **Semantic alignment:** G4 legacy "trial closeout" semantics fit cleanly with ADR 0002's "fidelity gate" framing — no semantic-divergence statement required (unlike G3 which had legacy mid-trial-review fields vs ADR-designated motion-clip-approval). Confirm at T1 §1.
- 2-class-regime compatibility: already widened by G1; verify G4Card recognized.

### AMELIA-P5 — DROP-row Heavy gate (V6; binding=hard)

Same protocol as G2C/G3. Contract-diff §2 schema `| field | disposition | audit_method | rationale |`. Every DROP row REQUIRES `audit_method=heavy` with smoke-pass evidence.

**T1 smoke-pass protocol:**
```bash
.venv/Scripts/python.exe -m pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k <field_name> --co -q
```

Apply to candidate DROP rows: `drafted_proposal`, `evidence`, `risks`, `reject_rate`, `party_mode_contributions`, `consolidated_at`, `sanctum_warnings`. Per G2C+G3 precedent, expect light-weight DROP verdicts (G2C+G3 found drafted_proposal/evidence reads are G1-only; party-mode metadata reads are G-PARTY-only). G4 verifies for itself.

After both artifacts authored, drop `_codex-handoff/7c-5-g4.t1-ready.md` notice. **HALT-AND-WAIT** for cross-agent T1 review verdict at `_bmad-output/implementation-artifacts/7c-5-g4-t1-cross-agent-review-2026-05-NN.md`.

## CROSS-AGENT T1 REVIEW CHECKPOINT (binding HALT)

## T2-T9 — Body extension + verification battery (POST-T1-PASS only)

T2: AMELIA-P4 verification + G4Card rewrite. Inheritance `DecisionCard` → `DecisionCardBase`. Re-declare base fields per G2A canonical. Preserve gate-specific:
- `final_status: Literal["completed", "partial", "failed"]` (closed 3-value Literal — preserve verbatim).
- `artifact_paths: list[str]` with default_factory=list (preserve).
- `outcome_summary: str` with strip-then-non-empty validator (mirror G2A).

ADD `gate_focus: Literal["fidelity_gate"]` + `schema_version: Literal["v1"]`. Drop legacy DecisionCard fields per AC-A contract-diff verdicts.

T3: Regenerate schema/g4.v1.schema.json via Path.write_text per A18 (canonical command):

```bash
.venv/Scripts/python.exe -c "from pathlib import Path; from app.models.decision_cards.g4 import G4Card; import json; Path('app/models/decision_cards/schema/g4.v1.schema.json').write_text(json.dumps(G4Card.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
```

T4: Author g4_golden.json (gate_id="G4", gate_focus="fidelity_gate", final_status="completed", artifact_paths=["course-content/courses/example/output/"], outcome_summary="Trial closed successfully with all artifacts produced.", etc.).

T5: Author shape-pin (10-11 tests; closed-enum on gate_id + gate_focus + final_status; non-empty outcome_summary; artifact_paths default-empty acceptance; JSON-Schema byte-match; golden round-trip; frozen mutation rejection). **MANDATORY guardrail #1 self-grep at T5.2.**

T6: Run R3 verification battery.

## PARALLEL-DISPATCH GUARDRAILS (binding even under serial dispatch — same six rules)

1. **AMEND-7d-i AST-scan compliance — MANDATORY T5.2 self-grep.** ZERO matches for `FOUR_FILE_GLOBS` / `all_four_present` outside bare `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` import lines.
2. **Pattern-replication discipline.** Prefer post-G1+G2C+G3-close `g1.py` / `g2c.py` / `g3.py` (canonical extend-and-audit bodies) + `g2a.py` (canonical fresh-author shape).
3. **Shared-file integration ordering** (informational under serial dispatch). `__init__.py` flat-export already extended through G3.
4. **Pattern-parity ratchet.** UUID4 typing + strip-then-non-empty on `outcome_summary`.
5. **Class-conformance baseline arithmetic.** Under serial dispatch, +1 exactly. T1 records observed (likely 18 if G2C+G3 closed); T6.5 verifies T1-baseline + 1 = 19.
6. **Broad-regression baseline shift with per-failure attribution.**

## V7 wave_3_lookahead_policy P2-clean-×3 baseline (G4 closes the cycle)

G4 close is the **third (final) consumed pre-auth** of the v1 baseline cycle (V7 codification at `57b92b2`). After G4 close, evaluate:
- Did AMELIA-P2 freshness check hold clean across G2C, G3, G4 close-batches?
- If YES → N+3 cap unlocks for Wave-3 7c.6+ stories.
- If NO → flag specific drift; revisit policy at next slab-opener party-mode.

Document P2-clean count in T10 dropbox.

## Files in scope

**New (4 files):**
- `_bmad-output/implementation-artifacts/migration-7c-5-g4-contract-diff.md`
- `_bmad-output/implementation-artifacts/migration-7c-5-g4-backward-consumer-audit.md`
- `tests/parity/test_decision_card_g4_shape.py`
- `tests/fixtures/decision_cards/g4_golden.json`

**Modified (3 files):**
- `app/models/decision_cards/g4.py` — REWRITTEN
- `app/models/decision_cards/schema/g4.v1.schema.json` — REGENERATED via Path.write_text
- `app/models/decision_cards/__init__.py` — flat-export verified

**Codex-handoff dropbox files (2):**
- `_codex-handoff/7c-5-g4.t1-ready.md`
- `_codex-handoff/7c-5-g4.ready-for-review.md`

**Do NOT modify:**
- 7c.4b deliverables; sibling closed cards (G0/G2A/G5/G6/G1/G2C/G3); legacy `base.py:DecisionCard` (will be removed by a separate cleanup story AFTER G4 closes — NOT this story); 2-class-regime compatibility validators (already widened); C4/C5/C6 contracts; `_frozen_hashes.py`; class-conformance validator.

## Critical implementation notes

- **2-class regime closes:** G4 is the LAST extend-and-audit. After G4 close, all 4 legacy gates (G1/G2C/G3/G4) inherit from DecisionCardBase. Legacy `base.py:DecisionCard` becomes unreferenced — but its REMOVAL is a separate cleanup story (NOT this one). Leave `base.py` intact.
- **Frozen-hash AMELIA-P4 binding** at T2 start.
- **CROSS-AGENT T1 REVIEW BINDING HALT** before T2.
- **K-target 1.4× ≈ 350 LOC ceiling.**
- **R-tier R3** at T9.
- **T11 standard tier.**
- **final_status closed Literal preservation:** legacy uses 3-value closed Literal; preserve verbatim. Shape-pin tests reject `"in_progress"`, `"unknown"`, `"COMPLETED"` (uppercase), and non-string values.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_decision_card_g4_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/parity/ tests/parametrized_harness/ tests/unit/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/structural/test_tw_7c_3_firing_spec_single_source.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g4-decision-card-extend-and-audit.md
.venv/Scripts/python.exe -m ruff check app/models/decision_cards/g4.py tests/parity/test_decision_card_g4_shape.py app/models/decision_cards/__init__.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-5-g4.ready-for-review.md`. Include all standard extend-and-audit T10 evidence + V7 P2-clean-×3 baseline summary (did P2 freshness check hold clean across G2C+G3+G4 close-batches?) + 2-class-regime closure note (all 4 legacy gates now inherit DecisionCardBase; legacy base.py:DecisionCard unreferenced post-this-close).

T11: Claude standard review.

## Boundary

HALT on:
- Predecessors not done; substrate not importable; `_frozen_hashes.py` G4 mismatch.
- Pre-T2 cross-agent T1 review NOT PASSed.
- AMELIA-P4 frozen-hash mismatch at T2 start.
- AMEND-7d-i guardrail #1 violations.
- Class-conformance count ≠ T1-baseline + 1.
- Broad-regression delta > 0 with non-inherited failures.
- G4Card still inheriting from legacy `base.py:DecisionCard`.
- final_status Literal accidentally widened or relaxed.
- Backward-consumer audit identifies required update neither co-committed nor deferred.
- Legacy `base.py:DecisionCard` accidentally removed (must remain; removal is a separate cleanup story).

DO NOT introduce: new third-party deps; defensive enum widening on gate_focus or final_status; non-deterministic golden values; concurrent dispatch with non-existent G5 (this is the final extend-and-audit).
```

---

## Operator dispatch checklist

1. ☐ 7c.4b/G0/G2A/G5/G6/G1 all `done`.
2. ☐ G2C + G3 `done` (chain predecessors — HELD until then; or operator (E)-elasticity override).
3. ☐ AMELIA-P2 freshness check.
4. ☐ Sandbox-AC validator PASS.
5. ☐ Governance JSON entry current.
6. ☐ Sprint-status: ready-for-dev.
7. ☐ Confirm Codex understands SERIAL-DISPATCH (or operator override) + PRE-T2 cross-agent T1 review checkpoint + V6 AMELIA-P5 binding + V7 P2-clean-×3 baseline closure.
8. ☐ Dispatch G4.

## Post-Codex-T1 + Post-Codex-T10 watches

(Same pattern as G1/G2C/G3.)

## V7 P2-clean-×3 baseline closure

After G4 close, the 3-cycle baseline (G2C + G3 + G4) is complete. If P2 freshness check held clean across all 3 → Wave-3 7c.6+ default cap elevates to N+3. If drift surfaced → revisit policy.
