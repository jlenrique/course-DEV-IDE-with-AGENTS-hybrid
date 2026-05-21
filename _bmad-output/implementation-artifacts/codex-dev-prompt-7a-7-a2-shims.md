# Codex dev-story prompt — Story 7a.7 (A2 single-decision shims for terminal gates G1/G2C/G3/G4)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 5 slot 1 (parallel with start of 7a.8; INDEPENDENT of 7a.4/7a.5/7a.6 substrate; only depends on 7a.6 for vocabulary closure test).

---

```
Run bmad-dev-story on Story 7a.7 (Slab 7a Wave 5 slot 1; single-gate; A2 single-decision CLI shims for terminal gates G1/G2C/G3/G4 + audience-layered help text + per-gate operator references).

## Required reading (read in order)

1. Story spec: `_bmad-output/implementation-artifacts/migration-7a-7-a2-single-decision-shims-terminal-gates.md` (status: ready-for-dev; 7 ACs A-G; 10 tasks T1-T10; you own T1-T9)
2. Predecessor 7a.4 (vocabulary may not yet be active): if 7a.4 has CLOSED, OperatorVerdict has the additive `revise_count` field; 7a.7's verdict-loading must accept the new shape
3. 7a.6 spec (parallel; for vocabulary closure): `app/models/decision_cards.py` lands when 7a.6 closes; 7a.7's `test_shim_verdict_vocabulary_closure` test starts `@pytest.mark.skip(reason="awaits Story 7a.6 vocabulary registry")` and activates when 7a.6 closes
4. 7a.1 surface: `app/marcus/cli/trial.py` (CLI argparse subparser pattern; mirror for shim parsers)
5. 7a.2 substrate: `app/manifest/compiler.py::production_gate_ids(manifest)` returns `{G1, G2C, G3, G4}` — the 4 terminal gates
6. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7a-7` (single-gate; expected_pts=2; expected_k_target=1.3)
7. `app/models/state/operator_verdict.py::OperatorVerdict` — Pydantic model that shims emit
8. Sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- `OperatorVerdict` is loadable with current shape (incl. 7a.4's `revise_count` if 7a.4 closed).
- `app/marcus/cli/gate_cli.py` argparse-extension shape understood; additive subparser registration pattern verified.
- 7a.7 is INDEPENDENT of 7a.4/7a.5; only soft-depends on 7a.6 for vocabulary closure (which gracefully degrades to skip-pending).

## Files in scope

**New:** `app/marcus/cli/gate_shims/__init__.py`, `app/marcus/cli/gate_shims/_shim_parser.py`, `app/marcus/cli/gate_shims/g{1,2c,3,4}_shim.py` (4 shim modules), `docs/conversational-gates/g{1,2c,3,4}-operator-reference.md` (4 operator-doc files), `tests/cli/__init__.py`, `tests/cli/test_{shim_basic_invocation,shim_help_structure}.py`, `tests/composition/test_a2_shims_composition_smoke.py`, `tests/structural/test_{shim_verdict_vocabulary_closure,per_gate_operator_reference_docs}.py`, `tests/unit/marcus/cli/__init__.py`, `tests/unit/marcus/cli/test_shim_parser_factory.py`, `_bmad-output/implementation-artifacts/migration-7-7-a2-shims-composition-smoke.{py,md}`, `_bmad-output/implementation-artifacts/7a-7-codex-self-review-2026-04-XX.md`.

**Modified:** `app/marcus/cli/gate_cli.py` (additive: register the 4 shim subparsers; do NOT modify existing entry points); `_bmad-output/implementation-artifacts/sprint-status.yaml` (Claude T11).

**Do NOT modify:** specialist bodies; OperatorVerdict model (7a.4 owns the additive `revise_count`); 7a.1-7a.6 surfaces; manifest.

## Critical implementation notes

- **OPERATOR/INPUTS/OUTPUTS/REFERENCE help-text structure (AC-7.7-B):** EXACT match (case + spacing); underlines exactly 8 chars (length-pinned for grep stability). Section order: OPERATOR → INPUTS → OUTPUTS → REFERENCE. CI lint test parametrized over 4 shims.
- **Shared `_shim_parser.py` factory (AC-7.7-E):** single source of truth for parser shape; per-gate shim file ≤80 lines.
- **Composition Smoke gate at A2 boundary (AC-7.7-C):** smoke script wires each shim → resume_production_trial stub → assert no raise; mirror 7a.1's `test_slab_7a_opener_composition_smoke.py` pattern.
- **Vocabulary closure test:** `@pytest.mark.skip` until 7a.6 closes.
- **Per-gate operator references (AC-7.7-F):** 4 docs with 5 named subsections (verdict file shape / decision tokens / directive tokens / common patterns / troubleshooting).
- **Exit codes:** 0 success, 1 RuntimeError, 2 ValidationError.
- **No new third-party deps.**

## Verification battery (T8)

```bash
.venv/Scripts/python.exe -m pytest tests/cli tests/composition/test_a2_shims_composition_smoke.py tests/structural/test_{shim_verdict_vocabulary_closure,per_gate_operator_reference_docs}.py tests/unit/marcus/cli -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold -q --tb=line
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-7-a2-single-decision-shims-terminal-gates.md
.venv/Scripts/python.exe -m ruff check app/marcus/cli/gate_shims tests/cli tests/composition/test_a2_shims_composition_smoke.py tests/structural tests/unit/marcus/cli
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe -m app.marcus.cli.gate_shims.g1_shim --help
.venv/Scripts/python.exe -m app.marcus.cli.gate_shims.g2c_shim --help
.venv/Scripts/python.exe -m app.marcus.cli.gate_shims.g3_shim --help
.venv/Scripts/python.exe -m app.marcus.cli.gate_shims.g4_shim --help
.venv/Scripts/python.exe _bmad-output/implementation-artifacts/migration-7-7-a2-shims-composition-smoke.py
```

Expected: zero new failures vs current baseline.

## T9 + T10

T9: Codex G6 self-review (Blind / Edge / Auditor) at `_bmad-output/implementation-artifacts/7a-7-codex-self-review-2026-04-XX.md`. Flip story status to `review`. Hand to Claude.

T10: Claude does FINAL bmad-code-review + remediation + commit + flips `migration-7a-7-a2-single-decision-shims-terminal-gates` review → done.

## Boundary

- HALT and surface on: (a) OperatorVerdict shape unexpected (e.g. 7a.4's `revise_count` field absent when 7a.4 is supposedly closed), (b) gate_cli.py argparse pattern blocks additive subparser registration, (c) Composition Spec §11 trigger fires (additive CLI surface; should not), (d) K-actual exceeds 1.7× target (~3.4K LOC OR ~31 active tests excluding skipped placeholders), (e) any sandbox-AC violation.
- Do NOT touch specialist bodies, OperatorVerdict model, or 7a.1-7a.6 surfaces.
- Do NOT introduce ruamel.yaml or new third-party deps.
```
