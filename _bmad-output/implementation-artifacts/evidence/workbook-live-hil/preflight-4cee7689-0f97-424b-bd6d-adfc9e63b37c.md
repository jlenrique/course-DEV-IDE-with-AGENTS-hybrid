# Story 38.3a / 38.1 governed live-acceptance preflight

- Authorization: four-seat native BMAD party `GO-WITH-AMENDMENTS` (John, Winston, Murat, Amelia); root concurs and folds every MUST control below.
- Authorization scope: exactly one fresh Marcus-SPOC production-runtime `start`.
- Trial ID: `4cee7689-0f97-424b-bd6d-adfc9e63b37c`
- Recorded: `2026-07-14`
- Git HEAD: `6ae42a5208bb4a9fcb5bee8668705d6c8b9dd1d7`
- Tracked binary-diff Git object: `9f7c97f5cd0e6b0945412458ca94306702fe82fb`
- Runner SHA-256: `a49c9b0e4fca25e820ec64189452d9e3e8205e53b4361c3f56b7e69efa22e71b`
- Policy-file SHA-256: `806f11388937d62e72396b469b04af61751a05dc1c54f3335c561b24edeef9b4`
- Canonical policy digest: `4205b4dcb2a34846bac0da9f889365eefd22969613aac4e1a4c65e055b9a74a5`

## Exact-tree identity

The runtime tree digest covers every regular non-compiled file under `app/`, `scripts/`, `state/config/`, and every `skills/bmad-agent-*` directory, plus `pyproject.toml`, `uv.lock`, and the delegated HIL policy. `__pycache__`, `.pytest_cache`, `.pyc`, and `.pyo` files are excluded. Records are sorted repository-relative POSIX paths in the form `<sha256><two spaces><path><LF>`, then SHA-256 hashed as UTF-8.

- Runtime/config/prompt file count: `8839`
- Runtime/config/prompt tree SHA-256: `83885c68a526515f79734c687ab5221edce3ee024fb343ffc6b88e25f7e59b07`
- Tejal Part-2 course-source file count: `12`
- Tejal Part-2 course-source tree SHA-256: `7431bcd0db201f7e60eb751ded28d750e89970a10b3b7fba9970b8038dda20c8`
- Fresh run directory absent before launch: yes
- Fresh evidence directory absent before launch: yes

No development, configuration, prompt, or course-source mutation is permitted between this identity capture and terminal postflight.

## Pre-spend verification

- Story 38.3a exact correction gate: `383 passed, 3 skipped, 1 deselected`.
- Story 38.3a exact-current independent review: Blind Hunter, Edge Case Hunter, and Acceptance Auditor each `ZERO FINDINGS`.
- Story 38.1 story-owned matrix: `184 passed, 3 skipped, 4 deselected`.
- Story 38.1 full matrix: `184 passed, 3 skipped, 4 failed`; all four failures reproduce the documented inherited `PreflightGateFailed` boundary before test subject at `production_runner.py:3102`, with the same `openai=fail` or `hud-server-healthz=fail, openai=fail` dependency signatures and no new failure signature.
- Delegated HIL runner: `42 passed, 1 skipped`.
- Additional runner/slide-authority/Deep-Dive/package gate independently run by Amelia: `167 passed, 4 skipped`.
- Pipeline-manifest lockstep: PASS, `reports/dev-coherence/2026-07-14-0522/check-pipeline-manifest-lockstep.PASS.yaml`.
- Scoped Ruff: clean.
- Scoped compileall: clean.
- Marcus import boundaries: `6 passed`.
- `git diff --check`: clean.

## Frozen prior evidence pins

| Trial | Files | `error-pause.json` SHA-256 | `run.json` SHA-256 |
|---|---:|---|---|
| `a28aa15a-fc80-46ae-b05a-09ac864829bb` | 67 | `4d9bc6f4c1c4ef5f662f6607326402dc741f1e845dd5ec1034f49283cc4fa6bc` | `3935b017d343bfd5c8bcdd1b7998d07ef82238ab74fa5031b6a1df60b90bc50f` |
| `c1c7135f-5b0d-4c59-bd5e-0bd58580b54b` | 28 | `1899c8fda1f7d3e233c410449b23536ae06f7a172679da3796f807906f2698ad` | `94eb23e055a5cafa6e720d04fb4045ca77bbb001997dc3c4cdbf56a818616d04` |

Both failed witnesses must remain byte-identical after this attempt.

## Launch posture

- Preset: `production`.
- Operator/delegate: `codex_hil_runner`.
- Input and course-source root: `course-content/courses/tejal-apc-c1-m1-p2-trends`.
- Components: deck `on`, workbook `on`, motion `off`.
- HUD: `off`.
- Encounter mode: `recorded`.
- Writer execution: live production path.
- LLM execution: `realtime`.
- Image-perception batching: `off` through realtime transport.
- Research: enabled only when demanded by the real workbook authority chain; no independent research switch or synthetic dispatch.
- No journal, authority map, packet, brief, receipt, contribution, cache, package, or other prior-run state is copied.

## Call ceilings and stop rules

- Deep Dive: at most one selectable provider invocation; `300s`; `max_retries=0`.
- Ask-A: at most one Texas dispatcher invocation and no story-added retry loop.
- Delegate: at most 12 gate actions, 48 specialist calls per segment, and 14,400 seconds wall time.
- Authorized action: one `start` only.
- Forbidden: attach, recover, re-entry, second start, retry-to-green, concurrent development, or mid-run code/config/prompt/source edits.
- Any refusal, timeout, provider exception, batch wait, authority failure, ambiguous journal, runner refusal, pause, or state other than exact `completed` freezes the attempt as negative evidence and returns to party review.

## Passing evidence

Exact `completed` is necessary but not sufficient. Passing postflight must prove:

1. Clustered 13-final/6-source authority validates without inference or fallback.
2. Deep Dive has one completed journal, an authored passing skeleton, nonempty exact bold terms, and a ready Ask-A demand.
3. Ask-A has exactly one dispatcher invocation, a completed journal, and a non-vacuous packet with at least one usable evidence-backed row associated with an exact ability and exact bold term.
4. `resolve_for_enrichment_pool(require_usable=True)` passes after disk reload.
5. The ordinary production path emits nonempty Markdown and DOCX workbook artifacts; hashes are recorded and current-point specification checks pass without claiming unbuilt Epic 37/39/40 enhancements.
6. Read-only reconciliation/replay preserves relevant digests with zero additional provider calls.
7. Gate journal, summary, model/config identity, receipts, latency/token/cost posture, packet/journal/envelope/workbook hashes, and prior failed-attempt lineage are preserved.

This attempt can close Story 38.3a and, only if its separate bar passes, Story 38.1. It cannot close Epics 36–40 or prove the final enhanced-workbook specification.
