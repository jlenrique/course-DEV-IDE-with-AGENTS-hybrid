# Migration Story 4.7: Pydantic + RetryPolicy Workaround + Slab 4 Close (SLAB CLOSING)

**Status:** ready-for-dev
**Sprint key:** `migration-4-7-pydantic-retry-policy-and-slab-4-close`
**Epic:** Slab 4 — M4 gate. **SLAB CLOSING.**
**Pts:** 3 | **Gate:** single (per governance JSON `4-7.expected_gate_mode = "single-gate"`, rationale: null). **K-target:** ~1.3× (target 10 / floor 8).

**Predecessor:** Stories 4.1-4.6 done. M4 close-gate.

---

## T1 Readiness Block

1. Governance: `4-7.expected_gate_mode = "single-gate"`.
2. **Substrate: `app/runtime/retry_policy.py`** — verify Slab-1 stub state OR fully absent.
3. **PRD §Implementation Considerations** — Pydantic + LangGraph RetryPolicy interaction gotcha; verify the documented gotcha description.
4. **`docs/dev-guide/langgraph-state-idioms.md` §6** — placeholder per Slab-1 substrate; 4.7 finalizes.
5. **M4 Required Evidence** — party-mode convening Winston + Murat + Paige + Quinn-R + Amelia (5-agent per 2c.3 + 3.6 pattern); evidence from 4.1-4.6.
6. **D12 close protocol per CLAUDE.md** — three-line per epic 4.7; SLAB CLOSING.
7. Severance posture.

### Substrate sweep

- `app/runtime/` exists per Slab-1.
- `docs/dev-guide/langgraph-state-idioms.md` §6 placeholder.
- 4.1-4.6 close-states verified at T1 (sprint-status all done).
- Anti-patterns catalog post-Slab-3 close state.

### TEMPLATE scope decisions

**Decision #1 — Bounded scope:** (a) `app/runtime/retry_policy.py` workaround impl per PRD gotcha; (b) `tests/integration/runtime/test_retry_policy_pydantic.py` demonstrating workaround; (c) `langgraph-state-idioms.md §6` finalized; (d) M4 5-agent party-mode + verdict at `slab-4-m4-acceptance-verdict.md` (mirror 2c.3 + 3.6 verdict-recording); (e) `slab-4-retrospective.md` SLAB-CLOSING artifact (mirror 2c + 3 retrospective format); (f) D12 close protocol; (g) `next-session-start-here.md` update; (h) anti-patterns harvest cycle complete annotation. NOT in scope: Slab 5a stories.

**Decision #2 — Workaround pattern (per PRD gotcha — verify exact text at T1):** Pydantic v2 models passed through LangGraph RetryPolicy may lose validation context across retries; workaround likely involves explicit re-validation OR retry-policy state-shape pin. T1 reads PRD §Implementation Considerations + langgraph-state-idioms.md §6 placeholder for the specific gotcha description.

**Decision #3 — M4 verdict format mirrors 2c.3 + 3.6:** 4-enum consensus level (GREEN-LIGHT / GREEN-WITH-RIDERS / CONDITIONAL-GREEN / YELLOW / RED); 6-enum per-agent (adds ABSTAIN). Verbatim recording per 2c.3 P-R1 + 3.6 W-R1 binding.

**Decision #4 — Slab 4 retrospective format mirrors slab-3-retrospective.md** (which mirrors slab-2c-retrospective.md per 3.6 spec) — 4 §-headers (Pre-Audit Bundle / Slab Outcomes / Next-Slab Preparation / Slab 5a Handoff).

---

## Story

As a **dev agent closing Slab 4 SLAB-CLOSING**,
I want **Pydantic + LangGraph RetryPolicy workaround implemented + tested + langgraph-state-idioms.md §6 finalized + 5-agent party-mode M4 verdict recorded + slab-4-retrospective.md authored + D12 close protocol satisfied + next-session-start-here.md updated**,
So that **Slab 5a inherits a stable substrate for replay + parity work and M4 milestone closes per "Governance regime is architectural"**.

---

## Acceptance Criteria

### AC-4.7-A — `app/runtime/retry_policy.py` workaround impl

- **Given** PRD §Implementation Considerations describes the Pydantic + RetryPolicy gotcha (read at T1 for exact text)
- **When** dev authors workaround at `app/runtime/retry_policy.py`
- **Then** workaround is testable + documented in inline docstring
- **Test pin:** `tests/integration/runtime/test_retry_policy_pydantic.py` — 2 tests: (a) without-workaround → demonstrates failure mode; (b) with-workaround → succeeds.

### AC-4.7-B — `langgraph-state-idioms.md §6` finalized

- **Given** §6 is placeholder
- **When** dev authors final content describing workaround + worked example
- **Then** §6 word-count ≥200 + ≥1 worked code example block
- **Test pin:** `tests/migration/test_langgraph_state_idioms_section_6_final.py` — 1 test asserting §6 present + ≥200 words + ≥1 code block + no `<!-- TODO -->` markers.

### AC-4.7-C — M4 5-agent party-mode verdict (mirror 2c.3 + 3.6)

- **Given** 4.1-4.6 close-evidence + party-mode roster pinned (Winston + Murat + Paige + Quinn-R + Amelia)
- **When** the dev agent (or operator) convenes party-mode with prompt: "M4 acceptance verdict review for Slab 4 (Lockstep + Gates + Cora + Ledger + Frozen-Graph). Full evidence: 4.1 graph-compile CI hook + 4.2 Cora dev-graph + 4.3 party-mode-as-interrupt + 4.4 learning ledger + 4.5 frozen-graph ceremony + 4.6 sanctum invalidation hook. Verdict (one of 6 enum tokens): GREEN-LIGHT / GREEN-WITH-RIDERS / CONDITIONAL-GREEN / YELLOW / RED / ABSTAIN. Each agent: verdict-token-on-its-own-line + reasoning + any riders. Roster fixed at 5; do not substitute."
- **Then** verbatim verdict recorded at `_bmad-output/implementation-artifacts/slab-4-m4-acceptance-verdict.md` mirroring 2c.3 + 3.6 format
- **Test pin:** `tests/migration/test_slab_4_m4_party_mode_5_agent_recording.py` — 1 test (mirror 3.6 AC-F structural assertion).

### AC-4.7-D — `slab-4-retrospective.md` SLAB-CLOSING artifact (mirror 3 + 2c precedent)

- **Given** retrospective format precedent at `slab-3-retrospective.md` (which mirrors `slab-2c-retrospective.md`)
- **When** dev authors `_bmad-output/implementation-artifacts/slab-4-retrospective.md` with 4 §-headers per Decision #4
- **Then** §"Next-Slab Preparation" lists ≥3 consulted deferred-inventory entries with per-entry verdicts (mirror 2c.4 M-R5+P-R1 binding + 3.6 AC-I)
- **Test pin:** `tests/migration/test_slab_4_retrospective_present.py` — 1 test asserting 4 §-headers + per-entry verdict regex per 2c.4 pattern.

### AC-4.7-E — Anti-pattern catalog harvest at SLAB CLOSE (per R6 + 2c.4 / 3.6 cycle-complete pattern)

- **Given** catalog at A1-A14+ post-3.6
- **When** 4.7 close runs final Slab-4 harvest (NOT preempted at story-author per Mary harvest-gate)
- **Then** harvest verdicts recorded in 4.7 close notes; harvest-cycle complete annotation added to catalog header per 2c.4 P-R3 / 3.6 AC-H pattern
- **Test pin:** `tests/migration/test_slab_4_anti_patterns_cycle_complete.py` — 1 test asserting catalog header contains "Slab 4 harvest cycle complete" annotation + entry count ≥ post-3.6 baseline.

### AC-4.7-F — TEMPLATE compliance

R1, R6, R8 honored.

### AC-4.7-G — D12 close protocol (single-gate; SLAB CLOSING; FOUR-line per A-R7; verified against 2c.4 + 3.6 precedent)

1. **Invariant preservation:** invariant #3 (deterministic neck — manifest CI from 4.1) + #5 (learning events from 4.4) + #9 (ledger side-effect from 4.4) + #15 (lane separation via Cora compilation from 4.2) preserved.
2. **Anti-pattern harvest:** per AC-E.
3. **Migration-guide update:** §6 (Lockstep CI from 4.1) + §7 (Frozen-Graph Ceremony from 4.5) deepened.
4. **TEMPLATE compliance:** R1, R6, R8 honored.

### AC-4.7-H — Sprint-status state-flips

At close: `migration-4-7-...: done`; `migration-epic-4-slab-4-lockstep-gates-cora-ledger: done` (with trailing comment if M4 conditional per 2c.4 AC-E enum-clarification pattern).

### AC-4.7-I — `next-session-start-here.md` update (per CLAUDE.md §closeout hygiene + §2)

Mirror 2c.4 AC-J + 3.6 AC-M. Active-slab transitions Slab 4 → Slab 5a. Deferred-inventory status line reflects post-4.7 counts. M4 milestone status reflects verdict.

---

## File Structure Requirements

### NEW files

- `app/runtime/retry_policy.py`
- `_bmad-output/implementation-artifacts/{slab-4-m4-acceptance-verdict, slab-4-retrospective}.md`
- `tests/integration/runtime/test_retry_policy_pydantic.py`
- `tests/migration/{test_langgraph_state_idioms_section_6_final, test_slab_4_m4_party_mode_5_agent_recording, test_slab_4_retrospective_present, test_slab_4_anti_patterns_cycle_complete}.py`

### MODIFIED files

- `docs/dev-guide/langgraph-state-idioms.md` — §6 finalized per AC-B.
- `docs/dev-guide/specialist-anti-patterns.md` — Slab 4 harvest-cycle complete annotation per AC-E.
- `_bmad-output/planning-artifacts/deferred-inventory.md` — per-entry verdicts per AC-D §Next-Slab Preparation.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-H.
- `next-session-start-here.md` — per AC-I.

---

## Testing Requirements

**K-target ~1.3× (target 10 / floor 8).** AC-A:2 + AC-B:1 + AC-C:1 + AC-D:1 + AC-E:1 = **6 K-floor**. RIDER: AC-A adds `test_workaround_documented_in_docstring` (orthogonal property) + AC-D adds `test_retrospective_handoff_section_present` (orthogonal §-header check) = **honest 8 K-floor**. Within band.

Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
