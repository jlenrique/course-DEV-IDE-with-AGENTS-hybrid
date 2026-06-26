# Cycle Charter — G0 Source-Content Enrichment ("source-content injection")

**Status:** PREP / pre-plan. Party-mode green-light round COMPLETE (2026-06-26). Ready for `bmad-create-epics-and-stories` once the operator answers the Open Decisions below (and Irene signs the LO-delta contract).
**When:** interjected AFTER the composition-catalog goal (the 07W workbook brick + B3 re-run) closes.
**Class:** S (substrate — directive schema, a SPOC-side LLM enrichment capability, an LO-schema unification). Likely the proven NEW-CYCLE brick pattern (spec → dev → T11 → live run → party).

## Governing principle (binding)
**Source content + Learning Objectives are KING — get them COMPLETE and RELIABLY ACCESSED.** Every downstream artifact (slides, quiz, workbook, narration) inherits any source/LO defect. See `[[feedback_material_partition_gate]]`, `[[feedback_agents_coach_operator_access]]`.

## Party verdict
3× GREEN-WITH-AMENDMENTS (John, Winston, Marcus) + 1× NEEDS-CLARIFICATION (Mary) — Mary's blockers are largely resolved by the others' amendments; a short Open-Decisions list remains for the operator.

## Converged architecture (the load-bearing calls)
- **LLM inference is SPOC-side, NOT in the deterministic composer** (Winston, the line he won't cross). Marcus-SPOC runs the content-type + LO pre-pass conversationally (off the critical path); the operator converges on it; the FROZEN, operator-confirmed result crosses the G0 gate as enriched Directive data. The `section_02a` composer is enriched only as a deterministic validator/normalizer that CONSUMES types+LOs — never infers them. **LLM output is cached keyed to corpus state** so graph replays read the frozen result (replay-determinism preserved).
- **Marcus-SPOC ownership is CUSTODIAL + gate-bearing, not authorial** (Marcus). He holds the manifest (every artifact: location, detected type, reachability), presents a typed + LO-annotated view, and gates. He is the single channel through which LOs enter the graph.
- **Completeness vs reliable-access are SEPARATE claims** (Marcus): COMPLETENESS = the operator's call (informed by the inventory Marcus presents — Marcus never asserts "complete," only "here's what I reached"); RELIABLE ACCESS = Marcus's to PROVE deterministically (fetched + extractable + content-fingerprint; unreachable surfaces **RED**, never silently absent).
- **One canonical LO entity** (Winston): promote a shared LO schema with a lifecycle status (`provisional → refined → ratified`) + provenance (source-row backrefs). LO-identification moves up to G0 as `provisional`; Irene refines IN PLACE (status transition), not a parallel set → reconciliation-by-status, not by merge. **Unifying the LO schema is a PRE-REQ story** (today: Irene Pass-1's LO logic + the workbook's `LearningObjectiveBrief`).
- **Authority rule** (Winston/Marcus): operator/SPOC **RATIFY**; Irene **PROPOSES** refinements (with a source-tied LO-delta).
- **Trust model** (Marcus, mirrors the S5 SPOC guard): deterministic guardrails (access + provenance un-fakeable; counts reconcile — artifacts-in == typed + ignored + flagged) + **operator-confirm-as-final** (the LLM proposes typing/LO-critique; it never autonomously decides either).

## v1 scope (OPERATOR-AMENDED — John's cut + the mandated Irene loop)
**⚠️ OPERATOR OVERRIDE (2026-06-26, NON-NEGOTIABLE for the next operator-run trial):** the lesson-plan **refinement loop is REQUIRED in v1**, NOT deferred. Specifically Irene must: refine the LOs, **assess SOURCE-CONTENT ADEQUACY against the LOs** (does the source actually support the lesson — flag inadequacy/gaps), and bake both into a refined lesson plan delivered BACK to Marcus-SPOC for iteration with the operator.

**v1 = the G0 enrichment brick + the Irene refinement loop:**
1. **types every source span** into a closed set (slide / quiz / workbook / narration) — persisted as a typed manifest; types-and-SHOWS, does **not** yet re-wire generation;
2. **extracts candidate LOs with source provenance** (the heart of the value);
3. is **owned as Marcus-SPOC state** and presented to the operator with a **genuine critical evaluation** (3-column type reconciliation; LO buckets: supported / unsupported-thin / orphan-content) for a **confirm gate before Irene**;
4. **REQUIRED — Irene refinement loop (S-D, pulled INTO v1):** Irene inspects source AGAINST the LOs, **refines the LOs** (status `provisional→refined`), produces an explicit **source-content-ADEQUACY assessment** (per-LO: is there enough source to teach/assess it? gaps named), bakes both into her **refined lesson plan**, and returns to Marcus-SPOC an **LO-delta + adequacy report + plan**;
5. **second operator gate** — Marcus re-presents Irene's refined plan + LO-delta + adequacy report; operator iterates → confirm (status `refined→ratified`);
6. **hard-asserts completeness** — every source span typed-or-ignored, every LO traceable, unreachable is RED — fail otherwise.

**Decoupled from the 07W/07D.5 generation bricks** (those are downstream consumers; v1 stops at typed+identified+owned+REFINED+confirmed, before re-wiring generation). Keeps the critical path clean.

## Deferred follow-ons (→ `deferred-inventory.md`, named so they don't drift)
- **Multi-turn Marcus↔operator LO negotiation** beyond the two confirm gates — v1 is confirm-or-rerun at each gate, not rich in-session haggling.
- **Acted-upon typing** — routing typed slide/quiz/workbook spans INTO the generators (where the typed manifest DRIVES generation; the quiz consumer may not exist yet — see D1). This is where 07W/07D.5 become consumers.

## ⚠️ Implication of the operator override (honesty flag)
The Irene refinement loop + source-adequacy assessment is now REQUIRED for the operator's next trial. Today Irene Pass-1 designs a lesson plan + LOs and the G1 gate reviews it, but the EXPLICIT chain — (LOs identified at G0) → Irene refines + assesses source adequacy → LO-delta + adequacy report back to Marcus → operator iterates — is net-new and coupled to the G0 LO-identification. **So this cycle (or at least its LO-id + Irene-refinement-loop legs) must SHIP BEFORE the next operator-run trial** if that trial is to have the mandated loop. If the trial precedes the build, today's Irene Pass-1 + G1 review is only a partial stand-in (it plans + reviews, but does not produce the explicit refined-LO-delta + source-adequacy report). Sequence accordingly when scheduling.

## Binding amendments (into the spec regardless of the Open Decisions)
- A1 **Access verification is deterministic + LOUD** — mechanical proof (fetched/extractable/fingerprinted); RED on failure; never silently dropped. (Mary AC-C1, Marcus A1.)
- A2 **Typing + LO-critique are proposals with MANDATORY provenance** — every type + LO finding carries a source-span pointer; provenance-less findings rejected pre-surface; confidence is a first-class field ("ambiguous/low-confidence" is valid). (Marcus A2, Mary AC-E1.)
- A3 **Mandatory real DISSENT artifact** — at least one run where Marcus dissents from an operator-suggested type/LO (proves "critically evaluate, don't rubber-stamp" is real). (Mary AC-E2.)
- A4 **Independent-parse-first ordering** — Marcus's own analysis is logged BEFORE the operator's suggestions are merged (anti-anchoring). (Mary AC-E3.)
- A5 **Two human gates** — operator confirms the manifest (completeness + access) BEFORE Irene; operator confirms the reconciled plan + LO-delta AFTER Irene. Pipeline never advances on model say-so. **Wire gate side-effects into BOTH `production_runner` walks** (`[[project_production_runner_two_walks]]`). (Marcus A3.)
- A6 **Completeness invariant** — deterministic enumeration of ALL sources stays in the composer; LLM ADVISES type/role/LO, never gates a file out; `ignored` stays operator-confirmed. (Winston.)
- A7 **Unify the LO schema first** (pre-req story) — single canonical entity + lifecycle + provenance. (Winston.)
- A8 **Never overturn the operator's prior unilaterally** — divergence surfaced for adjudication. (Marcus A5.)
- A9 **Iteration exit condition** — operator "lock" and/or max-iterations (anti-non-termination). (Winston.)
- A10 **Type taxonomy is a closed enum validated against real downstream consumers** — flag any type with no consumer. (Winston.)
- A11 **Access-coaching** — when access is RED, Marcus/Texas hand the operator a GROUNDED (proven-prior-run or doc-backed) access recipe, never speculative unless flagged. (`[[feedback_agents_coach_operator_access]]`.)

## Open Decisions (need the OPERATOR before `bmad-create-epics-and-stories`)
- **D1 — Ratify the closed TYPE taxonomy.** Proposed: `slide / quiz / workbook / narration`. Add `reference/citation`, `rubric`, `exercise/lab`? (Governance call, not dev. Note: a type with no downstream consumer — e.g. `quiz` today — gets flagged per A10.)
- **D2 — Define "complete source."** Do you provide an **expected-source inventory** for G0 to reconcile against (stronger completeness guarantee), OR is **"operator confirms the manifest Marcus presents"** sufficient? (Mary's #1 blocker; reliable-access half is settled = mechanical.)
- **D3 — Confirm the v1 cut** (type + LO-with-provenance + Marcus-owned single-pass confirm + completeness-hard-assert; Irene-loop + generation-routing DEFERRED).
- **D4 — Irene in the room.** Both John + Marcus want Irene to sign the **LO-delta contract** (what she returns: refined LOs + source-tied rationale diff) before stories open — she's the other owner of the hand-off.

## Build discipline (OPERATOR-MANDATED, binding)
- **MODULAR + DRY + existing patterns.** All new functionality + supporting functions: as modular as possible, DRY-driven (REUSE don't duplicate — e.g. the canonical LO schema A7 unifies 3 representations into one; the SPOC LLM pre-pass + access-coaching reuse existing seams; new nodes follow the proven 9-node scaffold / dispatch-registry / capability-overlay / canonical-roster registration pattern). New code must keep with existing architectural patterns (deterministic composer, HIL-side LLM, the NEW-CYCLE brick pattern, pydantic-v2 closed-enum idioms) — no parallel/bespoke mechanisms where a proven one exists.
- **D3 RESOLVED — BUILD-THEN-TRIAL.** The G0-enrichment cycle (LO-id + Irene refinement loop legs at minimum) ships BEFORE the operator's next content trial.
- **The BUILD PROCESS ITSELF includes LIVE TRIALS of every implicated segment — NO mocking, NO inauthentic validation** (`[[feedback_no_mocks_real_live_apis]]`). Offline RED-first tests are necessary but NOT sufficient: each implicated segment (the SPOC-side LLM type-parse, the LO-identification, the Irene source-adequacy + LO-refinement loop, the two operator gates) must be exercised with a REAL live run on real content before its story closes — the proven NEW-CYCLE pattern (spec → dev → T11 → **LIVE run** → party) that landed the motion (07D.5) + workbook (07W) bricks. A story is not "done" on green unit tests alone; it needs the authentic live-segment proof. The mandatory **dissent artifact (A3)** and the **completeness/RED-access invariants (A1/A6)** are themselves live-trial acceptance evidence, not fixtures.

## Next step
Operator answers D1, D2, D4 (D3 resolved = build-then-trial) → re-convene party (with **Irene**) to ratify the unified LO schema (A7) → `bmad-create-epics-and-stories` on this v1 scope → build each story spec → dev → T11 → **LIVE-segment trial** → party-close, per the build discipline above.
