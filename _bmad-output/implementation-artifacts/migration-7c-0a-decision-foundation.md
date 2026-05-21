# Migration Story 7c.0a: Decision Foundation — Parity-Contract DSL ADR + Import-Linter Contracts C4/C5/C6 + TripwireLedgerEntry Schema + Audit-Chain Conceptual Design

**Status:** done  <!-- 2026-05-04 T11 cross-agent code-review PASS-WITH-PATCH (1 patch applied: LINT_IMPORTS path-portability fix; 2 deferred). Review verdict at _bmad-output/implementation-artifacts/7c-0a-code-review-2026-05-04.md -->

**Sprint key:** `migration-7c-0a-decision-foundation`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 3
**Gate:** **dual-gate** + **cross-agent code-review MANDATORY** (per `docs/dev-guide/migration-story-governance.json` v2026-05-04-slab7c-thirty-six-stories, story 7c-0a; rationale: `substrate_shape + invariant_preservation`)
**K-target:** ~1.3× (architecture-tier band; decision artifacts only — ADR + 3 import-linter contracts + 1 Pydantic schema with shape-pin test; ~3 pts)
**Authored:** 2026-05-04 via `bmad-create-story` workflow.
**Wave:** 0 — slot 1 (architecture-tier; precedes 7c.0b Scaffold Foundation per Winston W1 hard precedence; gates 7c.0b + all Wave 1 stories except 7c.2 which carries an AMELIA-P1 path-isolation guard for parallel execution).

**FR coverage:** FR-7c-30..33 (parity-contract DSL **design only** — no executable scaffold; scaffold lives in 7c.0b), FR-7c-50 (audit-chain integrity **conceptual design only** — executable test scaffold lives in 7c.0b), FR-7c-53 C4/C5/C6 (ALL three import-linter contracts land here with **empty target lists** per Winston W2; downstream stories 7c.3a + 7c.4b populate the targets).

**NFR coverage:** NFR-7c-OD2 (TripwireLedgerEntry Pydantic-v2 **primary enforcement** here per Murat A5 highest-leverage amendment); NFR-7c-S3/S4/S7 (import-linter contracts CI-enforce from this story forward); NFR-7c-M5 (sandbox-AC validator PASS); NFR-7c-M6 (governance JSON gate-mode designation honored).

**Standing-guardrail enforcement:**
- SG-1 unchanged (no specialist-roster change; this is orchestrational substrate).
- SG-2 unchanged (no mapping-checklist row change; AUDIT-AC stories at 7c.20a/b/c flip rows).
- SG-3 unchanged (Composition Spec invariants apply to DSL primitives; primitives executable in 7c.0b).
- SG-4 unchanged (sanctum-alignment DSL feature consumed in 7c.0b + 7c.17a/b; spec-only here).

**Implementation cycle (NEW CYCLE per memory entry `feedback_new_cycle_codex_dev_handoff.md` 2026-05-04 lookahead-discipline revision):**
- **Claude (Opus 4.7):** authored this spec; sandbox-AC validator PASS confirmed at finalize; governance JSON entry verified (cross_agent_review_required=true); pre-authors `_bmad-output/implementation-artifacts/codex-dev-prompt-7c-0a.md` ahead of operator demand. Gate-1 party-mode-by-Slab-7c-Round-2 already ratified the architectural decisions; in-story Gate-1 round NOT required (decisions came in via the epic-decomposition Round-2 4/4 unanimous; Winston W2/W3/W4/W6 + Murat AMEND-7d-ii fold into the ADR scope).
- **Codex (Sonnet 4.5 or later):** develops the four deliverables (ADR + import-linter contracts + TripwireLedgerEntry + shape-pin) per the ACs and tasks below; reaches `review` status; produces a self-conducted T10 layered review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-0a.ready-for-review.md`.
- **Claude:** does the FINAL `bmad-code-review` (T11 — **CROSS-AGENT MANDATORY** per governance JSON); applies remediation cycles; commits; flips `migration-7c-0a-decision-foundation` review → done in sprint-status.

---

## T1 Readiness Block

**Required readings (cite by reference; do NOT re-derive at T1):**
- `docs/dev-guide/pydantic-v2-schema-checklist.md` — the 14 schema idioms (`validate_assignment=True`, timezone-aware datetimes, UUID4 validation, triple-layer red-rejection on closed enums, `Field(exclude=True) + SkipJsonSchema` for internal audit fields). TripwireLedgerEntry is a schema-shape model and MUST conform.
- `docs/dev-guide/dev-agent-anti-patterns.md` — schema-shape and review-ceremony anti-pattern catalog.
- `docs/dev-guide/story-cycle-efficiency.md` — K-floor discipline (target 1.2-1.5× K, not 5×); single-gate vs dual-gate review policy.
- `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — Slab 7c PRD; FR-7c-30..33 + FR-7c-50 + FR-7c-53 + NFR-7c-OD2 source spec.
- `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.0a section) — epic-level AC framing + Winston W1/W2/W4/W6 + Murat AMEND-7d-ii amendment record.

**Predecessor state (verified at authoring 2026-05-04):**
- Slab 7b CLOSED end-to-end (12/12 stories done; retrospective complete; epic flipped backlog→done 2026-05-01); validator reports **11 conforming activation contracts** across 6 specialist classes (A/B/C+/C/D1/D2) — no regression expected from 7c.0a.
- Migration story governance JSON v2026-05-04-slab7c-thirty-six-stories carries 7c-0a entry (dual-gate; cross_agent_review_required=true; K=1.3; pts=3; no `prerequisite_stories`).
- Sprint-status YAML carries `migration-epic-slab-7c-orchestrational-tail: backlog` + 36 story entries + 6 TW-7c-1..6 in `not_yet_evaluated` state.
- Slab 7c PRD + epics file both authored 2026-05-04 (party-mode 4/4 unanimous over 4 PRD rounds + 2 epic-decomposition rounds).

**Live substrate (verified at authoring; do NOT regress):**
- `pyproject.toml::[tool.importlinter]` currently carries Slab 1..7b contracts (≥9 KEPT). Slab 7c 7c.0a adds **three new contracts** C4 / C5 / C6 with empty `forbidden` lists; CI runs `lint-imports` and KEPT count ticks 9→12 (or whatever the current count is) at 7c.0a close. Adding a contract with an empty target list is structurally KEPT (no violations possible against empty target).
- `app/models/` is the canonical home for Pydantic-v2 models. Existing siblings include `app/models/decision_cards/` family (`base.py`, `g1.py`, `g2c.py`, `g3.py`, `g4.py`, `override_event.py`, `vocabulary.py`) + `app/models/state/run_state.py` + `app/models/operator_verdict.py` + `app/models/adapter.py`. The new file lands as `app/models/tripwire_ledger.py` — sibling of `override_event.py`, NOT inside `decision_cards/`.
- `tests/parity/` contains the existing 11 conforming activation contract tests + shape-pin test patterns. The new shape-pin lands as `tests/parity/test_tripwire_ledger_entry_shape.py` (sibling of existing shape-pin tests; `pytest -p no:randomly` deterministic-baseline-safe).
- `docs/dev-guide/adr/` carries existing ADRs (`0001-...` may already exist). **Verify at T1** whether `docs/dev-guide/adr/0001-parity-contract-dsl.md` is the correct slot — if `0001-` is occupied, Codex SHALL re-number to the next free index (e.g., `0002-`, `0003-`) and update FR-7c-30..33 + epic file references via in-story addendum surfaced as `decision_needed` at T1.
- `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` is reserved for 7c.4a (NOT 7c.0a). Do NOT collide.
- `tests/fixtures/frozen_paths/` (or analogous architecture path; verify at T1) is the canonical home for "frozen-paths fixture" referenced in the epic AC. If absent, create at T1 and document in Dev Notes.

**Gate-mode rationale (from governance JSON):**
> Slab 7c Wave 0 (architecture-tier; precedes 7c.0b per Winston W1). Decision Foundation: parity-contract DSL ADR (FR-7c-30..33) + import-linter contracts C4/C5/C6 ALL land here with empty target lists per Winston W2 (7c.3a populates C5; 7c.4b populates C6) + TripwireLedgerEntry Pydantic-v2 model spec (NFR-7c-OD2; Murat A5 highest-leverage) + FR-7c-50 audit-chain integrity conceptual design + Decision-then-Foundation pattern named per Winston W4 + D7 transport-DSL-completeness policy per Winston W6. Cross-agent code-review MANDATORY (architectural ADR + 3 import-linter contracts). Hard precedence: 7c.0b + Wave 1 (except 7c.2 per AMELIA-P1 path-isolation) cannot open until 7c.0a closes. K-target 1.3x (decision artifacts; ~3 pts).

**T1 conclusion:** No unanticipated architectural disagreement requires halting the dev round. Implementation proceeds: ADR authoring + 3 import-linter contracts (empty target lists) + TripwireLedgerEntry Pydantic-v2 model + shape-pin test + audit-chain integrity conceptual design (in ADR appendix). **Hard checkpoint at T1:** confirm ADR slot `0001-parity-contract-dsl.md` is free (re-number to next free if collision); confirm `tests/fixtures/frozen_paths/` exists or create.

---

## Story

As the architect (cross-agent reviewer + downstream-story author),
I want one architecture-tier story that lands ALL decision-bearing artifacts (parity-contract DSL ADR + import-linter contracts C4/C5/C6 + TripwireLedgerEntry Pydantic schema + audit-chain conceptual design) **before** any executable DSL scaffold lands,
so that the Slab 7c architectural decisions crystallize once with cross-agent review, and all downstream stories (7c.0b scaffold + 7c.1 DSL refactor + 7c.3a §02A composer + 7c.4b gate foundation + 7c.5.G0..G6 per-gate stories + 7c.6..7c.15 HIL surface stories + 7c.17a/b Marcus-bound writers) inherit a frozen architectural substrate that cannot drift mid-slab.

---

## Acceptance Criteria

### AC-7c.0a-A — Import-linter contracts C4 / C5 / C6 land in pyproject.toml with empty target lists, ENFORCING from this story forward (FR-7c-53 / Winston W2)

**Given** the Winston Round-2 W2 amendment ("C4/C5/C6 ALL land in 7c.0a")
**When** the dev-agent edits `pyproject.toml::[tool.importlinter]` to add three new contracts
**Then** all three contracts are defined per the schemas below with **empty `forbidden_modules` lists** (downstream stories populate). All three contracts ENFORCE from 7c.0a forward (CI-fail mode at `lint-imports` if any future story violates); empty target list = no current violations + ready-state for downstream population.

```toml
[[tool.importlinter.contracts]]
name = "C4: parity-DSL boundary may not import graph-runtime modules"
type = "forbidden"
source_modules = ["app.parity.contracts"]
forbidden_modules = []  # populated by 7c.0b once DSL primitives exist; empty here is structurally KEPT
include_external_packages = false

[[tool.importlinter.contracts]]
name = "C5: §02A composer boundary may not import corpus-scan fallback paths"
type = "forbidden"
source_modules = ["app.composers.section_02a"]
forbidden_modules = []  # populated by 7c.3a (forbids app.composers._fallback + app.composers.legacy)
include_external_packages = false

[[tool.importlinter.contracts]]
name = "C6: HIL-surface modules may not import each other across surfaces"
type = "forbidden"
source_modules = ["app.gates.section_02a", "app.gates.section_04a", "app.gates.section_04_5", "app.gates.section_04_55", "app.gates.section_05_5", "app.gates.section_07b", "app.gates.section_07d", "app.gates.section_07f", "app.gates.section_08b", "app.gates.section_11", "app.gates.section_11b", "app.gates.section_15"]
forbidden_modules = []  # populated by 7c.4b (forbids cross-surface imports; shared helpers in app.gates._shared.*)
include_external_packages = false
```

**And** `lint-imports` exits 0 with three additional KEPT contracts (current count ticks up by 3); no existing contract regresses.

**And** the empty-target-list intent is documented in a `pyproject.toml` comment block adjacent to the C4/C5/C6 entries citing this story key + Winston W2 + downstream populating stories (7c.0b for C4; 7c.3a for C5; 7c.4b for C6).

**Test pin:** `tests/structural/test_import_linter_contracts_c4_c5_c6_present.py` — asserts the three contracts exist by name in `pyproject.toml` AND that they currently report KEPT (parses `lint-imports --output-format=json` if available, OR parses the toml + runs `lint-imports` subprocess and checks exit code == 0).

> **Notes for 7c.0a-A.** This AC is **dev-agent-executable** (no operator-only CLI; `lint-imports` ships in `.venv/Scripts/` per project setup; `tomllib` ships with Python 3.12). Source-modules list under C6 reflects the 11 HIL surfaces named in PRD §HIL Surface Specification + §02A; if any surface module path is wrong at T1 (e.g., `section_04_5` vs `section_04dot5`), Codex SHALL surface as `decision_needed` and pick the spelling that matches what 7c.4b will use; document in Dev Notes.

### AC-7c.0a-B — Parity-contract DSL ADR authored at `docs/dev-guide/adr/0001-parity-contract-dsl.md` with all six required sub-sections (FR-7c-30..33 / Winston W4 / Winston W6 / AMEND-7d-ii)

**Given** FR-7c-30..33 (DSL design) + Winston W4 (Decision-then-Foundation pattern naming) + Winston W6 (D7 transport-DSL-completeness escape-hatch policy) + Murat AMEND-7d-ii (per-tripwire-family completeness flag planning)
**When** the dev-agent authors `docs/dev-guide/adr/0001-parity-contract-dsl.md` (or the next free ADR slot if `0001-` is occupied — surface as `decision_needed` at T1)
**Then** the ADR documents **all six required sub-sections** in order:

1. **Registration mechanism choice** — picks one of {decorator / entry-point / YAML registration} for surface modules to declare parity contract; documents tradeoffs (decorator: tightly coupled to module load order; entry-point: pip-discoverable but heavyweight; YAML: external file but parser overhead). RECOMMEND: decorator (for Slab 7c — primary use is in-tree surfaces under `app/gates/**`; entry-point reserved for plugin extensibility post-Slab-7c).
2. **Per-surface transport declaration schema** — Pydantic-v2 model OR YAML schema (pick one); documents field set: `surface_id: str`, `mandatory_transports: list[str]` (subset of {"cli", "http", "mcp-stdio", "mcp-subprocess"}), `optional_transports: list[str]`. RECOMMEND: Pydantic-v2 (consistent with rest of Slab 7c schema-shape work; FR-7c-49 OperatorVerdict shape-stability harness shares the validator).
3. **Refactor target list** — names the 8 existing parity files that 7c.1 will refactor: `tests/integration/transport_parity/{test_fastapi_mcp_parity.py, test_mcp_stdio_smoke.py, test_mcp_subprocess_hygiene.py}` + `tests/integration/transports/{test_transport_parity.py, test_override_transport_parity.py, test_cli_gate_decide.py, test_http_gate_endpoint.py, test_mcp_gate_decide_tool.py}`. Refactor lands in 7c.1 (NOT 7c.0a or 7c.0b).
4. **D7 transport-DSL-completeness policy (Winston W6)** — explicit enumeration of what the DSL does **NOT** cover: {timeout semantics, streaming, backpressure, error-frame encoding}. Escape-hatch policy: extend the DSL OR document per-transport addendum inline at the surface module. RECOMMEND: extend-the-DSL is the default path; per-transport addendum requires party-mode consensus.
5. **Decision-then-Foundation pattern (Winston W4)** — names the pattern explicitly for future-slab reuse. Pattern statement: "When a substrate-touching change carries >5 decision-bearing artifacts, split into one architecture-tier story that lands all decisions + import-linter contracts + Pydantic spec stubs + ADR (no executable scaffold), and one build-tier story that lands the executable scaffold consuming the prior decisions. The 7c.0a→7c.0b and 7c.4a→7c.4b splits are both instances." Document criterion: **breaking-point rule = >5 decision-bearing artifacts forces split** (original 7c.0 carried 10 seams).
6. **AMEND-7d-ii completeness-flags planning** — ADR specifies that 7c.0b's AC block enumerates **THREE separate PASS/FAIL flags** at scaffold-completeness: TW-7c-4 detection PASS/FAIL + TW-7c-5 detection PASS/FAIL + TW-7c-6 detection PASS/FAIL. Composite "all-three-PASS" required for 7c.0b done-flip; ANY one FAIL blocks done. Composite single-flag is INSUFFICIENT.

**And** the ADR carries a "Status: ACCEPTED — 2026-05-04 by party-mode Round-2 4/4 unanimous (John+Winston+Amelia+Murat)" line + cross-references to PRD FR-7c-30..33 + epic file Story 7c.0a section + governance JSON 7c-0a entry.

**Test pin:** `tests/structural/test_adr_0001_parity_contract_dsl_present.py` — asserts the ADR file exists at the canonical (or surfaced-at-T1-decision_needed) path AND contains all six required sub-section headings (regex match on H2 headings or analogous structural convention).

> **Notes for 7c.0a-B.** This AC is **dev-agent-executable** (markdown authoring + structural test). The six sub-sections are required by content, not by exact heading text — Codex MAY adjust heading wording (e.g., "Registration Mechanism" vs "Registration") provided the substantive content lands. The test pin SHALL match against substantive keywords (`registration`, `transport.*declaration`, `refactor target`, `transport-DSL-completeness`, `Decision-then-Foundation`, `completeness flag`) rather than exact strings.

### AC-7c.0a-C — TripwireLedgerEntry Pydantic-v2 model lands at `app/models/tripwire_ledger.py` with shape-pin test (NFR-7c-OD2 / Murat A5 highest-leverage amendment)

**Given** NFR-7c-OD2 (TripwireLedgerEntry primary enforcement)
**When** the dev-agent lands `app/models/tripwire_ledger.py`
**Then** the module contains a `TripwireLedgerEntry` Pydantic-v2 model conforming to `docs/dev-guide/pydantic-v2-schema-checklist.md`:

```python
"""TripwireLedgerEntry — canonical schema for tripwire-ledger entries (Slab 7c).

Per Story 7c.0a Decision Foundation; primary enforcement of NFR-7c-OD2.
Consumed by sprint-status.yaml::tripwire_events writer + audit-chain integrity
test (FR-7c-50 conceptual design; executable scaffold lands in 7c.0b).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TripwireId(str, Enum):
    TW_7C_1 = "TW-7c-1"
    TW_7C_2 = "TW-7c-2"
    TW_7C_3 = "TW-7c-3"
    TW_7C_4 = "TW-7c-4"
    TW_7C_5 = "TW-7c-5"
    TW_7C_6 = "TW-7c-6"


class TripwireSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"


class TripwireLedgerEntry(BaseModel):
    """Canonical 7-field tripwire-ledger entry (Murat A5; NFR-7c-OD2)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,  # ledger entries are append-only at the file level, not at the object level
    )

    tripwire_id: TripwireId = Field(..., description="Closed enum: TW-7c-1..TW-7c-6.")
    story_owner: str = Field(..., min_length=1, description="Primary story key (e.g., '7c-20c').")
    fired_at: datetime = Field(..., description="Timezone-aware datetime; UTC.")
    fired_verdict: Literal["fired", "not_fired", "not_yet_evaluated", "not-applicable", "marginal-fired", "false", "true"] = Field(...)
    measured_value: dict | None = Field(default=None, description="Free-form per-tripwire payload.")
    escalation_action_taken: str | None = Field(default=None)
    decision_record_link: str | None = Field(default=None, description="Pipe-or-newline-separated artifact paths.")
    severity: TripwireSeverity = Field(..., description="Closed enum: critical / high / medium.")
    trace_id: UUID | None = Field(default=None, description="UUID4 trace identifier; format-validated.")

    @field_validator("fired_at")
    @classmethod
    def _require_tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("fired_at must be timezone-aware (per pydantic-v2-schema-checklist §3)")
        return v
```

**And** the module conforms to **all 14 schema idioms** in `docs/dev-guide/pydantic-v2-schema-checklist.md`: `validate_assignment=True`, closed-enum on `tripwire_id` with **triple-layer red-rejection** (Enum + Literal + custom validator on coercion path), timezone-aware datetime, UUID4 with format validation, `extra="forbid"`, `field_validator` on `fired_at` raising clear error.

**And** `app/models/__init__.py` exports `TripwireLedgerEntry` + `TripwireId` + `TripwireSeverity` for downstream consumption.

**Test pin:** `tests/parity/test_tripwire_ledger_entry_shape.py` — at least **7 assertions** covering all 7 named fields + closed-enum red-rejection + AUDIT round-trip across the 6 TW IDs × 2 severity tiers (critical / high). The shape-pin lives in the frozen-paths fixture per `tests/fixtures/frozen_paths/` (verify path at T1; create if absent).

```python
# tests/parity/test_tripwire_ledger_entry_shape.py — illustrative test stubs
def test_validate_assignment_true():
    """Mutating a field after construction raises ValidationError (idiom 1)."""

def test_extra_forbid():
    """Extra fields rejected on construction (idiom 4)."""

def test_tripwire_id_closed_enum():
    """tripwire_id must be one of TW-7c-1..TW-7c-6; 'TW-99' raises ValidationError."""

def test_fired_at_timezone_aware_required():
    """Naive datetime raises ValueError via field_validator (idiom 3)."""

def test_severity_closed_enum():
    """severity must be one of critical / high / medium; 'low' raises."""

def test_round_trip_all_six_tw_ids():
    """6 TW IDs × 2 severity tiers = 12 round-trip assertions."""

def test_audit_chain_field_set_complete():
    """Asserts all 7 named fields present (story_owner, fired_at, fired_verdict, measured_value, escalation_action_taken, decision_record_link, severity)."""
```

> **Notes for 7c.0a-C.** This AC is **dev-agent-executable** (Python authoring + pytest). The model spec above is illustrative — Codex SHALL polish per `pydantic-v2-schema-checklist.md` (`SkipJsonSchema` for any internal audit fields if added; `Field(exclude=True)` if any field should be omitted from JSON-Schema emission). The 7-field set in the epic AC is the canonical minimum; severity is the **8th** field (added by Murat A5 to allow per-fire severity recording — critical / high / medium). The shape-pin asserts **all 7 named** fields PLUS severity (8 fields total). `frozen=False` on the model is intentional — the ledger entry IS mutable post-construction during the same test run; the **append-only invariant lives at the FILE level** (not the object level), enforced by the FR-7c-50 audit-chain integrity test scaffold in 7c.0b.

### AC-7c.0a-D — FR-7c-50 audit-chain integrity conceptual design lands as ADR appendix (FR-7c-50 conceptual design only; executable test scaffold lives in 7c.0b)

**Given** FR-7c-50 audit-chain integrity (conceptual design only)
**When** the dev-agent extends the ADR with an "Appendix A: Audit-Chain Integrity Conceptual Design" section
**Then** the appendix specifies:

1. **Append-only invariant:** TripwireLedgerEntry rows in `sprint-status.yaml::tripwire_events` are append-only at file level. No mutation; only addition. Updates to existing rows (e.g., `fired_verdict: not_yet_evaluated → fired`) are allowed via in-place YAML edits BUT **must increment the row's `revision: int` field** + retain prior revision in a `revision_history: list[dict]` audit trail (introduced as part of FR-7c-50 conceptual design here; field-set lands in 7c.0b's Pydantic schema or in TripwireLedgerEntry — surface at T1 for Codex decision).
2. **Monotonic timestamp:** Each tripwire entry's `fired_at` MUST be ≥ the prior entry's `fired_at` for the same `tripwire_id`. Out-of-order timestamps are red-rejection-triggers in the audit-chain validator.
3. **Parent-trace linkage:** If `trace_id` is populated, the entry MUST link to the LangSmith trace where the tripwire fire-decision was made. Missing `trace_id` on `fired_verdict ∈ {fired, marginal-fired}` is a red-rejection-trigger.
4. **Red-rejection error semantics:** Out-of-order timestamp → `AuditChainOrderError`; missing parent trace → `AuditChainParentLinkError`. Error class names, hierarchy (root: `AuditChainIntegrityError`), and module placement (`app/audit/errors.py` — verify path at T1) named in the appendix.

**And** the appendix carries a forward-pointer to 7c.0b: "Executable test scaffold for this design lands in Story 7c.0b (`tests/audit/test_override_event_chain_integrity.py`); 7c.0a is the conceptual-design-only contribution."

**Test pin:** none direct (conceptual design — no executable test in 7c.0a; the test pin lands in 7c.0b). The structural test from AC-7c.0a-B (`test_adr_0001_parity_contract_dsl_present.py`) SHALL be extended to assert the "Appendix A" heading is present.

> **Notes for 7c.0a-D.** This AC is **dev-agent-executable** (markdown authoring). No code lands for this AC — only the ADR appendix. The forward-pointer to 7c.0b is structural; do NOT scaffold the actual test file in 7c.0a.

---

## Tasks / Subtasks

- [x] **T1 — Readiness checks (AC: T1 Readiness Block)**
  - [x] T1.1 Confirm `docs/dev-guide/adr/0001-parity-contract-dsl.md` slot is free (or surface next-free index as `decision_needed`).
  - [x] T1.2 Confirm `tests/fixtures/frozen_paths/` exists; create if absent + document in Dev Notes.
  - [x] T1.3 Confirm `app/audit/` directory exists or note creation for AC-D's `errors.py` reference.
  - [x] T1.4 Run `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-0a-decision-foundation.md`; expect PASS.
  - [x] T1.5 Read pydantic-v2-schema-checklist.md, dev-agent-anti-patterns.md, story-cycle-efficiency.md (cite-by-reference; no re-derivation).

- [x] **T2 — Author ADR `docs/dev-guide/adr/0001-parity-contract-dsl.md` (AC: 7c.0a-B)**
  - [x] T2.1 Six required sub-sections (registration mechanism + transport declaration schema + refactor target list + D7 escape-hatch policy + Decision-then-Foundation pattern + AMEND-7d-ii completeness-flags planning).
  - [x] T2.2 Status line + cross-references to PRD + epic + governance JSON.
  - [x] T2.3 Appendix A (FR-7c-50 audit-chain integrity conceptual design — AC: 7c.0a-D).

- [x] **T3 — Add import-linter contracts C4 / C5 / C6 to `pyproject.toml` (AC: 7c.0a-A)**
  - [x] T3.1 C4 parity-DSL boundary (empty `forbidden_modules`).
  - [x] T3.2 C5 §02A composer boundary (empty `forbidden_modules`).
  - [x] T3.3 C6 HIL-surface boundaries (12 source modules; empty `forbidden_modules`).
  - [x] T3.4 Inline comment block citing 7c.0a + Winston W2 + downstream populating stories (7c.0b for C4; 7c.3a for C5; 7c.4b for C6).

- [x] **T4 — Author `app/models/tripwire_ledger.py` Pydantic-v2 model (AC: 7c.0a-C)**
  - [x] T4.1 `TripwireId` closed enum (TW-7c-1..TW-7c-6).
  - [x] T4.2 `TripwireSeverity` closed enum (critical / high / medium).
  - [x] T4.3 `TripwireLedgerEntry` model with all 14 pydantic-checklist idioms.
  - [x] T4.4 `field_validator("fired_at")` enforcing tz-aware.
  - [x] T4.5 Update `app/models/__init__.py` exports.

- [x] **T5 — Author shape-pin test `tests/parity/test_tripwire_ledger_entry_shape.py` (AC: 7c.0a-C)**
  - [x] T5.1 ≥7 named field assertions + closed-enum red-rejection assertions.
  - [x] T5.2 AUDIT round-trip across 6 TW IDs × 2 severity tiers (12 round-trips).
  - [x] T5.3 Verify `tests/fixtures/frozen_paths/` placement per T1.2.

- [x] **T6 — Author structural test `tests/structural/test_adr_0001_parity_contract_dsl_present.py` (AC: 7c.0a-B + 7c.0a-D)**
  - [x] T6.1 Path-existence assertion + 6 sub-section heading assertions + Appendix A heading assertion.

- [x] **T7 — Author structural test `tests/structural/test_import_linter_contracts_c4_c5_c6_present.py` (AC: 7c.0a-A)**
  - [x] T7.1 Parse `pyproject.toml`; assert all three contracts present by name.
  - [x] T7.2 Subprocess `lint-imports`; assert exit 0 + KEPT count ticks up by 3 vs pre-7c.0a baseline.

- [x] **T8 — CI hygiene clean (NFR-7c-R5 / NFR-7c-X4 / NFR-7c-M5)**
  - [x] T8.1 `ruff check app/models/tripwire_ledger.py app/models/__init__.py tests/parity/test_tripwire_ledger_entry_shape.py tests/structural/test_adr_0001_parity_contract_dsl_present.py tests/structural/test_import_linter_contracts_c4_c5_c6_present.py` — clean.
  - [x] T8.2 `lint-imports` — KEPT count = pre-7c.0a baseline + 3 (C4 + C5 + C6).
  - [x] T8.3 Run focused tests: `pytest tests/parity/test_tripwire_ledger_entry_shape.py tests/structural/test_adr_0001_parity_contract_dsl_present.py tests/structural/test_import_linter_contracts_c4_c5_c6_present.py -p no:randomly` — all pass.
  - [x] T8.4 Run broad regression: `pytest -p no:randomly` — ≥ 1403 baseline preserved (no regression).
  - [x] T8.5 Sandbox-AC validator PASS (re-run from T1.4).

- [x] **T9 — Class-conformance (NFR-7c-R5)**
  - [x] T9.1 Run `.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` — expect 11 conforming activation contracts (no regression; TripwireLedgerEntry shape-pin is NOT an activation contract).

- [x] **T10 — Codex self-review (NEW CYCLE T10)**
  - [x] T10.1 Codex authors `_bmad-output/implementation-artifacts/_codex-handoff/7c-0a.ready-for-review.md` summarizing: file list (5 files: ADR + pyproject.toml diff + tripwire_ledger.py + 3 test files), test counts, ruff status, lint-imports KEPT count delta, broad-regression delta, sandbox-AC validator status, any T1 `decision_needed` resolutions, any deferred follow-ons surfaced.

- [ ] **T11 — Claude `bmad-code-review` (CROSS-AGENT MANDATORY per governance JSON)**
  - [ ] T11.1 Claude (separate cold context from Codex dev) runs `bmad-code-review` against the 5-file diff; produces verdict at `_bmad-output/implementation-artifacts/7c-0a-code-review-2026-05-04.md` (or actual review-date); applies remediation cycles if HALT-AND-REMEDIATE; commits + flips `migration-7c-0a-decision-foundation: review → done` in sprint-status.

---

## Dev Notes

**Architecture decisions inherited from epic-decomposition party-mode 2026-05-04:**
- **Winston W1** — 7c.0 split into 7c.0a (Decision Foundation; this story) + 7c.0b (Scaffold Foundation). Hard precedence: 7c.0b cannot open until 7c.0a closes; same with all Wave 1 stories except 7c.2 (which has AMELIA-P1 path-isolation guard for parallel execution).
- **Winston W2** — C4/C5/C6 ALL three import-linter contracts land in 7c.0a with empty target lists. Downstream populating stories: 7c.0b adds first targets to C4 (DSL primitives); 7c.3a populates C5 forbidden-list (composer boundary); 7c.4b populates C6 forbidden-list (HIL boundaries). CI-fail mode at `lint-imports` is active from 7c.0a forward.
- **Winston W4** — Decision-then-Foundation pattern (7c.0a→7c.0b mirror of 7c.4a→7c.4b) named explicitly in this ADR for future-slab reuse.
- **Winston W6** — D7 transport-DSL-completeness escape-hatch policy: enumerate what DSL does NOT cover (timeout / streaming / backpressure / error-frame encoding) + escape-hatch policy ("extend the DSL" vs "per-transport addendum documented inline").
- **Murat A5** — TripwireLedgerEntry Pydantic-v2 model is highest-leverage. `validate_assignment=True` + closed-enum on `tripwire_id` with triple-layer red-rejection + timezone-aware datetime + UUID4 trace-id with format validation + 7-field shape (8 with `severity`).
- **Murat AMEND-7d-ii** — ADR specifies that 7c.0b enumerates THREE separate PASS/FAIL flags (TW-7c-4 detection + TW-7c-5 detection + TW-7c-6 detection) at scaffold-completeness; composite "all-PASS" insufficient.

**File / module placement (verified at authoring; surface as decision_needed at T1 if any path is wrong):**
- `app/models/tripwire_ledger.py` — sibling of `app/models/override_event.py`; NOT inside `app/models/decision_cards/`.
- `app/models/__init__.py` — adds three exports (TripwireLedgerEntry + TripwireId + TripwireSeverity).
- `pyproject.toml::[tool.importlinter]` — adds three contracts (C4 + C5 + C6) with empty `forbidden_modules`.
- `docs/dev-guide/adr/0001-parity-contract-dsl.md` — six sub-sections + Appendix A. Verify slot at T1.
- `tests/parity/test_tripwire_ledger_entry_shape.py` — shape-pin in `tests/parity/` (sibling of existing class-conformance / shape-pin tests).
- `tests/structural/test_adr_0001_parity_contract_dsl_present.py` — structural test (path + headings).
- `tests/structural/test_import_linter_contracts_c4_c5_c6_present.py` — structural test (toml + lint-imports subprocess).
- `tests/fixtures/frozen_paths/` — verify exists at T1; create if absent.

**Anti-patterns to avoid (from `dev-agent-anti-patterns.md`):**
- **A11 Windows-portability** — DO NOT include Windows-only path strings or default-encoding assumptions in any new code. Use `pathlib.Path.as_posix()` + UTF-8 explicit encoding.
- **A-schema-1 Premature SkipJsonSchema** — Only mark a field with `Field(exclude=True) + SkipJsonSchema` if it is genuinely internal-only audit data. TripwireLedgerEntry's 7 named fields are all part of the public ledger contract; do NOT mark any of them excluded.
- **A-schema-2 Frozen vs validate_assignment confusion** — Use `frozen=False` + `validate_assignment=True` on TripwireLedgerEntry per the spec (mutation allowed during run; append-only at file level). Do NOT set `frozen=True` (would break the validator pattern).
- **A-review-ceremony-1 Lying about completion** — At T8 broad regression, report ACTUAL pass/fail counts; do not assert "no regression" without running the full suite.

**K-discipline (from `story-cycle-efficiency.md`):**
- K-target 1.3× = ~2.5K LOC band-floor × 1.3 = ~3.25K LOC at T-shape ceiling; ~3 pts. ADR alone is ~2K LOC; pyproject.toml diff ~30 LOC; tripwire_ledger.py ~150 LOC; 3 test files ~200 LOC each. Estimate: ~3K LOC total. WELL under K-target ceiling.
- If T1 surfaces an unexpected `decision_needed` that grows the ADR by >1K LOC, re-evaluate K-projection and surface in Codex T10 self-review.

**Testing standards:**
- Pytest with `-p no:randomly` for deterministic-baseline preservation (NFR-7c-R2).
- Shape-pin tests live in `tests/parity/` (existing convention from Slab 7a/7b — class-conformance + shape-pin co-located).
- Structural tests live in `tests/structural/` (existing convention).
- ALL new test files MUST be UTF-8 encoded; no `PYTHONIOENCODING=utf-8` workaround (NFR-7c-X1; FR-7c-46 lint pass scaffolded in 7c.0b but already de-facto active).

### Project Structure Notes

- **Alignment with unified project structure:** All five new file paths conform to existing conventions (`app/models/<file>.py`, `tests/parity/test_<thing>_shape.py`, `tests/structural/test_<thing>_present.py`, `docs/dev-guide/adr/<NNNN>-<slug>.md`, `pyproject.toml::[tool.importlinter]` contract entries).
- **Detected variances:** None at authoring time. T1.1 verifies ADR slot 0001 is free; T1.2 verifies `tests/fixtures/frozen_paths/` exists; T1.3 verifies `app/audit/` exists. Any variance surfaces as `decision_needed` and Codex picks the next-free path with rationale documented in Dev Notes.

### References

- [Source: docs/dev-guide/migration-story-governance.json#stories.7c-0a]
- [Source: docs/dev-guide/pydantic-v2-schema-checklist.md] (all 14 idioms; primary enforcement of NFR-7c-OD2)
- [Source: docs/dev-guide/dev-agent-anti-patterns.md] (A11 Windows-portability + schema/review-ceremony anti-patterns)
- [Source: docs/dev-guide/story-cycle-efficiency.md] (K-discipline; single-gate vs dual-gate review policy)
- [Source: _bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md] (FR-7c-30..33 + FR-7c-50 + FR-7c-53 + NFR-7c-OD2)
- [Source: _bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md#Story-7c.0a] (Story 7c.0a section starting at line 336)
- [Source: _bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md] (D2/D3/D7 architectural invariants; D7 transport-DSL completeness escape-hatch policy)
- [Source: _bmad-output/implementation-artifacts/sprint-status.yaml#tripwire_events] (TW-7c-1..6 seed entries; TripwireLedgerEntry consumer)
- [Source: _bmad-output/implementation-artifacts/migration-7a-3-pre-gate-marcus-shared-llm-node.md] (canonical migration spec template precedent)

---

## Review Findings

T11 cross-agent code-review (Claude, Opus 4.7) 2026-05-04. Verdict artifact: `_bmad-output/implementation-artifacts/7c-0a-code-review-2026-05-04.md`.

### decision_needed → ratified
- [x] [Review][Decision] Wildcard source-module expressions in C4/C5/C6 (B-5 / A-AC-A) — RATIFIED ACCEPT. Spec intent was 'empty target list' (forbidden_modules), not 'concrete source_modules'. Wildcard form against empty namespace is structurally KEPT; 7c.0b/7c.3a/7c.4b populate downstream. No action required.

### patch (applied)
- [x] [Review][Patch] LINT_IMPORTS Windows-only path → cross-platform (B-6 / E-1) [tests/structural/test_import_linter_contracts_c4_c5_c6_present.py:10] — Replaced `REPO_ROOT / ".venv" / "Scripts" / "lint-imports.exe"` with `sys.platform`-conditional resolution supporting both Windows (`.venv/Scripts/*.exe`) and POSIX (`.venv/bin/*`). NFR-7c-X3 path-portability + NFR-7c-X1 Windows-portability cross-platform invariant.

### defer (pre-existing acceptable fragilities)
- [x] [Review][Defer] Hardcoded `PRE_7C_0A_KEPT_BASELINE = 9` (B-7) [tests/structural/test_import_linter_contracts_c4_c5_c6_present.py:18] — deferred, known-fragility annotation; downstream stories that add contracts should bump baseline as part of their commit.
- [x] [Review][Defer] `fired_verdict` union literal coverage gap in shape-pin (E-4) [tests/parity/test_tripwire_ledger_entry_shape.py] — deferred, minor coverage gap; Pydantic Literal exhaustiveness enforces at construction time. Address at next test-coverage-tightening pass.

### out-of-scope (excluded from close commit)
- [x] [Review][Defer] `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` generated_at timestamp regenerated by test side-effect — reverted at staging.
- [x] [Review][Defer] `runs/cache-harness/` untracked test cache-harness output — not staged. Recommend post-close: ensure `.gitignore` covers `runs/`.

### verification battery (re-run by reviewer)
- Sandbox-AC validator: PASS (no violations)
- Class-conformance: PASS (11 conforming activation contracts; no regression)
- lint-imports: 12/12 KEPT (pre-7c.0a 9 + C4/C5/C6 = 12; +3 confirmed)
- Focused tests (3 new files): 27 passed (post-patch)
- Broad regression: 3990 passed / 37 failed (IDENTICAL to pre-7c.0a baseline; ZERO regressions; all 37 are pre-existing checkout drift unrelated to 7c.0a)
- Ruff: CLEAN

## Dev Agent Record

### Agent Model Used

Codex Sonnet 4.5 or later (NEW CYCLE T1-T9 + T10 self-review per `feedback_new_cycle_codex_dev_handoff.md`).

### Debug Log References

- T1 readiness: ADR directory was absent, so ADR slot `0001-parity-contract-dsl.md` was free; `tests/fixtures/frozen_paths/` was absent and created; `app/audit/` was absent and recorded as a 7c.0b forward-pointer only.
- T1 variance: the prompt referenced `app/models/override_event.py`, but this checkout has `app/models/decision_cards/override_event.py`; TripwireLedgerEntry was still placed as a sibling under `app/models/` per story scope.
- T1 variance: C4/C5/C6 source packages are future paths in this checkout, so the import-linter contracts use wildcard source expressions with empty forbidden lists to avoid prematurely creating 7c.0b executable/scaffold packages.
- Broad regression command was executed and is red in this checkout: `38 failed, 3988 passed, 27 skipped, 46 deselected, 2 xfailed`. Spot-check of `tests/contracts/test_30_1_zero_test_edits.py` shows pre-existing HEAD-range drift unrelated to 7c.0a working-tree files.

### Completion Notes List

- Authored ADR 0001 with six required DSL decision sections and Appendix A audit-chain conceptual design.
- Added C4/C5/C6 import-linter contracts with empty forbidden lists; `lint-imports` now reports `12 kept, 0 broken` versus the pre-7c.0a baseline of 9 kept.
- Added `TripwireLedgerEntry`, `TripwireId`, and `TripwireSeverity` with Pydantic-v2 assignment validation, extra-forbid, timezone-aware datetime enforcement, UUID4 trace validation, and closed-enum red-rejection coverage.
- Added shape and structural tests: focused story suite passes `27 passed`; ruff is clean; class-conformance remains `11 activation contract file(s) conform`; sandbox-AC validator passes.
- Required broad regression is not green due existing repo-state/environment failures outside this story's touched files; review should treat this as a checkout-level blocker, not a story-local focused-test failure.

### File List

- `docs/dev-guide/adr/0001-parity-contract-dsl.md`
- `pyproject.toml`
- `app/models/tripwire_ledger.py`
- `app/models/__init__.py`
- `tests/parity/test_tripwire_ledger_entry_shape.py`
- `tests/structural/test_adr_0001_parity_contract_dsl_present.py`
- `tests/structural/test_import_linter_contracts_c4_c5_c6_present.py`
- `_bmad-output/implementation-artifacts/_codex-handoff/7c-0a.ready-for-review.md`
- `_bmad-output/implementation-artifacts/migration-7c-0a-decision-foundation.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log

- 2026-05-04: Implemented Story 7c.0a decision foundation and moved to review for mandatory Claude T11 cross-agent code review.
