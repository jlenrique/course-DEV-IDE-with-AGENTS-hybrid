# Migration Story 7a.3: Pre-Gate-Marcus Shared LLM Node

**Status:** done
**Sprint key:** `migration-7a-3-pre-gate-marcus-shared-llm-node`
**Epic:** Slab 7a — Inter-Gate Conversational Orchestration (`migration-epic-slab-7a-inter-gate-orchestration`)
**Pts:** 3
**Gate:** **single-gate** (per `docs/dev-guide/migration-story-governance.json` v2026-04-28-slab7a-eight-stories, story 7a-3; rationale: null — substrate-extension)
**K-target:** ~1.3× (gate-shape band 1.5-2.5K; ~2.5K target)
**Authored:** 2026-04-29 via `bmad-create-story` workflow.
**Wave:** 3 — slot 2 (parallel with 7a.6; needs 7a.2 manifest substrate; INDEPENDENT of 7a.6 at the substrate level — Jinja2 template-with-slots pre-fill is self-contained — but the FR-O4 vocabulary-closure test starts `@pytest.mark.skip` and activates when 7a.6 closes).
**FR coverage:** 7 — FR2 (xc with 7a.6), FR3 (xc with 7a.5), FR21 (xc with 7a.6), FR22-prep, FR23-prep, FR24 (xc with 7a.6); FR-A4
**Standing-guardrail enforcement:**
- SG-1 unchanged (Marcus is orchestrator, not specialist roster member).
- SG-2 multiple checklist rows preserved (every gate has a corresponding pre-fill mechanism); coverage carried forward via 7a.8 aggregated assertion.
- SG-3 Composition Spec §3.5 gate-precedence rule HONORED (per-specialist gates remain non-blocking by default; pre-gate-marcus does NOT alter precedence).

**Implementation cycle (NEW per operator instruction 2026-04-28):**
- **Claude (Opus 4.7):** authored this spec; Gate-1 party-mode NOT called (single-gate substrate-extension; Jinja2 + Pydantic patterns are well-established).
- **Codex (Sonnet 4.5 or later):** develops source code + corresponding test suite per the ACs and tasks below; reaches `review` status; produces a self-conducted G6 layered review.
- **Claude:** does the FINAL `bmad-code-review`; applies remediation cycles; commits; flips `migration-7a-3-pre-gate-marcus-shared-llm-node` review → done in sprint-status.

---

## T1 Readiness Block

**Predecessor state (verified at authoring 2026-04-29):**
- Story 7a.1 (directive-composer) **CLOSED done** 2026-04-29 (commit `05bb2aa`).
- Story 7a.2 (manifest fold-flags + compiler ext) **CLOSED done** 2026-04-29.
- Story 7a.6 (vocabulary registry + parity-table) is in parallel Wave 3 dev. 7a.3's FR-O4 vocabulary-closure test starts `@pytest.mark.skip(reason="awaits Story 7a.6 vocabulary registry")`; the test activates implicitly when 7a.6 closes (the registry path exists + tokens are loadable).

**Live substrate (verified at authoring; do NOT regress):**
- `app/marcus/orchestrator/` is the canonical home for orchestration modules; existing siblings: `directive_composer.py` (7a.1), `dispatch_adapter.py` (7a.1 modified), `production_runner.py` (7a.1 + 7a.2 modified), `routing.py`, `supervisor.py`, `write_api.py`. The new module lands as `app/marcus/orchestrator/pre_gate_marcus.py`.
- `app/marcus/orchestrator/production_runner.py::_build_decision_card` (lines 325-373) is the existing single-shot decision-card builder — for each active gate (G1, G2C, G3, G4) it returns a hardcoded card shape (G1Card / G2CCard / G3Card / G4Card). 7a.3 does NOT replace `_build_decision_card`; it ADDS pre-fill values that the runner threads into `_build_decision_card`'s `drafted_proposal` field BEFORE the existing build.
- `app/models/adapter.py::make_chat_model(specialist_id, **kwargs)` is the canonical chat-model factory used by Irene (`app/specialists/irene/graph.py:344`) and others. 7a.3 invokes it once per gate transition with `specialist_id="marcus"` (or a new sentinel `"pre_gate_marcus"` registered in the specialist alias map at `app/manifest/compiler.py:43-46` if model resolution distinction is needed — surface as decision_needed at T1 if so).
- `state/config/pipeline-manifest.yaml` now has the `directive-composer` orchestration node (added by 7a.2). The new `pre-gate-marcus` orchestration node lands as a sibling (also `gate: false`, `specialist_id: null`, `hud_tracked: false`, `dependencies: {}`) — orchestration-only-node lockstep tolerance from 7a.2 is the prereq.
- `docs/conversational-gates/g0-directive-composition.md` exists from 7a.1. The new Jinja2 templates land at `docs/conversational-gates/g{1,2c,3,4}.j2` (one per active pause-point).
- `tests/composition/test_texas_to_cd_chain.py` has the M-R4 composer-driven parametrize case from 7a.1 + 4 other parametrize axes; preserve.

**Gate-mode rationale (from governance JSON):**
> Slab 7a wave-3 (parallel with 7a-6): pre-gate-marcus shared LLM node. Single LLM call site before each conversational gate; C1 template-with-slots pre-fill with confidence + rationale; reads vocabulary registry from 7a-6.

**T1 conclusion:** No unanticipated architectural disagreement requires halting Gate 0. Implementation proceeds: pre-gate-marcus module + Jinja2 template-with-slots + manifest registration + runner-side pre-fill threading + Composition Spec §3.5 invariant test + LangSmith trace assertion. Hard checkpoints at T1: confirm 7a.2 done; confirm `make_chat_model` import-path exists at `app/models/adapter.py`.

---

## Story

As the orchestration runtime,
I want a single shared `pre-gate-marcus` LangGraph node at `app/marcus/orchestrator/pre_gate_marcus.py` that pre-fills C1 template-with-slots decision-card proposals with confidence + rationale before each conversational gate,
so that all 4 active conversational pause-points (G1, G2C, G3, G4 — derived via `app.manifest.compiler.production_gate_ids(manifest)` from 7a.2) inherit a uniform pre-fill mechanism (no per-gate hand-rolling), single LLM call site, single checkpoint boundary, and Tier-1 additive manifest bump (vs Tier-2 if added per-gate).

---

## Acceptance Criteria

### AC-7.3-A — Manifest registration of `pre-gate-marcus` orchestration node (FR2)

**Given** the new shared `pre-gate-marcus` node
**When** the dev agent edits `state/config/pipeline-manifest.yaml`
**Then** a new orchestration-only node entry lands (mirrors the 7a.1 directive-composer pattern, accepted by 7a.2's lockstep tolerance):

```yaml
  - id: "pre-gate-marcus"
    label: "Pre-Gate Marcus — C1 template-with-slots pre-fill (Slab 7a / Story 7a.3)"
    specialist_id: null
    scaffold_node: null
    model_config_ref: null
    dependencies: {}
    gate: false
    gate_code: null
    sub_phase_of: null
    insertion_after: null
    hud_tracked: false
    pack_section_anchor: "0.5)"
    pack_version: "v4.2"
    fold_with: null
    fold_target: null
    rationale: >-
      Pure orchestration node — single LLM call site before each conversational
      pause-point. Pre-fills C1 template-with-slots decision-card proposals
      with confidence + rationale. Composition Spec §3.5 gate precedence rule
      UNALTERED (per-specialist gates remain non-blocking by default).
```

**And** `python scripts/utilities/check_pipeline_manifest_lockstep.py` exits 0 (orchestration-only-node tolerance from 7a.2 carries through).

**Test pin:** `tests/structural/test_pre_gate_marcus_node_registered.py` — asserts the node exists with canonical orchestration-only fields per AC-A.

### AC-7.3-B — Pre-gate-marcus module with C1 template-with-slots renderer (FR2, FR3)

**Given** the new module `app/marcus/orchestrator/pre_gate_marcus.py`
**When** the dev agent authors it
**Then** it implements:

```python
"""Pre-gate-marcus shared LLM node (Story 7a.3).

One LLM call site before each conversational pause-point (G1, G2C, G3, G4).
Renders a C1 template-with-slots prompt from docs/conversational-gates/<gate>.j2,
invokes app.models.adapter.make_chat_model("marcus", ...), and emits a structured
PreFillProposal that the runner threads into _build_decision_card's drafted_proposal.

Composition Spec §3.5 (per-specialist gate precedence) UNALTERED — pre-gate-marcus
does NOT promote any gate from non-blocking to blocking.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

TEMPLATE_DIR = Path(__file__).resolve().parents[3] / "docs" / "conversational-gates"


@dataclass(frozen=True)
class PreFillProposal:
    """Structured pre-fill output passed to runner._build_decision_card."""

    decision: str  # closed-enum from vocabulary registry (7a.6 enforces)
    directive: str  # closed-enum from vocabulary registry
    rationale: str  # min 20 chars per NFR-OX3
    confidence: float  # 0.0..1.0
    confidence_signals: tuple[str, ...] = field(default_factory=tuple)


def _jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        undefined=StrictUndefined,  # fail-loud on missing slot vars
        autoescape=False,
    )


def render_pre_fill_prompt(*, gate_id: str, slot_values: dict[str, Any]) -> str:
    """Render C1 template-with-slots prompt for a given gate.

    Args:
        gate_id: 'G1', 'G2C', 'G3', or 'G4'.
        slot_values: dict of slot names → values; must satisfy the template's
            StrictUndefined contract (every {{ slot }} must be present).

    Returns:
        Rendered prompt string.

    Raises:
        FileNotFoundError if the template doesn't exist.
        jinja2.UndefinedError if any slot is missing.
    """
    template_name = f"{gate_id.lower()}.j2"
    env = _jinja_env()
    template = env.get_template(template_name)
    return template.render(**slot_values)


def invoke_pre_gate_marcus(
    *,
    gate_id: str,
    slot_values: dict[str, Any],
    chat_model_factory: Any | None = None,
) -> PreFillProposal:
    """Single LLM call site before a conversational gate.

    Args:
        gate_id: active pause-point gate code.
        slot_values: slot fills for the C1 template.
        chat_model_factory: optional override (default: app.models.adapter.make_chat_model).

    Returns:
        PreFillProposal with decision/directive/rationale/confidence/signals.
    """
    if chat_model_factory is None:
        from app.models.adapter import make_chat_model
        chat_model_factory = make_chat_model

    handle = chat_model_factory("marcus")
    prompt = render_pre_fill_prompt(gate_id=gate_id, slot_values=slot_values)
    response = handle.chat.invoke([{"role": "user", "content": prompt}])
    return _parse_pre_fill_response(response.content)


def _parse_pre_fill_response(content: str) -> PreFillProposal:
    """Parse LLM JSON output into PreFillProposal; fail-loud on shape drift."""
    data = json.loads(content)
    rationale = data["rationale"]
    if len(rationale) < 20:
        raise ValueError(
            f"pre-gate-marcus rationale shorter than NFR-OX3 floor (20 chars): "
            f"got {len(rationale)} chars"
        )
    return PreFillProposal(
        decision=data["decision"],
        directive=data["directive"],
        rationale=rationale,
        confidence=float(data["confidence"]),
        confidence_signals=tuple(data.get("confidence_signals") or ()),
    )


__all__ = [
    "PreFillProposal",
    "TEMPLATE_DIR",
    "invoke_pre_gate_marcus",
    "render_pre_fill_prompt",
]
```

**Test pin:** `tests/unit/marcus/orchestrator/test_pre_gate_marcus.py` — 6 cases: (a) `render_pre_fill_prompt` succeeds for valid gate + slots, (b) missing slot raises `jinja2.UndefinedError`, (c) missing template raises `FileNotFoundError`, (d) `_parse_pre_fill_response` parses valid JSON, (e) rationale shorter than 20 chars raises `ValueError`, (f) `invoke_pre_gate_marcus` with stub chat_model_factory returns expected PreFillProposal shape.

### AC-7.3-C — Per-gate Jinja2 templates (FR2 + FR3)

**Given** the four active pause-point gates (G1, G2C, G3, G4)
**When** the dev agent authors the templates
**Then** four Jinja2 templates exist at `docs/conversational-gates/g{1,2c,3,4}.j2` (lowercase filename), each producing a C1 template-with-slots prompt that:
- Loads upstream gate state (per-gate slot variables: `trial_id`, `gate_id`, `upstream_contributions`, `pending_nodes`, `artifact_paths`).
- Asks the LLM to emit a JSON object with fields `decision`, `directive`, `rationale`, `confidence`, `confidence_signals`.
- Includes the closed-enum value sets in-prompt so the LLM knows the valid tokens (post-7a.6: pull from registry; pre-7a.6: hardcode the same enum sets that 7a.6 will register).

Example `docs/conversational-gates/g1.j2`:

```jinja
You are pre-gate-marcus. Emit a JSON object pre-filling the operator's G1 decision card.

## Context
Trial: {{ trial_id }}
Gate: G1 (Ingestion Quality Gate + Irene Packet)
Upstream contributions: {{ upstream_contributions | tojson }}
Pending downstream nodes: {{ pending_nodes | tojson }}
Artifact paths: {{ artifact_paths | tojson }}

## Output schema (JSON; closed enums)
{
  "decision": one of ["confirm", "revise", "reject", "escape"],
  "directive": one of ["accept-as-is", "apply-edit", "re-emit", "halt-for-repair"],
  "rationale": string ≥20 chars explaining the reasoning,
  "confidence": float 0.0..1.0,
  "confidence_signals": [list of short strings; signal names that drove confidence]
}

Emit ONLY the JSON object. No prose.
```

**Test pin:** `tests/structural/test_pre_gate_marcus_templates_present.py` — asserts all 4 templates exist + each contains the expected slot variable names + the expected closed-enum value lists.

### AC-7.3-D — Single-LLM-call-site invariant (FR2 + NFR-IN1; @pytest.mark.skip until 7a.6 closes)

**Given** the runtime invariant: pre-gate-marcus is the only LLM-invoking node before any conversational gate
**When** the dev agent authors the closure test
**Then** `tests/structural/test_pre_gate_marcus_single_call_site.py` AST-scans `app/marcus/orchestrator/` + `app/marcus/cli/` + `app/specialists/*/graph.py` and asserts NO direct `make_chat_model` call site exists at "before-gate" code paths OTHER than `app/marcus/orchestrator/pre_gate_marcus.py`.

**And** `tests/structural/test_pre_gate_marcus_vocabulary_closure.py` AST-scans `app/marcus/orchestrator/pre_gate_marcus.py` + each `docs/conversational-gates/g{1,2c,3,4}.j2` template + asserts every emitted decision/directive token is present in the vocabulary registry from 7a.6 (`docs/conversational-gates/_registry/vocabulary.yaml`). **This test starts `@pytest.mark.skip(reason="awaits Story 7a.6 vocabulary registry")` and activates when 7a.6 closes.**

**Test pin:** the two structural tests above.

### AC-7.3-E — Composition Spec §3.5 gate precedence UNALTERED (FR-A4)

**Given** the per-specialist `gate_decision` precedence rule (Composition Spec §3.5)
**When** pre-gate-marcus runs under production composition
**Then** per-specialist gates remain non-blocking by default; pre-gate-marcus does NOT promote any gate to blocking; `gate_overrides` opt-in semantic preserved.

**Test pin:** `tests/composition/test_pre_gate_marcus_precedence_unaltered.py` — runs the composition harness with pre-gate-marcus invoked before G1, asserts the existing `tests/composition/test_specialist_isolation_preserved.py` invariants hold (no per-specialist gate promoted; precedence semantic unchanged).

### AC-7.3-F — LangSmith trace single-invocation pin (FR2 + NFR-IN1)

**Given** LangSmith tracing is configured (LANGSMITH_API_KEY env present)
**When** the runner traces a trial through G1
**Then** LangSmith spans show exactly one `pre-gate-marcus` invocation per gate transition; downstream gate handlers do NOT invoke LLM directly.

**Test pin:** `tests/integration/marcus/test_pre_gate_marcus_langsmith_trace.py` — uses the existing test infrastructure for LangSmith tracing (mocked unless `LANGSMITH_API_KEY` is set); asserts one pre-gate-marcus span per gate-transition transition + zero other LLM spans before the gate.

### AC-7.3-G — Runner-side pre-fill threading (FR2 + FR3 + NFR-OX3)

**Given** the runner at `app/marcus/orchestrator/production_runner.py`
**When** the dev agent threads pre-fill output into the existing `_build_decision_card` flow
**Then** before each gate-handler invocation in `run_production_trial` (and `resume_production_trial`), the runner:
1. Calls `pre_gate_marcus.invoke_pre_gate_marcus(gate_id=gate_id, slot_values={...})` to get a PreFillProposal.
2. Passes the PreFillProposal into `_build_decision_card` via a NEW kwarg `pre_fill: PreFillProposal | None = None`.
3. `_build_decision_card` merges the pre-fill values into the `drafted_proposal` field of the resulting decision card (G1Card / G2CCard / G3Card / G4Card).

**And** the rationale floor (NFR-OX3 ≥20 chars) is enforced at `_parse_pre_fill_response` (already covered by AC-B).

**Test pin:** `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py` — asserts `decision_card.drafted_proposal` carries the pre-fill values when pre-gate-marcus is invoked; falls back to existing default `{"node_id": ..., "operator_id": ...}` when pre-fill is None (backward compat).

### AC-7.3-H — N-item + anti-pattern + Composition Spec trace

The implementation must record:
- **N1 PASS:** new module follows substrate-inventory checklist.
- **N2 PASS:** Composition Spec §3.5 invariant honored (per-specialist gate precedence unchanged).
- **N4 PASS:** specialist isolation preserved — pre-gate-marcus is orchestration; no specialist body touched.
- **N9 PASS-PENDING-OPERATOR:** operator validates pre-fill UX at story close.
- **N10 PASS:** A12 procedural-coupling re-read; pre-fill is wired into the runner (no manual operator step).
- **A1, A11 honored** — `pathlib.Path` throughout; Jinja2 templates use POSIX line endings.
- **Composition Spec §10 Decision Log entry NOT REQUIRED for 7a.3** — additive orchestration node (Tier-1 patch).

### AC-7.3-I — D12 close protocol

At close:
- Update `_bmad-output/implementation-artifacts/sprint-status.yaml`: `migration-7a-3-pre-gate-marcus-shared-llm-node` → `done`.
- Cite sandbox-AC validator PASS + lockstep PASS + ruff clean + lint-imports 9/9 KEPT.
- Confirm Composition Spec §11 trigger did not fire (additive only).

---

## Tasks / Subtasks

- [x] **T1: T1 Readiness review (Codex)**
  - [x] Read this spec end-to-end + cited references.
  - [x] Confirm 7a.2 status is `done` in BOTH spec file + sprint-status.yaml.
  - [x] Verify `app/models/adapter.py::make_chat_model` is importable.
  - [x] If 7a.6 has CLOSED before 7a.3 dev opens, the FR-O4 vocabulary-closure test (AC-D) is no longer `@pytest.mark.skip` — flip it active. If 7a.6 is still in-flight, leave the skip.
  - [x] Surface decision_needed if `make_chat_model("marcus")` doesn't resolve cleanly (model alias `marcus` may need to be added to `SPECIALIST_ALIASES` if not present).

- [x] **T2: Author `pre_gate_marcus.py` module** (AC: B)
  - [x] Create `app/marcus/orchestrator/pre_gate_marcus.py` per AC-B template (PreFillProposal dataclass + render_pre_fill_prompt + invoke_pre_gate_marcus + _parse_pre_fill_response).
  - [x] Author `tests/unit/marcus/orchestrator/test_pre_gate_marcus.py` (6 cases per AC-B test pin).

- [x] **T3: Author per-gate Jinja2 templates** (AC: C)
  - [x] Create `docs/conversational-gates/g{1,2c,3,4}.j2` (4 templates) per AC-C shape.
  - [x] Author `tests/structural/test_pre_gate_marcus_templates_present.py` (per AC-C test pin).

- [x] **T4: Single-call-site + vocabulary-closure structural tests** (AC: D)
  - [x] Author `tests/structural/test_pre_gate_marcus_single_call_site.py` (AST scan; asserts no direct `make_chat_model` call before-gate other than pre-gate-marcus).
  - [x] Author `tests/structural/test_pre_gate_marcus_vocabulary_closure.py` (`@pytest.mark.skip(reason="awaits Story 7a.6 vocabulary registry")` if 7a.6 not closed; active otherwise).

- [x] **T5: Composition Spec §3.5 invariant test** (AC: E)
  - [x] Author `tests/composition/test_pre_gate_marcus_precedence_unaltered.py` (uses existing composition harness).

- [x] **T6: LangSmith trace single-invocation pin** (AC: F)
  - [x] Author `tests/integration/marcus/test_pre_gate_marcus_langsmith_trace.py` (mock LangSmith unless env present).

- [x] **T7: Runner-side pre-fill threading** (AC: G)
  - [x] Add `pre_fill: PreFillProposal | None = None` kwarg to `_build_decision_card` in `app/marcus/orchestrator/production_runner.py`.
  - [x] Merge pre-fill values into `drafted_proposal` when present.
  - [x] At each gate-handler intercept in `run_production_trial` + `resume_production_trial`, call `invoke_pre_gate_marcus` BEFORE `_build_decision_card`.
  - [x] Author `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py` (per AC-G test pin).

- [x] **T8: Manifest registration + lockstep verify** (AC: A)
  - [x] Edit `state/config/pipeline-manifest.yaml`: add the `pre-gate-marcus` orchestration-only node per AC-A shape.
  - [x] Run `python scripts/utilities/check_pipeline_manifest_lockstep.py` → exit 0; trace records `orchestration_only_nodes: [directive-composer, pre-gate-marcus]`.
  - [x] Author `tests/structural/test_pre_gate_marcus_node_registered.py` (per AC-A test pin).

- [x] **T9: Verification battery (Codex G6 self-review for single-gate)**
  - [x] `.\.venv\Scripts\python.exe -m pytest tests/unit/marcus/orchestrator tests/structural/test_pre_gate_marcus_*.py tests/composition/test_pre_gate_marcus_*.py tests/integration/marcus/test_pre_gate_marcus_*.py tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py -q --tb=short`
  - [x] `.\.venv\Scripts\python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold -q --tb=line` → no regression vs pre-7a.3 baseline (247 passed / 1 skipped post-7a.2 close).
  - [x] `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` → exit 0.
  - [x] `.\.venv\Scripts\python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-3-pre-gate-marcus-shared-llm-node.md` → exit 0.
  - [x] `.\.venv\Scripts\python.exe -m ruff check app/marcus/orchestrator/pre_gate_marcus.py tests/unit/marcus/orchestrator/test_pre_gate_marcus.py tests/structural/test_pre_gate_marcus_*.py tests/composition/test_pre_gate_marcus_*.py tests/integration/marcus/test_pre_gate_marcus_*.py tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py` → clean.
  - [x] `.\.venv\Scripts\lint-imports.exe` → 9/9 contracts KEPT.

- [x] **T10: Codex G6 self-review (single-gate convention)**
  - [x] Codex authors self-review at `_bmad-output/implementation-artifacts/7a-3-codex-self-review-2026-04-XX.md` (Blind / Edge / Auditor).
  - [x] Codex flips story status `in-progress` → `review`.

- [ ] **T11: Claude `bmad-code-review` + remediation + commit + close** (Claude)

---

## File Structure Requirements

**Expected new files:**
- `app/marcus/orchestrator/pre_gate_marcus.py`
- `docs/conversational-gates/g1.j2`
- `docs/conversational-gates/g2c.j2`
- `docs/conversational-gates/g3.j2`
- `docs/conversational-gates/g4.j2`
- `tests/unit/marcus/orchestrator/test_pre_gate_marcus.py`
- `tests/structural/test_pre_gate_marcus_node_registered.py`
- `tests/structural/test_pre_gate_marcus_templates_present.py`
- `tests/structural/test_pre_gate_marcus_single_call_site.py`
- `tests/structural/test_pre_gate_marcus_vocabulary_closure.py`
- `tests/composition/test_pre_gate_marcus_precedence_unaltered.py`
- `tests/integration/marcus/test_pre_gate_marcus_langsmith_trace.py`
- `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py`
- `_bmad-output/implementation-artifacts/7a-3-codex-self-review-2026-04-XX.md` (T10 deliverable)

**Expected modified files:**
- `state/config/pipeline-manifest.yaml` (additive `pre-gate-marcus` orchestration-only node)
- `app/marcus/orchestrator/production_runner.py` (additive `pre_fill` kwarg on `_build_decision_card` + invoke pre-gate-marcus before each gate intercept)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (Claude does this at T11)

**Do NOT modify:**
- Any specialist body
- `app/marcus/orchestrator/directive_composer.py` (7a.1 surface)
- `app/marcus/orchestrator/dispatch_adapter.py` (7a.1 surface)
- `app/marcus/cli/trial.py` (7a.1 surface)
- `app/manifest/` (7a.2 surface)
- v4.2 prompt pack
- `docs/conversational-gates/_registry/` (7a.6 surface)

---

## Testing Requirements

**K-floor 14 + K-target ~22 (per governance JSON expected_k_target=1.3):**
- 6 pre_gate_marcus module cases (AC-B)
- 1 manifest-node registered (AC-A)
- 1 templates-present (AC-C)
- 1 single-call-site (AC-D)
- 1 vocabulary-closure (`@pytest.mark.skip` placeholder until 7a.6; AC-D)
- 1 §3.5 precedence (AC-E)
- 1 LangSmith trace (AC-F)
- 1 runner threads pre-fill (AC-G)

**K-tripwire:** 1.7× target (~3.4K LOC OR ~28 tests) → close round + party-mode triage.

---

## Dev Notes

### Architecture compliance

- **Composition Spec §3.5 (per-specialist gate precedence):** UNALTERED. Pre-gate-marcus only pre-fills the operator decision card; it does NOT promote any per-specialist gate to blocking.
- **Composition Spec §3.6 (manifest-declared dependencies):** the new orchestration node declares `dependencies: {}`.
- **ADR-D6 manifest-as-graph-config:** strengthened — pre-gate-marcus is a manifest node.
- **Composition Spec §11 trigger check:** additive only.

### Library / framework requirements

- **Jinja2** (already shipped; check `pyproject.toml` to confirm; if not, surface as decision_needed at T1).
- **Pydantic v2** for any schema-emit (PreFillProposal is a dataclass; no Pydantic overhead unless serialization needed).
- **`app.models.adapter.make_chat_model`** — canonical chat-model factory (already used by Irene).

### Anti-patterns to avoid

- **A12 procedural-coupling:** pre-gate-marcus invocation MUST be wired into the runner (no manual operator step).
- **A11 Windows-portability:** Jinja2 templates use `\n` line endings; `Path.as_posix()` for any path serialization.
- **Sandbox-AC inventory rule:** Python + pytest + ruff + lint-imports only.
- **Multiple LLM call sites before a gate:** AC-D structural enforcement; do NOT add direct `make_chat_model` calls in any other before-gate path.
- **Hardcoded vocabulary tokens before 7a.6:** acceptable as a transitional pattern, but the templates MUST be designed so that 7a.6's vocabulary registry can replace the inline values without template-shape change (use `{% include %}` or simple string substitution that the AST scan can validate).

### References

- [Source: `_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md` Story 1.4]
- [Source: `_bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md` §FR2, FR3, FR21-xc, FR22-prep, FR23-prep, FR24-xc; §FR-A4]
- [Source: `docs/dev-guide/migration-story-governance.json` story `7a-3`]
- [Source: `docs/dev-guide/composition-specification.md` §3.5 (gate precedence — unaltered)]
- [Source: `docs/dev-guide/migration-ac-sandbox-inventory.json`]
- [Source: `app/marcus/orchestrator/production_runner.py:325-373` (`_build_decision_card` insertion target)]
- [Source: `app/models/adapter.py::make_chat_model` (canonical chat-model factory)]
- [Source: `app/specialists/irene/graph.py:344` (existing `make_chat_model` consumer pattern)]
- [Source: `_bmad-output/implementation-artifacts/migration-7a-2-manifest-fold-flags-compiler-extension.md` (7a.2 substrate; orchestration-only-node tolerance)]
- [Source: CLAUDE.md §Pipeline lockstep regime + §LangChain/LangGraph migration — sandbox-AC + gate-mode governance]

---

## Dev Agent Record

### Agent Model Used

Codex (GPT-5), 2026-04-29 dev-story execution. Claude authored the spec; Codex implemented T1-T10 and left T11 close actions to Claude per operator boundary.

### Debug Log References

- T1 hard checkpoints passed: 7a.2 `done` in both story + sprint-status, Jinja2 shipped in `pyproject.toml`, and `make_chat_model("marcus")` imports/resolves.
- Mid-dev update: 7a.6 closed to `done`; vocabulary-closure test was authored active against `docs/conversational-gates/_registry/vocabulary.yaml`.
- Focused pytest note: PowerShell does not expand pytest wildcards, so the focused battery was run with explicit file paths.
- Wider pytest note: the known 7a.1 POSIX editor fallback test requires a temporary `vi` PATH shim on this Windows environment; with the shim, the wider slice passed.
- Lockstep trace: `reports/dev-coherence/2026-04-29-0505/check-pipeline-manifest-lockstep.PASS.yaml`.

### Completion Notes List

- Added `app/marcus/orchestrator/pre_gate_marcus.py` with StrictUndefined Jinja rendering, single `make_chat_model("marcus")` call site, `PreFillProposal`, rationale floor, and confidence bounds.
- Added four per-gate C1 templates at `docs/conversational-gates/g{1,2c,3,4}.j2`.
- Registered `pre-gate-marcus` as an orchestration-only manifest node and updated existing manifest/lockstep regression pins for the second orchestration-only node.
- Threaded optional pre-fill data into `_build_decision_card.drafted_proposal`; runner start/resume gate intercepts call the pre-gate helper before card/bypass handling while preserving 7a.2's resume-mode `GateBypassError` behavior.
- Added unit, structural, composition, and integration coverage for renderer/parser behavior, templates, manifest registration, single-call-site closure, active vocabulary closure, precedence invariance, trace fixture, and persisted decision-card pre-fill.

### File List

- `app/marcus/orchestrator/pre_gate_marcus.py`
- `app/marcus/orchestrator/production_runner.py`
- `docs/conversational-gates/g1.j2`
- `docs/conversational-gates/g2c.j2`
- `docs/conversational-gates/g3.j2`
- `docs/conversational-gates/g4.j2`
- `state/config/pipeline-manifest.yaml`
- `tests/unit/marcus/orchestrator/test_pre_gate_marcus.py`
- `tests/unit/manifest/test_compiler.py`
- `tests/structural/test_pre_gate_marcus_node_registered.py`
- `tests/structural/test_pre_gate_marcus_templates_present.py`
- `tests/structural/test_pre_gate_marcus_single_call_site.py`
- `tests/structural/test_pre_gate_marcus_vocabulary_closure.py`
- `tests/structural/test_lockstep_orchestration_only_tolerance.py`
- `tests/composition/test_pre_gate_marcus_precedence_unaltered.py`
- `tests/integration/marcus/test_pre_gate_marcus_langsmith_trace.py`
- `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py`
- `_bmad-output/implementation-artifacts/7a-3-codex-self-review-2026-04-29.md`

### Codex G6 Self-Review (T10)

Self-review artifact: `_bmad-output/implementation-artifacts/7a-3-codex-self-review-2026-04-29.md`.

Summary: PASS. One in-cycle patch was applied to keep fake OpenAI keys from triggering live pre-gate invocation in existing tests. Active 7a.3 test count is 17, below the story tripwire.

### Verification

```
.\.venv\Scripts\python.exe -m pytest tests\unit\marcus\orchestrator <explicit pre_gate structural/composition/integration files> tests\integration\marcus\test_runner_threads_pre_fill_to_decision_card.py -q --tb=short
-> 35 passed

.\.venv\Scripts\python.exe -m pytest tests\unit\manifest tests\integration\marcus tests\composition tests\parity tests\structural tests\specialists\texas tests\specialists\_scaffold -q --tb=line
-> 281 passed, 20 skipped (with temporary vi PATH shim for known 7a.1 editor fallback environment assumption)

.\.venv\Scripts\python.exe scripts\utilities\check_pipeline_manifest_lockstep.py
-> exit 0; trace records orchestration_only_nodes: [directive-composer, pre-gate-marcus]

.\.venv\Scripts\python.exe scripts\utilities\validate_migration_story_sandbox_acs.py _bmad-output\implementation-artifacts\migration-7a-3-pre-gate-marcus-shared-llm-node.md
-> PASS

.\.venv\Scripts\python.exe -m ruff check app\marcus\orchestrator\pre_gate_marcus.py app\marcus\orchestrator\production_runner.py tests\unit\marcus\orchestrator\test_pre_gate_marcus.py tests\unit\manifest\test_compiler.py tests\structural\test_lockstep_orchestration_only_tolerance.py <explicit pre_gate structural/composition/integration files> tests\integration\marcus\test_runner_threads_pre_fill_to_decision_card.py
-> All checks passed

.\.venv\Scripts\lint-imports.exe
-> Contracts: 9 kept, 0 broken
```

### N-Item / Rider Trace

- N1 PASS: new module follows substrate-inventory checklist.
- N2 PASS: Composition Spec Section 3.5 invariant honored; per-specialist gate precedence unchanged.
- N4 PASS: specialist isolation preserved; no specialist body touched.
- N9 PASS-PENDING-OPERATOR: operator validates pre-fill UX at story close.
- N10 PASS: A12 procedural-coupling re-read; pre-fill is runner-wired, not manual.
- A1/A11 honored: `Path` used for filesystem surfaces; templates authored with LF line endings.
- Composition Spec Section 10 Decision Log entry not required; Section 11 trigger did not fire (additive orchestration node only).

### Decision Needed / Halt-And-Adapt

No halt condition triggered. 7a.6 closed during this dev cycle, so Codex activated the vocabulary-closure test rather than leaving it skipped.

