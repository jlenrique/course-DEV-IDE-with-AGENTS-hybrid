# Story: Evidence-Bolster Control Surface (Research Knob Wiring)

**Status:** ready-for-dev (green-lit 2026-04-22 — D5/D6 + riders applied below)
**Created:** 2026-04-22
**Epic:** Sprint #1 standalone story (Research-capability operator control — likely future Epic 35+ "Research Knobs & Profiles")
**Sprint key:** `evidence-bolster-control-surface`
**Sprint:** Sprint #1 (3 of 5 — opens position 3 per D7 sequencing)
**Points:** **2 pts firm** (ratified at green-light: one bool + three-seam wiring + hard-fail credential check)
**Depends on:** 27-2 (done — scite cross-val partner); 27-2.5 (ready-for-dev — Consensus cross-val partner); Irene retrieval-intake (sibling Sprint #1 story — provides the `evidence_bolster_active` flag's intake destination). Implicit dependency on 28-2 Tracy three-modes (done — corroborate posture is the knob's dispatch target).
**Blocks:** Trial #2 execution (trial #2 requires this knob working for research-capability activation per operator 2026-04-22 lock).

## TL;DR

- **What:** Wire the operator-facing **evidence-bolster** knob into run-constants + Marcus dispatch + Tracy's corroborate posture. When active: Tracy's corroborate dispatch emits `RetrievalIntent` with `cross_validate: true` + `provider_hints: [{provider: "scite"}, {provider: "consensus"}]`, and Irene Pass 2 intake (sibling story) surfaces `convergence_signal`-framed narration. When inactive: corroborate dispatch runs single-provider (historical behavior).
- **Why:** Operator lock 2026-04-22: trial #2 research capability = **evidence-bolster only** (NOT aspirational enrichment, NOT derivative-artifact gap-filling). That lock needs a concrete runtime knob — a binary flag the operator sets in `run-constants.yaml` (or equivalent) BEFORE trial #2 opens, which propagates through Marcus → Tracy → Irene Pass 2 intake deterministically.
- **Novelty:** Small. The knob is ONE bool. But the wiring touches **three seams** (run-constants schema → Marcus run-setup dispatch → Tracy posture invocation → Irene intake flag surfaces), and each seam's contract must be pinned for the knob to survive reshape pressure.
- **Size:** 2–3 pts (scope-bounded at green-light). Low floor = "bool flag + schema validation + propagation test"; high floor = "flag + schema + per-seam tests + operator docs + default-state policy documented".

## Background — Why This Story Exists

**Operator memory (2026-04-18 user memory: `project_enrichment_vs_gap_filling_control.md`):** THREE distinct parameters conflated historically — (a) aspirational enrichment (depth beyond SME), (b) derivative-artifact gap-filling (quiz/handout content not in SME), (c) **evidence-bolster** (corroboration of existing claims via cross-validation). The operator 2026-04-22 lock chose: **evidence-bolster only for trial #2**, defer enrichment + gap-filling.

**Why only evidence-bolster for trial #2:** lowest risk / highest signal. It augments existing narration with corroborating sources — doesn't invent new claims (that's enrichment), doesn't generate derivative artifacts (that's gap-filling). The narration stays SME-driven; retrieval makes it cite + cross-validate.

**Why a runtime knob vs a deploy-time flag:** the operator wants to toggle evidence-bolster per-run without code change — one trial with it, one without it, to A/B the narration quality. A `.env` flag would be too session-sticky. A CLI flag would require Marcus command-line surface expansion. Run-constants YAML is the established per-run config pattern (existing PR-RC capability validates it).

**Why a single flag not a dial:** dials are for continuous parameters (depth, tone, pace). Evidence-bolster is binary: cross-validate scite+Consensus or not. Adding a dial here would be YAGNI until trial #2 data shows we need gradations.

## Story

As the **HIL operator preparing trial #2**,
I want **a single `evidence_bolster: true | false` run-constant that, when true, flips Tracy's corroborate posture into cross-validated (scite+Consensus DOI-merge + convergence-signal) mode AND surfaces the flag to Irene's retrieval-intake so convergence-aware narration framing activates, and when false, preserves the historical single-provider corroborate behavior**,
So that **trial #2 executes the operator's locked research-capability scope deterministically, AND future trials can toggle the knob per-run to A/B the effect on narration quality without code change, AND the 3-parameter conflation risk (enrichment vs gap-fill vs evidence-bolster) is eliminated by making the ONE sanctioned knob obvious + the other two explicitly deferred + documented**.

## Acceptance Criteria (spine level — expand at green-light)

### Behavioral (AC-B.*)

1. **AC-B.1 — Run-constants schema extended.** `state/config/run-constants.yaml` (or wherever PR-RC writes; confirm at green-light) gains new optional key `evidence_bolster: bool` with default `false`. Pydantic schema updated to include this field; `emit_preflight_receipt.py` validator honors it.
2. **AC-B.2 — Marcus propagation.** Marcus reads `run_constants.evidence_bolster` at trial open; surfaces it in the `DispatchEnvelope` (if PR-R lands first) OR in the ad-hoc Tracy-dispatch payload (if PR-R lands after) when invoking Tracy's corroborate posture.
3. **AC-B.3 — Tracy corroborate posture branches on flag.** When `evidence_bolster: true`, `tracy.corroborate()` constructs a `RetrievalIntent` with:
   - `cross_validate: true`
   - `provider_hints: [{provider: "scite"}, {provider: "consensus"}]`
   - Acceptance criteria merges scite-honored + Consensus-honored keys (no-op for the providers that don't honor a given key; logged to `refinement_log` per 27-0 discipline).
   
   When `evidence_bolster: false`, posture emits the single-provider intent shape (historical behavior; default scite).
4. **AC-B.4 — Irene retrieval-intake receives the flag.** `IreneRetrievalIntake.evidence_bolster_active` (sibling-story field) is populated from `run_constants.evidence_bolster` at Pass 2 cluster entry. Intake logic branches on it: true → cross-validated convergence language; false → single-provider "per scite.ai" language. **Coordination with sibling story: field name + enum values + propagation path aligned at green-light.**
5. **AC-B.5 — Operator-facing documentation.** `docs/operations-context.md` OR a dedicated `docs/research-knobs-guide.md` (decide at green-light) documents:
   - The 3-parameter distinction (enrichment / gap-fill / evidence-bolster) clearly.
   - What evidence-bolster does (binary cross-val toggle).
   - When to set it `true` (trial #2 locked scope).
   - What it does NOT do (enrichment, gap-filling — explicitly out of scope).
   - How to set it in run-constants YAML.
6. **AC-B.6 — Default-state policy.** Default is `false` (opt-in). Flag explicitly logged at trial-open (grep-able line: `evidence_bolster: true | false`). Operator can't miss that it's active/inactive.

### Test (AC-T.*)

1. **AC-T.1 — Run-constants schema-pin test.** Flag present, default false, Pydantic round-trip preserves value (parametrized true/false/absent).
2. **AC-T.2 — Marcus propagation test.** Fixture run-constants with `evidence_bolster: true` → Marcus dispatch of Tracy corroborate carries the flag through envelope/payload.
3. **AC-T.3 — Tracy corroborate branching test.** Flag true → `RetrievalIntent.cross_validate == true` AND `provider_hints` has both scite + Consensus. Flag false → single-provider intent.
4. **AC-T.4 — Irene intake flag wiring test.** `IreneRetrievalIntake.evidence_bolster_active` receives flag correctly from run-constants → narration framing branches. (Cross-references sibling story's AC-T.4; may be shared test.)
5. **AC-T.5 — Default-state regression test.** Flag absent → defaults false → historical single-provider behavior preserved (no surprise cross-val on trial #2's predecessor runs).
6. **AC-T.6 — Operator-doc-parity test.** `docs/*-guide.md` evidence-bolster section references schema field name correctly (drift check; mirrors lockstep-lite pattern).
7. **AC-T.7 — Suite regression floor** (TBD at green-light, estimate ≥8 collecting).

### Contract Pinning (AC-C.*)

1. **AC-C.1 — Binary flag, not dial.** `evidence_bolster: bool`. Closed shape; no gradations in v1. Future "bolster_depth: int" if trial data justifies.
2. **AC-C.2 — Default-false, opt-in.** Existing run-constants without the field validate cleanly; historical trial semantics unchanged.
3. **AC-C.3 — Run-constants schema location inherits PR-RC.** `state/config/run-constants.yaml` is the source; `scripts.marcus_capabilities.pr_rc` validates.
4. **AC-C.4 — No enrichment / gap-filling knobs wired here.** Those remain deferred per operator lock. If a future contributor tries to add `enrichment_depth` / `gap_fill_mode` alongside, the story doc explicitly forbids it (flagged in operator docs AC-B.5).
5. **AC-C.5 — Flag logged at trial-open.** Grep-able `INFO` log line showing current value. Operator cannot miss state.
6. **AC-C.6 — No LLM-in-the-loop for flag handling.** Pure boolean check; deterministic branching.

## File Impact (estimated — scope-bounded at green-light)

| File | Change | Lines (est.) |
|------|--------|-------|
| `state/config/schemas/run-constants.schema.json` OR `skills/bmad-agent-marcus/capabilities/schemas/pr_rc.yaml` | Touch — additive `evidence_bolster: bool = false` field | +15 |
| `scripts/marcus_capabilities/pr_rc.py` | Touch — flag read + log | +10 |
| `skills/bmad_agent_tracy/scripts/...` (corroborate posture module — confirm path at green-light) | Touch — branch on flag; construct cross-val intent vs single-provider | +30 |
| `marcus/orchestrator/...` OR wherever Marcus dispatches Tracy | Touch — propagate flag in dispatch | +20 |
| `state/config/schemas/irene-retrieval-intake.schema.json` (coordination with sibling story) | Touch — `evidence_bolster_active` field (may already be added by sibling) | +5 |
| `docs/operations-context.md` OR new `docs/research-knobs-guide.md` | Touch / New — operator-facing documentation | +80 / +150 |
| `tests/marcus_capabilities/test_pr_rc_evidence_bolster.py` | New — AC-T.1 + AC-T.2 | +80 |
| `tests/tracy/test_corroborate_evidence_bolster_branching.py` | New — AC-T.3 | +60 |
| `tests/irene/test_retrieval_intake_evidence_bolster.py` | New — AC-T.4 | +50 |
| `tests/contracts/test_evidence_bolster_doc_parity.py` | New — AC-T.6 | +40 |

**No changes to:** retrieval dispatcher code path (already supports cross-val from 27-0); Tracy's other postures (embellish / gap_fill stay deferred); Irene's Pass 1; specialists outside the dispatch/intake chain.

## Tasks / Subtasks (spine — expand at green-light)

- [ ] T1 — Run-constants schema additive field + validator update
- [ ] T2 — PR-RC capability flag-read + trial-open log line
- [ ] T3 — Marcus propagation (via envelope if PR-R landed, else ad-hoc payload)
- [ ] T4 — Tracy corroborate branching (cross-val when true, single when false)
- [ ] T5 — Irene retrieval-intake flag receipt (coordinated with sibling story)
- [ ] T6 — Operator docs (3-parameter distinction + evidence-bolster semantics + run-constants example YAML)
- [ ] T7 — Tests per AC-T.1 through AC-T.6
- [ ] T(final) — Regression + pre-commit + review

## Risks (spine)

| Risk | Mitigation |
|------|------------|
| **3-parameter conflation returns — future contributor adds enrichment/gap-fill knobs alongside** | AC-B.5 operator doc explicitly distinguishes + forbids silently extending to other knobs. If future work needs those, it's a new story. |
| **Flag propagation breaks on PR-R coordination** | Story depends on PR-R sequencing (parallel-safe): if PR-R lands first, use envelope; else use ad-hoc payload and retrofit later. Green-light confirms sequence. |
| **Cross-val perf impact under flag-true runs** | 27-2.5 PDG-3 flake-gate is orthogonal guardrail (catches non-determinism). Perf is bounded by dispatcher iteration budget (default 3); cross-val adds at most 1 extra provider call per iteration. Acceptable for trial #2. |
| **Operator sets flag true but Consensus credential missing** | MCPClient lazy auth → `MCPAuthError` at execute → dispatcher's `ProviderResult.acceptance_met: False` path handles gracefully. Fallback could be "single-provider if cross-val partner unavailable" (decide at green-light — Paige may want explicit policy). |
| **Sibling-story field-name drift** (`evidence_bolster_active` vs `evidence_bolster` vs `cross_validate`) | Coordination step at green-light pins exact field names + enum values across this story + Irene retrieval-intake spec. |

## Non-goals

- Wiring enrichment and gap-filling knobs (explicitly deferred per operator 2026-04-22 lock).
- Extending evidence-bolster to embellish or gap-fill postures (corroborate only v1).
- Flag gradations (no dial; binary only).
- Auto-inference of when to bolster (operator sets explicitly per-run).
- Profile-level persistence of flag (Epic 34 scope — "freeze evidence-bolster as default for this profile"). V1 is per-run.
- Cross-provider retry / fallback logic (27-0 anti-pattern: cross-provider retry is Marcus re-dispatch).
- Tracy's posture-selection logic changes (28-2 stable).

## Questions for Green-Light Round

1. **Schema location:** extend existing `run-constants.yaml` (inherit PR-RC validator) vs separate research-knobs schema? Recommend inherit PR-RC per AC-C.3.
2. **Flag propagation:** via PR-R envelope (if PR-R lands first) or ad-hoc payload (if parallel)? Green-light sequences PR-R-vs-this-story.
3. **Default-state policy:** `false` default accepted? (Recommended — historical behavior preserved; operator opts in.)
4. **Missing-Consensus-credential fallback:** hard-fail (exit 30; operator must fix before bolster runs), OR graceful-degrade to single-provider with loud warning? Paige's operator-experience call.
5. **Docs location:** extend `docs/operations-context.md` vs new `docs/research-knobs-guide.md`? Recommend new file — research-knobs are their own concern, deferred enrichment/gap-fill have a home when they land.
6. **Trial-open log line format:** plain `INFO evidence_bolster: true` vs structured event (`INFO event=run_open evidence_bolster=true`)? Recommend structured (matches PR-R telemetry pattern).
7. **Field-name coordination with sibling stories:**
   - In run-constants: `evidence_bolster: bool`
   - In Irene intake: `evidence_bolster_active: bool`
   - In Tracy posture: implicit via `RetrievalIntent.cross_validate`
   
   Confirm these names at green-light so all three stories speak the same language.
8. **Points estimate:** 2 pts (flag + schema + propagation test only) / 3 pts (add operator docs + AC-T.4 + AC-T.6 doc-parity test).
9. **Coordination with Irene retrieval-intake story:** intake story's `evidence_bolster_active` field — does it pick up from THIS story's run-constants field, or is the intake field separately set? Recommend propagation from run-constants (single source of truth); intake merely reads + branches. Green-light confirms.
10. **AC-T.6 doc-parity test:** include in v1 (mirrors 27-2 AC-S6 lockstep discipline; +0.25 pt) or defer?

## References

- **27-2 scite adapter** ([27-2-scite-ai-provider.md](./27-2-scite-ai-provider.md)) — first cross-val partner (DONE).
- **27-2.5 Consensus adapter** ([27-2.5-consensus-adapter.md](./27-2.5-consensus-adapter.md)) — second cross-val partner (ready-for-dev); AC-B.8 is the cross-val semantics this flag toggles.
- **28-2 Tracy three-modes** ([28-2-tracy-three-modes.md](./28-2-tracy-three-modes.md)) — corroborate posture (DONE); flag toggles the dispatch-time cross-val shape.
- **Irene retrieval-intake** ([irene-retrieval-intake.md](./irene-retrieval-intake.md)) — sibling Sprint #1 story; `evidence_bolster_active` flag surfaces in intake.
- **PR-R Marcus dispatch reshaping** ([PR-R-marcus-dispatch-reshaping.md](./PR-R-marcus-dispatch-reshaping.md)) — sibling Sprint #1 story; if lands first, this flag propagates via envelope.
- **PR-RC Run-Constants capability** ([skills/bmad-agent-marcus/capabilities/pr-rc.md](../../skills/bmad-agent-marcus/capabilities/pr-rc.md)) — the run-constants validator this story extends.
- **Operator 2026-04-22 lock** (next-session-start-here.md §Strategic decisions) — evidence-bolster only for trial #2; explicit defer of enrichment + gap-filling.
- **User memory on 3-parameter distinction**: `_bmad-output/memory/user/project_enrichment_vs_gap_filling_control.md` concept — evidence-bolster is corroboration of existing claims via cross-validation; enrichment is depth beyond SME; gap-filling is derivative-artifact content.
- **Retrieval contract cross_validate semantics** ([retrieval-contract.md](../../skills/bmad-agent-texas/references/retrieval-contract.md) §For Tracy) — defines what `cross_validate: true` does under the hood.

---

## Green-Light Patches Applied (party-mode round 1, 2026-04-22)

Four-panelist roundtable: Winston (Architect) / Amelia (Dev) / Murat (Test) / Paige (Tech Writer). **Unanimous GREEN** after D5/D6 rulings + riders applied.

### Verdict

- 🏗️ Winston: GREEN with naming rider (D6 now ratified) + D5 hard-fail ratified
- 💻 Amelia: GREEN with module-level constant rider
- 🧪 Murat: GREEN (smallest blast radius; bool flag through 3 seams)
- 📚 Paige: GREEN-conditional → GREEN after docs/research-knobs-guide.md structure ratified as dedicated file (not appended to operations-context.md)

### D5 ruling: HARD-FAIL at Marcus boot (Winston's position)

When `evidence_bolster: true` AND `CONSENSUS_API_KEY` missing → Marcus exits non-zero at preflight with clear error naming the missing env var. No silent single-provider fallback.

**Rationale**: Operator set `evidence_bolster: true` — that's a contract they authored. Running single-provider would produce narration saying "corroborated by two independent sources" based on results that only came from one source. Silent structural lie. Fail-fast preserves contract integrity.

AC-B-new (added at green-light): **AC-B.7 — Hard-fail preflight**. Marcus preflight checks `CONSENSUS_API_KEY` presence when `evidence_bolster=true`. Missing → exit 30 with: `"evidence_bolster=true requires CONSENSUS_API_KEY in .env; set it or disable evidence_bolster."` Matches 27-2's `MCPAuthError` raise-not-fallback precedent.

AC-T-new: **AC-T.8 — Hard-fail preflight test**. Three atoms: (a) `evidence_bolster=true` + key present → preflight passes; (b) `evidence_bolster=true` + key missing → exit 30 with expected message; (c) `evidence_bolster=false` + key missing → preflight passes (flag disabled, no credential requirement).

### D6 ruling: Layer-2 field is `evidence_bolster_active` (Paige's position)

Canonical 3-layer naming (sprint-level decision, authoritative for all 5 stories):

| Layer | Field | Semantics |
|---|---|---|
| 1. Run-constants (operator YAML) | `evidence_bolster: bool = false` | Operator-authored knob — immutable per run |
| 2. Irene intake (Pydantic model) | `evidence_bolster_active: bool` | Runtime state projection — may vary per cluster |
| 3. Tracy posture (RetrievalIntent) | `cross_validate: bool` | Mechanical action — reusable outside bolster flow |

AC-B.4 updated: Irene intake's `evidence_bolster_active` is populated from `run_constants.evidence_bolster` at Pass 2 cluster entry. May be `false` for clusters with no corroborate posture even when the run-constant is `true` — this is by design (runtime state ≠ knob).

### Winston architectural riders applied

- **D5 hard-fail** (above).
- **Default state `false`** — opt-in, per operator's deliberate-posture framing. Confirmed.
- **3-parameter conflation forbidden**: spec docs explicitly state enrichment and gap-filling knobs are NOT wired here; future contributor adding them = separate story + new operator-facing documentation.

### Amelia dev-feasibility riders applied

- **Module-level constant discipline**: `evidence_bolster: bool = false` defined ONCE at `state/config/narration-script-parameters.yaml` (existing file, already modified per session git status). Imported via module-level constant in each of the 3 seams (Marcus / Tracy / Irene). NOT `os.environ.get` at import time. Exact 27-2 DEFER trap guard.
- **Sibling coordination**: Ships AFTER irene-retrieval-intake (or in same PR) — bolster has no meaning without intake's corroborate posture live. BUT per D7 sequencing, opens position 3 (after 27-2.5, before irene-retrieval-intake). Dependency: bolster's wiring targets (the intake side) can stub the `evidence_bolster_active` field read as the intake story authors it. Coordinate at integration.
- **Task order**: 3 seams = 3 parallel T-tasks after constant lands. T1 run-constant schema → T2 Marcus propagation → T3 Tracy corroborate branching → T4 Irene intake flag receipt (coordinated with sibling story) → T5 docs → T6 regression.
- **Points 2 firm** — don't let drift to 3.

### Murat test-discipline riders applied

- **AC-T.2 three-seam propagation**: each seam is its own atom. Don't combine "flag propagates through all three" into one test — you lose which seam broke.
- **AC-T.5 regression byte-identical**: default=False produces byte-identical behavior to pre-flag code path via captured fixture. Commit fixture.
- **AC-T.8 added** (D5 ruling): hard-fail preflight atoms (3 new).
- **Regression floor pinned ≥10 collecting** (raised from ≥8 — three-seam atomicity means T.2 alone is 3 tests + AC-T.8 adds 3 hard-fail atoms).
- **Flake-gate NOT NEEDED** — bool flag, deterministic; three-seam propagation is deterministic ordering.

### Paige docs riders applied

- **Rider 6 blocker RESOLVED**: NEW dedicated file `docs/research-knobs-guide.md` (NOT appended to operations-context.md). Required structure per Paige:
  - Opening paragraph naming 3 concepts as **distinct, not synonyms** (aspirational enrichment / derivative-artifact gap-filling / evidence-bolster).
  - One-row-per-concept comparison table: concept | what it does | what it does NOT do | when to use | knob name (+ "what it does NOT do" column is the anti-conflation vaccine).
  - Per-concept worked example — evidence-bolster example shows SAME claim under all three knobs so operator sees output difference + conflation collapses.
  - "Common mistakes" subsection naming the conflation directly.
  - Layer-boundary mapping table (D6): operator knob → intake state → Tracy action.
- **Anti-conflation cross-refs**: Every mention of `enrichment`, `gap_fill`, or `evidence_bolster` in any other doc gets footnote pointer to `docs/research-knobs-guide.md`. Section-heading level only; not every inline mention.
- **Operations-context.md pointer**: one-line entry under "Research controls" → points at research-knobs-guide.md.
- **AC-T.6 doc-parity lockstep IN SCOPE** (was "defer to hardening follow-on" as open Q) — matches 27-2 AC-S6 lockstep discipline. Roster-level shared doc-parity pattern (Murat rider) applies.

### Sprint-level canonical naming (D6 — roster-wide decision)

This story OWNS the naming decision for all 5 Sprint #1 stories. Canonical:
- `evidence_bolster` (run-constants)
- `evidence_bolster_active` (Irene intake — THIS story wires the propagation)
- `cross_validate` (Tracy RetrievalIntent — unchanged from 27-2)

### Dev sequence

**Opens position 3** per D7 (after 27-2.5 T1 — bolster wires `cross_validate: true` plumbing that 27-2.5 exercises). Before irene-retrieval-intake (which reads `evidence_bolster_active`).

### Vote record

- 🏗️ Winston: GREEN (D5 hard-fail ratified; naming rider from D6 applied)
- 💻 Amelia: GREEN (module-level constant rider applied)
- 🧪 Murat: GREEN (floor pinned; AC-T.8 hard-fail atoms added)
- 📚 Paige: GREEN-conditional → GREEN (research-knobs-guide.md as dedicated file; structure ratified)

**Unanimous GREEN → dev-story cleared to start** at position 3 (after 27-2.5 T1).

---

**Dev-story expansion triggered at:** green-light ratification (now). Sibling-story field-name coordination (D6) + PR-R sequencing (D7: open last; bolster opens position 3) + docs location (D6 rider: dedicated `research-knobs-guide.md`) + missing-credential policy (D5: hard-fail) all RATIFIED.
