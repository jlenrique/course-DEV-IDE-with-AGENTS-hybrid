# Migration Story 7a.7: A2 Single-Decision Shims for Terminal Gates (G1, G2C, G3, G4)

**Status:** done  # 2026-04-29: CLOSED. Claude developed AND self-reviewed directly per operator instruction (Codex on 7a.5).
**Sprint key:** `migration-7a-7-a2-single-decision-shims-terminal-gates`
**Epic:** Slab 7a — Inter-Gate Conversational Orchestration (`migration-epic-slab-7a-inter-gate-orchestration`)
**Pts:** 2
**Gate:** **single-gate** (per `docs/dev-guide/migration-story-governance.json` v2026-04-28-slab7a-eight-stories, story 7a-7; rationale: null)
**K-target:** ~1.3× (gate-shape band 1.5-2.5K; ~2K target)
**Authored:** 2026-04-29 via `bmad-create-story` workflow.
**Wave:** 5 — slot 1 (parallel with start of 7a.8; INDEPENDENT of 7a.4/7a.5/7a.6).
**FR coverage:** 5 — FR22, FR23; FR-A6 (xc); NFR-OD1, NFR-OD2 (first-class story-scoped operator-documentation surface)
**Standing-guardrail enforcement:**
- SG-1 unchanged.
- SG-2 four terminal-gate rows preserved (G1, G2C, G3, G4 already in mapping checklist).
- SG-3 Composition Spec §3.5 gate precedence honored.

**Implementation cycle (NEW):** Claude spec → Codex dev+tests → Claude review+commit.

---

## T1 Readiness Block

**Predecessor state (verified at authoring 2026-04-29):**
- Stories 7a.1 + 7a.2 CLOSED done. 7a.3, 7a.4, 7a.5, 7a.6 ready-for-dev (7a.7 INDEPENDENT of all of them at substrate level — only depends on 7a.6 vocabulary registry for closed-enum tokens).
- 7a.6 (vocabulary registry) provides `GateDecisionToken` enum (`confirm, revise, reject, escape, skip-slide, abort-run`) — used by AC-7.7-D verdict closure. If 7a.6 not yet closed when 7a.7 dev opens, the `test_shim_verdict_vocabulary_closure` test starts `@pytest.mark.skip` and activates when 7a.6 closes.

**Live substrate (verified at authoring):**
- `app/marcus/cli/` houses CLI shims (existing siblings: `trial.py`, `gate_cli.py`, `adhoc_cli.py`). NEW package: `app/marcus/cli/gate_shims/` with 4 modules + `__init__.py`.
- `app/models/state/operator_verdict.py::OperatorVerdict` is the existing Pydantic model that shims emit. 7a.7 does NOT modify the model (7a.4 may extend it with `revise_count` for max-3 oscillation; 7a.7 reads the post-7a.4 shape).
- `app/marcus/cli/gate_cli.py` is the existing single CLI entry point. 7a.7 adds 4 sibling modules under `gate_shims/` and registers them via `gate_cli.py` argparse subparsers (additive).
- `app/manifest/compiler.py::production_gate_ids(manifest)` (from 7a.2) returns `{G1, G2C, G3, G4}` — the 4 active terminal gates that 7a.7 shims target.

**Block-mode trigger paths touched by this story:** none.

**Gate-mode rationale (from governance JSON):**
> Slab 7a wave-5 (parallel with start of 7a-8): A2 single-decision CLI shims for terminal gates G1/G2C/G3/G4. Audience-layered help text (OPERATOR/INPUTS/OUTPUTS/REFERENCE structure). Carries NFR-OD1/OD2 first-class story-scoped; 5 FRs after Mary's augment per Step 2 finding.

**T1 conclusion:** Implementation proceeds. Hard checkpoints at T1: confirm `app/models/state/operator_verdict.py::OperatorVerdict` exists; confirm `app/marcus/cli/gate_cli.py` argparse-extension shape.

---

## Story

As the operator,
I want gate-scoped CLI shims at `app/marcus/cli/gate_shims/g{1,2c,3,4}_shim.py` for the four terminal gates that already pause cleanly today (G1, G2C, G3, G4), each with audience-layered help text following the OPERATOR/INPUTS/OUTPUTS/REFERENCE four-section structure,
so that I have a uniform single-decision CLI surface for terminal gates (no multi-field card required) and I can hand the PRD to Codex for parallel-authoring of similar shims in Slab 7b without reauthoring the help-text contract.

---

## Acceptance Criteria

### AC-7.7-A — Four shim modules + single-decision verdict (FR22)

**Given** four shim modules
**When** the operator invokes `python -m app.marcus.cli.gate_shims.g{1,2c,3,4}_shim --verdict-file <path>` (OR via `bmad-trial gate G_n --verdict-file <path>` after gate_cli.py registration)
**Then** the shim accepts a single-decision verdict (NO multi-field card required); structured payload conforms to `app/models/state/operator_verdict.py::OperatorVerdict`.
**And** each shim has the same skeleton:
1. `argparse` parser with `--trial-id`, `--verdict-file`, `--operator-id`.
2. Load OperatorVerdict from verdict file.
3. Call `app.marcus.orchestrator.production_runner.resume_production_trial(trial_id, verdict, runs_root)`.
4. Print resume payload as JSON; exit 0 on success; exit 1 on RuntimeError; exit 2 on ValidationError.

**Test pin:** `tests/cli/test_shim_basic_invocation.py` — 4 cases (one per gate); each asserts (a) shim accepts --verdict-file, (b) resume_production_trial called with correct args, (c) JSON payload printed, (d) exit code per success/error path.

### AC-7.7-B — OPERATOR/INPUTS/OUTPUTS/REFERENCE help-text structure (FR23, NFR-OD1, NFR-OD2)

**Given** each shim's `--help` output
**When** the operator runs `python -m app.marcus.cli.gate_shims.g{1,2c,3,4}_shim --help`
**Then** the help text contains FOUR named sections in EXACT order:

```
OPERATOR
========
<who this shim is for; when to invoke; what it does in one sentence>

INPUTS
======
<--trial-id, --verdict-file, --operator-id, --runs-root with shape + example>

OUTPUTS
=======
<JSON payload schema; exit codes; side-effects (run-state mutation, checkpoint write)>

REFERENCE
=========
<links to docs/conversational-gates/g<gate-id>-*.md, OperatorVerdict schema, Story 7a.7 spec>
```

**And** the four section headers are EXACT match (case + spacing); the underlines (`====`) are exactly 8 chars (length-pinned for grep stability).

**Test pin:** `tests/cli/test_shim_help_structure.py` — parametrized over the 4 shims; for each: (a) `--help` exit 0, (b) all four section headers present in order, (c) underlines correct, (d) all required content in each section.

### AC-7.7-C — Composition Smoke gate evidence at A2 boundary (FR-A6 cross-cite from 7a.6)

**Given** the Composition Smoke gate evidence at A2 boundary
**When** the dev-agent opens 7a.7
**Then** the shim layer is exercised in Composition Smoke: each terminal-gate shim accepts a stub verdict + advances the runner without raising.
**And** smoke evidence captures PASS verdict + pastes into Completion Notes once at `_bmad-output/implementation-artifacts/migration-7-7-a2-shims-composition-smoke.md`.

**Test pin:** `tests/composition/test_a2_shims_composition_smoke.py` (CI-runnable wrapper for the smoke script; mirrors 7a.1's `test_slab_7a_opener_composition_smoke.py` pattern).

### AC-7.7-D — Decision-card vocabulary closure (FR-O4 cross-cite from 7a.6)

**Given** the decision-card vocabulary registry from 7a.6
**When** any shim emits a verdict
**Then** the verdict tokens (decision/directive) are drawn EXCLUSIVELY from the registry; no inline string literals.
**And** the shims import `from app.models.decision_cards import GateDecisionToken, GateDirectiveToken` and use enum values (NOT raw strings).

**Test pin:** `tests/structural/test_shim_verdict_vocabulary_closure.py` — `@pytest.mark.skip(reason="awaits Story 7a.6 vocabulary registry")` if 7a.6 not closed; active otherwise. AST-scans the 4 shim modules for inline string literals matching vocabulary-token shape; asserts NONE found.

### AC-7.7-E — Argparse uniformity across shims (NFR-OD1)

**Given** the 4 shims share the OPERATOR/INPUTS/OUTPUTS/REFERENCE template
**When** the dev-agent authors the parsers
**Then** all 4 shims use a SHARED `_build_shim_parser(gate_id: str) -> argparse.ArgumentParser` factory at `app/marcus/cli/gate_shims/_shim_parser.py` (NEW module) — single source of truth for parser shape; reduces drift between shims.
**And** each per-gate shim file is ≤80 lines (the heavy lifting is in the shared factory).

**Test pin:** `tests/unit/marcus/cli/test_shim_parser_factory.py` — 5 cases: (a) factory builds parser with all required args, (b) parser help-text passes structure test, (c) trial-id parsed as UUID, (d) verdict-file parsed as Path, (e) factory raises on unknown gate_id.

### AC-7.7-F — Operator-doc surface: per-gate operator references (NFR-OD2)

**Given** the operator-documentation surface
**When** the dev-agent authors the per-gate references
**Then** four NEW operator-facing docs land at `docs/conversational-gates/g{1,2c,3,4}-operator-reference.md` with this template:

```markdown
# G<gate-id> — Operator Reference

**Use this doc when:** you've received a paused-at-G<gate-id> notification from a trial and need to author a verdict file.

## Verdict file shape
<JSON example with all required fields>

## Decision tokens
<closed enum from vocabulary registry; one-line per token>

## Directive tokens
<closed enum from vocabulary registry; one-line per token>

## Common patterns
<2-3 worked examples: minimal approve, edit-with-rationale, reject>

## Troubleshooting
<exit-code interpretation; common verdict-file errors>
```

**Test pin:** `tests/structural/test_per_gate_operator_reference_docs.py` — 4 cases: each doc has the 5 named subsections + non-empty content per section.

### AC-7.7-G — N-item + anti-pattern + Composition Spec trace + D12 close

**N4 PASS:** specialist isolation preserved — shims call resume_production_trial which calls into the dispatch adapter; specialist bodies untouched. **N9 PASS-PENDING-OPERATOR:** operator validates shim help-text + invocation UX at trial-2. **A11 honored:** `Path.as_posix()` in JSON payloads. **Composition Spec §3.5 (per-specialist non-blocking) HONORED.** **§11 trigger NEGATIVE.**

D12 close: sprint-status flip; sandbox-AC + ruff + lint-imports clean.

---

## Tasks / Subtasks

- [ ] **T1: Readiness review (Codex)** — confirm OperatorVerdict + gate_cli.py shape.
- [ ] **T2: Author `_shim_parser.py` factory** (AC-E) — single source of truth for parser shape.
- [ ] **T3: Author 4 shim modules** (AC-A) — `g{1,2c,3,4}_shim.py`; each ≤80 lines using the shared factory.
- [ ] **T4: Help-text structure** (AC-B) — embed OPERATOR/INPUTS/OUTPUTS/REFERENCE in each shim's parser.description; structural test.
- [ ] **T5: Per-gate operator references** (AC-F) — 4 docs at `docs/conversational-gates/g{1,2c,3,4}-operator-reference.md`; structural test.
- [ ] **T6: Composition Smoke gate at A2 boundary** (AC-C) — smoke script + CI wrapper + evidence file.
- [ ] **T7: Vocabulary closure** (AC-D) — AST scan; `@pytest.mark.skip` until 7a.6.
- [ ] **T8: Verification battery** — focused + wider regression slice; sandbox-AC; ruff; lint-imports.
- [ ] **T9: Codex G6 self-review.**
- [ ] **T10: Claude bmad-code-review + remediation + commit + close.**

---

## File Structure Requirements

**New:** `app/marcus/cli/gate_shims/__init__.py`, `app/marcus/cli/gate_shims/_shim_parser.py`, `app/marcus/cli/gate_shims/g1_shim.py`, `app/marcus/cli/gate_shims/g2c_shim.py`, `app/marcus/cli/gate_shims/g3_shim.py`, `app/marcus/cli/gate_shims/g4_shim.py`, `docs/conversational-gates/g1-operator-reference.md`, `docs/conversational-gates/g2c-operator-reference.md`, `docs/conversational-gates/g3-operator-reference.md`, `docs/conversational-gates/g4-operator-reference.md`, `tests/cli/__init__.py`, `tests/cli/test_shim_basic_invocation.py`, `tests/cli/test_shim_help_structure.py`, `tests/composition/test_a2_shims_composition_smoke.py`, `tests/structural/test_shim_verdict_vocabulary_closure.py`, `tests/structural/test_per_gate_operator_reference_docs.py`, `tests/unit/marcus/cli/__init__.py`, `tests/unit/marcus/cli/test_shim_parser_factory.py`, `_bmad-output/implementation-artifacts/migration-7-7-a2-shims-composition-smoke.{py,md}`, `_bmad-output/implementation-artifacts/7a-7-codex-self-review-2026-04-XX.md`.

**Modified:** `app/marcus/cli/gate_cli.py` (additive: register the 4 shim subparsers; do NOT modify existing entry points); `_bmad-output/implementation-artifacts/sprint-status.yaml` (Claude T11).

**Do NOT modify:** specialist bodies; OperatorVerdict model (7a.4 owns the additive `revise_count`); 7a.1-7a.6 surfaces; manifest.

---

## Testing Requirements

**K-floor 14 + K-target ~22 (per gate-shape band 1.5-2.5K):**
- 4 shim basic invocation cases (AC-A; one per gate)
- 16 help-structure cases (AC-B; 4 cases × 4 shims)
- 1 Composition Smoke gate (AC-C)
- 1 vocabulary closure (`@pytest.mark.skip` until 7a.6; AC-D)
- 5 shim parser factory cases (AC-E)
- 4 per-gate operator reference doc cases (AC-F)

**K-tripwire:** 1.7× target (~3.4K LOC OR ~31 active tests) → close round + party-mode triage.

---

## Dev Notes

**Architecture compliance:** Composition Spec §3.5 honored (shims invoke resume_production_trial which respects gate precedence); Composition Spec §11 NEGATIVE (additive CLI surface).

**Library/framework:** stdlib `argparse`, `json`, `pathlib`. Pydantic v2 (already shipped) for OperatorVerdict load. NO new third-party deps.

**Anti-patterns to avoid:** A12 procedural-coupling — shared `_shim_parser.py` factory prevents per-shim drift; A11 Windows-portability — POSIX paths in CLI output.

**Previous story intelligence:** 7a.1 (CLI subparser pattern in `app/marcus/cli/trial.py`); 7a.6 (vocabulary registry → enum import); 7a.2 (`production_gate_ids(manifest)` confirms 4 terminal gates).

**References:** Epic Story 1.7; PRD §FR22, FR23 + §FR-A6 + §NFR-OD1, NFR-OD2; governance JSON `7a-7`; CLAUDE.md governance.

---

## Dev Agent Record

(populate at dev-open)
