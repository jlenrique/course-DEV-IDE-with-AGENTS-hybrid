# Migration Story 7a.5: Conversation Persistence + Specialist-Summary Writer

**Status:** ready-for-dev
**Sprint key:** `migration-7a-5-conversation-persistence-specialist-summary-writer`
**Epic:** Slab 7a — Inter-Gate Conversational Orchestration (`migration-epic-slab-7a-inter-gate-orchestration`)
**Pts:** 3
**Gate:** **single-gate** (per `docs/dev-guide/migration-story-governance.json` v2026-04-28-slab7a-eight-stories, story 7a-5; rationale: null)
**K-target:** ~1.3× (gate-shape band 1.5-2.5K; ~2.5K target — CEILING per Mary's Step 2 audit; rebalance only if breach occurs at gate-closeout).
**Authored:** 2026-04-29 via `bmad-create-story` workflow.
**Wave:** 4 — slot 2 (parallel with 7a.4; needs 7a.3 [pre-gate-marcus]).
**FR coverage:** 20 — FR3 (xc with 7a.3), FR5 (xc with 7a.1), FR16, FR17, FR18, FR19, FR20, FR29, FR30, FR31, FR32, FR33; FR-A11, FR-A12, FR-A13, FR-A14, FR-A19, FR-A20; FR-O17, FR-O18, FR-O19
**Standing-guardrail enforcement:**
- SG-1 enforced — FR16 enumerates all 11 specialists explicitly; specialist-summary writer wired for all 11.
- SG-2 conversation-persistence rows + specialist-state-persistence rows preserved.
- SG-3 Composition Spec §3.1 append-only envelope + SHA256 invariants honored (FR-A11-A14).

**Implementation cycle (NEW):** Claude spec → Codex dev+tests → Claude review+commit.

---

## T1 Readiness Block

**Predecessor state (verified at authoring 2026-04-29):**
- Stories 7a.1 + 7a.2 CLOSED done. 7a.3 + 7a.6 ready-for-dev (Wave 3); 7a.5 dev opens after 7a.3 closes.
- 7a.3 (pre-gate-marcus) provides the pre-fill mechanism that emits `PreFillProposal` with `decision`, `directive`, `rationale`, `confidence`, `confidence_signals` — these are the structured-record-format fields that 7a.5 persists.

**Live substrate (verified at authoring):**
- `app/marcus/orchestrator/` houses orchestration modules; new modules: `conversation_persistence.py` + `specialist_summary_writer.py`.
- `app/models/runtime/production_envelope.py::SpecialistContribution` carries `output_digest: str` (SHA256 hex; FR-A2 invariant from Slab 6.0). 7a.5's tamper-evident chain reuses `compute_output_digest` patterns.
- `app/models/state/run_state.py::RunState` carries `production_envelope` field. 7a.5's conversation persistence writes alongside the envelope (separate file family at `runs/<trial_id>/conversation/<gate_id>/<turn_n>.json`).
- ADR-D3 (Postgres checkpointer): currently `langgraph.checkpoint.memory.InMemorySaver` per `app/marcus/orchestrator/dispatch_adapter.py:12`. Future Postgres checkpointer migration is post-Slab-7a per ADR-D3; 7a.5 does NOT migrate to Postgres but designs the persistence shape to be Postgres-compatible (additive-only schema; no DROP; no type narrowing per NFR-V2).
- `app/specialists/{texas, irene, gary, kira, wanda, enrique, quinn_r, vera, tracy}/` exist (9 of 11; `dan` and `compositor` deferred per Slab 7b roadmap). 7a.5's specialist-summary writer wires for all 11 via specialist_id-keyed dispatch — for deferred specialists, the writer is wired but emits a no-op summary (`<deferred per Slab 7b>`) until the specialist body lands.

**Block-mode trigger paths touched by this story:** none.

**Gate-mode rationale (from governance JSON):**
> Slab 7a wave-4 (parallel with 7a-4): conversation persistence (SHA256 tamper-evident chain) + specialist-summary writer (15-25 line envelope per FR-O19). Postgres checkpointer additive evolution (ADR-D3); FR-A11-A14 cluster.

**T1 conclusion:** Implementation proceeds. Hard checkpoints at T1: confirm 7a.3 done; verify SpecialistContribution digest invariant unchanged; verify all 11 specialists named in vocabulary registry from 7a.6 (or fallback to hardcoded canonical roster if 7a.6 not yet closed).

---

## Story

As the operator + the audit-trail substrate,
I want every operator turn persisted as a structured record under `runs/<trial_id>/conversation/<gate_id>/` with tamper-evident SHA256 chain, and every specialist to emit a "what I just did" summary at `runs/<trial_id>/specialist-summaries/<name>-<timestamp>.md` (15-25 lines) loaded inline by the next gate-handler,
so that I have hot-pickup context at every gate (no chasing artifact paths) and the trial trace is replay-deterministic + audit-recoverable.

---

## Acceptance Criteria

### AC-7.5-A — Conversation persistence module + structured-record format (FR3, FR-O17-prep)

**Given** the conversation persistence module at `app/marcus/orchestrator/conversation_persistence.py`
**When** the operator submits a turn (decision-card payload after pre-gate-marcus pre-fill)
**Then** the writer creates `runs/<trial_id>/conversation/<gate_id>/<turn_n>.json` with the structured-record format:

```python
{
  "trial_id": "<uuid>",
  "gate_id": "G1" | "G2C" | "G3" | "G4",
  "turn_index": <int>,
  "timestamp_utc": "<ISO 8601>",
  "operator_id": "<string>",
  "decision_card": {
    "decision": "<closed-enum from 7a.6 vocabulary>",
    "directive": "<closed-enum from 7a.6 vocabulary>",
    "rationale": "<string ≥20 chars>",
    "confidence": <float 0..1>,
    "confidence_signals": ["<string>", ...],
  },
  "free_text_rationale": "<string; operator's prose addendum>",
  "prior_envelope_digest": "<sha256 hex>",
  "digest": "<sha256 hex>",
}
```

**And** `<turn_n>` is zero-padded 4 digits (`0000.json`, `0001.json`, ...).
**And** the per-gate directory is created on first turn (`mkdir(parents=True, exist_ok=True)`).

**Test pin:** `tests/unit/marcus/orchestrator/test_conversation_persistence.py` — 4 cases per AC-A.

### AC-7.5-B — Tamper-evident SHA256 chain (FR-A14, NFR-I3)

**Given** the tamper-evident chain
**When** the writer computes the digest for turn N
**Then** the digest is computed as:

```
digest = SHA256(
    prior_envelope_digest_bytes ||
    canonical_json_bytes(decision_card) ||
    timestamp_utc_iso8601_bytes ||
    operator_id_utf8_bytes
)
```

(canonical_json: sorted keys, ensure_ascii, separators=`(",", ":")`, no trailing whitespace; per `app/models/runtime/production_envelope.py::compute_output_digest` precedent).

**And** the chain is verifiable end-to-end: `verify_chain(trial_id, runs_root) -> bool` walks all turns in order, re-computes each digest, asserts equality.
**And** broken link is hard audit failure (raises `ConversationChainBrokenError(RuntimeError)`), not warning.
**And** `prior_envelope_digest` for turn 0 is the digest of `runs/<trial_id>/directive.yaml` from 7a.1 (anchors the chain to the trial-start directive composition).

**Test pin:** `tests/unit/marcus/orchestrator/test_conversation_chain_integrity.py` — 5 cases: (a) chain verifies for valid 3-turn sequence, (b) tampered turn_2 raises ConversationChainBrokenError, (c) missing prior_envelope_digest field raises, (d) digest re-compute matches stored digest, (e) chain anchors at directive.yaml digest for turn 0.

### AC-7.5-C — Specialist-summary writer module (FR16, FR17, FR-O17)

**Given** the specialist-summary writer at `app/marcus/orchestrator/specialist_summary_writer.py`
**When** any of the 11 specialists completes its `_act` body
**Then** the writer emits `runs/<trial_id>/specialist-summaries/<canonical_specialist_id>-<utc_timestamp>.md` with the format:

```markdown
# <Specialist Display Name> — <gate_id> — <utc_timestamp>

## Received
<single line: input keys consumed from cache_prefix or RunState>

## Decided
<single line: what the specialist's _act produced (Y) BECAUSE (Z reasoning)>

## Emitted artifacts
- `<path/to/artifact1>`
- `<path/to/artifact2>`
- ...

## Resolution trail (model_resolution_trail entries)
- <model_resolution_trail entry summary, last 1-3 entries>
```

**And** the canonical specialist_id mapping uses `app/manifest/compiler.py::SPECIALIST_ALIASES` (e.g. `quinn-r → quinn_r`).
**And** the writer wires for ALL 11 specialists; deferred specialists (`dan`, `compositor`) emit a no-op summary `<deferred per Slab 7b roadmap>` until their bodies land.

**Test pin:** `tests/unit/marcus/orchestrator/test_specialist_summary_writer.py` — 5 cases: (a) writer emits for Texas's _act completion, (b) writer emits for Irene's _act completion, (c) deferred specialist (`dan`) emits no-op marker, (d) timestamp is ISO 8601 UTC, (e) canonical specialist_id used (e.g. `quinn_r`, NOT `quinn-r`).

### AC-7.5-D — 15-25 line summary envelope (FR-O19, NFR-OX4)

**Given** the length envelope enforced at write time
**When** the writer is invoked
**Then** summary length is enforced as 15-25 lines (inclusive); <15 OR >25 fails the writer's assertion (raises `SummaryLengthError(RuntimeError)`; NOT a lint warning).
**And** the line count includes ALL non-blank content lines but excludes leading/trailing blank lines.
**And** the writer's `_validate_length(text: str) -> None` helper is the single enforcement site.

**Test pin:** `tests/unit/marcus/orchestrator/test_specialist_summary_length_envelope.py` — 4 cases: (a) 15-line summary accepted, (b) 25-line summary accepted, (c) 14-line summary raises, (d) 26-line summary raises.

### AC-7.5-E — Next-gate-handler loads adjacent specialist summaries inline (FR-O18)

**Given** the next gate-handler imports adjacent specialist summaries
**When** the gate handler renders the decision card
**Then** the immediately-prior specialist summary is loaded inline into the decision card's `evidence` field (via `_build_decision_card`'s evidence list extension); operator never chases artifact paths.
**And** "adjacent" means the most recent summary file in `runs/<trial_id>/specialist-summaries/` whose timestamp precedes the gate-handler invocation time.

**Test pin:** `tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py` — 3 cases: (a) gate handler loads most-recent summary into evidence, (b) no summary present → evidence list unchanged (graceful fallback), (c) multiple summaries present → only the most-recent is loaded.

### AC-7.5-F — 11-specialist roster wiring + specialist_state schema (FR16-FR20, FR-A11)

**Given** the 11-specialist roster
**When** any specialist completes
**Then** that specialist's summary writer is wired into its emit-node; specialist persistence shape conforms to the declared schema in `app/models/state/specialist_state.py` (NEW module if not present; otherwise extend additively).
**And** specialist_state Pydantic model lands per four-file-lockstep (NFR-CG4):
1. **Model:** `app/models/state/specialist_state.py`.
2. **Emitted JSON Schema:** `app/models/schemas/specialist_state.schema.json`.
3. **Golden fixture:** `tests/fixtures/specialist_state/specialist_state_golden.json`.
4. **Shape-pin tests:** `tests/unit/models/test_specialist_state_shape_pin.py`.

**Test pin:** the 4 lockstep artifacts above.

### AC-7.5-G — Path Z first-contribution-wins compatibility (FR-A19, FR-A20, NFR-R3)

**Given** the multi-pass envelope Path Z (Slab 6.1)
**When** a specialist node fires repeatedly (e.g., Irene Pass-1 + Pass-2)
**Then** only the FIRST contribution lands; duplicates are skipped after first WITH explicit log entry; conversation persistence chain accommodates the skip (the skipped invocation does NOT create a new turn JSON; the original-contribution turn JSON remains canonical).

**Test pin:** `tests/integration/marcus/test_path_z_first_contribution_wins_with_persistence.py` — 2 cases: (a) Irene Pass-1 contributes + Pass-2 attempted → Pass-2 skipped + log emitted + no second turn JSON, (b) chain integrity preserved across the skip.

### AC-7.5-H — Trial-run capture envelope close (FR29-FR33)

**Given** the trial-run capture envelope
**When** the trial closes (operator handoff at G4 verdict)
**Then** `runs/<trial_id>/run_summary.yaml` captures:
- `terminal_gate: <gate_id>` (e.g. `G4` for clean run; `G1` for paused-at-G1 incomplete trial).
- `silent_bypass_events: 0` (FR36 — must be exactly 0; any non-zero is a trial-quality regression).
- `specialist_roster_count: 11`.
- `pack_hash_binding: <sha256 of state/config/pipeline-manifest.yaml>`.
- `conversation_chain_digest: <sha256 of last conversation turn>`.
- `langsmith_trace_id: <uuid or "skipped-no-langsmith-env">`.

**Test pin:** `tests/integration/marcus/test_run_summary_yaml_emit.py` — 3 cases: (a) clean trial run_summary populated correctly, (b) paused-at-G1 trial run_summary records paused state, (c) `silent_bypass_events != 0` triggers run-summary emit warning at debug level (gate-bypass refusal in 7a.2 prevents this in production but the trial-summary asserts it explicitly).

### AC-7.5-I — Postgres checkpointer additive evolution (FR-A11, FR-A12, NFR-V2)

**Given** Postgres checkpointer schema migrations (post-Slab-7a per ADR-D3)
**When** any 7a.5 field is added to the conversation persistence shape
**Then** the field is additive only (no DROP, no type narrowing); in-flight runs paused at any gate resume cleanly against bumped schema.
**And** the conversation persistence file format documents an `_schema_version: "1.0"` field at the top of every turn JSON to allow future loaders to detect version drift.

**Test pin:** `tests/unit/marcus/orchestrator/test_conversation_persistence_schema_versioning.py` — 2 cases: (a) turn JSON carries `_schema_version` field, (b) loader handles missing `_schema_version` field with default "1.0" + warning log.

### AC-7.5-J — N-item + anti-pattern + Composition Spec trace + D12 close

**N-item / N4 PASS:** specialist isolation preserved — summary writer is wired into each specialist's emit-node via existing scaffold pattern; specialist body untouched. **N9 PASS-PENDING-OPERATOR:** operator validates summary readability + chain-replay UX at trial-2. **A11 honored:** `Path.as_posix()` in turn JSON `evidence` paths. **Composition Spec §3.1 append-only envelope + SHA256 invariants HONORED** per FR-A11-A14. **Composition Spec §11 trigger NEGATIVE.**

D12 close: sprint-status flip; sandbox-AC + lockstep + ruff + lint-imports clean; deferred-inventory entries for any follow-ons.

---

## Tasks / Subtasks

- [ ] **T1: Readiness review (Codex)** — confirm 7a.3 done; verify SpecialistContribution digest invariant; canonical specialist_id alias map at `app/manifest/compiler.py:43-46`.
- [ ] **T2: Author `conversation_persistence.py`** (AC-A, B, I) — turn JSON writer + chain digest computer + chain verifier + schema versioning.
- [ ] **T3: Author `specialist_summary_writer.py`** (AC-C, D) — markdown emitter + length envelope + canonical specialist_id mapping + 11-specialist wiring.
- [ ] **T4: Wire summary writer into each specialist's emit-node** (AC-F) — `app/specialists/{texas,irene,gary,kira,wanda,enrique,quinn_r,vera,tracy}/graph.py::_emit_spans` (or equivalent emit-node) calls `specialist_summary_writer.emit_summary(...)` after _act completion. Deferred specialists (`dan`, `compositor`) emit no-op marker.
- [ ] **T5: SpecialistState four-file-lockstep** (AC-F) — model + JSON Schema + golden + shape-pin tests.
- [ ] **T6: Gate-handler loads adjacent summary** (AC-E) — extend `_build_decision_card` in `production_runner.py` to call `specialist_summary_writer.load_most_recent_summary(...)` and append to `evidence` list.
- [ ] **T7: Path Z first-contribution-wins compatibility** (AC-G) — verify existing duplicate-skip behavior in `production_runner.py` does NOT create stray turn JSONs; integration test.
- [ ] **T8: Trial-run capture envelope** (AC-H) — `run_summary.yaml` emitter at trial close; assert silent_bypass_events: 0; specialist_roster_count: 11.
- [ ] **T9: Verification battery** — focused + wider regression slice; sandbox-AC; lockstep; ruff; lint-imports.
- [ ] **T10: Codex G6 self-review** — Blind / Edge / Auditor.
- [ ] **T11: Claude bmad-code-review + remediation + commit + close.**

---

## File Structure Requirements

**New:** `app/marcus/orchestrator/conversation_persistence.py`, `app/marcus/orchestrator/specialist_summary_writer.py`, `app/models/state/specialist_state.py`, `app/models/schemas/specialist_state.schema.json`, `tests/fixtures/specialist_state/specialist_state_golden.json`, `tests/unit/marcus/orchestrator/test_conversation_persistence.py`, `tests/unit/marcus/orchestrator/test_conversation_chain_integrity.py`, `tests/unit/marcus/orchestrator/test_specialist_summary_writer.py`, `tests/unit/marcus/orchestrator/test_specialist_summary_length_envelope.py`, `tests/unit/marcus/orchestrator/test_conversation_persistence_schema_versioning.py`, `tests/unit/models/test_specialist_state_shape_pin.py`, `tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py`, `tests/integration/marcus/test_path_z_first_contribution_wins_with_persistence.py`, `tests/integration/marcus/test_run_summary_yaml_emit.py`, `_bmad-output/implementation-artifacts/7a-5-codex-self-review-2026-04-XX.md`.

**Modified:** `app/marcus/orchestrator/production_runner.py` (extend `_build_decision_card` for adjacent-summary load + run_summary.yaml emit at trial close); `app/specialists/{texas,irene,gary,kira,wanda,enrique,quinn_r,vera,tracy}/graph.py` (additive: call `specialist_summary_writer.emit_summary(...)` in emit-node); `_bmad-output/implementation-artifacts/sprint-status.yaml` (Claude T11).

**Do NOT modify:** specialist `_act` bodies (only emit-node hook); 7a.1/7a.2/7a.3/7a.4/7a.6 surfaces; v4.2 prompt pack; manifest.

---

## Testing Requirements

**K-floor 14 + K-target ~22 (CEILING per Mary's Step 2 audit):**
- 4 conversation persistence cases (AC-A)
- 5 chain integrity cases (AC-B)
- 5 specialist-summary writer cases (AC-C)
- 4 length envelope cases (AC-D)
- 3 gate-handler adjacent-summary cases (AC-E)
- 4 specialist_state shape-pin cases (AC-F)
- 2 Path Z compatibility cases (AC-G)
- 3 run_summary.yaml emit cases (AC-H)
- 2 schema versioning cases (AC-I)

**K-tripwire:** 1.7× target (~4.25K LOC OR ~37 tests) → close round + party-mode triage.

---

## Dev Notes

**Architecture compliance:** Composition Spec §3.1 (envelope append-only) + SHA256 invariants HONORED per FR-A11-A14; Composition Spec §11 trigger NEGATIVE (additive persistence files; no envelope shape change). ADR-D3 Postgres checkpointer evolution: 7a.5 designs file format Postgres-compatible (additive-only schema; `_schema_version` field) but does NOT migrate runtime to Postgres yet.

**Library/framework:** stdlib `hashlib.sha256` + `json` (canonical encoding via `json.dumps(sort_keys=True, ensure_ascii=True, separators=(",", ":"))`); PyYAML for `run_summary.yaml`; Pydantic v2 for SpecialistState model. NO new third-party deps.

**Anti-patterns to avoid:** A12 procedural-coupling — summary writer is wired into emit-node (no manual operator step); A11 Windows-portability — POSIX paths in evidence list; A14 (silent fallback) — chain-broken raises, NOT warns.

**Previous story intelligence:** 7a.1 (`runs/<trial_id>/directive.yaml` + SHA256 digest) anchors the chain at turn 0; 7a.2 (gate-runner GateBypassError) means `silent_bypass_events: 0` is structurally enforced; 7a.3 (pre-gate-marcus PreFillProposal) is the structured-record format that conversation persistence captures.

**References:** Epic Story 1.6; PRD §FR3, FR5, FR16-FR20, FR29-FR33 + §FR-A11-A14, FR-A19, FR-A20 + §FR-O17-O19; governance JSON `7a-5`; Composition Spec §3.1; ADR-D3; CLAUDE.md governance.

---

## Dev Agent Record

(populate at dev-open)
