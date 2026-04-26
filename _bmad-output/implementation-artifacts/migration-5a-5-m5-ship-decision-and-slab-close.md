# Migration Story 5a.5: M5 Ship Decision + Party-Mode Green-Light (SLAB CLOSING; THE MIGRATION SHIP GATE)

**Status:** ready-for-dev
**Sprint key:** `migration-5a-5-m5-ship-decision-and-slab-close`
**Epic:** Slab 5a — **M5 GO/NO-GO GATE "Migration ships"** — **SLAB CLOSING + THE central migration acceptance gate**.
**Pts:** 2 | **Gate:** dual (per governance JSON `5a-5.expected_gate_mode = "dual-gate"`, rationale: `operator_acceptance_gate`). **K-target:** ~1.2× (target 6 / floor 5).

**Predecessor:** Stories 5a.1 + 5a.2 + 5a.3 + 5a.4 done.

**Inheritance bindings (HARD; M5 verdict path resolves all):**
- **M2 conditional-resolution** if 2c.4 closed CLOSED-WITH-CONDITIONAL-M2 (operator addendum landed before M5 verdict, OR M5 verdict accepts unresolved-conditional state with explicit rider).
- **M3 conditional-resolution** if 3.6 closed CLOSED-WITH-CONDITIONAL-M3 (Texas AC-B-OP live evidence landed OR Marcus-envelope baseline gap resolved).
- **M4 conditional-resolution** if 4.7 closed CLOSED-WITH-CONDITIONAL-M4.
- **`slab-3-m5-dispatch-registry-swap`** deferred-inventory entry (referenced from 4.5; 5a.5 verifies the swap status; if pending, RECORD as M5 condition or RESOLVE pre-verdict).
- **15-invariant audit matrix** at 5a.4 close-state.
- **Anti-patterns catalog** FR64 final per 5a.4.
- **Economics ≥50% reduction** per 5a.3.
- **Head-to-head parity verdict** per 5a.2.
- **Trial-replay regression** per 5a.1.

---

## T1 Readiness Block

1. Governance: `5a-5.expected_gate_mode = "dual-gate"` (operator_acceptance_gate).
2. **Predecessor close evidence:** 5a.1 + 5a.2 + 5a.3 + 5a.4 ALL `done` per sprint-status.yaml. Verify pre-T1 proceed.
3. **5a.2 parity verdict** at `_bmad-output/implementation-artifacts/5a-2-parity-verdict.md`.
4. **5a.3 economics report** at `_bmad-output/economics-baselines/<latest>.json` + reduction percentage ≥50%.
5. **5a.4 invariant matrix** at `_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md` + anti-patterns catalog FR64-final state.
6. **5a.1 replay regression** GREEN per CI nightly run within 7 days of 5a.5 open.
7. **Conditional-state inheritance:** verify M2 + M3 + M4 verdict states from sprint-status.yaml; if any CONDITIONAL, the M5 verdict path inherits the condition or resolves pre-vote.
8. **6-agent party-mode roster** (epic 5a.5 binding): Winston + Murat + Paige + Quinn-R + Amelia + **Dr. Quinn for strategic framing** (NEW; expansion from 5-agent pattern at 2c.3+3.6+4.7 — Dr. Quinn carries strategic-framing voice for the migration's central go/no-go gate).
9. **FR60/FR61/FR62** — backport channel closed (FR60); forward-port playbook (FR61); rollback plan (FR62).
10. Severance posture (frozen primary reference at upstream/master @ 3ed7c56).

### TEMPLATE scope decisions

**Decision #1 — Bounded scope:** (a) 6-agent party-mode (mirror 2c.3+3.6+4.7 5-agent pattern + add Dr. Quinn strategic voice per epic 5a.5 binding); (b) Ship/Iterate/Rollback verdict at `_bmad-output/implementation-artifacts/m5-decision.md`; (c) per-agent verbatim recording; (d) per-verdict-path operational consequence (Ship → forward-port playbook FR61 + frozen-reference primary; Iterate → remediation stories open as Slab 5a extensions; Rollback → FR62 plan activates); (e) D12 close protocol; (f) Slab 5a retrospective (mirror 2c+3+4 retrospective format); (g) `next-session-start-here.md` update + final session-close hygiene. NOT in scope: 5b polish stories (separate epic; defer per PRD MVP table).

**Decision #2 — 6-agent party-mode prompt template:** "M5 ship/iterate/rollback verdict review for migration LangChain/LangGraph (Slabs 1-5a complete). Full evidence: 5a.1 trial-replay regression + 5a.2 head-to-head parity verdict + 5a.3 economics ≥50% reduction + 5a.4 15-invariant audit matrix + FR64 catalog final. Inherited conditional states: M2={GREEN-LIGHT|CONDITIONAL}; M3={GREEN-LIGHT|CONDITIONAL}; M4={GREEN-LIGHT|CONDITIONAL}. Verdict (one of 6 per-agent enum): SHIP / ITERATE / ROLLBACK / SHIP-WITH-RIDERS / SHIP-CONDITIONAL / ABSTAIN. Roster fixed at 6 (Winston + Murat + Paige + Quinn-R + Amelia + Dr. Quinn for strategic framing); do not substitute."

**Decision #3 — Verdict-path operational consequences (per epic 5a.5 + FR60/FR61/FR62):**
- **SHIP:** backport channel remains closed (FR60); forward-port from primary starts per FR61 playbook; primary repo marked frozen-reference; Slab 5b polish stories may open per PRD MVP cuttable table.
- **ITERATE:** operator names specific findings; remediation stories open as Slab 5a extensions; M5 target date renamed; Slab 5b may defer.
- **ROLLBACK:** operator names rollback reason; FR62 rollback plan activates; migration clone archived; primary repo continues production; learnings captured in retrospective.
- **SHIP-WITH-RIDERS:** SHIP path + named riders tracked as immediate-post-ship work.
- **SHIP-CONDITIONAL:** SHIP path conditional on resolution of inherited M2/M3/M4 conditions within named window (e.g., 7 days); if window lapses, ship-state demotes to ITERATE.

**Decision #4 — Slab 5a retrospective format mirrors slab-4-retrospective.md** (which mirrors slab-3 + slab-2c) — 4 §-headers (Pre-Audit Bundle / Slab Outcomes / Next-Slab Preparation / Slab 5b Handoff [optional if cuttable]).

---

## Story

As an **operator making the ship/iterate/rollback decision at M5 — THE central migration acceptance gate**,
I want **6-agent party-mode (Winston + Murat + Paige + Quinn-R + Amelia + Dr. Quinn for strategic framing) convening with full Slab-5a evidence + documented Ship/Iterate/Rollback verdict at `m5-decision.md` + per-verdict-path operational consequence per FR60/FR61/FR62 + Slab 5a retrospective + final D12 close**,
So that **the migration's central go/no-go gate has a defensible decision record, FR60/FR61/FR62 paths activate per verdict, and the migration ships, iterates, or rolls back with full operator agency and evidence**.

---

## Acceptance Criteria

### AC-5a.5-A — 6-agent party-mode convene + verdict (Decision #2; THE M5 ship gate)

- **Given** all Slab-5a evidence assembled (5a.1 + 5a.2 + 5a.3 + 5a.4 close-states verified at T1)
- **When** dev (or operator) convenes 6-agent party-mode with Decision #2 prompt
- **Then** each agent's verbatim verdict recorded at `_bmad-output/implementation-artifacts/m5-decision.md` under `### Winston`, `### Murat`, `### Paige`, `### Quinn-R`, `### Amelia`, `### Dr. Quinn` headers; per-agent 6-enum {SHIP / ITERATE / ROLLBACK / SHIP-WITH-RIDERS / SHIP-CONDITIONAL / ABSTAIN}; consensus verdict (5-enum, ABSTAIN excluded from consensus) recorded at top.
- **Test pin (DUAL-GATE acceptance gate-1):** `tests/migration/test_m5_party_mode_6_agent_recording.py` — 1 test asserting (a) 6 sub-headers present; (b) each section has `^Verdict: (SHIP|ITERATE|ROLLBACK|SHIP-WITH-RIDERS|SHIP-CONDITIONAL|ABSTAIN)$` line; (c) each section body ≥150 chars excluding verdict line; (d) consensus verdict line `^Consensus verdict: (SHIP|ITERATE|ROLLBACK|SHIP-WITH-RIDERS|SHIP-CONDITIONAL)$`.

### AC-5a.5-B — Per-verdict-path operational consequence per Decision #3 + FR60/FR61/FR62

- **Given** verdict per AC-A
- **When** operator executes per-verdict-path consequence:
  - SHIP → forward-port playbook activates; primary frozen-reference marker added at `_bmad-output/upstream-state.md` or equivalent
  - ITERATE → operator names ≥1 finding; remediation stories filed in sprint-status as `migration-5a-5-iter-<n>-...`
  - ROLLBACK → FR62 rollback plan executes; migration clone archived
  - SHIP-WITH-RIDERS → riders tracked at `_bmad-output/implementation-artifacts/m5-ship-riders.md`
  - SHIP-CONDITIONAL → window stated explicitly; auto-files `5a-5-m5-conditional-window-<expiry>` deferred-inventory entry
- **Test pin:** `tests/migration/test_m5_verdict_consequence_path.py` — 1 test asserting verdict line in m5-decision.md + matching consequence-artifact present per the 5 verdict enum cases (parametrize-collapsible to 1 K-floor).

### AC-5a.5-C — Inherited M2/M3/M4 conditional-state resolution

- **Given** M2 / M3 / M4 verdict states from sprint-status.yaml (any may be CONDITIONAL per 2c.4 + 3.6 + 4.7 hard-gate inheritance patterns)
- **When** 5a.5 dev reads inherited states at T1
- **Then** each conditional state is EITHER (a) RESOLVED pre-M5-vote (operator addendum landed) OR (b) explicitly carried forward into M5 verdict path (e.g., SHIP-CONDITIONAL with named M2-condition window) OR (c) escalated to BLOCK M5-vote (operator decides before convene).
- **Test pin:** `tests/migration/test_m5_inherited_conditional_resolved.py` — 1 test asserting m5-decision.md §"Inherited Conditional States" section enumerates each prior M-state + resolution-path.

### AC-5a.5-D — `slab-5a-retrospective.md` SLAB-CLOSING artifact (per Decision #4)

- **Given** retrospective format precedent at `slab-4-retrospective.md` (which mirrors 3 + 2c)
- **When** dev authors `_bmad-output/implementation-artifacts/slab-5a-retrospective.md` with 4 §-headers per Decision #4
- **Then** §"Next-Slab Preparation" lists ≥3 consulted deferred-inventory entries with per-entry verdicts per 2c.4 M-R5+P-R1 inheritance + 3.6+4.7 patterns; §"Slab 5b Handoff" notes whether 5b polish stories open (per Ship verdict) or defer (per Iterate/Rollback).
- **Test pin:** `tests/migration/test_slab_5a_retrospective_present.py` — 1 test asserting 4 §-headers + per-entry deferred-inventory verdict regex per 2c.4 pattern.

### AC-5a.5-E — Anti-pattern catalog harvest cycle complete + final-final annotation

- **Given** catalog at FR64-final state per 5a.4 close
- **When** 5a.5 close runs final cycle annotation
- **Then** catalog header gains `"MIGRATION COMPLETE — Slab 1+2+3+4+5a harvest cycles all complete; format-freeze v1 preserved through ship; post-ship harvest continues under same freeze unless format-version bump."` annotation.
- **Test pin:** absorbed in 5a.4 AC-C (no new test).

### AC-5a.5-F — TEMPLATE compliance (R1-R14 v2.4 honored where applicable for migration-close)

R1, R6, R8 honored. **MIGRATION COMPLETE annotation:** TEMPLATE doc gains close-of-migration note ("Slab 1-5a complete YYYY-MM-DD per M5 verdict; v2.4 R1-R14 carried through ship; future migration extensions follow this TEMPLATE per PRD §Future Work").

### AC-5a.5-G — D12 close protocol (DUAL-gate; operator_acceptance_gate; FIVE-line per dual-gate convention)

1. **Invariant preservation:** all 15 invariants preservation status (PRESERVED / DEFERRED-WITH-NAMED-FOLLOWUP / VIOLATED-WITH-RIDER) per 5a.4 matrix; M5 verdict resolves all.
2. **Anti-pattern harvest:** per AC-E migration-complete annotation.
3. **Migration-guide update:** §"M5 Ship Decision" added with verdict + verdict-path operational record; cross-references to m5-decision.md.
4. **TEMPLATE compliance:** R1, R6, R8 honored. Migration-complete annotation per AC-F.
5. **Dual-gate gate-2 (operator acceptance gate):** operator confirms M5 verdict + reads 6-agent verbatim record + signs off on per-verdict-path operational consequence per Decision #3.

### AC-5a.5-H — Sprint-status state-flips at filing AND close

At filing: `migration-5a-5-...: ready-for-dev`. At close: `migration-5a-5-...: done`; `migration-epic-5a-acceptance: done` (with trailing comment naming verdict per 2c.4 AC-E enum-clarification pattern); **`migration-master-status: shipped` OR `migration-master-status: iterate-pending` OR `migration-master-status: rolled-back`** per verdict (NEW top-level migration-status enum at sprint-status.yaml; defined in this story).

### AC-5a.5-I — `next-session-start-here.md` final update + session-close hygiene

Mirror 2c.4 AC-J + 3.6 AC-M + 4.7 AC-I patterns. Per-verdict:
- SHIP → next session opens forward-port from primary playbook OR Slab 5b polish stories
- ITERATE → next session opens remediation stories per AC-B operator-named findings
- ROLLBACK → FR62 plan executes; next session is migration-archive + primary-resumption hand-off

---

## File Structure Requirements

### NEW files (per verdict)

- `_bmad-output/implementation-artifacts/m5-decision.md` (ALWAYS)
- `_bmad-output/implementation-artifacts/slab-5a-retrospective.md` (ALWAYS)
- `_bmad-output/implementation-artifacts/m5-ship-riders.md` (CONDITIONAL on SHIP-WITH-RIDERS verdict)
- `_bmad-output/upstream-state.md` (CONDITIONAL on SHIP / SHIP-WITH-RIDERS / SHIP-CONDITIONAL verdict — primary frozen-reference marker)
- `tests/migration/{test_m5_party_mode_6_agent_recording, test_m5_verdict_consequence_path, test_m5_inherited_conditional_resolved, test_slab_5a_retrospective_present}.py`

### MODIFIED files

- `docs/dev-guide/specialist-anti-patterns.md` — migration-complete annotation per AC-E.
- `docs/dev-guide/specialist-migration-template.md` — migration-complete annotation per AC-F.
- `docs/dev-guide/langgraph-migration-guide.md` — §"M5 Ship Decision" added per AC-G §3.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-H + NEW `migration-master-status` top-level enum.
- `next-session-start-here.md` — per AC-I per verdict-path.
- `_bmad-output/planning-artifacts/deferred-inventory.md` — per-entry verdicts per AC-D + auto-file per SHIP-CONDITIONAL window.

---

## Testing Requirements

**K-target ~1.2× (target 6 / floor 5).** AC-A:1 + AC-B:1 + AC-C:1 + AC-D:1 = **4 K-floor**. RIDER: AC-A consensus-line strict-format pin → +1; AC-D §"Slab 5b Handoff" present-or-explicitly-deferred orthogonal pin → +1 = **honest 6 K-floor (meets target)**. Within band.

Sandbox-AC PASS (no live API; all assertions filesystem + structural).

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_

### M5 Party-Mode Verdict (6 agents per AC-A)

_(Recorded verbatim under ### Winston / ### Murat / ### Paige / ### Quinn-R / ### Amelia / ### Dr. Quinn headers in m5-decision.md)_

### Per-Verdict-Path Consequence Execution (per AC-B)

_(Operator records the consequence-path activation per Decision #3 — SHIP/ITERATE/ROLLBACK/SHIP-WITH-RIDERS/SHIP-CONDITIONAL)_

### Inherited M2/M3/M4 Conditional Resolution (per AC-C)

_(Per-prior-M-state resolution path recorded)_
