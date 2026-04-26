# Migration Story 3.6: End-to-End Trial Run with Marcus Supervisor + M3 Acceptance (SLAB CLOSING)

**Status:** ready-for-dev
**Sprint key:** `migration-3-6-e2e-trial-run-and-m3-acceptance-slab-close`
**Epic:** Slab 3 (migration Epic 3 — Marcus Orchestration; **M3 go/no-go gate "Marcus orchestrates end-to-end"**) — **SLAB CLOSING story**.
**Pts:** 5 | **Gate:** dual (per governance JSON `3-6.expected_gate_mode = "dual-gate"`, rationale: `operator_acceptance_gate`). **K-target:** ~1.4× (target 14 / floor 10; E2E trial run §01→§15 + DecisionCard emission per gate + operator verdict round-trip + at least one edit-verb propagation + Texas AC-B-OP reactivation per 2a.4 binding + 5-agent party-mode + invariant audit).

**Predecessor:** Stories 3.1–3.5 must be `done`. SLAB CLOSING; closes M3 milestone.

**Inheritance bindings (HARD):**
- **W-R7-3.1 baseline-capture:** post-3.6 Marcus envelope captured as frozen fixture (`3-6-marcus-envelope-baseline-capture-for-future-regression-detection` deferred-inventory entry filed at 3.1; resolves at 3.6 via AC-G below).
- **2a.4 deferred-inventory `2a.4-followon-ac-b-op-live-retrieval` (Murat hard-caveat BINDING):** Slab-3 close MUST re-execute Texas AC-B-OP on live wire with full M1-M5 test discipline per the inventory entry — this is BLOCKING for Slab 3 close.

**Lean party-mode amendments applied 2026-04-26 (Winston + Murat + Amelia):** 1 BLOCKER + 11 RIDERs integrated:
- **A-BLOCKER-3.6-A (§01-§15 step ID staleness):** T1 sub-task — cross-check `state/config/pipeline-manifest.yaml` for actual step IDs; if Slab 2 work renamed/renumbered any step, the §01→§15 enumeration is stale. Spec MUST reference step IDs by name (not ordinal) at dev-time.
- **A-R1-3.6 (2a.4 binding pin):** AC-D cites the 2a.4 binding artifact path explicitly (deferred-inventory entry id `2a.4-followon-ac-b-op-live-retrieval` at `_bmad-output/planning-artifacts/deferred-inventory.md`); operator can locate without spelunking.
- **A-R2-3.6 (5-agent enumeration):** AC-F roster pinned EXPLICITLY: Winston + Murat + Paige + Quinn-R + Amelia (NOT abbreviated as "5-agent" alone); mirrors 2c.3 5-agent pattern.
- **A-R3-3.6 (M3 numbered checklist):** AC-K D12 close protocol enumerates M3 acceptance as binary checklist items (NOT narrative): (1) trial run §01-§15 completed; (2) ≥1 edit-verb propagation; (3) Texas AC-B-OP M1-M5 evidence pasted; (4) Marcus-envelope baseline captured + BASELINE_METADATA.md present; (5) 5-agent verdict GREEN-LIGHT or CONDITIONAL-GREEN; (6) `slab-3-marcus-invariant-stub.md` filed.
- **W-R1-3.6-1 (provider-failure isolation policy per Winston):** AC-D Texas AC-B-OP harness MUST define explicit per-provider PASS/FAIL/SKIP graceful-degrade policy; spec captures policy (NOT left to harness discretion). One flaky provider does NOT fail entire AC-B-OP.
- **W-R1-3.6-2 (re-baseline protocol per Winston):** AC-E Marcus-envelope baseline ships with explicit re-baseline protocol (party-mode gated, version-bumped fixture migration path) covering schema evolution after Slab-3 closes. Documented in BASELINE_METADATA.md companion.
- **W-R1-3.6-3 (capture-environment hash per Winston):** BASELINE_METADATA.md pins capture-environment hash (Marcus persona-load SHA + sanctum-state SHA + reference-set SHA + capturing-agent + capture-command); byte-diff-on-CI surfaces as regression NOT environment drift.
- **W-R1-3.6-4 (CONDITIONAL-GREEN bounded triggers per Winston):** AC-F + Decision #2 enumerate bounded CONDITIONAL-GREEN trigger conditions for M3: ONLY evidence-completeness gaps (not behavioral). Behavioral gaps route to YELLOW (re-spec) or RED (pivot back). Examples: (a) Texas AC-B-OP partial-pass with ≥1 provider flake; (b) BASELINE_METADATA.md missing one provenance field; (c) E2E trial completes with non-blocking trace warning needing triage.
- **M-R1-3.6 (phase-vs-test K disambiguation):** AC-A E2E §01-§15 = ONE logical scenario = K=1 (NOT 15 phases as 15 K-floor units). Phases count as ASSERTIONS within one pytest function, NOT separate tests.
- **M-R2-3.6 (operator-gated AC-B-OP re-verification):** Re-verify AC-D Texas live-wire is in operator-gated AC block before dev-open (sandbox-AC PASSed at authoring; re-verify per CLAUDE.md sandbox-AC discipline).
- **M-R3-3.6 (golden-file content-hash):** AC-E Marcus-envelope baseline pinned with content-hash + schema-version (NOT byte-equal); baselines drift; design comparison forward-compat from day one.
- **M-R4-3.6 (process-gate not test):** AC-F 5-agent party-mode is a PROCESS GATE not a test; do NOT inflate K count. It's an operator-gated AC, full stop. AC-F test asserts the verdict-recording artifact STRUCTURE (per Murat M-R2-2c.3 inheritance), NOT the verdict content.

---

## T1 Readiness Block

### Standing Pre-Flight items

1. **Governance lookup** — `3-6.expected_gate_mode = "dual-gate"` (rationale: `operator_acceptance_gate`).
2. **Predecessor close evidence** — Stories 3.1, 3.2, 3.3, 3.4, 3.5 expected `done` per sprint-status.yaml. Verify before T1 proceed.
3. **Trial corpus** — verify identifiable input content bundle for §01→§15 trial run (operator-supplied; pin location at T1).
4. **Marcus orchestrator** per 3.1 — facade + supervisor + routing + intake + write_api ready.
5. **DecisionCard schema family** per 3.2 — G1, G2C, G3, G4 models present.
6. **OperatorVerdict + resume_api** per 3.3 — tamper-evidence enforced.
7. **Three transports** per 3.4 — MCP + FastAPI + CLI all callable.
8. **Override surface** per 3.5 — submit_override + apply_override + warnings.
9. **2a.4 deferred-inventory binding (BLOCKING):** Texas AC-B-OP reactivation per Murat hard-caveat point c (re-execute on live wire with M1-M5 test discipline; helper script + directive template at `scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py` + `tests/fixtures/specialists/texas/ac_b_op_directive.yaml` pre-authored at 2a.4 SHIP UNINVOKABLE-ON-HYBRID-TODAY; Slab-3 inherits without re-authoring).
10. **3.1 baseline-capture filed-forward (W-R7-3.1):** capture post-3.6 Marcus envelope on first trial corpus run as frozen fixture for future regression-detection (rebinds primary's Story 30-1 amendment 12 Golden-Trace Baseline to migration substrate from Slab 4 onward).
11. **Anti-patterns catalog** — read for any 3.x harvest signals.
12. **Slab 2 + Slab 1 retrospectives** as format precedent for `slab-3-retrospective.md` SLAB-CLOSING artifact.
13. **Severance posture** — hybrid working tree.

### Slab 3.6 artifact-existence sweep (8-point)

- **A** Sprint-status: 3.1 + 3.2 + 3.3 + 3.4 + 3.5 all `done`.
- **B** Trial corpus identified (operator-supplied; pin at T1).
- **C** `tests/fixtures/specialists/texas/ac_b_op_directive.yaml` exists (pre-authored at 2a.4).
- **D** `scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py` exists (pre-authored at 2a.4).
- **E** `_bmad-output/implementation-artifacts/3-6-marcus-envelope-baseline-capture-for-future-regression-detection` deferred-inventory entry exists per 3.1 W-R7 filing.
- **F** No `slab-3-retrospective.md` exists yet (3.6 creates it; precedent at `slab-2c-retrospective.md` if it exists post-2c.4 close, else `slab-2b-retrospective.md`).
- **G** `_bmad-output/implementation-artifacts/slab-3-m3-acceptance-verdict.md` does not exist (3.6 creates it as M3 verdict-recording artifact mirroring 2c.3 `slab-2c-m2-acceptance-verdict.md` pattern).
- **H** Operator credentials available for live API calls in trial run (operator-side per sandbox-AC discipline).

### Epic-doc-vs-architecture cross-check (per R6)

#### (a) Framework drifts

NONE expected at SLAB CLOSE if Stories 3.1-3.5 closed cleanly. If any drift surfaced during 3.x, document in retrospective.

#### (b) TEMPLATE scope decisions

**Decision #1 — Bounded scope:** scope is (a) E2E trial run §01→§15 with `preset: production`; (b) DecisionCard emission per gate (G1/G2C/G3/G4 fire per substrate); (c) operator emits verdict at each gate via CLI (MCP + FastAPI optional at this milestone per PRD); (d) at least one `edit` verb exercised + propagated downstream; (e) reject-rate KPI tracks decision distribution; (f) **Texas AC-B-OP reactivation per 2a.4 BLOCKING binding** with full M1-M5 test discipline; (g) Marcus-envelope baseline capture per W-R7-3.1; (h) 5-agent party-mode (Winston + Murat + Paige + Quinn-R + Amelia) M3 acceptance verdict; (i) invariant audit matrix Marcus + gates entries (FR63 incremental roll-up per 2c.3 D pattern); (j) `slab-3-retrospective.md` SLAB-CLOSING artifact; (k) D12 close protocol; (l) `next-session-start-here.md` update.

**Decision #2 — M3 verdict format:** mirror 2c.3 `slab-2c-m2-acceptance-verdict.md` 4-enum + verdict-token + verbatim-recording pattern. Consensus enum: `(GREEN-LIGHT | GREEN-WITH-RIDERS | CONDITIONAL-GREEN | YELLOW | RED)`; per-agent enum adds `ABSTAIN`.

**Decision #3 — Marcus-envelope baseline capture (per W-R7-3.1):** capture post-3.6 Marcus envelope on first trial corpus run as frozen fixture at `tests/fixtures/marcus/baseline_envelope/<YYYY-MM-DD>/`. From Slab 4 onward, regression tests against this baseline detect Marcus-output drift. Resolves the regression-detection blind spot from primary's Story 30-1 amendment 12 Golden-Trace Baseline that hybrid couldn't substrate-mine at 3.1.

**Decision #4 — Texas AC-B-OP M1-M5 test discipline (BLOCKING per 2a.4 inventory):**
- **M1:** 7 parametrized parse-branch cases against actual scite/Consensus MCP responses (NOT fixture bundles)
- **M2:** sha256 baselines re-validated post-Slab-3-changes (sanctum lock + NFR-I5 retrieval-contract preservation)
- **M3:** subprocess-dispatch-latency p50/p95 measured + recorded as substitute-metric baseline (FR54 pure-tool-dispatch substitute per 2a.4 close)
- **M4:** two-sided assertions on parse outcome AND resolution-trail tag
- **M5:** operator runs helper script end-to-end + pastes filled-in evidence Markdown into 3.6 Dev Agent Record §"Texas AC-B-OP Live Evidence"

---

## Story

As an **operator closing M3**,
I want **a new tracked trial run §01→§15 completes with Marcus as supervisor + DecisionCards at every gate + operator verdict via CLI at every gate + at least one `edit` verb exercised + Texas AC-B-OP reactivated per 2a.4 binding with M1-M5 evidence + Marcus-envelope baseline captured + 5-agent party-mode (Winston + Murat + Paige + Quinn-R + Amelia) M3 acceptance verdict recorded verbatim + Slab 3 retrospective + D12 close protocol**,
So that **M3 Required Evidence is accrued ("Marcus orchestrates end-to-end"), Slab 3 closes to done, the 2a.4-deferred Texas live-wire evidence is on file, the migration-equivalent Golden-Trace baseline is captured for future regression detection, and Slab 4 (lockstep + ledger + Cora) opens with a clean predecessor**.

---

## Acceptance Criteria

### AC-3.6-A — E2E trial run §01→§15 with `preset: production`

- **Given** Stories 3.1–3.5 closed; trial corpus identified at T1
- **When** operator starts a trial via CLI: `app.marcus.cli trial start --preset production --input <corpus-path>`
- **Then** §01 through §15 executes; Marcus routes per manifest; every gate emits a DecisionCard; operator emits verdict at each gate via CLI; run closes cleanly (terminal state per RunState)
- **Test pin:** N/A as a single test (this is an operator-driven E2E trial); evidence captured in Dev Agent Record §T8 trial-run log + final RunState fixture.

### AC-3.6-B — At least one `edit` verb exercised + propagation

- **Given** operator opportunity at any gate to issue `edit` verb
- **When** operator chooses `edit` at one gate (≥1 across §01-§15)
- **Then** the edit propagates downstream via `RunState` payload; reject-rate KPI tracks the decision distribution; ledger event emitted with `kind="verdict"` + `verb="edit"` + `edit_payload` populated
- **Test pin:** `tests/integration/marcus/test_edit_verb_propagation.py` — 1 test simulating edit verdict at G2C + asserting downstream node receives modified RunState payload.

### AC-3.6-C — DecisionCard emission + operator verdict per gate

- **Given** trial run executes per AC-A
- **When** each gate fires (G1, G2C, G3, G4 per epic-3.6 §01→§15 substrate)
- **Then** DecisionCard emitted with all required fields per 3.2 schema; operator verdict consumed via 3.3 resume_api; verdict.decision_card_digest matches emitted card digest
- **Test pin:** `tests/integration/marcus/test_decision_card_emission_per_gate.py` — 4 tests parametrize over 4 gates → 1 K-floor unit per M-R18.

### AC-3.6-D — Texas AC-B-OP live-wire reactivation per 2a.4 BLOCKING binding (M1-M5 discipline)

- **Given** 2a.4 deferred-inventory entry `2a.4-followon-ac-b-op-live-retrieval` BLOCKING per Murat hard-caveat point c
- **When** operator runs:
  ```
  .venv/Scripts/python.exe scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py \
    --directive tests/fixtures/specialists/texas/ac_b_op_directive.yaml \
    --bundle-dir <operator-supplied-path>
  ```
- **Then** M1-M5 test discipline executes per Decision #4:
  1. **M1:** 7 parametrized parse-branch cases against actual scite/Consensus MCP responses pass
  2. **M2:** sha256 baselines re-validated (sanctum lock + NFR-I5 retrieval-contract preserved)
  3. **M3:** subprocess-dispatch-latency p50/p95 measured + recorded
  4. **M4:** two-sided parse outcome + resolution-trail tag assertions pass
  5. **M5:** operator pastes filled-in evidence Markdown into Dev Agent Record §"Texas AC-B-OP Live Evidence"
- **And** anti-pattern catalog reviews `A13 — Premature live-wire AC against not-yet-ported substrate` per Paige proposal at party-mode 2026-04-25 (confirms harvest at slab-3 close OR augments A9 sibling subsection); harvest verdict recorded in 3.6 close notes per harvest-gate (Mary).
- **Test pin:** `tests/integration/specialists/texas/test_ac_b_op_live_retrieval_evidence_present.py` — 1 test asserting evidence-Markdown block present in 3.6 Dev Agent Record + parses for 5 required M1-M5 sections + measurement values populated.

### AC-3.6-E — Marcus-envelope baseline capture per Decision #3 + W-R7-3.1

- **Given** post-3.6 Marcus envelope on first trial corpus run available per AC-A
- **When** the dev agent captures the envelope as frozen fixture at `tests/fixtures/marcus/baseline_envelope/2026-04-XX/`
- **Then**:
  1. Envelope serialized as canonical-JSON per 31-1 digest convention
  2. `BASELINE_METADATA.md` companion authored documenting: trial-id, corpus path, Marcus commit SHA at capture, capture timestamp, operator name, one-line "frozen baseline for Slab-4+ Marcus-output regression-detection per W-R7-3.1" purpose statement
  3. Resolves `3-6-marcus-envelope-baseline-capture-for-future-regression-detection` deferred-inventory entry filed at 3.1 (mark `RESOLVED-AT-3.6` in inventory)
- **Test pin:** `tests/integration/marcus/test_marcus_envelope_baseline_present.py` — 1 test asserting fixture + BASELINE_METADATA.md present + metadata fields populated.

### AC-3.6-F — 5-agent party-mode M3 acceptance verdict (mirror 2c.3 pattern per Decision #2)

- **Given** trial run + Texas reactivation + baseline capture all complete
- **When** the dev agent (or operator) convenes party-mode with prompt: "M3 acceptance verdict review for Slab 3 (Marcus Orchestration). Full evidence: trial run §01→§15 + DecisionCard emission per gate + operator verdict at each gate + at least one edit-verb propagation + Texas AC-B-OP M1-M5 evidence + Marcus-envelope baseline. Verdict (one of 6 enum tokens): GREEN-LIGHT / GREEN-WITH-RIDERS / CONDITIONAL-GREEN / YELLOW / RED / ABSTAIN. Each agent: verdict-token-on-its-own-line + reasoning + any riders. Roster fixed at 5 (Winston + Murat + Paige + Quinn-R + Amelia); do not add or substitute."
- **Then** each agent's response recorded **verbatim** in `_bmad-output/implementation-artifacts/slab-3-m3-acceptance-verdict.md` under `### <agent>` headers per 2c.3 pattern; consensus verdict line per 4-enum (consensus-level adds GREEN-WITH-RIDERS to {GREEN-LIGHT, CONDITIONAL-GREEN, YELLOW, RED}).
- **Test pin per Murat M-R2 inheritance from 2c.3:** `tests/migration/test_slab_3_m3_party_mode_5_agent_recording.py` — 1 test asserting (a) §"Party-Mode Verdict (5 agents)" section + 5 sub-headers; (b) each section contains `^Verdict: (GREEN-LIGHT|GREEN-WITH-RIDERS|CONDITIONAL-GREEN|YELLOW|RED|ABSTAIN)$`; (c) each sub-header section body ≥150 chars excluding verdict line; (d) consensus verdict line `^Consensus verdict: (GREEN-LIGHT|GREEN-WITH-RIDERS|CONDITIONAL-GREEN|YELLOW|RED)$`.

### AC-3.6-G — Invariant audit matrix Marcus + gates entries (FR63 incremental roll-up)

- **Given** invariant audit matrix file does NOT exist in repo (per 2c.3 A-R1 BLOCKER B1 RESOLVED-BY-DEFERRAL: matrix creation is Slab 5a scope)
- **When** 3.6 close runs
- **Then** produce `_bmad-output/implementation-artifacts/slab-3-marcus-invariant-stub.md` — entries for Marcus + each gate (G1, G2C, G3, G4) + OperatorVerdict + resume_api per Slab 5a absorption pattern (mirror `slab-2c-wondercraft-invariant-stub.md` from 2c.3)
- **Test pin:** `tests/migration/test_slab_3_marcus_invariant_stub.py` — 1 test asserting stub present + ≥6 entries (Marcus + 4 gates + OperatorVerdict).

### AC-3.6-H — Anti-pattern catalog harvest at SLAB CLOSE (per R6 + Paige A13 candidate)

- **Given** the catalog at 13-N entries post-2c.4 close
- **When** 3.6 close runs final Slab-3 harvest
- **Then**:
  1. Evaluate Paige's A13 candidate ("Premature live-wire AC against not-yet-ported substrate") per harvest-gate; if 3.x exhibited the pattern, ACCEPT or AUGMENT A9; else DEFER. Verdict recorded in 3.6 close notes (NOT preempted at story-author per Mary harvest-gate; same discipline as 2c.4 AC-C).
  2. Any A14+ candidates from 3.x dev work evaluated per harvest-gate.
  3. Catalog header updated with Slab 3 harvest-cycle complete annotation (mirror 2c.4 phrasing per Paige P-R3-2c.4).

### AC-3.6-I — `slab-3-retrospective.md` SLAB-CLOSING artifact (per `bmad-retrospective` skill)

- **Given** retrospective format precedent at `slab-2c-retrospective.md` (or `slab-2b-retrospective.md` if 2c not yet closed)
- **When** the dev agent authors `_bmad-output/implementation-artifacts/slab-3-retrospective.md` mirroring canonical 4-section structure
- **Then** the retrospective contains:
  - **§"Pre-Audit Bundle"** — sprint key + slab key + dates + storypoint roll-up (3.1=5 + 3.2=4 + 3.3=5 + 3.4=3 + 3.5=3 + 3.6=5 = **25pts** vs 6 stories) + commit anchors per story close
  - **§"Slab Outcomes"** — per-story outcome (BMAD-CLOSED + verdict); M3 verdict roll-up; cumulative anti-pattern harvest verdict; Texas reactivation verdict; Marcus baseline-capture verdict
  - **§"Next-Slab Preparation"** — **deferred-inventory consultation per CLAUDE.md §1 (BINDING)** with per-entry verdicts in format `<entry-id>: <RESOLVED|DEFERRED-CONTINUES|REACTIVATED-AT-SLAB-X|NOT-APPLICABLE>` + one-sentence justification (mirror 2c.4 D + M-R5+P-R1). Notable: `2a.4-followon-ac-b-op-live-retrieval` (RESOLVED-AT-3.6 per AC-D); `3-6-marcus-envelope-baseline-capture-for-future-regression-detection` (RESOLVED-AT-3.6 per AC-E); any 3.x-filed entries.
  - **§"Slab 4 Handoff"** — `slab-3-marcus-invariant-stub.md` is the Slab 5a invariant-audit-matrix-creation seed; M3 verdict-state; Cora dev-graph (Slab 4) opens; learning ledger (Slab 4) consumes 3.5's proto-events
- **Test pin:** `tests/migration/test_slab_3_retrospective_present.py` — 1 test asserting all 4 §-headers present + per-entry deferred-inventory verdicts (regex per 2c.4 D pattern) + ≥3 consulted entries.

### AC-3.6-J — TEMPLATE compliance (per R1–R14 v2.4)

R1, R6, R8 honored.

### AC-3.6-K — D12 close protocol (DUAL-gate; operator_acceptance_gate; FIVE-line per dual-gate convention)

1. **Invariant preservation:** Marcus SPOT (`get_facade()` is sole operator-facing surface); cold-start sanctum-read; HIL-paused (FR34 architectural enforcement); Marcus-first activation; specialist registry consumed via routing; Texas dispatch-contract substrate stable; D7 transport parity preserved.
2. **Anti-pattern harvest:** per AC-H (Paige A13 candidate evaluated; cycle-complete annotation landed).
3. **Migration-guide update:** §"Marcus Walkthrough" closed with M3 verdict-state; §"Gate Migration" deepened; `slab-3-retrospective.md` is the SLAB-CLOSING artifact.
4. **TEMPLATE compliance:** R1, R6, R8 honored. Numeric anchors: trial run §01→§15 ≤N hours; ≥1 edit verb exercised; Texas M1-M5 evidence; baseline capture; M3 verdict.
5. **Dual-gate gate-2 (operator acceptance):** operator confirms M3 verdict + reads `slab-3-m3-acceptance-verdict.md` party-mode verbatim + signs off on Marcus-orchestrates-end-to-end claim.

### AC-3.6-L — Sprint-status state-flips at filing AND at close

At filing: `migration-3-6-...: ready-for-dev`. At close: `migration-3-6-...: done`; `migration-epic-3-slab-3-marcus-orchestration: done` (with trailing comment if M3 conditional per 2c.4 AC-E enum-clarification pattern); Slab parent state updated likewise. `last_updated` field updated.

### AC-3.6-M — `next-session-start-here.md` update (per CLAUDE.md §closeout hygiene + §2)

Mirror 2c.4 AC-J. Active-slab transitions Slab 3 → Slab 4. Deferred-inventory status line reflects post-3.6 counts. M3 milestone status reflects verdict.

---

## File Structure Requirements

### NEW files (PERSISTENT)

```
_bmad-output/implementation-artifacts/
├── slab-3-m3-acceptance-verdict.md                # M3 verdict-recording artifact (AC-F)
├── slab-3-marcus-invariant-stub.md                # 2-row+ stub for Slab 5a absorption (AC-G)
└── slab-3-retrospective.md                        # SLAB-CLOSING retrospective (AC-I)

tests/fixtures/marcus/baseline_envelope/2026-04-XX/
├── envelope.json                                  # Frozen Marcus envelope (AC-E)
└── BASELINE_METADATA.md                           # Companion metadata (AC-E)

tests/integration/marcus/
├── test_edit_verb_propagation.py                  # 1 test (AC-B)
├── test_decision_card_emission_per_gate.py        # 4 tests parametrize → 1 K-floor (AC-C)
└── test_marcus_envelope_baseline_present.py       # 1 test (AC-E)

tests/integration/specialists/texas/
└── test_ac_b_op_live_retrieval_evidence_present.py # 1 test (AC-D)

tests/migration/
├── test_slab_3_m3_party_mode_5_agent_recording.py # 1 test (AC-F)
├── test_slab_3_marcus_invariant_stub.py           # 1 test (AC-G)
└── test_slab_3_retrospective_present.py           # 1 test (AC-I)
```

### MODIFIED files

- `docs/dev-guide/specialist-anti-patterns.md` — Slab 3 harvest-cycle complete annotation per AC-H; possibly +1 entry (A14 if 3.x-harvest yields one OR Paige A13 candidate ACCEPTED).
- `_bmad-output/planning-artifacts/deferred-inventory.md` — `2a.4-followon-ac-b-op-live-retrieval` marked RESOLVED-AT-3.6 per AC-D; `3-6-marcus-envelope-baseline-capture-for-future-regression-detection` marked RESOLVED-AT-3.6 per AC-E; new entries (if any) per AC-I §"Next-Slab Preparation" with per-entry verdicts.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-L.
- `next-session-start-here.md` — per AC-M.
- `docs/dev-guide/langgraph-migration-guide.md` — §"Marcus Walkthrough" + §"Gate Migration" closed for M3.

---

## Testing Requirements

**K-target ~1.4× (target 14 / floor 10).** Test count + K-floor:

| AC | Tests collected | Honest K-floor units |
|---|---|---|
| A | 0 (operator-driven E2E; evidence in Dev Agent Record) | **0** |
| B | 1 (edit-verb propagation) | **1** |
| C | 4 parametrize → 1 K-floor (4 gates same property) | **1** |
| D | 1 (Texas evidence-Markdown present + M1-M5 sections) | **1** |
| E | 1 (baseline fixture + metadata) | **1** |
| F | 1 (5-agent recording) | **1** |
| G | 1 (invariant stub) | **1** |
| H | 0 (harvest verdict in close notes; no test) | **0** |
| I | 1 (retrospective + per-entry verdicts) | **1** |
| **Total** | **10 collected** | **7 firm K-floor units** |

**Honest K-floor: 7** — under floor 10 minimum. **RIDER:** AC-D Texas M1-M5 evidence test parametrizes over 5 sections (M1/M2/M3/M4/M5) → +4 K-floor units (each section asserts a distinct evidence-property); AC-E baseline-capture adds `test_baseline_envelope_canonical_json_format` orthogonal property → +1; total honest K-floor: 12 (above floor 10). Within ~1.4× K-target band (14/10 = 1.4×; 12/10 = 1.2×). Confirms.

**Regression target at T8:** baseline + previous Slab 3 stories. +10 collected at file level. Import-linter contracts unchanged. Sandbox-AC PASS (Texas live evidence is operator-gated per 2a.4 binding; CLI subprocess + AST-grep + filesystem-presence all via shipped Python tooling).

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_

### Texas AC-B-OP Live Evidence (per AC-D — operator-paste landing zone)

_(Operator pastes here per AC-D after running `ac_b_op_texas_live_retrieval_evidence.py`)_

### Marcus-Envelope Baseline Capture (per AC-E)

_(Populated at T8 with capture timestamp + commit SHA + trial-id + canonical-JSON envelope path)_

### M3 Party-Mode Verdict (5 agents per AC-F)

_(Recorded verbatim under ### Winston / ### Murat / ### Paige / ### Quinn-R / ### Amelia headers in slab-3-m3-acceptance-verdict.md)_
