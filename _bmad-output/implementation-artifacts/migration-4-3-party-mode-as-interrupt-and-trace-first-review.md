# Migration Story 4.3: Party-Mode-as-`interrupt()` + Trace-First Review

**Status:** ready-for-dev
**Sprint key:** `migration-4-3-party-mode-as-interrupt-and-trace-first-review`
**Epic:** Slab 4 — M4 gate.
**Pts:** 4 | **Gate:** single (per governance JSON `4-3.expected_gate_mode = "single-gate"`, rationale: null). **K-target:** ~1.3× (target 10 / floor 8).

**Predecessor:** 4.1 + 4.2 done. Drafted-for-queue.

---

## T1 Readiness Block

1. Governance: `4-3.expected_gate_mode = "single-gate"`.
2. Substrate: `app/gates/` exists; resume_api.py + verdict path pattern landed at 3.3 (canonical OperatorVerdict at `app/models/state/operator_verdict.py` per 3.3 substrate-aware adaptation).
3. **LangGraph `interrupt()` substrate** — verify Slab-1 LangGraph interrupt pattern; if Slab-2 specialists use `interrupt()` at `_act` for HIL gates, that's the precedent.
4. **PartyModeContribution model** is NEW — schema-shape per 31-1 precedent (Pydantic v2 strict + four-file-lockstep applies).
5. **LangSmith trace-link evidence** — trace tags from Slab-2 substrate provide span_id + trace_id; FR42 requires bmad-code-review gates cite a trace link as evidence.
6. **bmad-code-review skill** — verify location at `skills/bmad-code-review/` or equivalent; AC-B integration touches this skill.
7. Severance posture.

### Substrate sweep

- `app/gates/__init__.py` exists; canonical OperatorVerdict at `app/models/state/operator_verdict.py`.
- `langgraph` dep present per Slab 1.
- `bmad-code-review` skill present per BMAD installation.

### TEMPLATE scope decisions

**Decision #1 — Bounded scope:** (a) `app/gates/party_mode_as_interrupt.py` wrapping party-mode gate as checkpointed `interrupt()` node; (b) `PartyModeContribution` Pydantic v2 strict model; (c) consolidated DecisionCard emission before operator verdict; (d) M4 evidence — at least one bmad-code-review gate cites LangSmith trace link in finding record. NOT in scope: ledger (4.4); transports (3.4 done); Cora (4.2 done).

**Decision #2 — `PartyModeContribution` shape:** `{contribution_id: UUID4, persona: str, payload: dict[str, Any], submitted_at: datetime (tz-aware), trace_link: str | None}`. List of contributions consumed by `party_mode_as_interrupt(contributions: list[PartyModeContribution]) -> DecisionCard`; emits consolidated DecisionCard with `meta.party_mode_contributions = [...]`.

**Decision #3 — Trace-link evidence format:** `trace_link: str` shape pin = `https://smith.langchain.com/traces/<trace_id>` OR repo-relative trace export path; FR42 satisfied when ≥1 bmad-code-review finding record contains a trace_link matching the regex.

---

## Story

As a **BMAD reviewer consuming gate evidence per FR41+FR42**,
I want **`app/gates/party_mode_as_interrupt.py` wrapping party-mode as a checkpointed interrupt() node + `PartyModeContribution` Pydantic v2 strict model + consolidated DecisionCard emission + M4 evidence (bmad-code-review gate cites LangSmith trace link in finding record)**,
So that **FR41 + FR42 are met and party-mode becomes a first-class graph primitive (not just a skill invocation)**.

---

## Acceptance Criteria

### AC-4.3-A — `app/gates/party_mode_as_interrupt.py` wrapper

- **Given** no `app/gates/party_mode_as_interrupt.py` exists; `langgraph.types.Command + interrupt()` substrate from Slab-1
- **When** the dev agent authors `party_mode_as_interrupt(contributions, gate_id) -> DecisionCard` that:
  1. Validates each contribution against `PartyModeContribution` Pydantic
  2. Emits `interrupt()` checkpoint with consolidated DecisionCard payload
  3. Resumes via OperatorVerdict per 3.3 resume_api flow
- **Then** integration test simulates multi-persona contribution + verdict resume.
- **Test pin:** `tests/integration/gates/test_party_mode_as_interrupt.py` — 1 test (full-flow integration).

### AC-4.3-B — `PartyModeContribution` schema (four-file-lockstep per 31-1)

- **Given** no model exists
- **When** dev authors at `app/models/gates/party_mode_contribution.py` (or co-located with party_mode_as_interrupt.py — verify naming convention with 3.2 DecisionCard precedent)
- **Then** four-file-lockstep present: model + JSON Schema + shape-pin test + golden fixture
- **Test pins:** `test_party_mode_contribution_strict.py` (3 tests: strict_config + tz-aware + persona-non-empty); `test_party_mode_contribution_json_schema_parity.py` (1 test).

### AC-4.3-C — Consolidated DecisionCard meta enrichment

- **Given** DecisionCardMeta from 3.2
- **When** party_mode_as_interrupt emits the card
- **Then** `meta.party_mode_contributions: list[PartyModeContribution]` is populated; `meta.consolidated_at: datetime`
- **Test pin:** `test_consolidated_decision_card_carries_contributions.py` — 1 test.

### AC-4.3-D — M4 evidence: bmad-code-review cites LangSmith trace link

- **Given** real story review at M4 (this is operator-driven evidence; could be exercised at 4.7 SLAB CLOSING)
- **When** a bmad-code-review gate's finding record contains `trace_link: <regex match>`
- **Then** M4 Required Evidence per FR42 satisfied
- **Test pin:** `test_m4_evidence_trace_link_present.py` — 1 test asserting that when `bmad-code-review` is invoked with the trace-link convention enabled, ≥1 finding record contains a trace_link string matching the FR42 regex; OR DEFER to 4.7 SLAB CLOSING for operator-evidence paste.

### AC-4.3-E — Anti-pattern catalog harvest

NO new entries expected.

### AC-4.3-F — TEMPLATE compliance

R1, R6, R8 honored.

### AC-4.3-G — D12 close protocol (single-gate; FOUR-line)

1. Invariant preservation: party-mode as graph primitive; FR41+FR42 met.
2. Anti-pattern harvest: N/A.
3. Migration-guide update: §"Party-Mode-as-Interrupt" added.
4. TEMPLATE compliance: R1, R6, R8.

### AC-4.3-H — Sprint-status state-flips at filing AND close.

---

## File Structure Requirements

### NEW files

- `app/gates/party_mode_as_interrupt.py`
- `app/models/gates/party_mode_contribution.py` + schema/party_mode_contribution.v1.schema.json
- `tests/integration/gates/{test_party_mode_as_interrupt, test_consolidated_decision_card_carries_contributions, test_m4_evidence_trace_link_present}.py`
- `tests/unit/gates/{test_party_mode_contribution_strict, test_party_mode_contribution_json_schema_parity}.py`
- `tests/fixtures/gates/party_mode_contribution_golden.json`

### MODIFIED files

- `app/gates/__init__.py` — exports party_mode_as_interrupt.
- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` — entry.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-H.

---

## Testing Requirements

**K-target ~1.3× (target 10 / floor 8).** AC-A:1 + AC-B:4 (3 strict + 1 schema parity) + AC-C:1 + AC-D:1 = **7 collected; honest K-floor 6**. RIDER: add 1 negative integration test for AC-A (invalid contribution rejected) + 1 schema-roundtrip golden test = honest **8 K-floor**. Within band.

Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
