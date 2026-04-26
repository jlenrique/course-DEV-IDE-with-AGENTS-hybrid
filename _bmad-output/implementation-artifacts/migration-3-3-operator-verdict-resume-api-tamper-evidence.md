# Migration Story 3.3: OperatorVerdict + ResumeApi + Import-Linter Tamper-Evidence (FR34)

**Status:** ready-for-dev
**Sprint key:** `migration-3-3-operator-verdict-resume-api-tamper-evidence`
**Epic:** Slab 3 (migration Epic 3 — Marcus Orchestration; M3 go/no-go gate).
**Pts:** 5 | **Gate:** dual (per governance JSON `3-3.expected_gate_mode = "dual-gate"`, rationale: `invariant_preservation`). **K-target:** ~1.5× (target 18 / floor 14; OperatorVerdict four-file-lockstep + resume_api authority enforcement + scheduler-import-forbidden + digest-match enforcement + M3 evidence bullet test surface).

**Predecessor:** Stories 3.1 + 3.2 must be `done` (3.1 establishes Marcus + dispatch substrate; 3.2 establishes DecisionCard schema family that OperatorVerdict references via `decision_card_digest`). Drafted-for-queue per operator directive.

**SUBSTRATE-AWARE ADAPTATION applied 2026-04-26 post-Codex 3.1 T1 halt cascade analysis (MAJOR REWRITE on AC-A):**

**Substrate truth — `OperatorVerdict` ALREADY EXISTS at `app/models/state/operator_verdict.py`** (verified 2026-04-26 — file docstring: *"Architecture D3 (HIL Tamper-Evidence) places this model in Slab 1 substrate per architecture decision-of-record (overrides epics §3.3 drift). The verdict surface MUST never accept 'timeout' or 'auto_approve' as legitimate verbs... Triple-layer red-rejection (field + model_validator + schema-pin test) enforces the constraint. Frozen by invariant."*). **AC-A REFRAMED:** 3.3 does NOT author `app/gates/verdict.py::OperatorVerdict`; canonical home is `app/models/state/operator_verdict.py` per D3 Slab-1 substrate BINDING. 3.3 enriches around the existing model:
- **AC-A becomes AUDIT-AND-ENRICH:** verify existing `OperatorVerdict` carries all required fields per 3.3 spec (verdict_id, trial_id, gate_id, verb Literal, operator_id, timestamp tz-aware, decision_card_digest, edit_payload | None) + cross-field validator enforcing `edit_payload` required iff `verb == "edit"`. If any field missing, file as additive minimal extension (ship at 3.3 against existing model). Re-export from `app/gates/__init__.py` for 3.3-spec-cited access path.
- **AC-B + AC-C + AC-E + AC-F unchanged in substance** but consume existing `app.models.state.operator_verdict.OperatorVerdict` (NOT new `app.gates.verdict.OperatorVerdict`).
- **`app/gates/resume_api.py`** — Slab-1 stub exists; 3.3 IMPLEMENTS `resume_from_verdict()` body per AC-B (this remains additive minimal extension; correct in original spec).

**Substrate truth — `app/marcus/cli/` and `app/http/` parent dirs do NOT exist yet** (verified 2026-04-26); A-BLOCKER-3.3-A T0 mkdir holds. **HOWEVER:** per Story 3.1 substrate-aware adaptation, the canonical Marcus home is `marcus/` (not `app/marcus/`). 3.3 bridge stubs land at:
- **`marcus/cli/{__init__,gate_cli}.py`** (canonical home; consistent with existing `marcus/{intake,orchestrator,facade.py}` package layout)
- **`app/http/{__init__,gate_endpoint}.py`** (HTTP transport at app/ tree per existing `app/mcp_server/` precedent — verify `app/mcp_server/` location at T1)

**Substrate truth — `pyproject.toml:88-95` C3 staged-delivery comment** anticipates `app.marcus.cli.gate_cli -> app.gates.resume_api` ignore_imports entry; per substrate-adaptation, this becomes `marcus.cli.gate_cli -> app.gates.resume_api`. Spec amends C3 import paths accordingly.

**Lean party-mode amendments applied 2026-04-26 (Winston + Murat + Amelia):** 1 BLOCKER + 8 RIDERs integrated:
- **A-BLOCKER-3.3-A (bridge-stub parent dirs):** T1 sub-task — verify `app/marcus/cli/` and `app/http/` parent directories exist; if absent, T0 step `mkdir + __init__.py` for both before any AC-D work. Prevents silent unintentional package layout.
- **W-R1-3.3-1 (runtime sys.modules guard):** Add runtime guard in `app/gates/verdict.py` module init: assert `"asyncio.tasks" / "scheduler" / "apscheduler" / "schedule"` not in `sys.modules` at operator_verdict import time; closes dynamic `importlib.import_module(...)` evasion path that ruff + import-linter + AST test all miss.
- **W-R1-3.3-2 (anti-replay digest binding):** Decision #4 strengthened — `decision_card_digest` MUST bind tuple `(card_content_canonical_json, trial_run_id, issuance_timestamp_iso, server_nonce)` NOT just card_content. Server-issued nonce in card at issuance; resume_from_verdict rejects if nonce already-consumed. AC-B adds explicit anti-replay test `test_resume_from_verdict_rejects_replayed_verdict_from_prior_trial`.
- **W-R1-3.3-3 (transport=stub markers):** Bridge stubs MUST set `X-Gate-Transport: stub` response header (HTTP) and `[transport=stub]` log prefix (CLI); 3.4 transport bodies REMOVE these markers. Prevents 3.3 stubs accidentally shipping to transport-claimed environment.
- **A-R1-3.3 (quad-layer enumeration):** AC-E + Decision #3 enumerate the 4 layers EXPLICITLY: (1) ruff rule, (2) import-linter forbidden contract, (3) AST test, (4) pre-commit hook. NO under-implementation via "quad-layer" hand-wave.
- **A-R2-3.3 (cross-module verdict↔card linkage):** OperatorVerdict adds `card_id: UUID4` field linking to DecisionCard from 3.2; cross-field validator asserts `card_id` matches a card emitted for `(trial_id, gate_id)`. Augments digest-match enforcement.
- **M-R1-3.3 (mutation tests for digest):** AC-B adds **mutation tests** — flip one byte in serialized verdict → resume MUST reject. Without mutation pair, only happy-path of security boundary tested. Non-negotiable for invariant_preservation gate.
- **M-R2-3.3 (asyncio test consistency):** All `resume_from_verdict` tests use `pytest.mark.asyncio` (or anyio) consistently; verify NO sync/async fixture mixing; watch "test passes because the coroutine was never awaited" pattern.
- **M-R3-3.3 (don't mock digest):** Tamper-evidence tests use real `hashlib`; mock ONLY the storage layer. Mocking digest is mock-the-spy anti-pattern.
- **K-floor recount post-amendments:** AC-B +2 (mutation tests) + AC-C +1 (anti-replay test) + AC-A +1 (card_id linkage validator) = honest K-floor 19 (above target 18; well above floor 14). K-target ~1.5× holds.

---

## T1 Readiness Block

### Standing Pre-Flight items

1. **Governance lookup** — `docs/dev-guide/migration-story-governance.json` confirms `3-3.expected_gate_mode = "dual-gate"` (rationale: `invariant_preservation`). Do not relitigate.
2. **Slab 1 substrate** — `app/gates/{__init__.py, resume_api.py}` exist as Slab-1 stubs (verified 2026-04-26 per Glob); `resume_api.py` is the authoritative resume entry point.
3. **C3 import-linter precedent (BINDING)** — `pyproject.toml:88-95` C3 contract — "import-linter rejects unused ignores, so pre-seeding them here would fail" + "Slab 3 Story 3.3 adds the two future ignore_imports entries (`app.http.gate_endpoint ->` and `app.marcus.cli.gate_cli ->`) when the bridge modules materialize." 3.3 ADDS those entries when transports materialize at this story.
4. **Architecture doc D3** — FR34 architecturally unavailable to bypass (NOT merely conventionally avoided); HIL tamper-evidence enforced via import-linter contract + scheduler-import-forbidden ruff rule + digest-match runtime enforcement.
5. **3.1 architectural foundation** — `app.marcus.cli.gate_cli` substrate authored at this story (NEW per Decision #1); transport implementations at 3.4.
6. **3.2 DecisionCard schema family** — OperatorVerdict.decision_card_digest references DecisionCard digest (canonical-JSON sha256 per 31-1 precedent).
7. **31-1 schema-shape precedent** — OperatorVerdict is itself a four-file-lockstep schema (Pydantic v2 strict + JSON Schema + shape-pin test + golden fixture); 14 idioms apply.
8. **Pydantic-v2 schema checklist** — frozen + validate_assignment + extra=forbid + UUID4 + tz-aware datetime + cross-field validator (edit_payload-iff-edit-verb).
9. **Anti-patterns catalog** — A4 silent-mutation, A5 naive datetime, A6 closed-enum-one-rejection-surface (verb closed-enum).
10. **Severance posture** — hybrid working tree.

### Slab 3.3 artifact-existence sweep (5-point)

- **A** `app/gates/{__init__.py, resume_api.py}` exist as Slab-1 stubs (verified 2026-04-26).
- **B** `app/marcus/cli/` does NOT exist; this story creates it for `gate_cli`.
- **C** `app/http/` does NOT exist; this story creates it for `gate_endpoint` (or 3.4 — verify scope at T1).
- **D** `app/mcp_server/tools/gate_decide.py` exists per Slab 1 substrate (per pyproject.toml:108 ignore_imports entry); this story does NOT modify but consumes the import-linter authorization.
- **E** Pre-commit hook + ruff config carries scheduler-import-forbidden infrastructure (verify; if absent, AC-C adds it).

### Epic-doc-vs-architecture cross-check (per R6)

#### (a) Framework drifts

**One scope ambiguity:** epic 3.3 references `app.http.gate_endpoint` as authorized resume_api caller; epic 3.4 also references HTTP transport at `app.http.gate.py`. **Resolution:** 3.3 establishes `app/http/gate_endpoint.py` minimal substrate (callable surface only; full FastAPI implementation at 3.4); 3.3 import-linter authorizes the dotted path so 3.4 transport-impl story can populate the body without an additional contract change.

#### (b) TEMPLATE scope decisions

**Decision #1 — Bounded scope:** scope is (a) `app/gates/verdict.py::OperatorVerdict` Pydantic v2 strict frozen + four-file-lockstep; (b) `app/gates/resume_api.py::resume_from_verdict()` implementation; (c) import-linter contract C3 extension (add `app.http.gate_endpoint ->` and `app.marcus.cli.gate_cli ->` ignore_imports per pyproject.toml:88-95 C3 precedent); (d) scheduler-import-forbidden ruff + import-linter rules for `app/gates/**`; (e) digest-match enforcement runtime check; (f) bridge-module callable stubs at `app/marcus/cli/gate_cli.py` + `app/http/gate_endpoint.py` (full transport-impl at 3.4); (g) M3 evidence test (synthetic asyncio.sleep + Command(resume=...) bypass attempt rejected at compile). NOT in scope: full transport surfaces (3.4); model-override (3.5); E2E trial (3.6).

**Decision #2 — Cross-field validator pattern (Pydantic v2):** `edit_payload: dict[str, Any] | None = None`; cross-field validator enforces `edit_payload` is required iff `verb == "edit"`. Implementation pin: use `@model_validator(mode="after")` returning `self`; raise `ValueError` on violation (Pydantic converts to `ValidationError`).

**Decision #3 — Scheduler-import-forbidden enforcement layers:** TWO layers per FR34 architectural-not-conventional discipline:
- **Layer 1 (static):** ruff rule + import-linter contract on `app/gates/**` forbidden modules `{asyncio.sleep, threading.Timer, apscheduler, schedule}`
- **Layer 2 (test-time):** `tests/integration/gates/test_no_scheduler_import.py` synthetic violation against each of the 4 forbidden modules; assert pre-commit hook + CI both reject with `SchedulerImportError`

**Decision #4 — Digest-match enforcement runtime check:** `resume_from_verdict(verdict)` reads the emitted DecisionCard for `verdict.gate_id` + `verdict.trial_id`; recomputes the canonical-JSON sha256; compares to `verdict.decision_card_digest`. Mismatch raises `GateError("digest_mismatch", ...)` + refuses to resume. Tamper evidence: any operator-supplied verdict against a stale or fabricated card is rejected.

---

## Story

As an **architect of HIL invariant preservation per FR34**,
I want **`app/gates/verdict.py::OperatorVerdict` Pydantic v2 strict frozen + `app/gates/resume_api.py::resume_from_verdict()` implementation + import-linter contract C3 extension making resume_api callable only from three authorized transports + scheduler-import-forbidden ruff + import-linter rules for `app/gates/**` + digest-match enforcement + M3 evidence bullet test (synthetic asyncio.sleep + Command(resume=...) bypass attempt rejected at compile)**,
So that **FR34 is architecturally unavailable to bypass (NOT merely conventionally avoided), HIL tamper-evidence is enforced at compile-time + runtime, and operator verdicts cannot be spoofed against stale or fabricated DecisionCards**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Sandbox-AC compliant.

### AC-3.3-A — `OperatorVerdict` Pydantic v2 strict frozen + four-file-lockstep

- **Given** no `app/gates/verdict.py` exists at Slab-1 close
- **When** the dev agent authors `OperatorVerdict` per 31-1 schema-shape precedent:
  - `model_config = ConfigDict(frozen=True, validate_assignment=True, extra="forbid")`
  - Fields: `verdict_id: UUID4`, `trial_id: UUID4`, `gate_id: str`, `verb: Literal["approve", "edit", "reject"]`, `operator_id: str` (non-empty regex `^[a-zA-Z][a-zA-Z0-9_-]+$`), `timestamp: datetime` (tz-aware UTC), `decision_card_digest: str` (sha256-hex shape), `edit_payload: dict[str, Any] | None = None`
  - Cross-field validator per Decision #2: `edit_payload` is required iff `verb == "edit"`
- **Then** four-file-lockstep present: model + JSON Schema (`schema/operator_verdict.v1.schema.json`) + shape-pin test + golden fixture.
- **Test pin:** `tests/unit/gates/test_operator_verdict_strict.py` — 5 tests:
  1. `test_strict_config` — `frozen=True` + `validate_assignment=True` + `extra="forbid"`; mutation post-construction raises.
  2. `test_verb_closed_enum_triple_layer` — invalid verb raises at construction + JSON-parse + assignment.
  3. `test_edit_payload_required_iff_edit_verb` — verb="edit" + edit_payload=None raises; verb="approve" + edit_payload={...} raises (cross-field validator both directions).
  4. `test_tz_aware_datetime_required` — naive datetime raises.
  5. `test_operator_id_non_empty_regex` — empty string + invalid chars raise.

### AC-3.3-B — `resume_from_verdict()` implementation + digest-match enforcement (DUAL-GATE invariant-preservation gate-1)

- **Given** `app/gates/resume_api.py` exists as Slab-1 stub
- **When** the dev agent authors `resume_from_verdict(verdict: OperatorVerdict) -> CompiledGraphHandle`:
  1. Read the emitted DecisionCard for `verdict.gate_id` + `verdict.trial_id` from the per-trial card-store
  2. Recompute canonical-JSON sha256 of the card per 31-1 digest convention
  3. Compare to `verdict.decision_card_digest`; mismatch raises `GateError("digest_mismatch", ...)` + refuses to resume
  4. On match: resume the graph at the gate node via `langgraph.Command(resume=verdict.verb)` payload
- **Then** synthetic test constructs valid + invalid digest cases; both behaviors validated.
- **Test pins:**
  1. `tests/integration/gates/test_resume_from_verdict_digest_match.py` — 2 tests: `test_digest_match_resumes` (valid digest → graph resumes) + `test_digest_mismatch_raises_gate_error` (mutated digest → `GateError("digest_mismatch")`).
  2. `tests/integration/gates/test_resume_from_verdict_card_missing.py` — 1 test: card-store has no entry for `gate_id`+`trial_id` → `GateError("card_missing")`.

### AC-3.3-C — Import-linter authority enforcement (C3 extension per pyproject.toml:88-95)

- **Given** `pyproject.toml:107-...` C3 contract `ignore_imports` list at Slab-1+Slab-2 close (currently 14+ entries for specialists + `app.mcp_server.tools.gate_decide`)
- **When** the dev agent extends C3 ignore_imports per pyproject.toml:88-95 staged-delivery comment:
  - `"app.http.gate_endpoint -> app.gates.resume_api"` (NEW — bridge module materializes at AC-D below)
  - `"app.marcus.cli.gate_cli -> app.gates.resume_api"` (NEW — bridge module materializes at AC-D below)
- **Then** `lint-imports --config pyproject.toml` returns N/N KEPT (all contracts including C3 with extended allowlist); negative test `tests/integration/gates/test_resume_api_authority.py` greps `app/` tree for unauthorized callers + asserts only the 3 authorized bridges (`app.mcp_server.tools.gate_decide`, `app.http.gate_endpoint`, `app.marcus.cli.gate_cli`) construct OperatorVerdict OR call `resume_from_verdict`.
- **Test pins:**
  1. `tests/integration/gates/test_resume_api_authority.py` — 2 tests: `test_authorized_bridges_call_resume_api` (3 bridge files contain `from app.gates.resume_api import resume_from_verdict`); `test_no_unauthorized_callers` (grep `app/**/*.py` excluding 3 bridges + `app/gates/**`; assert ZERO hits for `resume_from_verdict` or `OperatorVerdict(`).
  2. `tests/integration/gates/test_resume_api_unauthorized_construction_rejected_at_compile.py` — 1 test: synthetic `app/runtime/synthetic_violation.py` containing `OperatorVerdict(...)` → `lint-imports` fails (test creates synthetic, invokes lint-imports subprocess, asserts non-zero exit + `OperatorVerdict` named in stderr, restores state).

### AC-3.3-D — Bridge-module callable stubs (resume_api consumers at 3.3; full transport-impl at 3.4)

- **Given** `app/marcus/cli/` and `app/http/` do NOT exist at 3.2 close
- **When** the dev agent authors minimal callable stubs per Decision #1:
  - `app/marcus/cli/__init__.py`
  - `app/marcus/cli/gate_cli.py` — function `gate_decide_cli(args: argparse.Namespace) -> int`; calls `resume_from_verdict(...)` + returns exit code; full CLI impl deferred to 3.4
  - `app/http/__init__.py`
  - `app/http/gate_endpoint.py` — function `gate_verdict_endpoint(payload: dict) -> dict`; calls `resume_from_verdict(...)` + returns response dict; full FastAPI route deferred to 3.4
- **Then** both bridge stubs import `resume_from_verdict` (resolves the C3 ignore_imports entries from AC-C — no unused-ignore failure).
- **Test pin:** `tests/unit/gates/test_bridge_module_stubs_present.py` — 2 tests: `gate_cli` and `gate_endpoint` files exist + import `resume_from_verdict` + are non-trivially callable.

### AC-3.3-E — Scheduler-import-forbidden ruff + import-linter rules + test-layer per Decision #3

- **Given** scheduler-import-forbidden infrastructure may or may not exist at Slab-2 close (verify at T1; if absent, AC-E adds)
- **When** the dev agent authors:
  - Ruff rule via `pyproject.toml [tool.ruff.lint.per-file-ignores]` OR custom ruff plugin: forbid `asyncio.sleep`, `threading.Timer`, `apscheduler`, `schedule` imports in `app/gates/**`
  - Import-linter contract: forbidden contract on `app.gates.**` source modules + `{asyncio, threading, apscheduler, schedule}` forbidden modules (with `app.gates.resume_api` allowlist for legitimate `asyncio` graph-handle uses if any — pin at dev-time)
- **Then** synthetic test attempts add `import asyncio; asyncio.sleep(...)` to `app/gates/verdict.py`; pre-commit + CI both reject with `SchedulerImportError`.
- **Test pin:** `tests/integration/gates/test_no_scheduler_import.py` — 4 tests parametrize-collapsible per M-R18 → 1 K-floor unit (4 forbidden modules; same property = "forbidden by import-linter"): each module synthesized as violation; assert lint-imports rejects.

### AC-3.3-F — M3 evidence bullet (D3 + epic 3.3 AC binding)

- **Given** M3 Required Evidence per architecture D3 + epic 3.3 AC: trial run confirms every gate's resume is driven by valid `OperatorVerdict` AND staged bypass attempt via `asyncio.sleep + direct Command(resume=...)` is rejected at graph-compile
- **When** the dev agent authors a synthetic-bypass test:
  - Construct `app/runtime/synthetic_bypass_attempt.py` containing `import asyncio; asyncio.sleep(0); from langgraph import Command; Command(resume="approve")` 
  - Invoke graph-compile (`compile_run_graph(manifest, validation_mode=True)`) on a manifest that references the synthetic
  - Assert compile fails with `SchedulerImportError` AND/OR `UnauthorizedResumeBypassError` per layered enforcement from AC-C + AC-E
- **Test pin:** `tests/integration/gates/test_m3_bypass_attempt_rejected.py` — 1 test asserting graph-compile rejection.

### AC-3.3-G — Anti-pattern catalog harvest (per R6)

NO new entries expected. If FR34-bypass-pattern surfaces (e.g., a NEW bypass vector via subprocess that scheduler-import rule misses), file as candidate per harvest-gate.

### AC-3.3-H — TEMPLATE compliance (per R1–R14 v2.4)

R1, R6, R8 honored. Schema-shape stories (OperatorVerdict) follow `docs/dev-guide/scaffolds/schema-story/` scaffold per Lesson-Planner-MVP convention.

### AC-3.3-I — D12 close protocol (DUAL-gate; invariant_preservation; FIVE-line)

1. **Invariant preservation:** FR34 architectural enforcement (NOT conventional); HIL tamper-evidence at compile + runtime; digest-match anti-spoof; scheduler-import-forbidden quad-layer.
2. **Anti-pattern harvest:** N/A unless surfaced.
3. **Migration-guide update:** §"Gate Migration" deepened; OperatorVerdict + resume_from_verdict are the canonical HIL substrate; scheduler-import-forbidden documented as architectural rule (NOT review-time discipline).
4. **TEMPLATE compliance:** R1, R6, R8 honored. Numeric anchors: 1 OperatorVerdict model + 1 resume_api impl + 2 bridge stubs + 4 scheduler-forbidden modules + 2 NEW C3 ignore_imports + 1 M3 evidence bypass test.
5. **Dual-gate gate-2 (operator invariant-preservation review):** operator confirms FR34 architectural-not-conventional discipline + reads M3 evidence test result.

### AC-3.3-J — Sprint-status state-flips at filing AND at close

At filing: `migration-3-3-...: ready-for-dev`. At close: `migration-3-3-...: done`.

---

## File Structure Requirements

### NEW files

```
app/gates/
├── verdict.py                                    # AC-A OperatorVerdict
└── schema/
    └── operator_verdict.v1.schema.json

app/marcus/cli/
├── __init__.py
└── gate_cli.py                                   # AC-D bridge stub

app/http/
├── __init__.py
└── gate_endpoint.py                              # AC-D bridge stub

tests/unit/gates/
├── test_operator_verdict_strict.py               # 5 tests (AC-A)
└── test_bridge_module_stubs_present.py           # 2 tests (AC-D)

tests/integration/gates/
├── test_resume_from_verdict_digest_match.py      # 2 tests (AC-B)
├── test_resume_from_verdict_card_missing.py      # 1 test (AC-B)
├── test_resume_api_authority.py                  # 2 tests (AC-C)
├── test_resume_api_unauthorized_construction_rejected_at_compile.py  # 1 test (AC-C)
├── test_no_scheduler_import.py                   # 4 tests parametrize → 1 K-floor (AC-E)
└── test_m3_bypass_attempt_rejected.py            # 1 test (AC-F)

tests/fixtures/gates/
└── operator_verdict_golden.json
```

### MODIFIED files

- `app/gates/resume_api.py` — Slab-1 stub gets `resume_from_verdict()` impl per AC-B.
- `app/gates/__init__.py` — exports OperatorVerdict + resume_from_verdict + GateError.
- `pyproject.toml` `[tool.importlinter]` C3 contract — 2 NEW ignore_imports entries per AC-C + scheduler-import-forbidden contract per AC-E.
- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` — entry for OperatorVerdict family.
- `docs/dev-guide/langgraph-migration-guide.md` — §"Gate Migration" deepened.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-J.

---

## Testing Requirements

**K-target ~1.5× (target 18 / floor 14).** Test count + K-floor:

| AC | Tests collected | Honest K-floor units |
|---|---|---|
| A | 5 (strict_config + verb-enum + edit-payload-cross-field + tz-aware + operator-id) | **5** (5 orthogonal Pydantic-v2 properties) |
| B | 3 (digest-match + digest-mismatch + card-missing) | **3** |
| C | 3 (authorized-bridges + no-unauthorized + synth-construction-rejected) | **3** |
| D | 2 (gate_cli + gate_endpoint stubs present + callable) | **2** |
| E | 4 parametrize → 1 K-floor (4 forbidden modules) | **1** |
| F | 1 (M3 bypass rejection) | **1** |
| **Total** | **18 collected** | **15 K-floor units** |

**Honest K-floor: 15** (above floor 14). Within ~1.5× K-target band (target 18 / floor 14; 18/14 = 1.29×; 15/14 = 1.07×). Recalibrate down to ~1.3× if 15 K-floor is judged firm at story-open.

**Regression target at T8:** baseline + previous Slab 3 stories. +18 collected at file level. Import-linter contracts EXPAND with C3 +2 ignore_imports + scheduler-forbidden NEW contract. Ruff clean (after scheduler-forbidden rule lands). Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
