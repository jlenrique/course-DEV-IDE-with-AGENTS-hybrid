# Codex dev-story prompt — Story 7a.5 (conversation persistence + specialist-summary writer)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 4 slot 2 (parallel with 7a.4; needs 7a.3 [pre-gate-marcus]).

---

```
Run bmad-dev-story on Story 7a.5 (Slab 7a Wave 4 slot 2; single-gate; conversation persistence + SHA256 tamper-evident chain + specialist-summary writer + run_summary.yaml emit).

## Required reading (read in order)

1. Story spec: `_bmad-output/implementation-artifacts/migration-7a-5-conversation-persistence-specialist-summary-writer.md` (status: ready-for-dev; 10 ACs A-J; 11 tasks T1-T11; you own T1-T10)
2. Predecessor 7a.3 (pre-gate-marcus): must be `done` before 7a.5 dev opens (provides `PreFillProposal` shape that 7a.5 persists)
3. 7a.1/7a.2 substrate: `runs/<trial_id>/directive.yaml` (anchors the chain at turn 0); `production_runner.py` patterns
4. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7a-5` (single-gate; expected_pts=3; expected_k_target=1.3)
5. Pydantic v2 checklist: `docs/dev-guide/pydantic-v2-schema-checklist.md` (four-file-lockstep on SpecialistState model)
6. Composition Spec §3.1 (envelope append-only + SHA256 invariants — HONORED) at `docs/dev-guide/composition-specification.md`
7. ADR-D3 Postgres checkpointer (additive-only schema; NFR-V2)
8. `app/models/runtime/production_envelope.py::SpecialistContribution::compute_output_digest` — canonical SHA256 pattern to mirror
9. `app/manifest/compiler.py:43-46::SPECIALIST_ALIASES` — canonical specialist_id mapping (`quinn-r → quinn_r`; `elevenlabs → enrique`)
10. Sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- 7a.3 status `done` in BOTH spec status + sprint-status.yaml.
- `app/models/runtime/production_envelope.py::SpecialistContribution::output_digest` invariant unchanged from Slab 6.0.
- 11-specialist roster verifiable (either from 7a.6's `app/models/decision_cards.py::SpecialistId` if 7a.6 closed, or from hardcoded canonical list `[texas, irene, dan, tracy, gary, kira, wanda, enrique, compositor, quinn_r, vera]` if 7a.6 not yet closed).

## Files in scope

**New:** `app/marcus/orchestrator/conversation_persistence.py`, `app/marcus/orchestrator/specialist_summary_writer.py`, `app/models/state/specialist_state.py`, `app/models/schemas/specialist_state.schema.json`, `tests/fixtures/specialist_state/specialist_state_golden.json`, `tests/unit/marcus/orchestrator/test_{conversation_persistence,conversation_chain_integrity,specialist_summary_writer,specialist_summary_length_envelope,conversation_persistence_schema_versioning}.py`, `tests/unit/models/test_specialist_state_shape_pin.py`, `tests/integration/marcus/test_{gate_handler_loads_adjacent_summary,path_z_first_contribution_wins_with_persistence,run_summary_yaml_emit}.py`, `_bmad-output/implementation-artifacts/7a-5-codex-self-review-2026-04-XX.md`.

**Modified:** `app/marcus/orchestrator/production_runner.py` (extend `_build_decision_card` for adjacent-summary load + `run_summary.yaml` emit at trial close); `app/specialists/{texas,irene,gary,kira,wanda,enrique,quinn_r,vera,tracy}/graph.py` (additive: call `specialist_summary_writer.emit_summary(...)` in emit-node — DO NOT touch _act bodies); `_bmad-output/implementation-artifacts/sprint-status.yaml` (Claude T11).

**Do NOT modify:** specialist `_act` bodies (only emit-node hook); 7a.1/7a.2/7a.3/7a.4/7a.6 surfaces; `OperatorVerdict` model (7a.4 owns the additive `revise_count`); v4.2 prompt pack; manifest.

## Critical implementation notes

- **Tamper-evident SHA256 chain (AC-7.5-B):** `digest = SHA256(prior_envelope_digest_bytes || canonical_json_bytes(decision_card) || timestamp_utc_iso8601_bytes || operator_id_utf8_bytes)`. Use canonical JSON (sorted keys, ensure_ascii, separators=`(",", ":")`); mirror `compute_output_digest` patterns. `prior_envelope_digest` for turn 0 is the digest of `runs/<trial_id>/directive.yaml` from 7a.1.
- **Chain verifier:** `verify_chain(trial_id, runs_root) -> bool` walks all turns in order, re-computes each digest, asserts equality; broken link raises `ConversationChainBrokenError(RuntimeError)` (NOT warning).
- **15-25 line summary envelope (AC-7.5-D):** enforced as RAISE not lint warning; `_validate_length(text)` is single enforcement site.
- **Canonical specialist_id mapping (AC-7.5-C):** use `app/manifest/compiler.py::SPECIALIST_ALIASES`. Deferred specialists (`dan`, `compositor`) emit no-op summary `<deferred per Slab 7b roadmap>` until their bodies land.
- **SpecialistState four-file-lockstep (AC-7.5-F):** model + emitted JSON Schema + golden + shape-pin tests (NFR-CG4).
- **Schema versioning (AC-7.5-I):** turn JSON carries `_schema_version: "1.0"` field; loader handles missing field with default + warning log; additive-only future evolution per ADR-D3 + NFR-V2.
- **Path Z compatibility (AC-7.5-G):** Slab 6.1 first-contribution-wins; duplicate skip → no second turn JSON; chain integrity preserved.
- **Trial-run capture (AC-7.5-H):** `runs/<trial_id>/run_summary.yaml` emitted at trial close; `silent_bypass_events: 0` invariant from 7a.2.
- **PyYAML, NOT ruamel.**
- **No new third-party deps.**

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/unit/marcus/orchestrator/test_{conversation_persistence,conversation_chain_integrity,specialist_summary_writer,specialist_summary_length_envelope,conversation_persistence_schema_versioning}.py tests/unit/models/test_specialist_state_shape_pin.py tests/integration/marcus/test_{gate_handler_loads_adjacent_summary,path_z_first_contribution_wins_with_persistence,run_summary_yaml_emit}.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold -q --tb=line
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-5-conversation-persistence-specialist-summary-writer.md
.venv/Scripts/python.exe -m ruff check app/marcus/orchestrator/conversation_persistence.py app/marcus/orchestrator/specialist_summary_writer.py app/models/state/specialist_state.py tests/unit/marcus/orchestrator tests/unit/models/test_specialist_state_shape_pin.py tests/integration/marcus
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-7a.3 baseline.

## T10 + T11

T10: Codex G6 self-review (Blind / Edge / Auditor) at `_bmad-output/implementation-artifacts/7a-5-codex-self-review-2026-04-XX.md`. Flip story status to `review`. Hand to Claude.

T11: Claude does FINAL bmad-code-review + remediation + commit + flips `migration-7a-5-conversation-persistence-specialist-summary-writer` review → done.

## Boundary

- HALT and surface on: (a) 7a.3 status mismatch, (b) SpecialistContribution.output_digest invariant changes, (c) chain-verifier raises silently in any non-tampered scenario, (d) Composition Spec §3.1 append-only OR SHA256 invariant breaks, (e) K-actual exceeds 1.7× target (~4.25K LOC OR ~37 active tests) — K-target is at CEILING per Mary's Step 2 audit, (f) any sandbox-AC violation.
- Do NOT touch specialist `_act` bodies (emit-node hook only).
- Do NOT introduce ruamel.yaml or new third-party deps.
```
