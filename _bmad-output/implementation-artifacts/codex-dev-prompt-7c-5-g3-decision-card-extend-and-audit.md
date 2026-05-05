# Codex dev-story prompt — Story 7c.5.G3 (G3 DecisionCard Extend-and-Audit; dual-gate-cross-agent-CONTRACT-EVOLUTION; standard T11)

**Cycle:** Claude spec (lookahead_tier=2) → Codex T0-T1 → **PRE-T2 CROSS-AGENT REVIEW CHECKPOINT (Claude)** → Codex T2-T10 → Claude T11 standard → commit + flip done.
**Wave:** 2 — slot 11 (third per-gate extend-and-audit; G3 motion-clip approval migration).
**Pre-authored:** 2026-05-05.
**Dispatch state:** **HELD until G2C closes** (serial dispatch chain G1 → G2C → G3 → G4). AMELIA-P2 freshness check at dispatch-time.

**Semantic alignment note (BINDING at T1 contract-diff §1):** ADR 0002 §1 designates G3 as "motion-clip approval gate" but the legacy G3Card fields (`progress_percent`, `active_node_id`, `pending_nodes`, `operator_prompt`) describe mid-trial in-flight operator review. T1 contract-diff §1 MUST address this divergence — recommended verdict: preserve legacy fields verbatim under `gate_focus="motion_clip_approval"` family marker; defer operator semantic refinement to a future story. See spec metadata for the full statement.

---

```
Run bmad-dev-story on Story 7c.5.G3 (Slab 7c Wave 2 slot 11; dual-gate-cross-agent-CONTRACT-EVOLUTION; extend-and-audit; standard T11; SERIAL dispatch only).

Spec: `_bmad-output/implementation-artifacts/migration-7c-5-g3-decision-card-extend-and-audit.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T0-T10 task structure; **CRITICAL: read the semantic alignment note in spec metadata + AC-A §1 wording**).
2. **`_bmad-output/implementation-artifacts/migration-7c-5-g1-decision-card-extend-and-audit.md`** (canonical extend-and-audit; T1 deliverable patterns).
3. **`_bmad-output/implementation-artifacts/migration-7c-5-g2c-decision-card-extend-and-audit.md`** (predecessor; canonical pattern for ADD-gate_focus migration; G3 follows same pattern with motion-clip-approval value).
4. `_bmad-output/implementation-artifacts/migration-7c-5-g1-contract-diff.md` AND `migration-7c-5-g2c-contract-diff.md` (canonical contract-diff structures).
5. `_bmad-output/implementation-artifacts/migration-7c-5-g1-backward-consumer-audit.md` AND `migration-7c-5-g2c-backward-consumer-audit.md`.
6. `_bmad-output/implementation-artifacts/7c-5-g1-t1-cross-agent-review-2026-05-05.md` AND `7c-5-g2c-t1-cross-agent-review-2026-05-NN.md` (canonical T1 review verdicts).
7. `_bmad-output/implementation-artifacts/7c-5-g1-code-review-2026-05-NN.md` AND `7c-5-g2c-code-review-2026-05-NN.md` (predecessor T11 verdicts; document any patches affecting G3).
8. `app/models/decision_cards/_base.py`.
9. `app/models/decision_cards/g3.py` (LEGACY pre-extension; pre-extension SHA256 = `bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3`).
10. `app/models/decision_cards/g1.py` AND `g2c.py` (POST-close MIGRATED canonical extend-and-audit bodies).
11. `app/models/decision_cards/g2a.py` (canonical fresh-author shape).
12. `app/parity/contracts/tw_7c_3_firing.py` + `tests/structural/test_tw_7c_3_firing_spec_single_source.py`.
13. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G3 = motion-clip approval gate per §1 family table).
14. `docs/dev-guide/pydantic-v2-schema-checklist.md`.
15. Governance JSON `7c-5-g3` (extend_and_audit_t1_deliverables binding=hard).

## T0 PRE-T1 hard checkpoints (HALT-AND-SURFACE)

- 7c.4b/G0/G2A/G5/G6/G1/G2C done.
- `DecisionCardBase` + `LOCKSTEP_CHECK` importable.
- `_frozen_hashes.py` exists + contains `g3` key with value `bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3`.
- 2-class-regime compatibility validators already updated (G1 close).
- Class-conformance baseline at T1: record observed (likely 17 if G1+G2C closed; +1 increment expected for G3).
- Broad-regression baseline: re-run at T1.

## T0 — Frozen-hash pre-check

```bash
.venv/Scripts/python.exe -c "import hashlib; print(hashlib.sha256(open('app/models/decision_cards/g3.py', 'rb').read()).hexdigest())"
.venv/Scripts/python.exe -c "from app.models.decision_cards._frozen_hashes import FROZEN_AT_SHIP_HASHES; print(FROZEN_AT_SHIP_HASHES['g3'])"
```

Both MUST equal `bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3`. Mismatch → HALT.

## T1 — Contract-diff + backward-consumer audit

Author per spec AC-A. Mirror G1+G2C structure. G3-specific:
- Legacy G3Card fields: `progress_percent: float` (preserve with `Field(..., ge=0.0, le=100.0)` bounds), `active_node_id: str` (min_length=1; mirror with strip-then-non-empty per G2A), `pending_nodes: list[str]` (default empty), `operator_prompt: str` (mirror with strip-then-non-empty).
- **NEW field added:** `gate_focus: Literal["motion_clip_approval"]` per ADR 0002.
- **§1 SEMANTIC ALIGNMENT STATEMENT:** explicit verdict on legacy mid-trial vs ADR-designated motion-clip-approval semantic divergence. Recommended verdict: preserve legacy fields; add gate_focus per family taxonomy; defer operator semantic refinement. State this verdict explicitly in the contract-diff §1.
- 2-class-regime compatibility: already widened by G1; verify G3Card recognized.

After both artifacts authored, drop `_codex-handoff/7c-5-g3.t1-ready.md` notice. **HALT and await cross-agent T1 review verdict.**

## CROSS-AGENT T1 REVIEW CHECKPOINT (binding HALT)

## T2-T9 — Body extension + verification battery (POST-T1-PASS only)

T2: AMELIA-P4 verification + G3Card rewrite. Inheritance change `DecisionCard` → `DecisionCardBase`. Re-declare base fields per G2A canonical. Preserve gate-specific:
- `progress_percent: float` with `Field(..., ge=0.0, le=100.0)` (Pydantic-native bounds preserve from legacy).
- `active_node_id: str` with strip-then-non-empty validator (mirror G2A `plan_unit_summary` pattern).
- `pending_nodes: list[str]` with default_factory=list.
- `operator_prompt: str` with strip-then-non-empty validator.

ADD `gate_focus: Literal["motion_clip_approval"]` + `schema_version: Literal["v1"]`. Drop legacy DecisionCard fields per AC-A contract-diff verdicts.

T3: Regenerate `app/models/decision_cards/schema/g3.v1.schema.json` via Python file-write (NOT shell `>` redirection — see anti-pattern A18 in `docs/dev-guide/specialist-anti-patterns.md`; PowerShell `>` emits a UTF-8 BOM that breaks byte-for-byte schema-match in T6; first manifested at G1 T3 2026-05-05).

Canonical command (use this exact form):

```bash
.venv/Scripts/python.exe -c "from pathlib import Path; from app.models.decision_cards.g3 import G3Card; import json; Path('app/models/decision_cards/schema/g3.v1.schema.json').write_text(json.dumps(G3Card.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
```
T4: Author g3_golden.json (gate_id="G3", gate_focus="motion_clip_approval", progress_percent=50.0, active_node_id="example-node-id", operator_prompt="Approve motion clip continuation?", etc.).
T5: Author shape-pin (10-11 tests including: progress_percent boundary tests at 0.0 / 100.0 / -0.1 / 100.1; closed-enum red-rejection on gate_id + gate_focus; non-empty active_node_id; strip-then-non-empty operator_prompt; JSON-Schema byte-match; golden round-trip; frozen mutation rejection). **MANDATORY guardrail #1 self-grep at T5.2.**

T6: Run R3 verification battery.

## PARALLEL-DISPATCH GUARDRAILS (binding even under serial dispatch — same six rules as G1/G2C prompts)

1. **AMEND-7d-i AST-scan compliance — MANDATORY T5.2 self-grep.** ZERO matches for `FOUR_FILE_GLOBS` / `all_four_present` outside bare `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` import lines.
2. **Pattern-replication discipline.** Prefer post-G1+G2C-close `g1.py` / `g2c.py` (canonical extend-and-audit bodies) + `g2a.py` (canonical fresh-author shape).
3. **Shared-file integration ordering** (informational under serial dispatch).
4. **Pattern-parity ratchet.** UUID4 typing + strip-then-non-empty on `active_node_id` + `operator_prompt`.
5. **Class-conformance baseline arithmetic.** +1 exactly under serial dispatch.
6. **Broad-regression baseline shift with per-failure attribution.**

## Files in scope

**New (4 files):**
- `_bmad-output/implementation-artifacts/migration-7c-5-g3-contract-diff.md`
- `_bmad-output/implementation-artifacts/migration-7c-5-g3-backward-consumer-audit.md`
- `tests/parity/test_decision_card_g3_shape.py`
- `tests/fixtures/decision_cards/g3_golden.json`

**Modified (3 files):**
- `app/models/decision_cards/g3.py` — REWRITTEN
- `app/models/decision_cards/schema/g3.v1.schema.json` — REGENERATED
- `app/models/decision_cards/__init__.py` — flat-export verified

**Codex-handoff dropbox files (2):**
- `_codex-handoff/7c-5-g3.t1-ready.md`
- `_codex-handoff/7c-5-g3.ready-for-review.md`

**Do NOT modify:**
- 7c.4b deliverables; sibling closed cards (G0/G2A/G5/G6/G1/G2C); legacy `base.py:DecisionCard` (still used by G4); legacy G4 card; 2-class-regime compatibility validators (already updated); C4/C5/C6 contracts; `_frozen_hashes.py`; class-conformance validator.

## Critical implementation notes

- **2-class regime continues:** G3 migrates; G4 stays on legacy until its own story.
- **Frozen-hash AMELIA-P4 binding** at T2 start.
- **CROSS-AGENT T1 REVIEW BINDING HALT** before T2.
- **K-target 1.4× ≈ 350 LOC ceiling.**
- **R-tier R3** at T9.
- **T11 standard tier.**
- **progress_percent BOUNDS PRESERVATION:** legacy uses `Field(ge=0.0, le=100.0)`. Preserve verbatim in migrated body. Shape-pin tests boundary cases.
- **Semantic alignment note:** preserve legacy fields verbatim; add gate_focus per ADR 0002; defer operator semantic refinement.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_decision_card_g3_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/parity/ tests/parametrized_harness/ tests/unit/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/structural/test_tw_7c_3_firing_spec_single_source.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g3-decision-card-extend-and-audit.md
.venv/Scripts/python.exe -m ruff check app/models/decision_cards/g3.py tests/parity/test_decision_card_g3_shape.py app/models/decision_cards/__init__.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-5-g3.ready-for-review.md`. Include all standard extend-and-audit T10 evidence + progress_percent boundary test matrix + semantic-alignment-statement reference (the §1 verdict in the contract-diff).

T11: Claude standard review.

## Boundary

HALT on:
- Predecessors not done; substrate not importable; `_frozen_hashes.py` G3 mismatch.
- Pre-T2 cross-agent T1 review NOT PASSed.
- AMELIA-P4 frozen-hash mismatch at T2 start.
- AMEND-7d-i guardrail #1 violations.
- Class-conformance count ≠ T1-baseline + 1.
- Broad-regression delta > 0 with non-inherited failures.
- G3Card still inheriting from legacy `base.py:DecisionCard`.
- progress_percent bounds dropped or relaxed (legacy is `[0.0, 100.0]`).
- Backward-consumer audit identifies required update neither co-committed nor deferred.
- Legacy `base.py:DecisionCard` removed (must remain for G4).

DO NOT introduce: new third-party deps; defensive enum widening on gate_focus; non-deterministic golden values; concurrent dispatch with G4 (serial only).
```

---

## Operator dispatch checklist

1. ☐ 7c.4b/G0/G2A/G5/G6/G1/G2C all `done`.
2. ☐ G2C `done` (chain predecessor — HELD until then).
3. ☐ AMELIA-P2 freshness check.
4. ☐ Sandbox-AC validator PASS.
5. ☐ Governance JSON entry current.
6. ☐ Sprint-status: ready-for-dev.
7. ☐ Confirm Codex understands SERIAL-DISPATCH + PRE-T2 cross-agent T1 review checkpoint + semantic alignment statement requirement.
8. ☐ Dispatch G3 ALONE.

## Post-Codex-T1 + Post-Codex-T10 watches

(Same pattern as G1/G2C: PRE-T2 cross-agent T1 review (~25-35 min) → POST-T9 standard T11 review (~25-35 min).)
