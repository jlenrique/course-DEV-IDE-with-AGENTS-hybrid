# Migration Story 7a.6: Vocabulary Registry + Operator-Control Parity Table

**Status:** done
**Sprint key:** `migration-7a-6-vocabulary-registry-parity-table`
**Epic:** Slab 7a — Inter-Gate Conversational Orchestration (`migration-epic-slab-7a-inter-gate-orchestration`)
**Pts:** 3
**Gate:** **single-gate** (per `docs/dev-guide/migration-story-governance.json` v2026-04-28-slab7a-eight-stories, story 7a-6; rationale: null — substrate-extension)
**K-target:** ~1.3× (gate-shape band 1.5-2.5K; ~2K target)
**Authored:** 2026-04-29 via `bmad-create-story` workflow.
**Wave:** 3 — slot 1 (PROMOTED from slot 6 per Step 1 batch-approved adjustment because the registry must precede stories that emit vocabulary into it: 7a.3, 7a.5, 7a.7). Parallel with 7a.3 (independent).
**FR coverage:** 14 — FR21 (xc with 7a.3), FR24 (xc with 7a.3), FR34, FR35, FR38; FR-A5, FR-A6 (xc), FR-A17; FR-O1, FR-O2, FR-O4, FR-O20, FR-O21, FR-O22
**Standing-guardrail enforcement:**
- **SG-1 PRIMARY structural enforcement HERE** — FR-O21 hard-codes the 11-specialist roster (Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera) as a closed list; `len(specialists) == 11` build assertion blocks build if violated.
- **SG-2 PRIMARY structural enforcement HERE** — FR-O20 + FR-O2: 33-row operator-control parity table + parity-test suite; row-count CI assertion blocks merge if `len(rows) != 33`.
- SG-3 Composition Spec §3.6 + §10 Decision Log entries honored (FR-A5).

**Implementation cycle (NEW from 7a.2 onward per operator instruction 2026-04-28):**
- **Claude (Opus 4.7):** authored this spec; ran initial `bmad-party-mode` Gate-1 if called for (NOT called here — single-gate substrate-extension following established Pydantic-v2 + parity-test patterns).
- **Codex (Sonnet 4.5 or later):** develops source code + corresponding test suite per the ACs and tasks below; reaches `review` status; produces a self-conducted G6 layered review.
- **Claude:** does the FINAL `bmad-code-review`; applies remediation cycles; commits; flips `migration-7a-6-vocabulary-registry-parity-table` review → done in sprint-status.

---

## T1 Readiness Block

**Predecessor state (verified at authoring 2026-04-29):**
- Story 7a.1 (directive-composer) **CLOSED done** 2026-04-29 (commit `05bb2aa`).
- Story 7a.2 (manifest fold-flags + compiler ext) is in-flight (substrate work appearing on disk: `app/manifest/gate_fold_manifest_emit.py`, `app/manifest/gate_topology.py`, `state/config/gate_fold_manifest.yaml`, NodeSpec `fold_with`/`fold_target` fields, `directive-composer` node now in manifest, lockstep orchestration-only tolerance landing). 7a.6 OPENS only after 7a.2 closes — strict-prereq per Wave 2 → Wave 3 sequencing.
- Story 7a.3 (pre-gate-marcus shared LLM node) is parallel with 7a.6 in Wave 3; both depend on 7a.2 substrate. 7a.3 READS the vocabulary registry that 7a.6 emits; 7a.3 spec authoring may proceed in parallel with 7a.6 dev but 7a.3 dev requires 7a.6 close.
- Slab 7-mapping-checklist at `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` is the canonical 33-row floor for SG-2. Current row count: walk the file with `grep -cE "^\| ?\d+ ?\|" _bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` BEFORE writing the parity table to confirm the row count matches the SG-2 floor of 33. **If the live file shows fewer than 33 rows, HALT and surface to operator** — the SG-2 floor is the AUTHORITATIVE invariant; the file may need rows added before 7a.6 dev opens, OR the floor needs operator-ratified adjustment.

**Live substrate (verified at authoring; do NOT regress):**

- `docs/conversational-gates/g0-directive-composition.md` exists (authored by 7a.1 as the at-gate operator context for G0). 7a.6 adds the `_registry/` subdirectory siblings: `vocabulary.yaml`, `glossary.md` (auto-generated), and a per-gate Jinja2 template family at `docs/conversational-gates/<gate-id>.j2` (authored by 7a.3, NOT 7a.6 — but the directory shape is reserved here).
- `app/models/decision_cards.py` does NOT yet exist. 7a.6 creates it as the Pydantic-v2 enum loader for the vocabulary registry. Follow `docs/dev-guide/pydantic-v2-schema-checklist.md` four-file-lockstep (model + emitted JSON Schema + golden + shape-pin tests).
- `app/specialists/` houses the 11 specialist directories: `texas/`, `irene/`, `dan/` (deferred per Slab 2b), `tracy/`, `gary/`, `kira/`, `wanda/`, `enrique/`, `compositor/`, `quinn_r/` (note canonical underscore form per `SPECIALIST_ALIASES` in `app/manifest/compiler.py:43-46`: `quinn-r → quinn_r`; `elevenlabs → enrique`), `vera/`. Confirm 11 directories at T1 walk; raise mismatch as decision_needed.
- `docs/operator/` is the canonical location for operator-facing docs. Existing neighbors: `production-trial-playbook.md`, `trial-run-runbook.md`, `step-02a-prior-run-defaults.md`, `hud-guide.md`, `adhoc-mode.md`. The new parity table lands as `docs/operator/legacy-vs-langgraph-control-parity.md`.
- `tests/parity/` exists (created by 7a.1; carries `__init__.py` + `test_trial_475_directive_composition_regression.py`). 7a.6's parity test suite lands here.
- The 7a.1-landed Composition Spec §10 Decision Log row (2026-04-29 entry for `runner_supplied_payload` kwarg) is the precedent for Composition Spec evolution documentation. 7a.6 does NOT add a new §10 entry (vocabulary registry is data + Pydantic schema, not composition substrate evolution).

**Block-mode trigger paths touched by this story (per CLAUDE.md §Pipeline lockstep regime):**
- NONE. 7a.6 does not touch `state/config/pipeline-manifest.yaml`, `scripts/utilities/check_pipeline_manifest_lockstep.py`, `scripts/utilities/run_hud.py`, `scripts/utilities/progress_map.py`, `marcus/orchestrator/workflow_runner.py`, `tests/test_run_hud.py`, `tests/test_progress_map.py`, the v4.2 prompt pack, `state/config/learning-event-schema.yaml`, `scripts/utilities/learning_event_capture.py`, or `skills/bmad-agent-marcus/scripts/validate-literal-visual-pre-dispatch.py`.

**Gate-mode rationale (from governance JSON):**
> Slab 7a wave-3 (PROMOTED from wave-6 per Step 1 batch-approved adjustment — registry must precede stories that emit vocabulary into it). Vocabulary registry (Pydantic-v2 namespaced enum) + 33-row operator-control parity table. SG-1 + SG-2 primary structural enforcement here (FR-O20 row-count CI; FR-O21 specialist-roster build assertion).

**T1 conclusion:** No unanticipated architectural disagreement requires halting Gate 0. Implementation proceeds: vocabulary registry YAML + Pydantic enum loader (four-file-lockstep) + parity table + parity-test suite + auto-glossary emit + AST-scan structural test. **Hard checkpoint at T1: confirm 33 rows in mapping checklist BEFORE writing the parity table; HALT-and-surface if mismatch.**

---

## Story

As the orchestration runtime + dev-agents (Claude/Codex),
I want a unified namespaced decision-card vocabulary registry at `docs/conversational-gates/_registry/vocabulary.yaml` and an operator-control parity table at `docs/operator/legacy-vs-langgraph-control-parity.md`,
so that downstream stories (7a.3 pre-gate-marcus, 7a.5 conversation persistence, 7a.7 A2 shims) emit decision-card vocabulary that's pre-registered (FR-O4 no-inline-string-literals; closed-set red-rejection) and so that the 33-row mapping-checklist legacy↔migrated trace is operator-readable + CI-enforceable.

---

## Acceptance Criteria

### AC-7.6-A — Vocabulary registry artifact (FR21, FR-O1)

**Given** the new vocabulary registry artifact at `docs/conversational-gates/_registry/vocabulary.yaml`
**When** a dev-agent edits it
**Then** the registry uses three top-level namespaces with closed-enum value sets per namespace:

```yaml
# Vocabulary registry — Slab 7a Story 7a.6.
# Authoritative closed-enum source for decision-card vocabulary across all
# 10 essential conversational gates + 11-specialist roster + shared tokens.
# Loaded by app/models/decision_cards.py via Pydantic v2 enum loader.
schema_version: "1.0"
namespaces:
  gates:
    description: "Decision tokens emitted at conversational gates."
    tokens:
      decision:
        - confirm
        - revise
        - reject
        - escape
        - skip-slide
        - abort-run
      directive:
        - accept-as-is
        - apply-edit
        - re-emit
        - halt-for-repair
      rationale_floor_chars: 20  # NFR-OX3 per-token rationale floor
  specialists:
    description: "Canonical specialist roster (SG-1 11-floor)."
    tokens:
      roster:
        - texas
        - irene
        - dan
        - tracy
        - gary
        - kira
        - wanda
        - enrique
        - compositor
        - quinn_r
        - vera
  shared:
    description: "Tokens shared across gates + specialists (e.g., gate_decision verdicts)."
    tokens:
      gate_decision:
        - approved
        - approved-with-edits
        - rejected
        - escalated
      escape_card_options:
        - accept-as-is
        - reject-and-skip-slide
        - abort-run
```

**And** the registry is the SOLE source of truth for decision-card vocabulary; downstream stories (7a.3, 7a.5, 7a.7) MUST pull tokens from this registry, not inline string literals (FR-O4 enforcement is in AC-7.6-F).
**And** `schema_version: "1.0"` is the canonical opening version; future structural changes to the registry require an additive bump (e.g. `1.1`) per NFR-V3 (registry additive-only post-Slab-7a-close).

**Test pin:** `tests/unit/models/test_vocabulary_registry_load.py` — 4 cases: (a) registry loads successfully, (b) all three namespaces present, (c) `gates.tokens.decision` and `gates.tokens.directive` are non-empty closed lists, (d) `specialists.tokens.roster` has exactly 11 entries.

### AC-7.6-B — Pydantic v2 enum loader (FR-A6 four-file-lockstep, NFR-CG4)

**Given** the new module `app/models/decision_cards.py`
**When** the dev agent authors it
**Then** it implements a Pydantic-v2 enum loader that imports the registry at module load and emits closed-enum types per namespace:

```python
"""Decision-card vocabulary enum loader (Story 7a.6).

Loads docs/conversational-gates/_registry/vocabulary.yaml at module-load time
and emits Pydantic v2 closed-enum types for every token group. Triple-layer
red-rejection per docs/dev-guide/pydantic-v2-schema-checklist.md.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "docs" / "conversational-gates" / "_registry" / "vocabulary.yaml"


def _load_registry() -> dict[str, Any]:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


_REGISTRY = _load_registry()


def _enum(group_path: str, name: str) -> type[StrEnum]:
    """Build a StrEnum from a registry token group like 'gates.decision'."""
    namespace, token_group = group_path.split(".")
    tokens = _REGISTRY["namespaces"][namespace]["tokens"][token_group]
    return StrEnum(name, {t.upper().replace("-", "_"): t for t in tokens})


GateDecisionToken = _enum("gates.decision", "GateDecisionToken")
GateDirectiveToken = _enum("gates.directive", "GateDirectiveToken")
SpecialistId = _enum("specialists.roster", "SpecialistId")
SharedGateDecision = _enum("shared.gate_decision", "SharedGateDecision")
EscapeCardOption = _enum("shared.escape_card_options", "EscapeCardOption")


class DecisionCard(BaseModel):
    """Base decision-card shape with closed-enum vocabulary."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,
    )

    decision: GateDecisionToken
    directive: GateDirectiveToken
    rationale: str = Field(..., min_length=20)  # NFR-OX3 floor
```

**And** the four-file-lockstep is honored:
1. **Model:** `app/models/decision_cards.py` (above)
2. **Emitted JSON Schema:** `app/models/schemas/decision_cards.schema.json` (auto-emitted via a `python -m app.models.decision_cards --emit-schema` flag OR via a CI test that re-emits and asserts byte-equality)
3. **Golden fixture:** `tests/fixtures/decision_cards/decision_card_golden.json` (a canonical valid card; pinned)
4. **Shape-pin tests:** `tests/unit/models/test_decision_card_shape_pin.py` (asserts schema fields, enum closure, frozen=True, extra=forbid, rationale min_length=20)

**And** triple-layer red-rejection per the Pydantic v2 checklist:
- Layer 1: enum field rejects unknown tokens at construction with `pydantic.ValidationError`.
- Layer 2: `extra="forbid"` rejects unexpected fields (e.g. typo'd `decison`).
- Layer 3: JSON Schema closed-enum + `additionalProperties: false` so consumers (downstream stories, operator-facing tooling) get the same rejection at the wire boundary.

**Test pin:** `tests/unit/models/test_decision_card_shape_pin.py` — 6 cases: (a) valid card constructs cleanly, (b) unknown decision token raises ValidationError, (c) unknown directive token raises ValidationError, (d) extra field raises ValidationError, (e) rationale shorter than 20 chars raises ValidationError, (f) emitted JSON Schema is byte-identical to the on-tree `app/models/schemas/decision_cards.schema.json`.

### AC-7.6-C — Operator-control parity table (FR-O2, SG-2 floor structurally enforced)

**Given** the new doc at `docs/operator/legacy-vs-langgraph-control-parity.md`
**When** the dev agent authors it
**Then** the document opens with this header:

```markdown
# Legacy v4.2 ↔ LangGraph Migrated Operator-Control Parity Table

**Authority.** This table is the operator-readable trace of every legacy v4.2
operator-control lever and its LangGraph-migrated equivalent. **Row count is
SG-2 floor: 33 rows. The CI parity-test suite at
`tests/parity/test_operator_control_parity.py` asserts `len(rows) == 33` and
fails the merge if violated.**

**Source.** Rows derive from the 33-row mapping checklist at
`_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`.
Every row in this table corresponds 1:1 to a row in the mapping checklist;
the parity-test suite enforces the bidirectional correspondence.

**Updates.** Adding or removing rows requires (a) updating the mapping
checklist FIRST, (b) updating this table in lockstep, (c) updating the parity
test count assertion, (d) party-mode consensus (not dev-agent authority) per
NFR-V3 (registry-style artifacts are additive-only post-Slab-7a-close).
```

**And** the table has exactly 33 rows (one per legacy operator-control lever from the mapping checklist), with this column shape:

| # | Legacy v4.2 control lever | LangGraph migrated path / command | Parity test ID |
|---|---|---|---|
| 1 | Operator GO at §01 activation | `bmad-trial start --input <corpus> --auto-confirm-directive=false` (G0 confirm-or-edit prompt; Story 7a.1) | `test_row_01_g0_directive_composition_confirm` |
| ... | ... | ... | ... |
| 33 | (last legacy lever) | (LangGraph equivalent) | `test_row_33_<lever-slug>` |

**And** every row has a non-empty `Parity test ID` field that names a real test function in `tests/parity/test_operator_control_parity.py` (AC-7.6-D).

**Test pin:** `tests/structural/test_parity_table_row_count.py` — asserts the table has exactly 33 numbered rows + every row has a non-empty parity_test_id field.

### AC-7.6-D — Operator-control parity test suite (FR-O2, FR-O20, NFR-I6 SG-2 floor structurally enforced)

**Given** the new test suite at `tests/parity/test_operator_control_parity.py`
**When** CI runs
**Then** the suite contains EXACTLY 33 test functions, one per row of the parity table, named `test_row_NN_<lever-slug>` where NN is `01..33`.
**And** each test function asserts the right-column command produces the asserted control behavior:
- For commands like `bmad-trial start --auto-confirm-directive=false`: assert the option is exposed in the CLI argument parser (smoke; do NOT execute the live command).
- For doc-pointer commands (e.g. `see docs/operator/<...>.md§<section>`): assert the doc + section exist (smoke).
- For Pydantic-shape commands (e.g. `OperatorVerdict.decision in {confirm, revise, reject}`): assert the enum closure matches the mapping-checklist expectation.
- For not-yet-implemented commands (post-7a.1; e.g. 7a.4-deferred per-slide subgraph commands): mark `@pytest.mark.skip(reason="awaits Story 7a.4 implementation")` with the deferred-story ID in the reason — but the SHELL of the test must exist so the row-count assertion passes.

**And** the row-count CI assertion is implemented as a `tests/parity/test_operator_control_parity_row_count.py` separate file:

```python
"""SG-2 floor structural enforcement: 33-row parity-test suite (Story 7a.6, FR-O20)."""
from pathlib import Path
import re

def test_parity_test_suite_has_exactly_34_rows() -> None:
    suite_path = Path(__file__).parent / "test_operator_control_parity.py"
    text = suite_path.read_text(encoding="utf-8")
    test_funcs = re.findall(r"^def (test_row_\d+_\w+)", text, re.MULTILINE)
    assert len(test_funcs) == 33, (
        f"SG-2 floor violation: parity-test suite has {len(test_funcs)} test "
        f"functions; expected exactly 33. Adding/removing rows requires "
        f"party-mode consensus per NFR-V3."
    )
```

**Test pin:** the row-count CI assertion above PLUS a parametrized cross-check `tests/structural/test_parity_table_to_test_suite_correspondence.py` that walks the parity table rows + asserts each row's `parity_test_id` field names a function that exists in `tests/parity/test_operator_control_parity.py`.

### AC-7.6-E — 11-specialist roster build assertion (FR-O21, NFR-I7, SG-1 floor structurally enforced)

**Given** the canonical specialist roster declared in `docs/conversational-gates/_registry/vocabulary.yaml::namespaces.specialists.tokens.roster`
**When** the dev agent loads `app.models.decision_cards`
**Then** a module-level assertion (not a test — a real assertion at import time) runs:

```python
# At module scope in app/models/decision_cards.py, AFTER SpecialistId is defined:
_SPECIALIST_ROSTER_FLOOR = 11  # SG-1 invariant (Slab 7a PRD)
assert len(SpecialistId) == _SPECIALIST_ROSTER_FLOOR, (
    f"SG-1 floor violation: vocabulary registry roster has {len(SpecialistId)} "
    f"specialists; expected exactly {_SPECIALIST_ROSTER_FLOOR}. "
    f"Adding/removing specialists requires Slab 7b party-mode consensus."
)
```

**And** a CI test re-asserts the floor at test collection time (catches any registry-roster drift even if the module-level assertion is bypassed):

```python
# tests/unit/models/test_specialist_roster_floor.py
from app.models.decision_cards import SpecialistId

def test_specialist_roster_is_exactly_eleven() -> None:
    assert len(list(SpecialistId)) == 11, "SG-1 floor violation"
    expected = {"texas", "irene", "dan", "tracy", "gary", "kira", "wanda",
                "enrique", "compositor", "quinn_r", "vera"}
    assert {s.value for s in SpecialistId} == expected
```

**And** the `compositor` and `quinn_r` canonical-form spellings are honored (per `app/manifest/compiler.py::SPECIALIST_ALIASES` mapping `quinn-r → quinn_r` and `elevenlabs → enrique`).

**Test pin:** `tests/unit/models/test_specialist_roster_floor.py` (above).

### AC-7.6-F — No-ad-hoc-vocabulary-tokens AST scan (FR-O4)

**Given** downstream stories (7a.3, 7a.5, 7a.7) will emit decision-card vocabulary
**When** the dev agent authors `tests/structural/test_no_ad_hoc_vocabulary_tokens.py`
**Then** the test AST-scans gate-handler modules (specifically `app/marcus/orchestrator/`, `app/specialists/*/graph.py`, `app/marcus/cli/`, and any new `app/marcus/cli/gate_shims/` module from 7a.7 if it exists) and FAILS on any string literal that:
1. Looks like a vocabulary token (lowercase, hyphenated OR underscored, ≤20 chars), AND
2. Is passed positionally or as a kwarg to a function name matching `emit_decision_card`, `register_decision_card`, `emit_verdict`, OR appears in a `decision=`, `directive=`, `gate_decision=` kwarg, AND
3. Is NOT present in the vocabulary registry's flat token set.

**Implementation hint for Codex:** use Python's `ast` module to walk source files; collect all string literals appearing in calls to the named functions/kwargs; cross-reference against the flat token set built from the registry; emit a single failing assertion per non-registered token with the file + line + token.

**And** the test runs on every PR via standard pytest; failures are HIGH-severity (vocabulary drift breaks operator-control parity).

**Test pin:** `tests/structural/test_no_ad_hoc_vocabulary_tokens.py` (the AST scanner itself + 2 cases: (a) clean codebase passes, (b) injecting a fake `emit_decision_card("not-a-real-token", ...)` call into a tmp file fails).

### AC-7.6-G — Auto-generated glossary emit (FR-O1)

**Given** operators want a human-readable glossary alongside the YAML registry
**When** the dev agent authors `app/models/glossary_emit.py` with `python -m` entry point
**Then** running `.venv/Scripts/python.exe -m app.models.glossary_emit` emits `docs/conversational-gates/_registry/glossary.md` with the canonical shape:

```markdown
# Decision-Card Vocabulary Glossary

**Auto-generated.** Do NOT hand-edit. Re-emit via:
```bash
.venv/Scripts/python.exe -m app.models.glossary_emit
```
**Source:** `docs/conversational-gates/_registry/vocabulary.yaml` (schema_version 1.0)
**Generated:** <iso-timestamp-utc>

## Namespace: gates

### Token group: decision
- **confirm** — operator approves the pre-filled decision verbatim.
- **revise** — operator requests re-emission with deltas.
- **reject** — operator declines; trial halts at this gate.
- ...

## Namespace: specialists

### Token group: roster (SG-1 floor: 11 names)
- **texas** — retrieval; bundle assembly.
- **irene** — lesson-plan + Pass-1/Pass-2 narration design.
- **dan** — creative-direction (cd-shaped specialist).
- ...
```

**And** the emitter is idempotent: re-running produces byte-stable output (deterministic timestamp via env var or fixed clock for tests).
**And** a CI sync-check `tests/structural/test_glossary_in_sync.py` re-emits to tmp_path + asserts byte-equality against the on-tree file (catches drift between registry edits + un-regenerated glossary).

**Test pin:** `tests/structural/test_glossary_in_sync.py` (sync-check) + `tests/unit/models/test_glossary_emit.py` (3 cases: (a) emit produces the expected sections, (b) idempotency, (c) byte-stable across two runs).

### AC-7.6-H — Composition Spec §3.6 + §11 invariants honored (NFR-V3)

**Given** 7a.6 adds new artifacts (registry YAML + Pydantic loader + parity table + parity tests + glossary)
**When** the dev agent commits
**Then** Composition Spec §3.6 (manifest-declared dependencies) is unaffected — 7a.6 does not touch the manifest.
**And** Composition Spec §11 trigger check fires NEGATIVE — additive only (new files; no envelope shape change; no adapter contract change; no specialist body touch).
**And** NFR-V3 (registry additive-only post-Slab-7a-close) is documented at the top of `vocabulary.yaml` AND in the parity table header — adding/removing rows OR tokens requires party-mode consensus + version bump.
**And** Composition Spec §10 Decision Log entry NOT REQUIRED for 7a.6 (vocabulary registry is data + Pydantic schema, not composition-substrate evolution).

### AC-7.6-I — N-item + anti-pattern + Composition Spec trace

The implementation must record:
- **N1 PASS:** new modules `app/models/decision_cards.py` + `app/models/glossary_emit.py` follow substrate-inventory checklist.
- **N2 PASS:** Composition Spec §3.6 + §11 invariants honored (no manifest change; no envelope shape change).
- **N4 PASS:** specialist isolation preserved — vocabulary registry is operator-facing + dev-agent-facing; no specialist body touched.
- **N9 PASS-PENDING-OPERATOR:** operator validates the parity table + glossary readability at story close.
- **N10 PASS:** A12 procedural-coupling re-read; the glossary is auto-generated (no manual operator step); the AST scan is structural (no manual classification).
- **A1, A11 honored** — `pathlib.Path` throughout; YAML emission via `yaml.safe_dump(default_flow_style=False, sort_keys=False, allow_unicode=True)` (PyYAML; NO ruamel per 7a.1 dev-cycle finding).
- **A12 explicitly avoided** — glossary regeneration is wired into a CI sync-check (`tests/structural/test_glossary_in_sync.py`); operators never manually re-emit.

### AC-7.6-J — D12 close protocol

At close:
- Update `_bmad-output/implementation-artifacts/sprint-status.yaml`: `migration-7a-6-vocabulary-registry-parity-table` → `done`; epic stays `in-progress` (Wave 4 = 7a.4 + 7a.5 unblocked once 7a.3 also closes).
- Cite sandbox-AC validator PASS.
- Cite full focused + wider regression slice PASS (target: zero new failures vs pre-7a.6 baseline).
- Confirm Composition Spec §11 trigger did not fire (additive only).
- File any follow-ons surfaced during dev into `_bmad-output/planning-artifacts/deferred-inventory.md`.

---

## Tasks / Subtasks

- [x] **T1: T1 Readiness review (Codex)**
  - [x] Read this spec end-to-end + cited references (governance JSON; Composition Spec §3.6/§11; pydantic-v2-schema-checklist.md; sandbox-AC inventory; 7a.1 spec for context on at-gate doc family at `docs/conversational-gates/`).
  - [x] Read `docs/dev-guide/pydantic-v2-schema-checklist.md` end-to-end (the four-file-lockstep + triple-layer-red-rejection pattern).
  - [x] Walk `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` and **CONFIRM the row count matches the SG-2 floor**. The PRD/epic state SG-2 floor as 33 (operator-ratified amendment 2026-04-29; original PRD prose said 34, corrected to 33 per off-by-one bookkeeping fix); live file has 33 rows depending on operator-ratified state at dev-open. If row count is NOT 33, HALT and surface to operator (operator-ratified floor is 33 as of 2026-04-29; deviation needs party-mode review).
  - [x] Walk `docs/conversational-gates/_registry/vocabulary.yaml` (once you author it in T2) and **CONFIRM `namespaces.specialists.tokens.roster` contains exactly 11 entries** matching the canonical roster (`texas, irene, dan, tracy, gary, kira, wanda, enrique, compositor, quinn_r, vera`). The vocabulary registry IS the structural source of truth for SG-1 (not directory presence). **Note:** `app/specialists/dan/` and `app/specialists/compositor/` are deferred-greenfield per Slab 7b roadmap (Category-D / Category-E deferrals); the SG-1 invariant is enforced by the closed-list registry + the module-level `assert len(SpecialistId) == 11` at `app/models/decision_cards.py` import time, NOT by directory existence. Do NOT halt on missing directories for `dan` or `compositor`.
  - [x] Confirm 7a.2 has CLOSED before opening 7a.6 dev (strict Wave 2 → Wave 3 sequencing). Verify by reading both `_bmad-output/implementation-artifacts/migration-7a-2-manifest-fold-flags-compiler-extension.md` Status: done AND `_bmad-output/implementation-artifacts/sprint-status.yaml::development_status['migration-7a-2-manifest-fold-flags-compiler-extension']` is `done`.

- [x] **T2: Author vocabulary registry YAML** (AC: A)
  - [x] Create `docs/conversational-gates/_registry/vocabulary.yaml` with the canonical 3-namespace shape per AC-A.
  - [x] Author `tests/unit/models/test_vocabulary_registry_load.py` (4 cases per AC-A test pin).

- [x] **T3: Author Pydantic v2 enum loader** (AC: B)
  - [x] Create `app/models/decision_cards.py` per AC-B template (StrEnum loader + DecisionCard model + four-file-lockstep).
  - [x] Emit JSON Schema to `app/models/schemas/decision_cards.schema.json` (use `DecisionCard.model_json_schema()` + `json.dumps(indent=2, sort_keys=True)`).
  - [x] Create golden fixture `tests/fixtures/decision_cards/decision_card_golden.json` (one canonical valid card; pinned).
  - [x] Author `tests/unit/models/test_decision_card_shape_pin.py` (6 cases per AC-B test pin).
  - [x] Optional CI sync test: `tests/structural/test_decision_cards_schema_in_sync.py` re-emits the JSON Schema and asserts byte-equality against the on-tree file.

- [x] **T4: SG-1 specialist-roster build assertion** (AC: E)
  - [x] Add the module-level assertion to `app/models/decision_cards.py` (per AC-E template).
  - [x] Author `tests/unit/models/test_specialist_roster_floor.py` (per AC-E test pin).

- [x] **T5: Operator-control parity table** (AC: C)
  - [x] Walk `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` and extract the 33 rows in order; map each to a LangGraph-migrated path/command using existing 7a.1 surfaces (the `bmad-trial start --auto-confirm-directive=false` pattern; `OperatorVerdict.decision` enum closures; doc pointers; etc.). For not-yet-implemented commands (post-7a.1 deliverables), reference the deferred story ID.
  - [x] Author `docs/operator/legacy-vs-langgraph-control-parity.md` per AC-C shape with the canonical header + 33 rows + parity_test_id column.
  - [x] Author `tests/structural/test_parity_table_row_count.py` (asserts 33 numbered rows + non-empty parity_test_id field per row).

- [x] **T6: Operator-control parity test suite** (AC: D)
  - [x] Author `tests/parity/test_operator_control_parity.py` with EXACTLY 33 test functions named `test_row_NN_<lever-slug>` per AC-D shape. Implement the per-row assertions per the four asserter categories (CLI argparse smoke / doc-pointer smoke / Pydantic-shape closure / @pytest.mark.skip for not-yet-implemented).
  - [x] Author `tests/parity/test_operator_control_parity_row_count.py` (SG-2 floor structural enforcement; per AC-D shape).
  - [x] Author `tests/structural/test_parity_table_to_test_suite_correspondence.py` (parametrized cross-check: every parity-table row's parity_test_id names a real function in the suite).

- [x] **T7: No-ad-hoc-vocabulary-tokens AST scan** (AC: F)
  - [x] Author `tests/structural/test_no_ad_hoc_vocabulary_tokens.py` per AC-F shape. Use `ast.walk()` to collect string literals in calls to `emit_decision_card`, `register_decision_card`, `emit_verdict` + `decision=`, `directive=`, `gate_decision=` kwargs. Cross-reference against the flat token set from the registry. Emit one assertion per offending token with file:line:token detail.
  - [x] Include 2 verification cases per AC-F test pin (clean baseline passes; injected ad-hoc-token fails).

- [x] **T8: Auto-generated glossary emitter** (AC: G)
  - [x] Create `app/models/glossary_emit.py` with `python -m` entry point; signature: `def emit_glossary(registry_path: Path, output_path: Path, *, now: datetime | None = None) -> None`.
  - [x] Generate `docs/conversational-gates/_registry/glossary.md` per AC-G shape (commit to repo).
  - [x] Author `tests/unit/models/test_glossary_emit.py` (3 cases per AC-G test pin).
  - [x] Author `tests/structural/test_glossary_in_sync.py` (sync-check; CI fails on drift).

- [x] **T9: Verification battery (Codex self-conducted G6 layered review for single-gate)**
  - [x] `.\.venv\Scripts\python.exe -m pytest tests/unit/models tests/parity tests/structural -q --tb=short` → all PASS.
  - [x] `.\.venv\Scripts\python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/specialists/texas tests/specialists/_scaffold -q --tb=line` → no regression vs pre-7a.6 baseline.
  - [x] `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` → exit 0 (7a.6 doesn't touch manifest; should be unchanged).
  - [x] `.\.venv\Scripts\python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-6-vocabulary-registry-parity-table.md` → exit 0.
  - [x] `.\.venv\Scripts\python.exe -m ruff check app/models tests/unit/models tests/parity tests/structural` → clean.
  - [x] `.\.venv\Scripts\lint-imports.exe` → 9/9 contracts KEPT.
  - [x] `.\.venv\Scripts\python.exe -m app.models.glossary_emit` (manual verify; output is the on-tree glossary).

- [x] **T10: Codex G6 self-review (single-gate convention)**
  - [x] Codex authors self-review at `_bmad-output/implementation-artifacts/7a-6-codex-self-review-2026-04-XX.md` covering Blind Hunter / Edge Case Hunter / Acceptance Auditor passes.
  - [x] Codex flips story status `in-progress` → `review` in the spec file (NOT in sprint-status.yaml).
  - [x] Codex hands back to Claude for final `bmad-code-review` + commit + sprint-status flip.

- [ ] **T11: Claude `bmad-code-review` + remediation cycles + commit + close**
  - [ ] Claude reads Codex's developed code + self-review.
  - [ ] Claude runs `bmad-code-review` independently.
  - [ ] Claude triages findings: PATCH applied, DEFER filed, DISMISS recorded.
  - [ ] Claude re-runs verification battery after remediation.
  - [ ] Claude commits.
  - [ ] Claude flips `migration-7a-6-vocabulary-registry-parity-table` review → done in sprint-status.yaml.

---

## File Structure Requirements

**Expected new files:**
- `docs/conversational-gates/_registry/vocabulary.yaml`
- `docs/conversational-gates/_registry/glossary.md` (auto-generated)
- `docs/operator/legacy-vs-langgraph-control-parity.md`
- `app/models/decision_cards.py`
- `app/models/glossary_emit.py` (`python -m` entry point)
- `app/models/schemas/decision_cards.schema.json` (auto-emitted)
- `tests/fixtures/decision_cards/decision_card_golden.json`
- `tests/unit/models/test_vocabulary_registry_load.py`
- `tests/unit/models/test_decision_card_shape_pin.py`
- `tests/unit/models/test_specialist_roster_floor.py`
- `tests/unit/models/test_glossary_emit.py`
- `tests/parity/test_operator_control_parity.py`
- `tests/parity/test_operator_control_parity_row_count.py`
- `tests/structural/test_parity_table_row_count.py`
- `tests/structural/test_parity_table_to_test_suite_correspondence.py`
- `tests/structural/test_no_ad_hoc_vocabulary_tokens.py`
- `tests/structural/test_glossary_in_sync.py`
- `tests/structural/test_decision_cards_schema_in_sync.py` (optional)
- `_bmad-output/implementation-artifacts/7a-6-codex-self-review-2026-04-XX.md` (T10 deliverable)

**Expected modified files:**
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (status flips per T11; Claude does this)

**Do NOT modify:**
- Any specialist body
- `app/marcus/orchestrator/directive_composer.py` (7a.1 surface)
- `app/marcus/orchestrator/dispatch_adapter.py` (7a.1 surface)
- `app/marcus/cli/trial.py` (7a.1 surface)
- `app/manifest/` (7a.2 surface)
- `state/config/pipeline-manifest.yaml` (7a.2 surface)
- `scripts/utilities/check_pipeline_manifest_lockstep.py` (7a.2 surface)
- v4.2 prompt pack
- `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` (READ-ONLY for 7a.6; if rows are missing/wrong, HALT and surface — do NOT edit)

---

## Testing Requirements

**K-floor 13 (per gate-shape band 1.5-2.5K minimum; per governance JSON expected_k_target=1.3):**
- 4 vocabulary registry load cases (AC-A)
- 6 decision-card shape-pin cases (AC-B)
- 1 specialist-roster floor case (AC-E)
- 1 parity-table row-count case (AC-C)
- 1 parity-test-suite row-count case (AC-D)

**K-target ~20 (~1.3× per governance JSON):**
- + 33 parity-test functions (AC-D; many @pytest.mark.skip with deferred-story rationale)
- + 1 parity-table↔test-suite correspondence parametrize case (AC-D)
- + 2 AST-scan cases (AC-F)
- + 3 glossary-emit cases (AC-G)
- + 1 glossary-in-sync structural test (AC-G)
- + 1 decision-cards-schema-in-sync structural test (AC-B optional)

**Note on test-count interpretation:** the 33 parity-test functions (AC-D) are NOT all "active" tests in the K-target sense — many are `@pytest.mark.skip` placeholders for not-yet-implemented commands (deferred to 7a.4/7a.5/7a.7/7a.8). They count toward the SG-2 floor enforcement but not toward K-target inflation. Codex MUST report active-vs-skipped breakdown in T10 self-review.

**K-tripwire (per CLAUDE.md §Lesson Planner governance):** if K-actual exceeds 1.7× target (~3.4K LOC OR ~33 active tests excluding skipped placeholders), close the dev round and surface to operator.

**Required verification at implementation close (per T9):**
- `.\.venv\Scripts\python.exe -m pytest tests/unit/models tests/parity tests/structural tests/unit/manifest tests/integration/marcus tests/composition tests/specialists/texas tests/specialists/_scaffold -q --tb=line`
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py`
- `.\.venv\Scripts\python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-6-vocabulary-registry-parity-table.md`
- `.\.venv\Scripts\python.exe -m ruff check app/models tests/unit/models tests/parity tests/structural`
- `.\.venv\Scripts\lint-imports.exe`

---

## Dev Notes

### Architecture compliance

- **Composition Spec §3.6 (manifest-declared dependencies):** unaffected (7a.6 does not touch the manifest).
- **Composition Spec §11 trigger check:** additive only. Confirm no §11 trigger fires.
- **NFR-V3 registry additive-only:** documented at top of `vocabulary.yaml` + in parity table header.

### Library / framework requirements

- **PyYAML** (already shipped; per 7a.1 finding: ruamel NOT shipped, use PyYAML).
- **Pydantic v2** for `DecisionCard` model + StrEnum loader; follow `docs/dev-guide/pydantic-v2-schema-checklist.md`.
- **`enum.StrEnum`** (Python 3.11+; project uses 3.12 per `pyproject.toml`).
- **NO new third-party deps.**

### Anti-patterns to avoid

- **A12 procedural-coupling:** glossary emit + JSON Schema emit MUST be wired into CI sync-checks; do NOT introduce manual operator regen steps.
- **A9 epic-doc structural-name drift:** the canonical specialist names (`quinn_r`, `enrique`) match `app/manifest/compiler.py::SPECIALIST_ALIASES` aliases. Do NOT use `quinn-r` or `elevenlabs` in the registry roster.
- **A11 Windows-portability:** YAML emission uses `default_flow_style=False, allow_unicode=True`; line endings `\n`.
- **Sandbox-AC inventory rule:** ACs above use only Python + pytest + ruff + lint-imports. No `docker`, `psql`, `gh`, `curl`, etc.
- **Inline-string-literal vocabulary leak (FR-O4):** the AST scan in AC-F prevents downstream stories from emitting un-registered tokens. Do NOT weaken the scan to "warn" instead of "fail" — the SG-2 floor + FR-O4 are structural enforcement, not best-effort.

### Previous story intelligence

- **7a.1 substrate landings absorbed by 7a.6:**
  - PyYAML over ruamel.yaml.
  - `docs/conversational-gates/g0-directive-composition.md` exists (peer of the new `_registry/` siblings).
  - `tests/parity/__init__.py` + `tests/parity/test_trial_475_directive_composition_regression.py` already exist.
  - Composition Spec §10 entry pattern (the 2026-04-29 row for `runner_supplied_payload`) is the canonical example for substrate evolution documentation — but 7a.6 does NOT add a §10 entry (data + Pydantic schema, not composition substrate).
- **7a.2 substrate landings (in-flight; assumed-closed before 7a.6 opens):**
  - NodeSpec `fold_with` / `fold_target` fields don't affect 7a.6 (vocabulary registry is independent of manifest fold-flags).
  - `app/manifest/gate_topology.py` CLI from 7a.2 is a peer of 7a.6's `app/models/glossary_emit.py` CLI — same `python -m` pattern.
- **Slab 6 / Lesson Planner MVP precedents:** the four-file-lockstep pattern (model + JSON Schema + golden + shape-pin tests) is established by Story 31-1 and reinforced by Slab 6.4 Irene Pass-2 template; 7a.6 honors the same pattern.

### Project structure notes

- `app/models/` is the canonical location for Pydantic models (consistent with existing `app/models/{registry,specialist_model_config,state/...}.py`).
- `app/models/schemas/` is a NEW directory for emitted JSON Schemas; the in-sync test catches drift.
- `docs/conversational-gates/_registry/` is a NEW directory for the vocabulary registry + glossary; sibling of the per-gate doc family `docs/conversational-gates/g0-directive-composition.md` etc.
- `tests/fixtures/decision_cards/` is a NEW directory for golden fixtures.
- `tests/unit/models/` already exists (consistent with existing `tests/unit/models/test_*.py`).

### References

- [Source: `_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md` Story 1.3 (Vocabulary Registry + Parity-Table)]
- [Source: `_bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md` §FR21, FR24, FR34, FR35, FR38; §FR-A5, A6, A17; §FR-O1, O2, O4, O20, O21, O22]
- [Source: `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` (33-row SG-2 floor (operator-ratified 2026-04-29; previously PRD prose said 34 due to off-by-one))]
- [Source: `docs/dev-guide/migration-story-governance.json` story `7a-6`]
- [Source: `docs/dev-guide/pydantic-v2-schema-checklist.md` (four-file-lockstep + triple-layer red-rejection)]
- [Source: `docs/dev-guide/composition-specification.md` §3.6, §10 (Decision Log — NOT required for 7a.6), §11 (no trigger fires)]
- [Source: `docs/dev-guide/migration-ac-sandbox-inventory.json`]
- [Source: `docs/dev-guide/specialist-anti-patterns.md` A9, A11, A12]
- [Source: `app/manifest/compiler.py:43-46` (SPECIALIST_ALIASES canonical-form mapping)]
- [Source: `_bmad-output/implementation-artifacts/migration-7a-1-directive-composer.md` (7a.1 dev-cycle context — `docs/conversational-gates/` precedent + PyYAML finding)]
- [Source: CLAUDE.md §Pipeline lockstep regime (7a.6 doesn't trigger) + §LangChain/LangGraph migration — sandbox-AC + gate-mode governance]

---

## Dev Agent Record

### Agent Model Used

Codex (GPT-5), 2026-04-29 `bmad-dev-story` execution. Claude authored the
story spec; Codex implemented T1-T10 and leaves final T11 code-review/commit
close to Claude per the story boundary.

### Debug Log References

- T1 verified 7a.2 `done` in both the 7a.2 story and sprint-status.
- T1 verified mapping checklist row count exactly 33 via regex
  `^\| ?\d+ ?\|`; no SG-2 halt.
- Existing `app.models.decision_cards` is a package, not an unused module path.
  Vocabulary loader was implemented at `app/models/decision_cards/vocabulary.py`
  and exported from `app.models.decision_cards` to preserve existing gate-card
  imports.
- Unshimmed wider pytest has one known 7a.1 environment failure:
  `test_resolve_editor_posix_fallback` expects `vi` on PATH. Same temporary
  `vi` PATH shim pattern from 7a.2 yields a clean wider run.

### Completion Notes List

- Added the Slab 7a vocabulary registry with canonical 3 namespaces and the
  exact 11-specialist roster: `texas`, `irene`, `dan`, `tracy`, `gary`, `kira`,
  `wanda`, `enrique`, `compositor`, `quinn_r`, `vera`.
- Added Pydantic v2 vocabulary enums plus `VocabularyDecisionCard` schema pins,
  JSON Schema emission, golden fixture, and SG-1 import-time assertion.
- Added auto-generated glossary emitter and committed generated glossary with a
  drift-catching sync test.
- Added the operator-control parity table with exactly 33 rows and a matching
  33-function parity suite. Deferred rows are present as skipped placeholders
  with explicit story/slab reasons.
- Added structural checks for parity-table/test correspondence, schema sync,
  glossary sync, and ad-hoc vocabulary token leakage.
- No specialist body, manifest, runner, Marcus CLI, v4.2 prompt pack, or mapping
  checklist files were modified by 7a.6.

### File List

- `_bmad-output/implementation-artifacts/7a-6-codex-self-review-2026-04-29.md`
- `_bmad-output/implementation-artifacts/migration-7a-6-vocabulary-registry-parity-table.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/models/decision_cards/__init__.py`
- `app/models/decision_cards/__main__.py`
- `app/models/decision_cards/vocabulary.py`
- `app/models/glossary_emit.py`
- `app/models/schemas/decision_cards.schema.json`
- `docs/conversational-gates/_registry/glossary.md`
- `docs/conversational-gates/_registry/vocabulary.yaml`
- `docs/operator/legacy-vs-langgraph-control-parity.md`
- `tests/fixtures/decision_cards/decision_card_golden.json`
- `tests/parity/test_operator_control_parity.py`
- `tests/parity/test_operator_control_parity_row_count.py`
- `tests/structural/test_decision_cards_schema_in_sync.py`
- `tests/structural/test_glossary_in_sync.py`
- `tests/structural/test_no_ad_hoc_vocabulary_tokens.py`
- `tests/structural/test_parity_table_row_count.py`
- `tests/structural/test_parity_table_to_test_suite_correspondence.py`
- `tests/unit/models/test_decision_card_shape_pin.py`
- `tests/unit/models/test_glossary_emit.py`
- `tests/unit/models/test_specialist_roster_floor.py`
- `tests/unit/models/test_vocabulary_registry_load.py`

### Codex G6 Self-Review (T10)

Self-review artifact:
`_bmad-output/implementation-artifacts/7a-6-codex-self-review-2026-04-29.md`.

Summary: PASS-WITH-NOTES. SG-1 and SG-2 floors are structurally enforced.
Composition Spec section 11 trigger is negative. Wider verification is clean
with the known temporary `vi` PATH shim; unshimmed failure is unrelated 7a.1
environment brittleness.

### Claude Final Code-Review (T11)

(Claude pastes bmad-code-review verdict + remediation cycles here)

### N-Item / Rider Trace

- N1 PASS: new vocabulary loader and glossary emitter follow additive substrate
  checklist discipline and are test-pinned.
- N2 PASS: Composition Spec §3.6 and §11 invariants honored; no manifest change,
  envelope change, adapter contract change, or specialist body touch.
- N4 PASS: specialist isolation preserved; registry is operator/dev-agent-facing
  substrate only.
- N9 PASS-PENDING-OPERATOR: parity table and glossary readability ready for
  operator validation at close.
- N10 PASS: no manual glossary/schema sync step; generated artifacts have CI
  sync checks.
- A1/A11/A12 honored: `pathlib.Path`, PyYAML, deterministic generated files, no
  ruamel dependency.

### Decision Needed / Halt-And-Adapt

None. No HALT condition triggered.
