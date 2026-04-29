# Codex dev-story prompt — Story 7a.3 (pre-gate-marcus shared LLM node)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 3 slot 2 (parallel with 7a.6; needs 7a.2 substrate [DONE 2026-04-29]; INDEPENDENT of 7a.6 at substrate level).

---

```
Run bmad-dev-story on Story 7a.3 (Slab 7a Wave 3 slot 2; single-gate; pre-gate-marcus shared LLM node + Jinja2 templates + manifest registration + runner-side pre-fill threading).

## Required reading (read in order)

1. Story spec: `_bmad-output/implementation-artifacts/migration-7a-3-pre-gate-marcus-shared-llm-node.md` (status: ready-for-dev; 9 ACs A-I; 11 tasks T1-T11; you own T1-T10)
2. Predecessor 7a.2 (CLOSED done 2026-04-29): `_bmad-output/implementation-artifacts/migration-7a-2-manifest-fold-flags-compiler-extension.md` — orchestration-only-node lockstep tolerance + manifest fold-flag substrate
3. 7a.1 surface (DONE; reference only): `app/marcus/orchestrator/{directive_composer,dispatch_adapter,production_runner}.py` — reuse the `runner_supplied_payload` pattern
4. 7a.6 spec (parallel; NOT yet closed): `_bmad-output/implementation-artifacts/migration-7a-6-vocabulary-registry-parity-table.md` — vocabulary registry shape; 7a.3's FR-O4 vocabulary-closure test starts `@pytest.mark.skip(reason="awaits Story 7a.6 vocabulary registry")` and activates when 7a.6 closes
5. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7a-3` (single-gate; expected_pts=3; expected_k_target=1.3)
6. Composition Spec §3.5 (gate precedence — UNALTERED by 7a.3) at `docs/dev-guide/composition-specification.md`
7. `app/models/adapter.py::make_chat_model(specialist_id, **kwargs)` — canonical chat-model factory (used by Irene at `app/specialists/irene/graph.py:344`)
8. `app/marcus/orchestrator/production_runner.py:325-373` (`_build_decision_card` insertion target)
9. Sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- 7a.2 status `done` in BOTH `_bmad-output/implementation-artifacts/migration-7a-2-manifest-fold-flags-compiler-extension.md` line 3 AND `_bmad-output/implementation-artifacts/sprint-status.yaml::development_status['migration-7a-2-manifest-fold-flags-compiler-extension']`. **Both TRUE as of 2026-04-29.**
- `app/models/adapter.py::make_chat_model` is importable. If `make_chat_model("marcus")` doesn't resolve cleanly (model alias `marcus` may need to be added to `SPECIALIST_ALIASES` at `app/manifest/compiler.py:43-46`), surface as decision_needed.
- Jinja2 is shipped (check `pyproject.toml` for `Jinja2>=...`). If not, surface as decision_needed.

## Files in scope

**New:** `app/marcus/orchestrator/pre_gate_marcus.py`, `docs/conversational-gates/g{1,2c,3,4}.j2` (4 templates), `tests/unit/marcus/orchestrator/test_pre_gate_marcus.py`, `tests/structural/test_pre_gate_marcus_{node_registered,templates_present,single_call_site,vocabulary_closure}.py`, `tests/composition/test_pre_gate_marcus_precedence_unaltered.py`, `tests/integration/marcus/test_pre_gate_marcus_langsmith_trace.py`, `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py`, `_bmad-output/implementation-artifacts/7a-3-codex-self-review-2026-04-XX.md`.

**Modified:** `state/config/pipeline-manifest.yaml` (additive `pre-gate-marcus` orchestration-only node per AC-7.3-A); `app/marcus/orchestrator/production_runner.py` (additive `pre_fill: PreFillProposal | None = None` kwarg on `_build_decision_card` + invoke pre-gate-marcus before each gate intercept in BOTH `run_production_trial` AND `resume_production_trial`).

**Do NOT modify:** any specialist body; `app/marcus/orchestrator/{directive_composer,dispatch_adapter}.py` (7a.1 surfaces); `app/marcus/cli/trial.py` (7a.1 surface); `app/manifest/` (7a.2 surface); `docs/conversational-gates/_registry/` (7a.6 surface — when it lands); v4.2 prompt pack.

## Critical implementation notes

- **PyYAML, NOT ruamel** (per 7a.1 finding).
- **Single LLM call site invariant (FR2 + NFR-IN1):** the AST scan in AC-7.3-D asserts NO direct `make_chat_model` call site exists at "before-gate" code paths OTHER than `app/marcus/orchestrator/pre_gate_marcus.py`. If you find existing pre-gate `make_chat_model` calls anywhere else, surface as decision_needed.
- **Composition Spec §3.5 UNALTERED:** pre-gate-marcus does NOT promote any per-specialist gate to blocking; it only pre-fills the operator decision card.
- **Templates use `StrictUndefined`** so missing slot variables raise `jinja2.UndefinedError` at render time (fail-loud).
- **PreFillProposal rationale floor:** ≥20 chars per NFR-OX3; enforced in `_parse_pre_fill_response` with `ValueError` raise.
- **No new third-party deps.**

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/unit/marcus/orchestrator tests/structural/test_pre_gate_marcus_*.py tests/composition/test_pre_gate_marcus_*.py tests/integration/marcus/test_pre_gate_marcus_*.py tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold -q --tb=line
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-3-pre-gate-marcus-shared-llm-node.md
.venv/Scripts/python.exe -m ruff check app/marcus/orchestrator/pre_gate_marcus.py tests/unit/marcus/orchestrator/test_pre_gate_marcus.py tests/structural/test_pre_gate_marcus_*.py tests/composition/test_pre_gate_marcus_*.py tests/integration/marcus/test_pre_gate_marcus_*.py tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs the post-7a.2-close baseline (247 passed / 1 skipped on the wider slice as of 2026-04-29).

## T10 + T11

T10: Codex G6 self-review (Blind / Edge / Auditor) at `_bmad-output/implementation-artifacts/7a-3-codex-self-review-2026-04-XX.md`. Flip story status `in-progress` → `review` in spec file. Hand to Claude.

T11: Claude does FINAL bmad-code-review + remediation + commit + flips `migration-7a-3-pre-gate-marcus-shared-llm-node` review → done in sprint-status.yaml.

## Boundary

- HALT and surface to operator on: (a) 7a.2 status mismatch, (b) `make_chat_model("marcus")` doesn't resolve, (c) Jinja2 not shipped, (d) Composition Spec §11 trigger fires (it shouldn't — additive orchestration node), (e) K-actual exceeds 1.7× target (~4.25K LOC OR ~37 active tests), (f) any sandbox-AC violation, (g) collision with other parallel Codex work on adjacent stories.
- Do NOT touch any specialist body.
- Do NOT introduce ruamel.yaml or new third-party deps.
- The `test_pre_gate_marcus_vocabulary_closure` test starts `@pytest.mark.skip(reason="awaits Story 7a.6 vocabulary registry")`; if 7a.6 has CLOSED before you start, flip the skip active.
```
