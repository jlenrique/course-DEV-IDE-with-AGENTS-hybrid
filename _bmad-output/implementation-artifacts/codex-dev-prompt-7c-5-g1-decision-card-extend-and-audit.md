# Codex dev-story prompt — Story 7c.5.G1 (G1 DecisionCard Extend-and-Audit; dual-gate-cross-agent-CONTRACT-EVOLUTION; standard T11)

**Cycle:** Claude spec (lookahead_tier=2 author-skeleton-ahead; predecessor 7c.4b CLOSED at `8b12970`; siblings G0+G2A CLOSED at `e2aa599`; G5+G6 in flight 2026-05-05) → Codex T0-T1 (frozen-hash + contract-diff + backward-consumer audit) → **PRE-T2 CROSS-AGENT REVIEW CHECKPOINT (Claude)** → Codex T2-T10 (extension + verification) → drops `_codex-handoff/7c-5-g1.ready-for-review.md` → Claude T11 standard → commit + flip done.
**Wave:** 2 — slot 9 (first per-gate extend-and-audit; G1 directive-ratification migration to `DecisionCardBase`).
**Pre-authored:** 2026-05-05.
**Dispatch state:** **HELD until G5+G6 close** — serial dispatch only (NOT concurrent with G2C/G3/G4; all 4 extend-and-audit stories touch the same legacy `DecisionCard` migration surface). AMELIA-P2 freshness check at dispatch-time.

**Serial-dispatch context:** Unlike fresh-author G0/G2A/G5/G6 which dispatched in parallel pairs, this story dispatches ALONE. The PARALLEL-DISPATCH GUARDRAILS section below still includes guardrails #1, #2, #4, #5, #6 (which apply universally) — guardrail #3 (`__init__.py` integration coordination) is informational since there's no concurrent worker, but documented for when G2C/G3/G4 dispatch in subsequent serial slots.

---

```
Run bmad-dev-story on Story 7c.5.G1 (Slab 7c Wave 2 slot 9; dual-gate-cross-agent-CONTRACT-EVOLUTION; extend-and-audit; standard T11; SERIAL dispatch only).

Spec: `_bmad-output/implementation-artifacts/migration-7c-5-g1-decision-card-extend-and-audit.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T0-T10 task structure with PRE-T2 CROSS-AGENT REVIEW CHECKPOINT).
2. `_bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md` (predecessor; D1-D8 — particularly D2 2-class regime).
3. `_bmad-output/implementation-artifacts/7c-4b-code-review-2026-05-05.md` (T11 verdict; 2-class regime documented).
4. `_bmad-output/implementation-artifacts/7c-5-g0-code-review-2026-05-05.md` AND `_bmad-output/implementation-artifacts/7c-5-g2a-code-review-2026-05-05.md` (sibling fresh-author T11 verdicts; canonical pattern references).
5. `app/models/decision_cards/_base.py` (canonical `DecisionCardBase` — TARGET inheritance).
6. `app/models/decision_cards/base.py` (LEGACY `DecisionCard` — being migrated AWAY FROM).
7. `app/models/decision_cards/g1.py` (LEGACY G1Card pre-extension; pre-extension SHA256 = `4fe0e985d2285e3219b103424765dec009043564960ec43af1fb5710d2a1a196`).
8. `app/models/decision_cards/g0.py` AND `g2a.py` (canonical fresh-author patterns post-T11; mirror inheritance + field structure + validators + serializers — particularly `g2a.py` for UUID4 typing + strip-then-non-empty validators per pattern-parity ratchet).
9. `tests/parity/test_decision_card_g0_shape.py` AND `test_decision_card_g2a_shape.py` (canonical shape-pin patterns).
10. `tests/fixtures/decision_cards/g0_golden.json` AND `g2a_golden.json` (canonical golden patterns).
11. `app/marcus/orchestrator/production_runner.py:411` (PRIMARY backward consumer; G1Card construction site — read line 405-425 for `**common` field-set context).
12. `app/parity/contracts/tw_7c_3_firing.py` (LOCKSTEP_CHECK; AMEND-7d-i).
13. `tests/structural/test_tw_7c_3_firing_spec_single_source.py` (AMEND-7d-i AST-scan boundary).
14. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G1 = directive-ratification; extend-and-audit per §1).
15. `docs/dev-guide/pydantic-v2-schema-checklist.md` (AC-E 14-idiom).
16. Governance JSON `7c-5-g1` (dual-gate-cross-agent-CONTRACT-EVOLUTION; cross_agent_review_required=false [T11 tier]; extend_and_audit_t1_deliverables binding=hard; pts=2; K=1.4; r_tier=R3; t11_tier=standard; lookahead_tier=2; prerequisite_stories=[7c-4b]).

## T0 PRE-T1 hard checkpoints (HALT-AND-SURFACE)

- 7c.4b done; G0+G2A done (committed at `e2aa599`); G5+G6 done (HELD condition satisfied — serial dispatch only).
- `DecisionCardBase` importable from `app.models.decision_cards._base`.
- Legacy `DecisionCard` importable from `app.models.decision_cards.base` (still present pre-migration).
- `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` importable from `app.parity.contracts.tw_7c_3_firing`.
- Class-conformance baseline at T1: record observed (likely 15 if G5+G6 closed; 13 if not — adjust expected delta).
- Broad-regression baseline: re-run at T1; record for T9 R3 delta-compare.

## T0 — Frozen-hash recording (PRE-T1)

Compute SHA256 hashes:
```bash
.venv/Scripts/python.exe -c "import hashlib; print('g1', hashlib.sha256(open('app/models/decision_cards/g1.py', 'rb').read()).hexdigest())"
.venv/Scripts/python.exe -c "import hashlib; print('g2c', hashlib.sha256(open('app/models/decision_cards/g2c.py', 'rb').read()).hexdigest())"
.venv/Scripts/python.exe -c "import hashlib; print('g3', hashlib.sha256(open('app/models/decision_cards/g3.py', 'rb').read()).hexdigest())"
.venv/Scripts/python.exe -c "import hashlib; print('g4', hashlib.sha256(open('app/models/decision_cards/g4.py', 'rb').read()).hexdigest())"
```

Author `app/models/decision_cards/_frozen_hashes.py` per spec AC-A bullet 3. The g1 hash MUST equal `4fe0e985d2285e3219b103424765dec009043564960ec43af1fb5710d2a1a196` (recorded in spec at author-time). If observed g1 hash differs, HALT-AND-SURFACE — the legacy file has drifted post-spec-author and the contract-diff baseline must be re-grounded.

## T1 — Contract-diff + backward-consumer audit (Winston W3 + AMELIA-P4 deliverables)

Author both artifacts per spec AC-A bullets 1-2. Contract-diff at `_bmad-output/implementation-artifacts/migration-7c-5-g1-contract-diff.md`. Backward-consumer audit at `_bmad-output/implementation-artifacts/migration-7c-5-g1-backward-consumer-audit.md`.

Backward-consumer audit grep commands (run all three; consolidate):
```bash
.venv/Scripts/python.exe -c "import subprocess; subprocess.run(['rg', '-n', 'G1Card', '--type=py'])"
.venv/Scripts/python.exe -c "import subprocess; subprocess.run(['rg', '-n', 'from app.models.decision_cards.g1', '--type=py'])"
.venv/Scripts/python.exe -c "import subprocess; subprocess.run(['rg', '-n', 'from app.models.decision_cards import.*G1Card', '--type=py'])"
```

(Or use ripgrep directly if available; ≥24 sites identified at spec-author time.)

After both artifacts authored, drop the T1 READY notice at `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g1.t1-ready.md` listing the three deliverable paths + per-deliverable summary. **HALT and await cross-agent T1 review verdict** at `_bmad-output/implementation-artifacts/7c-5-g1-t1-cross-agent-review-2026-05-NN.md`.

## CROSS-AGENT T1 REVIEW CHECKPOINT (binding HALT before T2)

Codex MUST NOT proceed to T2 until Claude (or designated cross-agent reviewer) drops a PASS verdict at `_bmad-output/implementation-artifacts/7c-5-g1-t1-cross-agent-review-2026-05-NN.md`. If verdict is HALT-AND-REMEDIATE, Codex applies the remediation to the contract-diff + backward-consumer audit + frozen-hash artifacts and re-surfaces T1 READY. Iterate until PASS.

This is the contract_evolution discipline per Winston W3 (Round-2 party-mode 2026-05-04). Do NOT skip.

## T2-T9 — Body extension + verification battery (POST-T1-PASS only)

Resume here ONLY after cross-agent T1 review PASSes.

T2: AMELIA-P4 frozen-hash delta-AC verification + G1Card body rewrite per spec AC-B + AC-C bullet 1. Inheritance changes from `DecisionCard` (legacy `base.py`) to `DecisionCardBase` (new `_base.py`). Re-declare card_id (UUID4-typed) + trial_id (UUID4-typed) + gate_id (Literal["G1"]) + gate_focus (Literal["trial_open"]) + created_at + verb + schema_version (Literal["v1"]). Preserve trial_summary (strip-then-non-empty per G2A pattern; mirror exactly) + opened_by (min_length=1) + next_nodes (default empty list). Mirror G0/G2A field_validator chain. Drop legacy DecisionCard fields per AC-A contract-diff verdicts.

T3: Regenerate `app/models/decision_cards/schema/g1.v1.schema.json` via the canonical command. Byte-compare with previous schema; document changes in contract-diff artifact.

T4: Author `tests/fixtures/decision_cards/g1_golden.json` per spec AC-C bullet 4 with deterministic stable values.

T5: Author `tests/parity/test_decision_card_g1_shape.py` per spec AC-C bullet 3 with 9-10 test cases. **MANDATORY guardrail #1 self-check at T5.2:** grep your own file for `FOUR_FILE_GLOBS` and `all_four_present`. ZERO matches outside bare `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` import lines.

T6: Run R3 verification battery (focused + AC-D backward-consumer + AMEND-7d-i AST-scan + smoke + R3 broad + class-conformance + lint-imports + sandbox-AC + ruff). All must PASS per spec AC-C / AC-D / AC-E.

## PARALLEL-DISPATCH GUARDRAILS (binding even though G1 is serial-dispatch — harvested from G0+G2A 2026-05-05 dual-Codex run)

These six rules are derived from a real validated parallel run. Treat as binding constraints alongside the standard ACs. Guardrail #3 is informational under serial dispatch but applies to subsequent G2C/G3/G4 stories.

1. **AMEND-7d-i AST-scan compliance — MANDATORY T5.2 self-grep.** During the G2A parallel run, a worker thread initially shipped `tests/parity/test_decision_card_g2a_shape.py` with a re-derivation of `all_four_present` from `FOUR_FILE_GLOBS`. Mandatory check: ZERO matches for `FOUR_FILE_GLOBS` / `all_four_present` outside bare `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` import lines.

2. **Pattern-replication discipline — read the canonical sibling, not the spec hedging.** When in doubt about field shapes, validators, or serializer signatures: **prefer reading `g0.py` / `g2a.py` over re-interpreting spec natural-language description.** For G1 specifically, mirror G2A's UUID4 typing + strip-then-non-empty validator pattern.

3. **Shared-file integration ordering** (informational under serial dispatch; binding when G2C dispatches concurrently). `app/models/decision_cards/__init__.py` flat-export should expand to include G1Card alongside G0/G2A/G5/G6 union. Under serial dispatch (THIS story), straightforward edit. When G2C/G3/G4 dispatch later: coordinate.

4. **Pattern-parity ratchet (cosmetic — but apply at T2).** G0 T11 review flagged 2 SHOULD-FIX nits where G0 diverged from G2A:
   - **Non-empty-string validators:** strip whitespace before non-empty check. Apply G2A's strip-then-check pattern to G1's `trial_summary` and `opened_by`. Pattern: `if not value.strip(): raise ValueError("<field> must be non-empty (excluding whitespace)")`.
   - **UUID type annotation:** use Pydantic-typed `UUID4` for `card_id` / `trial_id`. Import: `from pydantic import UUID4`.

5. **Class-conformance baseline arithmetic.** Under SERIAL dispatch, this story increments by exactly +1. T1 records observed baseline; T6.6 verifies T1-baseline + 1.

6. **Broad-regression baseline shift with per-failure attribution.** Codex's G0+G2A T9 reported `44 failed, 4132 passed`. T11 verified all 44 inherited via `git log` per failing test. **At T1, record post-G0+G2A+G5+G6 baseline** (re-run R3 broad regression; expect ~44 ± G5/G6 changes if any). At T9, delta MUST be ≤ 0; ≥1 new failure attributable to G1 is HALT. Do NOT attribute new failures to "inherited" without `git log` verification.

## Files in scope

**New (5 files):**
- `app/models/decision_cards/_frozen_hashes.py` — frozen-at-ship hash record (T0 deliverable; covers G1+G2C+G3+G4 in one file).
- `_bmad-output/implementation-artifacts/migration-7c-5-g1-contract-diff.md` — diff-against-prior-contract artifact (T1 cross-agent review target).
- `_bmad-output/implementation-artifacts/migration-7c-5-g1-backward-consumer-audit.md` — per-call-site verdict artifact (T1 cross-agent review target).
- `tests/parity/test_decision_card_g1_shape.py` — NEW shape-pin (mirror G2A pattern; 9-10 tests).
- `tests/fixtures/decision_cards/g1_golden.json` — NEW golden fixture (deterministic).

**Modified (3 files):**
- `app/models/decision_cards/g1.py` — REWRITTEN: inheritance migration `DecisionCard` → `DecisionCardBase`; FR-7c-51 schema_version add; pattern-parity ratchets per guardrail #4.
- `app/models/decision_cards/schema/g1.v1.schema.json` — REGENERATED from new G1Card.model_json_schema().
- `app/models/decision_cards/__init__.py` — flat-export G1Card alongside G0/G2A/G5/G6 union (verify post-G5/G6 close state at T1).

**Codex-handoff dropbox files (2):**
- `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g1.t1-ready.md` — PRE-T2 cross-agent review trigger.
- `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g1.ready-for-review.md` — POST-T9 standard T11 trigger.

**Do NOT modify:**
- 7c.4b's `_base.py` / `tw_7c_3_firing.py` — read-only.
- Sibling G0/G2A/G5/G6 cards or schemas / fixtures / shape-pins — read-only pattern reference.
- Legacy `app/models/decision_cards/base.py:DecisionCard` — left intact (it remains as the parent for G2C/G3/G4 until those stories also extend-and-audit; do NOT remove the legacy class).
- Other legacy G2C/G3/G4 cards — they migrate in their own stories.
- C4/C5/C6 import-linter contracts.
- `scripts/utilities/validate_parity_test_class_conformance.py` (already extended).

## Critical implementation notes

- **2-class regime continues:** G1Card migrates to `DecisionCardBase`; G2C/G3/G4 stay on legacy `DecisionCard` (`base.py`) until their own extend-and-audit stories. Legacy `base.py:DecisionCard` MUST remain importable post-this-story.
- **Backward-consumer audit is binding:** every G1Card consumer site enumerated in the audit artifact has a verdict. If any site requires field-access pattern changes, those changes are co-committed in this story OR explicitly deferred via `_bmad-output/planning-artifacts/deferred-inventory.md`.
- **Frozen-hash AMELIA-P4 is binding:** at T2 start, observed g1.py hash MUST equal `FROZEN_AT_SHIP_HASHES["g1"]`. Mismatch → HALT.
- **CROSS-AGENT T1 REVIEW is BINDING:** Codex stops at T1 and waits for verdict. No T2 work happens before T1 review PASS.
- **K-target 1.4× ≈ 350 LOC ceiling.** Estimate ~400 LOC actual (heavier due to T0 frozen-hash + T1 artifacts).
- **R-tier R3:** full broad regression at T9 (xdist-accelerated post-7c.0c).
- **T11 tier standard:** despite gate-mode `dual-gate-cross-agent-CONTRACT-EVOLUTION`, T11 itself is standard tier (the "cross-agent" component refers to the T1 PRE-T2 review).

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_decision_card_g1_shape.py -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest tests/parity/ tests/parametrized_harness/ tests/unit/ -p no:randomly -q --tb=short   # AC-D backward-consumer

.venv/Scripts/python.exe -m pytest tests/structural/test_tw_7c_3_firing_spec_single_source.py -p no:randomly -q --tb=short   # AMEND-7d-i guardrail #1

.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line   # R3 broad

.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

.venv/Scripts/lint-imports.exe

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g1-decision-card-extend-and-audit.md

.venv/Scripts/python.exe -m ruff check app/models/decision_cards/g1.py app/models/decision_cards/_frozen_hashes.py app/models/decision_cards/__init__.py tests/parity/test_decision_card_g1_shape.py
```

Expected:
- Focused: 9-10 tests passed.
- AC-D backward-consumer: PASS UNCHANGED (production_runner.py + unit tests green).
- AMEND-7d-i AST-scan: PASS.
- Smoke: 200-nodeid baseline UNCHANGED.
- R3 broad: ~44 inherited preserved (delta ≤ 0; per-failure attribution at T10).
- Class-conformance: T1-baseline + 1.
- Lint-imports: 12 KEPT.
- Sandbox-AC: PASS.
- Ruff: clean.

## T10 + T11

T10: dropbox at `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g1.ready-for-review.md`. Include:
- 4-file lockstep verification.
- Frozen-hash AMELIA-P4 verdict (g1.py pre-T2 hash matched recorded hash).
- Cross-agent T1 review verdict link + PASS confirmation.
- Backward-consumer audit verdict (per-call-site PASS; any updates co-committed).
- Class-conformance delta (T1-baseline observed N → +1).
- AMEND-7d-i compliance evidence (paste `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` line + "ZERO matches for FOUR_FILE_GLOBS / all_four_present in test body").
- Pattern-parity-ratchet confirmation (trial_summary + opened_by use strip-then-non-empty per G2A; card_id + trial_id typed UUID4 not bare UUID).
- 2-class-regime migration confirmation (G1Card now inherits DecisionCardBase; legacy base.py:DecisionCard untouched for G2C/G3/G4).
- R3 broad-regression delta WITH per-failure attribution (per guardrail #6).
- Pydantic-v2 14-idiom checklist line-by-line.

T11: Claude standard review. AC-A through E line-by-line; cross-agent T1 review verdict cross-checked; backward-consumer audit re-verified; AMEND-7d-i AST-scan; Pydantic-v2 14-idiom; pattern-parity ratchets; 2-class-regime preservation. Verdict at `_bmad-output/implementation-artifacts/7c-5-g1-code-review-2026-05-NN.md`.

## Boundary

HALT on:
- 7c.4b not done; G0/G2A/G5/G6 not done.
- LOCKSTEP_CHECK / DecisionCardBase / legacy DecisionCard not importable.
- Pre-T2 cross-agent T1 review NOT PASSed.
- AMELIA-P4 frozen-hash mismatch at T2 start.
- Any LOCKSTEP_CHECK re-derivation, `FOUR_FILE_GLOBS` import, or `all_four_present` reference in test body (guardrail #1).
- Class-conformance count after this story ≠ T1-baseline + 1.
- Broad-regression failure count > T1 baseline AND any new failure not demonstrably inherited (guardrail #6).
- G1Card still inheriting from legacy `base.py:DecisionCard` (must inherit from `_base.py:DecisionCardBase`).
- Backward-consumer audit identifies a call site where field-access pattern change is required AND that change is neither co-committed nor explicitly deferred via deferred-inventory.
- Legacy `app/models/decision_cards/base.py:DecisionCard` accidentally removed (it must remain for G2C/G3/G4).

DO NOT touch: 7c.4b deliverables; sibling G0/G2A/G5/G6 deliverables; legacy G2C/G3/G4 cards (separate stories); C4/C5/C6 contracts; class-conformance validator (already extended).

DO NOT introduce: new third-party deps; defensive enum widening (gate_id MUST be exactly Literal["G1"]); golden fixtures with non-deterministic timestamps or random UUIDs; concurrent dispatch with G2C/G3/G4 (serial only).
```

---

## Operator dispatch checklist

1. ☐ 7c.4b `done`; G0/G2A `done` (`e2aa599`).
2. ☐ G5/G6 `done` (current session pending — HELD until then).
3. ☐ AMELIA-P2 freshness check: re-diff this prompt against on-disk g0.py / g2a.py for any post-T11 pattern divergence.
4. ☐ Sandbox-AC validator PASS on spec.
5. ☐ Governance JSON entry current (extend_and_audit_t1_deliverables binding=hard).
6. ☐ Sprint-status: `migration-7c-5-g1-decision-card-extend-and-audit: ready-for-dev`.
7. ☐ Confirm Codex understands the SERIAL-DISPATCH constraint (NOT concurrent with G2C/G3/G4) + the PRE-T2 CROSS-AGENT T1 REVIEW CHECKPOINT.
8. ☐ Dispatch G1 ALONE.

## Post-Codex-T1 cross-agent review-watch (NEW for extend-and-audit)

1. Codex drops T1 READY notice at `_codex-handoff/7c-5-g1.t1-ready.md`.
2. Claude T1 cross-agent review (~25-35 min: read contract-diff + backward-consumer audit + frozen-hash artifacts; verify completeness + per-site verdict accuracy + diff-against-prior coherence).
3. Drop T1 verdict at `7c-5-g1-t1-cross-agent-review-2026-05-NN.md`. PASS unblocks Codex T2; HALT-AND-REMEDIATE iterates.

## Post-Codex-T10 dropbox-watch (standard T11)

1. Codex drops ready-for-review notice with all guardrail evidence + pattern-parity ratchet confirmation + 2-class-regime confirmation + cross-agent T1 review link.
2. Claude T11 standard review (~25-35 min; heavier than fresh-author due to backward-consumer re-verification).
3. Apply remediation cycles per HALT-AND-REMEDIATE if any.
4. Commit + flip done.
5. At 7c.5.G1 close: 7c.6 / 7c.7 / 7c.8 unblock (Wave-3 §04A G1A + §04.5 G1.5 + §04.55 G1.5 run-constants — all with `lookahead_tier=1` + `t11_tier=lite`; can pre-author next as queue-fill).
