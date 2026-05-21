# Story 7a.3 Codex G6 Self-Review — 2026-04-29

## Scope

Story: `migration-7a-3-pre-gate-marcus-shared-llm-node`

Implementation reviewed:
- `app/marcus/orchestrator/pre_gate_marcus.py`
- `docs/conversational-gates/g{1,2c,3,4}.j2`
- `state/config/pipeline-manifest.yaml`
- `app/marcus/orchestrator/production_runner.py`
- 7a.3 unit, structural, composition, and integration tests
- Existing manifest/lockstep regression pins updated for the second orchestration-only node

## Blind Hunter

Verdict: PASS-WITH-NOTE.

Findings:
- PATCHED: Fake OpenAI keys such as `sk-test-fake` initially triggered the pre-gate LLM call path in existing regression tests. The guard now suppresses pre-gate invocation for `sk-test*`, `sk-fake*`, and offline-cost-report runs.
- NOTE: The runner records synthetic local trace usage for the mocked pre-gate span so existing cost-report code treats the span as billable when a trace fixture is emitted. This is only used in the local fixture path; real invocation still goes through `make_chat_model("marcus")`.

## Edge Case Hunter

Verdict: PASS.

Coverage:
- Missing Jinja2 slots fail loudly via `StrictUndefined`.
- Missing gate template raises `FileNotFoundError`.
- Short rationale raises `ValueError` at the NFR-OX3 floor.
- Confidence outside `[0.0, 1.0]` fails at parse time.
- No-pre-fill path preserves the prior `drafted_proposal` shape.
- 7a.6 is now `done`; the vocabulary-closure test is active and validates template tokens against `docs/conversational-gates/_registry/vocabulary.yaml`.

## Acceptance Auditor

Verdict: PASS.

Trace:
- AC-A: `pre-gate-marcus` registered as orchestration-only; lockstep PASS records `directive-composer` + `pre-gate-marcus`.
- AC-B: PreFillProposal, renderer, LLM invocation, parser, and unit tests implemented.
- AC-C: Four Jinja2 templates present with required slots and closed enums.
- AC-D: Single-call-site structural test plus active vocabulary closure test implemented.
- AC-E: Composition Spec Section 3.5 precedence remains unchanged; pre-fill only changes decision-card draft content.
- AC-F: Trace fixture test asserts exactly one `pre-gate-marcus` LLM span for G1.
- AC-G: Runner threads pre-fill into `_build_decision_card` and persists it in decision-card JSON.
- AC-H: N-item trace recorded in story Dev Agent Record.
- AC-I: D12 close remains Claude-owned per T11; Codex flipped to review only.

## Verification

- Focused 7a.3 slice: `35 passed`
- Wider slice: `281 passed, 20 skipped` with temporary `vi` PATH shim for the known 7a.1 editor fallback environment assumption
- Lockstep: PASS, trace `reports/dev-coherence/2026-04-29-0505/check-pipeline-manifest-lockstep.PASS.yaml`
- Sandbox-AC validator: PASS
- Ruff: clean
- Import-linter: 9/9 contracts KEPT

## K-Actual

Active 7a.3 tests added: 17. This is below the story tripwire of ~37 active tests.

## Final Codex Verdict

PASS. Ready for Claude final `bmad-code-review`, remediation if needed, commit, and sprint-status `review` -> `done`.
