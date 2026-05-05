# Migration Story 7c.5.G1: G1 DecisionCard Extend-and-Audit (Directive Ratification)

**Status:** in-progress *(Codex T0/T1 posted 2026-05-05; predecessor 7c.4b CLOSED at `8b12970`; siblings G0+G2A CLOSED at `e2aa599`; G5+G6 CLOSED per sprint status. **HALTED before T2 pending PRE-T2 cross-agent review** — serial dispatch only.)*
**Sprint key:** `migration-7c-5-g1-decision-card-extend-and-audit`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 2
**K-target:** 1.4× (heavier than fresh-author due to backward-consumer audit + contract-diff artifact + 2-class-regime migration)
**Estimated LOC:** ~400 (g1.py rewrite ~80 + schema regen ~50 + new shape-pin ~120 + new golden ~40 + _frozen_hashes.py ~40 + contract-diff artifact ~80 + backward-consumer-audit artifact ~50 + __init__.py edit)
**Gate-mode:** **`dual-gate-cross-agent-CONTRACT-EVOLUTION`** (NAMED gate-mode per Winston W3 Round-2 party-mode 2026-05-04)
**Cross-agent review:** false (per governance JSON entry; T11 tier is `standard` despite the gate-mode name — the "cross-agent" component refers to the **T1 PRE-T2 cross-agent review of contract-diff + backward-consumer audit artifacts**, NOT T11)
**R-tier:** R3 (full broad regression)
**T11-tier:** standard
**Lookahead-tier:** 2 (author-skeleton-ahead; substrate fully landed — G0/G2A canonical patterns on disk; placeholder `<TBD>` markers used for backward-consumer enumeration deferred to Codex T1)
**files_touched:** 3 modified (`g1.py`, `schema/g1.v1.schema.json`, `__init__.py`) + 5 new (`tests/parity/test_decision_card_g1_shape.py`, `tests/fixtures/decision_cards/g1_golden.json`, `app/models/decision_cards/_frozen_hashes.py`, `_bmad-output/implementation-artifacts/migration-7c-5-g1-contract-diff.md`, `_bmad-output/implementation-artifacts/migration-7c-5-g1-backward-consumer-audit.md`)

---

## Story

As the dev-agent,
I want the legacy G1Card (Slab 7a substrate; inherits from legacy `app.models.decision_cards.base.DecisionCard`) extended-and-migrated to inherit from the new `app.models.decision_cards._base.DecisionCardBase` (post-7c.4b shipped at commit `8b12970`) AND add FR-7c-51 `schema_version` field AND complete the four-file lockstep co-commit (regenerated schema + new shape-pin + new golden fixture),
So that G1 directive-ratification gate conforms to the post-Slab-7c contract while preserving every backward-consumer access pattern via the AMELIA-P4 frozen-hash delta-AC + per-call-site backward-consumer audit + diff-against-prior-contract artifact reviewed BEFORE T2 begins.

---

## Predecessor / Dependency Context

- **7c.4b** (CLOSED 2026-05-05 at `8b12970`): provides `DecisionCardBase` + `DecisionCardMeta` + `LOCKSTEP_CHECK` + class-conformance validator extension + C6 import-linter contract.
- **7c.5.G0 + 7c.5.G2A** (CLOSED at `e2aa599`): canonical fresh-author pattern on disk — `app/models/decision_cards/g0.py` + `g2a.py` + their schemas + their shape-pins + their goldens. **G1 migration MUST mirror this pattern's inheritance + field structure + validator/serializer idioms.**
- **7c.5.G5 + 7c.5.G6** (in flight 2026-05-05): later siblings consuming the same `DecisionCardBase`; close before G1 dispatches per the HELD constraint above.
- **Existing G1Card legacy substrate:** `app/models/decision_cards/g1.py` (39 LOC; inherits from legacy `app.models.decision_cards.base.DecisionCard`). Pre-extension SHA256: `4fe0e985d2285e3219b103424765dec009043564960ec43af1fb5710d2a1a196` (recorded by THIS story at T0 in `_frozen_hashes.py`).
- **Backward consumers (24 files identified at spec-author time; Codex T1 enumerates exhaustively):**
  - Production: `app/marcus/orchestrator/production_runner.py:411` constructs `G1Card(**common, trial_summary=...)`.
  - Tests: `tests/unit/models/decision_cards/_helpers.py`, `test_per_gate_strict.py`, `test_manifest_dotted_reference_resolver.py`, `test_discriminated_union_routing.py`; `tests/unit/marcus/test_routing_manifest_driven.py`; `tests/unit/gates/_helpers.py`.
  - Schema: `app/models/decision_cards/schema/g1.v1.schema.json` (regen target).
  - Documentation: `docs/dev-guide/sources-of-truth.md`, `docs/operator/production-trial-playbook.md`, `_bmad-output/implementation-artifacts/migration-3-2-decision-card-schema-family.md`, `_bmad-output/implementation-artifacts/migration-7a-3-pre-gate-marcus-shared-llm-node.md`, `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md`.
- **2-class-regime follow-on:** This story (and 7c.5.G2C/G3/G4 sibling extend-and-audit stories) IS the implementation of the deferred-inventory follow-on `slab-7c-7c-4b-decision-card-2-class-regime-migration`.

---

## Acceptance Criteria

### AC-7c.5.G1-A — Pre-T2 contract-diff + backward-consumer audit artifacts (Winston W3 + AMELIA-P4)

**Given** the prior G1 contract is shipped at `app/models/decision_cards/g1.py` with frozen-at-ship SHA256 `4fe0e985d2285e3219b103424765dec009043564960ec43af1fb5710d2a1a196`
**When** Codex executes T0/T1 deliverables
**Then** before T2 (extension) begins:
1. **`_bmad-output/implementation-artifacts/migration-7c-5-g1-contract-diff.md`** is authored — diff-against-prior-contract artifact enumerating: (a) every field on legacy `G1Card(DecisionCard)` and its disposition in migrated `G1Card(DecisionCardBase)` (preserved / re-declared / dropped); (b) every behavior on legacy `DecisionCard` base (drafted_proposal / evidence / risks / verb / meta with reject_rate / party_mode_contributions / consolidated_at / sanctum_warnings) and its disposition under `DecisionCardBase` (preserved / dropped / migrated); (c) FR-7c-51 `schema_version: Literal["v1"]` add; (d) explicit STATEMENT for each dropped field: "this field is dropped because no backward consumer accesses it" OR "this field is preserved by re-declaration on G1Card directly".
2. **`_bmad-output/implementation-artifacts/migration-7c-5-g1-backward-consumer-audit.md`** is authored — per-call-site verdict for every G1Card consumer (≥24 sites identified at spec-author time; Codex T1 grep `G1Card` AND `from app.models.decision_cards.g1` AND `from app.models.decision_cards import.*G1Card` exhaustively): (a) site path + line number; (b) field-access pattern observed; (c) verdict (preserved-via-re-declaration / preserved-via-DecisionCardBase / requires-update-at-this-story / requires-deferred-followon).
3. **`app/models/decision_cards/_frozen_hashes.py`** is authored — Python module exporting a frozen mapping of legacy gate hashes for AMELIA-P4 verification. Contents:
   ```python
   """Frozen-at-ship SHA256 hashes for Slab 7a legacy DecisionCard subclasses.
   
   Recorded BEFORE 7c.5.G1/G2C/G3/G4 extend-and-audit stories rewrite each gate.
   AMELIA-P4 delta-AC: extend-and-audit stories verify the on-disk legacy file
   matches the recorded hash BEFORE extension begins.
   """
   from __future__ import annotations
   
   FROZEN_AT_SHIP_HASHES: dict[str, str] = {
       "g1": "4fe0e985d2285e3219b103424765dec009043564960ec43af1fb5710d2a1a196",
       "g2c": "<TBD-codex-T0-records>",
       "g3": "<TBD-codex-T0-records>",
       "g4": "<TBD-codex-T0-records>",
   }
   
   __all__ = ["FROZEN_AT_SHIP_HASHES"]
   ```
   Codex T0 computes `g2c.py` / `g3.py` / `g4.py` SHA256 hashes via `python -c "import hashlib; print(hashlib.sha256(open('app/models/decision_cards/<gate>.py', 'rb').read()).hexdigest())"` and substitutes the four `<TBD>` placeholders.

**Cross-agent T1 review checkpoint:** Codex MUST surface a "T1 READY" notice at `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g1.t1-ready.md` listing the three deliverable paths + per-deliverable summary. Claude (or the cross-agent reviewer) reviews the contract-diff + backward-consumer audit artifacts BEFORE T2 begins. If the cross-agent reviewer flags a MUST-FIX, Codex remediates the artifacts and re-surfaces T1 READY before proceeding.

### AC-7c.5.G1-B — AMELIA-P4 frozen-hash delta-AC

**Given** `_frozen_hashes.py` records pre-extension SHA256 = `4fe0e985d2285e3219b103424765dec009043564960ec43af1fb5710d2a1a196` for g1.py
**When** Codex begins T2 (body extension)
**Then** at T2 start, Codex verifies: `hashlib.sha256(open("app/models/decision_cards/g1.py", "rb").read()).hexdigest() == FROZEN_AT_SHIP_HASHES["g1"]`. If FALSE → HALT (the on-disk file has drifted from the frozen-at-ship state; cross-agent reviewer must re-baseline before extension). If TRUE → proceed.

At T9 (post-extension), the on-disk hash will NOT match (intentional; body extended). The contract-diff artifact (AC-A) is the audit trail justifying the divergence.

### AC-7c.5.G1-C — Four-file lockstep co-commit (FR-7c-6 + FR-7c-7 + FR-7c-49)

**Given** AC-A artifacts approved + AC-B frozen-hash verified
**When** Codex executes T2-T5
**Then** the four files are co-committed in one diff:
1. `app/models/decision_cards/g1.py` — REWRITTEN: `class G1Card(DecisionCardBase)` (NEW inheritance from `app.models.decision_cards._base.DecisionCardBase`); preserve G1-specific fields per AC-A contract-diff verdicts; add `schema_version: Literal["v1"]`; add `gate_id: Literal["G1"]` + `gate_focus: Literal["trial_open"]` (closed Literals replacing legacy bare-string defaults); add `card_id: UUID4` + `trial_id: UUID4` + `created_at` + `verb: DecisionCardVerb` (re-declared per G0 pattern; not inherited because new `DecisionCardBase` is slimmer than legacy `DecisionCard`); preserve `trial_summary: str` (strip-then-non-empty validator per G2A pattern) + `opened_by: str` (min_length=1 preserved) + `next_nodes: list[str]` (default empty list preserved); use field_validator chain mirroring G2A pattern.
2. `app/models/decision_cards/schema/g1.v1.schema.json` — REGENERATED via `python -c "from app.models.decision_cards.g1 import G1Card; import json; print(json.dumps(G1Card.model_json_schema(), indent=2, sort_keys=True))" > app/models/decision_cards/schema/g1.v1.schema.json` (deterministic emission; sort_keys=True; FR-7c-51 schema_version v1 emitted from Literal field).
3. `tests/parity/test_decision_card_g1_shape.py` — NEW shape-pin: 9-10 test cases per G0/G2A pattern: field-presence (count depends on AC-A verdicts) + closed-enum red-rejection on `gate_id` (rejects `"G2A"` / `"G99"` / non-string) + closed-enum red-rejection on `gate_focus` (rejects `"final_operator_handoff"` / non-string) + JSON-Schema byte-match + golden round-trip + non-empty `trial_summary` + non-empty `opened_by` + frozen mutation rejection. MUST `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (AMEND-7d-i; bare import only).
4. `tests/fixtures/decision_cards/g1_golden.json` — NEW deterministic golden fixture with all required fields + UUID4-shape `card_id` / `trial_id` + tz-aware `created_at` + `meta.cache_state: "healthy"` + `meta.affected_nodes: []` + `meta.override_trail: []` + `gate_id: "G1"` + `gate_focus: "trial_open"` + `trial_summary` non-empty + `opened_by` non-empty + `next_nodes: []` + `verb: "approve"` + valid 64-char lowercase hex `decision_card_digest`.

### AC-7c.5.G1-D — Backward-consumer non-regression (post-migration verification)

**Given** AC-A backward-consumer audit lists every call site + per-site verdict
**When** the four-file lockstep lands (T6.2 verification)
**Then** `pytest tests/parity/ tests/parametrized_harness/ tests/unit/ -p no:randomly -q` PASSES with all per-gate construction tests green AND `app/marcus/orchestrator/production_runner.py:411` G1Card construction is verified by an integration test (existing or NEW per audit verdict). Any per-call-site update required by the audit (e.g., field-access pattern changed) is co-committed in this story OR explicitly deferred via a named follow-on at `_bmad-output/planning-artifacts/deferred-inventory.md`.

### AC-7c.5.G1-E — Class-conformance recognition + Pydantic-v2 14-idiom conformance

**Given** 7c.4b's class-conformance validator extension
**When** `scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` runs after this story lands
**Then** the validator confirms `tests/parity/test_decision_card_g1_shape.py` is structurally well-formed AND class-conformance count = T1-baseline + 1.

Pydantic-v2 14-idiom checklist conformance per `docs/dev-guide/pydantic-v2-schema-checklist.md`: inherited `validate_assignment=True` + inherited `extra="forbid"` + inherited `frozen=True` (from `DecisionCardBase` model_config) + closed Literals on `gate_id` / `gate_focus` / `schema_version` + tz-aware datetime via `enforce_tz_aware` + UUID4 typing via Pydantic `UUID4` (not bare `UUID`; mirror G2A per pattern-parity ratchet) + strip-then-non-empty validator on `trial_summary` (mirror G2A) + Field descriptions on every field.

---

## Tasks / Subtasks

- [x] **T0 — Frozen-hash recording (PRE-T1)**
  - [x] T0.1 Compute SHA256 hashes for legacy `g1.py` / `g2c.py` / `g3.py` / `g4.py`.
  - [x] T0.2 Author `app/models/decision_cards/_frozen_hashes.py` per AC-A bullet 3. Substitute the three `<TBD>` placeholders with computed hashes. Verify the spec-recorded G1 hash matches.
  - [x] T0.3 Confirm 7c.4b done; G0+G2A done; G5+G6 done (HELD condition satisfied — serial dispatch only).

- [ ] **T1 — Contract-diff + backward-consumer audit (Winston W3 + AMELIA-P4 deliverables)**
  - [x] T1.1 Author `_bmad-output/implementation-artifacts/migration-7c-5-g1-contract-diff.md` per AC-A bullet 1. Section structure:
    - §1 Legacy G1Card field disposition matrix
    - §2 Legacy DecisionCard base field disposition matrix
    - §3 New fields added (FR-7c-51 schema_version)
    - §4 Closed-enum tightening (gate_id / gate_focus from bare-string-with-default to closed Literal)
    - §5 Pattern-parity ratchets (UUID4 typing + strip-then-non-empty validators per G2A pattern)
    - §6 Net diff summary (fields added / preserved / dropped; behavior preserved / changed)
  - [x] T1.2 Author `_bmad-output/implementation-artifacts/migration-7c-5-g1-backward-consumer-audit.md` per AC-A bullet 2. Per-call-site enumeration (grep `G1Card` exhaustively; minimum 24 sites identified at spec-author time):
    - Per-site row: path:line + field-access pattern + verdict
  - [x] T1.3 Drop `_codex-handoff/7c-5-g1.t1-ready.md` notice listing the three deliverable paths + per-deliverable summary; HALT and await cross-agent T1 review verdict.
  - [ ] T1.4 (gated; only after cross-agent T1 review PASS) refresh broad-regression baseline. Run sandbox-AC validator on this spec; expect PASS. Record class-conformance baseline (current expected = 13 + Codex G5/G6 increment if landed, so 14 or 15).

- [ ] **T2 — Frozen-hash AMELIA-P4 delta-AC verification + G1Card body extension (AC-B + AC-C)**
  - [ ] T2.1 Verify per AC-B: `hashlib.sha256(open("app/models/decision_cards/g1.py", "rb").read()).hexdigest() == FROZEN_AT_SHIP_HASHES["g1"]`. HALT if mismatch.
  - [ ] T2.2 Rewrite `app/models/decision_cards/g1.py` per AC-A contract-diff verdicts: change inheritance to `DecisionCardBase` from `_base.py`; re-declare card_id/trial_id (UUID4) + gate_id/gate_focus (closed Literals) + created_at + verb + schema_version; preserve trial_summary (strip-then-non-empty) / opened_by (min_length=1) / next_nodes (default empty); add field_validator chain mirroring G2A pattern; add field_serializer for any Path fields if AC-A audit identifies them; update `__all__` if needed.
  - [ ] T2.3 Update `app/models/decision_cards/__init__.py` if the flat-export pattern requires re-import (verify post-G0/G2A/G5/G6 union state at T1).

- [ ] **T3 — Schema regeneration (AC-C)**
  - [ ] T3.1 Regenerate `app/models/decision_cards/schema/g1.v1.schema.json` via the canonical command. Byte-compare with previous schema; document all schema-emission changes in the contract-diff artifact (T1.1).

- [ ] **T4 — Golden fixture authoring (AC-C)**
  - [ ] T4.1 Author `tests/fixtures/decision_cards/g1_golden.json` with deterministic stable values per AC-C bullet 4. Verify byte-deterministic round-trip.

- [ ] **T5 — Shape-pin authoring (AC-C + AC-E)**
  - [ ] T5.1 Author `tests/parity/test_decision_card_g1_shape.py` with 9-10 test cases mirroring G2A's pattern (field-presence + 2 closed-enum rejections + JSON-Schema byte-match + golden round-trip + 2-3 non-empty validations + frozen mutation rejection).
  - [ ] T5.2 **MANDATORY parallel-dispatch guardrail #1 self-check (carried even though G1 is serial-dispatch):** grep your shape-pin file for `FOUR_FILE_GLOBS` and `all_four_present`. ZERO matches outside bare `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` import lines.

- [ ] **T6 — Verification battery (R-tier R3 — full broad regression)**
  - [ ] T6.1 Focused: `pytest tests/parity/test_decision_card_g1_shape.py -p no:randomly -q --tb=short` PASS (9-10 tests).
  - [ ] T6.2 AC-D backward-consumer non-regression: `pytest tests/parity/ tests/parametrized_harness/ tests/unit/ -p no:randomly -q --tb=short` PASS UNCHANGED. Particularly verify `tests/unit/marcus/test_routing_manifest_driven.py` + `tests/unit/models/decision_cards/test_per_gate_strict.py` + `tests/unit/models/decision_cards/test_discriminated_union_routing.py` green.
  - [ ] T6.3 AMEND-7d-i AST-scan: `pytest tests/structural/test_tw_7c_3_firing_spec_single_source.py -p no:randomly -q --tb=short` PASS.
  - [ ] T6.4 Smoke: `pytest --smoke -p no:randomly -q --tb=short` 200-nodeid baseline UNCHANGED.
  - [ ] T6.5 R3 broad: `pytest -p no:randomly -q --tb=line` failure count ≤ T1 baseline. Per-failure attribution required at T10.
  - [ ] T6.6 Class-conformance: validator reports T1-baseline + 1.
  - [ ] T6.7 Lint-imports: 12 KEPT / 0 broken UNCHANGED.
  - [ ] T6.8 Sandbox-AC: PASS.
  - [ ] T6.9 Ruff: clean on g1.py + test_decision_card_g1_shape.py + _frozen_hashes.py + __init__.py.

- [ ] **T10 — Codex self-review (NEW CYCLE T10)**
  - [ ] T10.1 Codex authors `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g1.ready-for-review.md` summarizing: 4-file lockstep verification + frozen-hash AMELIA-P4 verdict + cross-agent T1 review verdict (link) + backward-consumer audit verdict (no untracked-call-site break) + class-conformance delta + R3 broad-regression delta with per-failure attribution + AMEND-7d-i compliance + Pydantic-v2 14-idiom conformance + 2-class-regime migration confirmation (G1Card now inherits `DecisionCardBase` from `_base.py`).
  - [ ] T10.2 Self-review across 3 lenses (Blind / Edge / Auditor) inline.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md` (predecessor; D1-D8).
3. `_bmad-output/implementation-artifacts/7c-4b-code-review-2026-05-05.md` (T11 verdict; documents 2-class regime).
4. `_bmad-output/implementation-artifacts/7c-5-g0-code-review-2026-05-05.md` AND `7c-5-g2a-code-review-2026-05-05.md` (sibling fresh-author T11 verdicts).
5. `app/models/decision_cards/_base.py` (canonical `DecisionCardBase`).
6. `app/models/decision_cards/base.py` (LEGACY `DecisionCard` being migrated AWAY FROM).
7. `app/models/decision_cards/g1.py` (LEGACY G1Card pre-extension; pre-extension SHA256 in spec metadata above).
8. `app/models/decision_cards/g0.py` AND `g2a.py` (canonical fresh-author patterns; mirror inheritance + field structure + validators + serializers).
9. `tests/parity/test_decision_card_g0_shape.py` AND `test_decision_card_g2a_shape.py` (canonical shape-pin patterns).
10. `tests/fixtures/decision_cards/g0_golden.json` AND `g2a_golden.json` (canonical golden patterns).
11. `app/marcus/orchestrator/production_runner.py:411` (PRIMARY backward consumer; G1Card construction site).
12. `app/parity/contracts/tw_7c_3_firing.py` (LOCKSTEP_CHECK; AMEND-7d-i).
13. `tests/structural/test_tw_7c_3_firing_spec_single_source.py` (AMEND-7d-i AST-scan boundary).
14. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G1 = directive-ratification gate; extend-and-audit per §1).
15. `docs/dev-guide/pydantic-v2-schema-checklist.md` (AC-E 14-idiom).
16. `docs/dev-guide/dev-agent-anti-patterns.md` (schema/test-authoring trap catalog).
17. Governance JSON `7c-5-g1` entry (extend-and-audit T1 deliverables binding).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks (only `.venv/Scripts/` invocations + `python -c "import hashlib..."` for hash computation + `python -c "from ... import ..."` for schema regeneration). Sandbox-AC: PASS (verified at T0).

---

## Dispatch Hold

**HELD until G5+G6 close** (not G0/G2A — those are already done; the constraint is keeping main-thread-coordinator focus on the new extend-and-audit pattern + serial dispatch). After G5+G6 close, dispatch G1 alone (NOT concurrent with G2C/G3/G4 — all 4 extend-and-audit stories touch the same legacy `DecisionCard` migration surface; concurrent dispatch creates merge conflicts on `__init__.py` + `_frozen_hashes.py` + the legacy `base.py` if it gets removed).

At dispatch-time, Claude verifies AMELIA-P2 freshness + re-runs sandbox-AC on this spec.

## Cross-agent T1 review checkpoint (NEW pattern for extend-and-audit)

Unlike the fresh-author pattern (Codex T1-T10 → Claude T11), this story has TWO Claude review checkpoints:
1. **Pre-T2 cross-agent T1 review** — Claude (or designated cross-agent reviewer) reads the contract-diff + backward-consumer audit + frozen-hash artifacts BEFORE Codex begins T2. Verdict at `_bmad-output/implementation-artifacts/7c-5-g1-t1-cross-agent-review-2026-05-NN.md`. PASS allows T2 to proceed; FAIL HALTs Codex with required remediation.
2. **Post-T9 standard T11 review** — Claude reads the body extension + verification battery results. Verdict at `_bmad-output/implementation-artifacts/7c-5-g1-code-review-2026-05-NN.md`.

Both verdicts must PASS before commit + flip done.

---

## Dev Agent Record

### Debug Log

- 2026-05-05: Confirmed dependency close state in `sprint-status.yaml`: 7c.4b, G0, G2A, G5, and G6 are `done`.
- 2026-05-05: Computed frozen hashes: G1 `4fe0e985d2285e3219b103424765dec009043564960ec43af1fb5710d2a1a196`; G2C `237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a`; G3 `bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3`; G4 `98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a`.
- 2026-05-05: Ran G1 consumer grep commands required by T1 and consolidated 24 executable `G1Card` sites.
- 2026-05-05: Ran class-conformance baseline: `PASS: 15 parity contract file(s) conform (11 activation + 4 decision-card shape-pin)`.
- 2026-05-05: Ran sandbox-AC validator on this spec: `PASS - no sandbox-AC violations across 1 story file(s).`

### Completion Notes

- T0/T1 deliverables are complete and posted for cross-agent review.
- `app/models/decision_cards/g1.py` remains unmodified at T1.
- Codex is halted before T2 until the required cross-agent T1 review verdict passes.

### File List

- `app/models/decision_cards/_frozen_hashes.py`
- `_bmad-output/implementation-artifacts/migration-7c-5-g1-contract-diff.md`
- `_bmad-output/implementation-artifacts/migration-7c-5-g1-backward-consumer-audit.md`
- `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g1.t1-ready.md`
- `_bmad-output/implementation-artifacts/migration-7c-5-g1-decision-card-extend-and-audit.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log

- 2026-05-05: Marked G1 in progress, recorded T0 hashes, authored T1 contract-diff and backward-consumer audit artifacts, posted T1-ready handoff, and halted before T2.
