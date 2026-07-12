---
baseline_commit: a498f9b476d5fbef744461d2573031ea9b92536d
---

# Story 38.0: Two-packet intake contract

Status: done

## Story

As the Marcus-SPOC workbook runtime,
I want the lesson-plan research-packet intake to resolve the Ask-A enrichment and Ask-B hot-topics packets independently,
so that each downstream workbook producer consumes the intended disk-mediated evidence pool with a stable witnessed digest while the existing generic research packet remains unchanged.

## Dependency Position

This is the first implementation slice in the ratified workbook DAG:

`38.0 -> 38.3b (deterministic stub band) -> {36.*, 37.1, 37.2a, 37.3, 37.4} -> 38.3a -> 38.1 -> 37.2b -> 39.1 -> 38.2 -> 39.2 -> 40.1`

No later slice may rely on Ask-A or Ask-B intake until this story is closed.

## Acceptance Criteria

1. **Exact parameterized load with backward-compatible defaults**
   - Given a fixture `run.json` containing all three research contributions, when `load_research_packet` is called with an explicit `(specialist_id, node_id)`, then it reads only that exact contribution through `ProductionEnvelope.get_contribution(specialist_id, node_id)`.
   - With no explicit coordinates, behavior remains byte-compatible at the public contract level with the existing generic packet: `specialist_id="research_wiring"`, `node_id="04.55"`.
   - The returned `ResearchPacket.specialist_id` and `.node_id` always identify the requested packet, including absent and empty results.

2. **Two frozen named packet resolvers**
   - `resolve_for_enrichment_pool` resolves only Ask A at `ask_a_enrichment@07W.2`.
   - `resolve_for_hot_topics` resolves only Ask B at `ask_b_hot_topics@07W.4`.
   - Both use the shared loader, validation, digest, and `require_usable` path. Neither may fall back to generic `04.55` or to the other workbook packet.
   - The public API is pinned exactly:
     - `GENERIC_RESEARCH_SPECIALIST_ID = "research_wiring"`; `GENERIC_RESEARCH_NODE_ID = "04.55"`
     - `ASK_A_ENRICHMENT_SPECIALIST_ID = "ask_a_enrichment"`; `ASK_A_ENRICHMENT_NODE_ID = "07W.2"`
     - `ASK_B_HOT_TOPICS_SPECIALIST_ID = "ask_b_hot_topics"`; `ASK_B_HOT_TOPICS_NODE_ID = "07W.4"`
     - `load_research_packet(run_dir: Path, *, specialist_id: str = GENERIC_RESEARCH_SPECIALIST_ID, node_id: str = GENERIC_RESEARCH_NODE_ID) -> ResearchPacket`
     - `resolve_for_enrichment_pool(run_dir: Path, *, require_usable: bool = False) -> ResearchPacket`
     - `resolve_for_hot_topics(run_dir: Path, *, require_usable: bool = False) -> ResearchPacket`
     - `ConsumerId` adds `enrichment_pool` and `hot_topics`; all existing literals remain.
     - All six coordinate constants and both resolvers are included in `__all__`; `RunEnvelopeCorruptError` remains exported.

3. **Three packets, independently witnessed digests**
   - Generic research, Ask A, and Ask B are independently selected and independently digested from their own canonical payloads.
   - The invariant is: **one digest per packet, witnessed identically by every consumer of that packet**.
   - Tests use distinct payloads and prove three distinct witness digests plus repeated same-packet equality and no cross-resolution.
   - Packet coordinates do not enter the digest formula in this story; identical payloads may legitimately hash equally. Do not change `research-packet.v1` or existing digest semantics.

4. **Honesty and validation parity across all packet identities**
   - Existing credibility-field validation, malformed-row `known_losses`, empty/absent honesty, corrupt-envelope fail-loud behavior, and `require_usable=True` failure apply to generic, Ask-A, and Ask-B packets.
   - Missing generic contribution preserves `research_wiring_contribution_absent`. Missing non-generic contribution records exactly `packet_contribution_absent:<specialist_id>@<node_id>`. `run_json_absent`, `research_entries_key_absent`, `research_entries_empty`, and existing malformed-row loss strings remain shared and unchanged. Every empty path returns the requested coordinates.
   - No resolver invents rows or silently substitutes another packet.

5. **M3-safe, model-free compatibility**
   - `app/marcus/lesson_plan/research_packet.py` remains a model-free disk-seam reader and imports no `app.marcus.orchestrator` module.
   - Existing generic consumers and their results remain unchanged. Current glossary/trends consumer repoints are explicitly deferred to Stories 39.1 and 39.2.
   - Existing public exports remain available; new constants/types/resolvers required by this story are explicitly exported and shape-pinned.

6. **Focused verification is green**
   - The research-packet suite covers default compatibility, exact three-coordinate selection, same-packet digest witnesses, cross-resolution refusal, absent/empty/malformed/corrupt behavior, and fail-closed `require_usable` for the new resolvers.
   - Existing glossary and trends focused suites remain green.
   - Ruff and the M3/import-boundary verification pass in the project Python 3.11 environment. The boundary witness is an AST-based test in the focused test file that rejects imports rooted at `app.marcus.orchestrator`; `lint-imports` alone is not evidence for this direction.
   - Full-object equality pins backward compatibility: no-argument generic load equals explicit `research_wiring@04.55` load for ready, absent-run, missing-contribution, missing-key, empty, degraded, and all-invalid cases. Existing glossary/trends wrappers continue to equal their pre-38.0 generic resolution.

## Tasks / Subtasks

- [x] Generalize packet selection without changing the existing payload schema (AC: 1, 3, 4, 5)
  - [x] Keep the generic coordinate constants and default behavior unchanged.
  - [x] Add explicit packet-coordinate parameters to the shared load path.
  - [x] Make `_empty_packet` accept requested coordinates and thread them through every honest-empty return and loss report.
  - [x] Preserve `_digest_payload`, `REQUIRED_ENTRY_FIELDS`, `ResearchPacket`, and `SCHEMA_VERSION` semantics.
- [x] Add the two named resolvers (AC: 2, 4, 5)
  - [x] Freeze Ask-A to `ask_a_enrichment@07W.2`.
  - [x] Freeze Ask-B to `ask_b_hot_topics@07W.4`.
  - [x] Extend `resolve_for_consumer` with keyword-only packet coordinates; keep it as the sole `require_usable` implementation and make both named resolvers delegate through it.
  - [x] Update `ConsumerId`/public exports only as needed; do not repoint existing glossary/trends wrappers.
- [x] Extend hermetic tests (AC: 1-6)
  - [x] Build one fixture envelope containing generic, Ask-A, and Ask-B contributions with distinct valid entries.
  - [x] Pin exact returned coordinates and intended content for every resolver.
  - [x] Pin repeated same-packet digest equality and distinct-payload digest separation.
  - [x] Prove no missing-coordinate fallback and packet-specific honest-empty evidence.
  - [x] Cover `require_usable`, malformed rows, wrong entry type, and corrupt envelope on new identities.
  - [x] Add a source/import fence preventing an orchestrator dependency.
  - [x] Add a collision fixture: the Ask-A specialist at another node and another specialist at `07W.2`; prove both coordinate dimensions are required.
  - [x] Exercise generic, Ask-A, and Ask-B across ready, missing contribution, missing key, empty rows, degraded rows, all-invalid rows, wrong container, corrupt envelope, and `require_usable` (parameterization is acceptable where behavior is identical).
- [x] Run focused regression and static checks (AC: 6)

### Review Findings

- [x] [Review][Patch] Reject `node_id=None` before exact contribution lookup; otherwise `ProductionEnvelope.get_contribution` silently uses any-node semantics [app/marcus/lesson_plan/research_packet.py:148]
- [x] [Review][Patch] Complete the promised Generic/Ask-A/Ask-B identity-by-state verification matrix, including empty, degraded, missing-key, wrong-container, corrupt-envelope, and required-unusable parity [tests/unit/marcus/lesson_plan/test_research_packet_w1.py:324]
- [x] [Review][Patch] Update the module contract to describe coordinate-selected Generic, Ask-A, and Ask-B packets instead of claiming the reader is confined to `research_wiring@04.55` [app/marcus/lesson_plan/research_packet.py:1]

## Dev Notes

### Current implementation

- `research_packet.py` is the W1 M3-safe facade introduced by commit `3231dd43`. It reads `run.json` through `load_run_envelope`, selects one `SpecialistContribution`, validates common research-entry credibility fields, and computes a canonical payload digest.
- `ProductionEnvelope.get_contribution` already supplies the required exact `(specialist_id, node_id)` lookup. Reuse it; do not use `latest_for_specialist` and do not create a second envelope reader.
- `ProductionEnvelope.add_contribution` guarantees one contribution per `(specialist_id, node_id)` and replaces same-node retries in place. No envelope-model change is required.

### Packet coordinates and future consumers

| Packet | Specialist | Node | Resolver / consumer id | Later consumers | Missing-contribution loss |
|---|---|---|---|---|---|
| Generic research | `research_wiring` | `04.55` | existing wrappers / existing ids | Irene intake, SPOC receipt, future collateral; current glossary/trends stay generic in 38.0 | `research_wiring_contribution_absent` |
| Ask-A enrichment | `ask_a_enrichment` | `07W.2` | `resolve_for_enrichment_pool` / `enrichment_pool` | Deep-dive enrichment (37.2b), glossary (39.1) | `packet_contribution_absent:ask_a_enrichment@07W.2` |
| Ask-B hot topics | `ask_b_hot_topics` | `07W.4` | `resolve_for_hot_topics` / `hot_topics` | Door-Ajar/trends (39.2) | `packet_contribution_absent:ask_b_hot_topics@07W.4` |

### Scope fences

Authorized production/test scope is exactly:

- `app/marcus/lesson_plan/research_packet.py`
- `tests/unit/marcus/lesson_plan/test_research_packet_w1.py`

Do **not** change in this story:

- `app/marcus/orchestrator/research_wiring.py` or any `04.55` writer/output behavior.
- `state/config/pipeline-manifest.yaml`, `production_runner.py`, `block_mode_trigger_paths`, graph topology, or learning-event types. Those lockstep changes belong to 38.3b.
- `glossary_projection.py`, `trends_projection.py`, `workbook_producer.py`, `workbook_enrichment.py`, specialist graphs, or `_act.py`.
- Packet minting, Tracy/Texas dispatch, the `07W.*` node implementations, live writer instantiation, prose enrichment, or consumer repointing.
- Any proofing-only accommodation. This contract exists solely for the Marcus-SPOC production runtime.

### Digest interpretation

The ratified phrase “three packets / three digests” means independently selected and witnessed packet digests. Coordinates are currently outside the digest payload. Do not alter the digest formula merely to force unequal hashes; tests obtain unequal witnesses using genuinely distinct payloads.

All packet identities consume the same contribution-output contract: `research_entries` plus optional `research_intake` and `triangulation_receipt`. Selection changes; payload schema does not. There is no schema-version bump and no `ProductionEnvelope` edit.

### Gate taxonomy

| Condition | Disposition | Witness |
|---|---|---|
| Wrong coordinate or cross-packet resolution | FAIL | Automated exact-selection tests |
| Digest mismatch for repeated intended-packet consumers | FAIL | Automated digest witness tests |
| Corrupt envelope / wrong entries container / required unusable packet | FAIL | Automated exception tests |
| Missing or empty packet | Honest empty with `known_losses` | Automated status/loss tests |
| Partially malformed rows | Honest degraded packet with losses | Automated row-validation tests |
| M3/orchestrator import breach | FAIL | Static source/import-linter check |

### Verification commands

Use the repository's Python 3.11 environment; the global Python 3.10 interpreter is not sufficient.

- `pytest -n0 tests/unit/marcus/lesson_plan/test_research_packet_w1.py`
- `pytest -n0 tests/unit/marcus/lesson_plan/test_glossary_w2.py tests/unit/marcus/lesson_plan/test_trends_w3.py`
- `ruff check app/marcus/lesson_plan/research_packet.py tests/unit/marcus/lesson_plan/test_research_packet_w1.py`
- focused AST boundary test (part of the W1 pytest command); `lint-imports` may run as broader regression evidence but does not prove the lesson-plan-to-orchestrator fence

No live run is required for 38.0 because the new graph nodes and packet producers do not exist yet. Do not claim that three packets are minted at runtime from reader-only evidence.

### References

- [Source: `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` — Green-light amendments A1/A5 and Epic 38 graph-shape decision]
- [Source: `_bmad-output/planning-artifacts/workbook-presentation-support-redesign-2026-07-12.md` — §§7-8 and §13]
- [Source: `app/marcus/lesson_plan/research_packet.py` — current W1 intake/digest contract]
- [Source: `app/models/runtime/production_envelope.py` — exact contribution selection and retry replacement]
- [Source: `pyproject.toml` — Python 3.11, Ruff, pytest, and import-linter contracts]
- [Source: `SESSION-HANDOFF.md` and `next-session-start-here.md` — 38.0 first in the ratified DAG]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex (Amelia)

### Debug Log References

- RED: focused suite collection failed because both named resolvers were absent.
- GREEN: research-packet focused suite `19 passed`; glossary/trends compatibility suites `14 passed`; Ruff clean.
- Full repository `pytest -n0 -q` did not reach a result: unrelated HUD/notifier tests leaked more than 100 polling subprocesses. The identified pytest process tree was terminated after the run hung; no failure was emitted.
- Review RED: `node_id=None` selected an arbitrary same-specialist contribution and failed to raise.
- Review GREEN: research-packet suite `38 passed`; glossary/trends compatibility suites `14 passed`; Ruff and `git diff --check` clean. Full suite intentionally not repeated because its existing infrastructure hang is recorded above.

### Completion Notes List

- Added exact coordinate-aware packet selection while preserving generic defaults, schema, and digest semantics.
- Added frozen Ask-A and Ask-B resolvers through the shared consumer/`require_usable` path with packet-specific honest-empty evidence.
- Added hermetic three-packet, collision, digest, validation, corruption, compatibility, and AST import-boundary coverage.
- ✅ Resolved review finding: rejected `node_id=None` before envelope lookup, closing any-node ambiguity.
- ✅ Resolved review finding: completed Generic/Ask-A/Ask-B parity across ready, empty, degraded, missing-key, wrong-container, corrupt, and required-unusable states.
- ✅ Resolved review finding: updated the module contract for coordinate-selected Generic, Ask-A, and Ask-B packets.

- Ultimate context engine analysis completed — comprehensive developer guide created.

### File List

- `app/marcus/lesson_plan/research_packet.py`
- `tests/unit/marcus/lesson_plan/test_research_packet_w1.py`
- `_bmad-output/implementation-artifacts/38-0-two-packet-intake-contract.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-07-12: Implemented the two-packet intake contract and moved Story 38.0 to review.
- 2026-07-12: Addressed code review findings — 3 patch items resolved; status remains review.
