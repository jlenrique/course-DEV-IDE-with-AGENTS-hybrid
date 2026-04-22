# Story: Irene Retrieval-Intake (Shape 3 Integration at Irene's Edge)

**Status:** ready-for-dev (green-lit 2026-04-22 — D4 + riders applied below)
**Created:** 2026-04-22
**Epic:** Sprint #1 standalone story (Irene–Texas–Tracy integration — likely future Epic 23-extension or Epic 29+ "Irene Research Intake")
**Sprint key:** `irene-retrieval-intake`
**Sprint:** Sprint #1 (4 of 5 — opens position 4 per D7 sequencing)
**Points:** **3 pts firm** (ratified at green-light: corroborate-only v1 per operator 2026-04-22 lock + D4 new file + Amelia import-time traps closed)
**Depends on:** 28-1/28-2/28-3 (all done); 28-3 IreneTracyBridge provides the OUTBOUND dispatch edge — this story closes the INBOUND intake edge. Implicit dependency on 27-2.5 (once Consensus lands, cross-validated results become part of intake).
**Blocks:** Evidence-bolster control surface (that story wires the operator-facing knob that toggles `cross_validate: true` inside this intake's dispatch). §7.1 Irene template authoring (template-authoring-driven; may cite intake results in exemplar narration).

## TL;DR

- **What:** Close the loop on Irene ↔ Tracy integration. 28-3 ships the OUTBOUND path (Irene plan-lock → Tracy dispatch). This story ships the INBOUND path: Tracy's `suggested-resources.yaml` + downstream `extraction-report.yaml` (from Texas second-pass) LAND inside Irene's Pass 2 narration flow, with Irene weaving retrieved evidence into narration segments that reference specific sources.
- **Why:** Trial run `C1-M1-PRES-20260419B` (the first end-to-end motion-enabled lesson) ran WITHOUT any Tracy / Texas retrieval integration — narration was all internal SME content. The next trial ("trial #2") will exercise the full research capability: scite + Consensus cross-validation (evidence-bolster only per operator lock 2026-04-22). Without a formal intake seam, Irene gets retrieval results as loose YAML + has to improvise how to cite them. **This story formalizes the seam so Irene's Pass 2 has deterministic consumption of retrieval outputs.**
- **Novelty:** The intake contract is new. It includes: (a) where in Pass 2's flow retrieved evidence lands, (b) how narration cites retrieved sources (natural-language mention vs footnote vs segment-manifest provenance-only), (c) fail-closed vs graceful-degradation when retrieval is empty / failed / partial, (d) how Irene's narration references `convergence_signal` annotations (e.g., "corroborated by two independent sources" vs unsupported single-source claims).
- **Size:** 3–5 pts (scope-bounded at green-light). Low floor = "schema + sentinel handling + embellish-only intake"; high floor = "all three postures + citation style ratified + convergence-aware narration + intake L1 lockstep check."

## Background — Why This Story Exists

**Current gap:** 28-3 IreneTracyBridge wires the dispatch direction (Irene's plan reveals `IdentifiedGap` → bridge triggers Tracy posture method). But **the path back — Tracy's results flowing into Irene's Pass 2 narration — is NOT formalized**. Irene currently would need to:

1. Read Tracy's `suggested-resources.yaml` manifest (written by any of the three postures).
2. Optionally wait for Marcus → Texas second-pass extraction of operator-approved rows → `extraction-report.yaml`.
3. Decide how to weave the retrieved material into narration (embellishment? direct citation? paraphrase with source?).
4. Emit `segment-manifest.yaml` with `visual_references` + narration text that correctly attributes the retrieved evidence.

Without a formal contract for steps 3–4, Irene will improvise — meaning every trial run produces a different "how retrieval landed in narration" pattern. Evidence-bolster control (Sprint #1 downstream story) adds a runtime toggle; §7.1 Irene template is about the template artifact quality. This story (retrieval-intake) is the ARCHITECTURAL seam that makes both land cleanly.

**Operator directive (2026-04-22 lock):** research capability for trial #2 = evidence-bolster knob only (no aspirational enrichment / no derivative-artifact gap-fill). This story's v1 scope aligns: intake the **corroborate** posture's output (scite + Consensus cross-validated + convergence-annotated). Embellish / gap-fill intake may be scoped in or deferred at green-light per the single-posture simplification.

## Story

As **Irene (Pass 2 author)**,
I want **a formal intake contract that reads Tracy's `suggested-resources.yaml` + Texas's `extraction-report.yaml` into my Pass 2 workflow, with pinned semantics for how retrieved evidence weaves into narration + gets cited + handles empty/failed retrieval**,
So that **every trial run's retrieval-augmented narration is deterministic (same inputs → same narration-citation pattern), AND the convergence_signal from scite+Consensus cross-validation shows up as narration-level confidence language ("corroborated by two independent sources" vs "per scite.ai") rather than being buried in provenance metadata, AND the evidence-bolster operator knob (Sprint #1 downstream) has a real intake surface to toggle against**.

## Acceptance Criteria (spine level — expand at green-light)

### Behavioral (AC-B.*)

1. **AC-B.1 — Intake contract pinned.** Pydantic model `IreneRetrievalIntake` defines required fields: `run_id`, `pass_2_cluster_id`, `suggested_resources_ref` (path to Tracy's YAML), `extraction_report_ref` (path to Texas's YAML, optional if Marcus-Texas second-pass is not yet dispatched), `intake_mode` (enum: `corroborate` / `embellish` / `gap_fill` / `mixed`), `evidence_bolster_active` (bool — evidence-bolster knob wired in downstream story).
2. **AC-B.2 — Pass 2 procedure extended.** `skills/bmad-agent-content-creator/references/pass-2-procedure.md` gains a new section "§Retrieval intake" after the existing cluster intelligence section. Specifies: when to read intake ref (at cluster entry), how to process it (per posture), where to weave results (narration text + segment-manifest `visual_references`).
3. **AC-B.3 — Posture-specific intake semantics.**
   - **corroborate intake**: narration references the retrieved claim + natural-language convergence signal ("corroborated by peer-reviewed studies A and B, with strong research synthesis agreement" for `providers_agreeing: ["scite", "consensus"]` + high `consensus_score`). Single-source annotations use cautious language ("per scite.ai" / "per Consensus research synthesis").
   - **embellish intake** (scope-bounded): retrieved material augments narration depth beyond SME — pending operator directive 2026-04-22 lock (trial #2 = corroborate only); scope in/out at green-light.
   - **gap-fill intake** (scope-bounded): retrieved material populates derivative-artifact content (quiz/handout) — similarly gated.
4. **AC-B.4 — Empty-retrieval graceful degradation.** When Tracy's manifest is empty (no usable candidates) OR Texas extraction failed for all approved rows, Irene Pass 2 MUST:
   - Emit narration WITHOUT the intake-dependent segment.
   - Log `known_losses: ["retrieval_empty_for_cluster_<id>"]` in `segment-manifest.yaml`.
   - NOT block Pass 2 completion (retrieval is augmentative, not blocking).
5. **AC-B.5 — Convergence signal surfaces in narration language.** Natural-language rules map `convergence_signal` fields to cautious-vs-confident narration framing. Documented in `pass-2-procedure.md` §Retrieval intake with worked examples. Examples:
   - `providers_agreeing: ["scite", "consensus"], single_source_only: false` → "Corroborated by multiple independent sources" / "Supported by peer-reviewed evidence and research synthesis".
   - `providers_agreeing: ["scite"], single_source_only: true` → "According to scite.ai analysis" / "Per peer-reviewed citation context".
   - `providers_agreeing: ["consensus"], single_source_only: true` → "Per Consensus research synthesis".
6. **AC-B.6 — Segment-manifest schema addition.** `segment-manifest.yaml` gains new optional field `retrieval_provenance: list[{source_id, providers, convergence_signal}]` per narration segment. Additive; backward-compatible with trial #1 manifests (empty list).

### Test (AC-T.*)

1. **AC-T.1 — Intake schema-pin tests.** Pydantic round-trip + frozen-field tests per 31-1 precedent.
2. **AC-T.2 — Posture-specific intake-to-narration test.** For corroborate posture (v1 scope), fixture Tracy manifest + Texas extraction → Irene narration output has expected citation language + convergence framing. One test per posture in scope.
3. **AC-T.3 — Empty-retrieval graceful-degradation test.** Empty Tracy manifest → narration emits without intake segment + `known_losses` sentinel + no crash.
4. **AC-T.4 — Convergence-signal-to-language mapping test.** Parametrized over signal shapes × expected narration patterns. Lookup table, not inference (AC-C.5 anti-pattern).
5. **AC-T.5 — Pass 2 procedure doc-parity test.** `pass-2-procedure.md` §Retrieval intake section matches schema — drift = CI fail (mirrors 27-2 AC-S6 transform-registry lockstep pattern).
6. **AC-T.6 — Suite regression floor pinned** (TBD at green-light, estimate ≥12 collecting).

### Contract Pinning (AC-C.*)

1. **AC-C.1 — Intake schemas live in `state/config/schemas/`** (consistent with envelope schemas).
2. **AC-C.2 — Pass 2 procedure doc is the SSOT for intake semantics.** Code references the doc section anchor for normative behavior (mirrors retrieval-contract.md's audience-segmented SSOT pattern).
3. **AC-C.3 — Segment-manifest additive only.** `retrieval_provenance` field is optional with default `[]`; legacy manifests (trial #1) pass validation unchanged.
4. **AC-C.4 — No LLM-in-the-loop for intake routing.** Posture discriminator is Pydantic enum + deterministic match; narration framing is lookup table.
5. **AC-C.5 — Convergence-signal-to-language mapping is data, not inference.** Module-level `CONVERGENCE_NARRATION_PATTERNS: dict[str, str]` analogous to scite's `SCITE_AUTHORITY_TIERS` lookup.
6. **AC-C.6 — No specialist-to-specialist runtime calls.** Irene reads Tracy's file + Texas's file via Marcus dispatch (consistent with governing architecture principle: specialists never dispatch specialists at runtime; artifact handoff via filesystem only).

## File Impact (estimated — scope-bounded at green-light)

| File | Change | Lines (est.) |
|------|--------|-------|
| `state/config/schemas/irene-retrieval-intake.schema.json` | New — `IreneRetrievalIntake` + `RetrievalProvenance` schemas | +100 |
| `marcus/irene/intake.py` OR `skills/bmad-agent-content-creator/scripts/retrieval_intake.py` (location TBD) | New — intake loader + posture discriminator + convergence→narration mapper | +280 |
| `skills/bmad-agent-content-creator/references/pass-2-procedure.md` | Touch — new §Retrieval intake section with worked examples per posture + convergence signal | +100 |
| `state/config/schemas/segment-manifest.schema.json` | Touch — additive `retrieval_provenance` field | +20 |
| `skills/bmad-agent-content-creator/references/retrieval-intake-contract.md` (new reference file) | New — audience-segmented contract (for Irene authors / for operators / for dev-agents) mirroring retrieval-contract.md pattern | +180 |
| `tests/irene/test_retrieval_intake.py` | New — AC-T.1/T.2/T.3/T.4 | +250 |
| `tests/contracts/test_pass_2_procedure_parity.py` | New — AC-T.5 doc-parity lockstep | +80 |

**No changes to:** Tracy's emission side (28-3 + 28-2 stable), Texas retrieval (27-0/27-2 stable), dispatcher (27-0 stable), Irene's Pass 1 (intake is Pass 2 only).

## Tasks / Subtasks (spine — expand at green-light)

- [ ] T1 — Intake schema Pydantic model + JSON schema
- [ ] T2 — Segment-manifest additive schema update + backward-compat test
- [ ] T3 — Intake loader + posture discriminator module
- [ ] T4 — Convergence→narration mapping table + unit tests
- [ ] T5 — Pass 2 procedure doc §Retrieval intake section (Paige owns; Irene specialist countersigns semantics)
- [ ] T6 — New reference `retrieval-intake-contract.md` (audience-segmented) — at green-light decide whether separate file or section in existing `retrieval-contract.md`
- [ ] T7 — Corroborate-posture intake-to-narration test (v1 scope)
- [ ] T8 — Empty-retrieval graceful-degradation test
- [ ] T9 — Doc-parity lockstep test
- [ ] T(final) — Regression + pre-commit + review

## Risks (spine)

| Risk | Mitigation |
|------|------------|
| **Intake format premature — Tracy's manifest shape may evolve during trial #2** | Pydantic intake model uses `model_config={"extra": "allow"}` on posture-specific sub-objects v1; tighten post-trial-#2. |
| **Narration-language mapping is too rigid / too permissive** | CONVERGENCE_NARRATION_PATTERNS as data (AC-C.5); operator adjusts without code change; party can ratify the initial mapping at green-light. |
| **Empty-retrieval handling produces narration that reads as if material is missing** | AC-B.4 requires Irene to emit WITHOUT intake segment (not with placeholder/apology). Tests cover this. |
| **Scope creep — all three postures + cross-validation + convergence + citation styles all at once** | Green-light scope-bounds to corroborate posture only (matches operator 2026-04-22 evidence-bolster-only lock for trial #2). Embellish/gap-fill intake deferred. |
| **Pass 2 procedure doc vs code drift** | AC-T.5 doc-parity lockstep — CI fails on drift. Inherit 27-2 AC-S6 transform-registry lockstep precedent. |
| **Citation style rows with operator voice intent** | §7.1 Irene Pass 2 template story (Sprint #1 sibling) may inform citation-style conventions. Coordinate at green-light if §7.1 lands first. |

## Non-goals

- Changing Tracy's emission side (28-3 + 28-2 stable).
- Changing retrieval dispatcher or providers.
- Operator-facing knob (evidence-bolster control) wiring — that's a separate Sprint #1 story.
- §7.1 Irene Pass 2 template authoring (separate Sprint #1 story; this story delivers the INTAKE CONTRACT; §7.1 delivers the TEMPLATE AUTHORING GUIDANCE).
- Voice/tone tuning for retrieval-augmented narration (dials territory; trial #2 uses locked evidence-bolster, not full dial experimentation).
- Auto-approval of Tracy's suggestions (operator-in-the-loop by design per Epic 28 architecture).
- Retrieval-driven segment-timing recalculation (narration duration may shift slightly; handled by 20c-15 slide-count/runtime estimator; intake-induced shifts in-scope only if measurably large).

## Questions for Green-Light Round

1. **Posture scope:** v1 = corroborate only (matches operator 2026-04-22 evidence-bolster-only lock)? Or corroborate + embellish? gap-fill deferred regardless?
2. **Code location:** `marcus/irene/intake.py` (marcus package) vs `skills/bmad-agent-content-creator/scripts/retrieval_intake.py` (specialist skill)? Architectural call.
3. **Contract doc choice:** new `retrieval-intake-contract.md` OR section appended to existing `retrieval-contract.md`? Paige's call.
4. **Convergence-narration mapping:** should the mapping be party-ratified at green-light (team agrees to specific narration language for each signal shape), or authored by Irene agent + ratified at review time?
5. **Segment-manifest field addition:** `retrieval_provenance` as additive (AC-C.3), OR bump `segment-manifest` schema version to 2.0? Green-light decides backward-compat strategy.
6. **Doc-parity lockstep (AC-T.5):** in scope (follows 27-2 AC-S6 pattern, +1 contract test) or defer to hardening follow-on?
7. **Points estimate:** 3 pts (corroborate only, minimal doc) / 4 pts (corroborate + lockstep + full doc) / 5 pts (all postures).
8. **Coordination with evidence-bolster control:** that story wires the `evidence_bolster_active` flag; this story's schema must expose it. Green-light confirms flag semantics + default.
9. **Coordination with §7.1 Irene template:** §7.1 produces template-authoring guidance that may cite intake output examples; does §7.1 land before or after this story? Recommend THIS story first so §7.1 has intake contract to reference.
10. **PR-R interaction:** if PR-R lands first, intake uses PR-R envelope discipline for reading Tracy/Texas artifacts. If in parallel, this story uses the current ad-hoc YAML read + retrofits to PR-R later. Green-light sequences.

## References

- **28-3 IreneTracyBridge (outbound half)** ([28-3-irene-tracy-bridge.md](./28-3-irene-tracy-bridge.md)) — this story is the INBOUND complement; 28-3 reads `plan.locked` → dispatches Tracy; this story reads Tracy+Texas outputs → Irene Pass 2.
- **28-2 Tracy three-modes** ([28-2-tracy-three-modes.md](./28-2-tracy-three-modes.md)) — emits `suggested-resources.yaml` per posture; this intake reads those files.
- **Pass 2 procedure** ([skills/bmad-agent-content-creator/references/pass-2-procedure.md](../../skills/bmad-agent-content-creator/references/pass-2-procedure.md)) — existing Pass 2 flow; intake appends §Retrieval intake section.
- **Retrieval contract** ([skills/bmad-agent-texas/references/retrieval-contract.md](../../skills/bmad-agent-texas/references/retrieval-contract.md)) — audience-segmented pattern template; intake contract mirrors the shape.
- **27-2.5 Consensus adapter** ([27-2.5-consensus-adapter.md](./27-2.5-consensus-adapter.md)) — produces the `convergence_signal`-annotated rows this intake consumes.
- **Reproducibility report §7.1** ([run-reproducibility-report-c1m1-tejal-20260419b.md](./run-reproducibility-report-c1m1-tejal-20260419b.md)) — trial-#1 surfaced intake absence as a gap.
- **Governing architecture principle**: specialists never dispatch specialists; artifact handoff via filesystem is not a rule violation.

---

## Green-Light Patches Applied (party-mode round 1, 2026-04-22)

Four-panelist roundtable: Winston (Architect) / Amelia (Dev) / Murat (Test) / Paige (Tech Writer). **Unanimous GREEN** after D4 ruling + riders applied.

### Verdict

- 🏗️ Winston: YELLOW → GREEN after code-location pin + contract-doc pin (D4) + segment-manifest-additive-not-bump
- 💻 Amelia: YELLOW → GREEN after module-level-constant rider + lazy-import rider + corroborate-only scope lock
- 🧪 Murat: YELLOW → GREEN after empty-retrieval structural-shape rider + doc-parity test mechanism pinned
- 📚 Paige: YELLOW → GREEN after D4 ruling (new file in Irene's skill folder) + convergence-narration mapping ratified at party-mode (not review-time)

### D4 ruling: NEW `skills/bmad-agent-content-creator/references/retrieval-intake-contract.md` (Paige's position)

Separate file in Irene's skill folder (NOT extension of Tracy's `retrieval-contract.md`). Mirror the audience-segmented pattern (For Irene / For operators / For dev-agents). Rationale: skill-folder proximity + "fresh dev lands in wrong file" heuristic. Dev-agent debugging Irene's convergence-narration issue should NOT need to read Tracy's provider directory first.

Cross-link at handoff seam: each contract doc points to the other. `retrieval-contract.md` unchanged (Texas-domain); `retrieval-intake-contract.md` new (Irene-domain).

AC-C.2 updated: contract doc is the SSOT for intake semantics; code references the doc section anchor for normative behavior.

### Winston architectural riders applied

- **Code location: `marcus/irene/intake.py`** (NOT under `skills/bmad-agent-content-creator/scripts/`). Production data-flow code lives under `marcus/`; skills tree is operator-facing scaffold.
- **Segment-manifest: ADDITIVE only** (new optional `retrieval_provenance: list` field) — NO schema version bump. The convergence_signal → narration-language lookup is a *read* of an existing field, not a new segment-level field.

### Amelia dev-feasibility riders applied

- **Rider 1 (convergence_signal → narration mapping)**: Module-level constant `CONVERGENCE_NARRATION_PATTERNS: dict[str, str]` at `marcus/irene/intake.py`, NOT computed at first-use. Prevents 27-2 DEFER import-time trap.
- **Rider 2 (lazy import)**: `retrieval/__init__.py` does NOT eager-import Tracy's suggested-resources reader. Lazy per `__init_subclass__` pattern. Same trap guard as 27-2.
- **Rider 3 (scope lock)**: **Corroborate-only posture v1.** Multi-posture = scope balloon. Embellish + gap-fill intake are explicitly deferred per operator 2026-04-22 evidence-bolster-only lock. Matches user memory note on 3-parameter distinction.
- **Rider 4 (segment-manifest bump)**: Additive-only, no version bump (aligned with Winston).
- **Task order (NEW at green-light)**: T1 intake-reader skeleton → T2 lookup-constant → T3 Pass 2 injection point → T4 deterministic tests → T5 doc-parity lockstep → T6 integration smoke → T-final review. Skeleton-first pattern (mirrors 27-2 MUST-FIX #3).

### Murat test-discipline riders applied

- **AC-T.3 empty-retrieval assertion**: STRUCTURAL shape (returns dict with specific keys/types), NOT log strings or absence-of-exception. Log assertions flake; shape assertions don't.
- **AC-T.4 parametrization**: Use `@pytest.mark.parametrize` with lookup table as param source. One atom, multiple param ids. Don't hand-write 5 tests.
- **AC-T.5 doc-parity**: Test parses `retrieval-intake-contract.md` headings/sections and compares to schema keys. Not a "visual inspection" step.
- **Coverage-gap fill**: Under-covered on empty-retrieval edge cases per Murat's intuition check. Add 3 atoms distinguishing: (a) retrieval returned empty array, (b) retrieval failed with timeout, (c) retrieval succeeded with malformed response. Three different failure modes masquerading as one — separate atoms.
- **Flake-gate**: NOT binding at CI level (low combinatorial surface), but "local 3x-run before PR open" as hygiene.
- **Regression floor pinned ≥14 collecting** (raised from ≥12 in spec — AC-T.4 parametrize yields ≥5 param ids; coverage-gap fill adds ≥2; doc-parity lockstep +1).

### Paige docs riders applied

- **R-4 (D4 ruling)**: New file `skills/bmad-agent-content-creator/references/retrieval-intake-contract.md`. Audience-segmented: For Irene / For operators / For dev-agents.
- **R-5 (convergence-narration mapping)**: Mapping ratified at party-mode (this round) — mapping table in spec before dev opens. Prevents review-gate punch-list extending the story cycle. Canonical mapping:

  | ConvergenceSignal shape | Narration framing |
  |---|---|
  | `providers_agreeing: ["scite", "consensus"]` + both present | "Corroborated by multiple independent sources" / "Supported by peer-reviewed evidence and research synthesis" |
  | `providers_agreeing: ["scite"]` + `single_source_only: true` | "According to scite.ai analysis" / "Per peer-reviewed citation context" |
  | `providers_agreeing: ["consensus"]` + `single_source_only: true` | "Per Consensus research synthesis" |
  | (retrieval empty for cluster) | (no narration attribution; segment omitted per AC-B.4 graceful degradation) |

- **R-sibling (§7.1 coordination)**: Intake contract doc carries the worked examples for retrieval-consuming segments. §7.1 authoring template will NOT replicate these — pointer only (per Paige worked-example-count ruling on §7.1).

### Sprint-level canonical naming applied (D6)

- Intake field: **`evidence_bolster_active: bool`** (layer-2, runtime state projection with `_active` suffix)
- Read-upstream from: `evidence_bolster: bool` (run-constants layer)
- Passes downstream to: `cross_validate: bool` on `RetrievalIntent` (Tracy's mechanical action)

### Dev sequence

**Opens position 4** per D7. Depends on:
- 28-3 IreneTracyBridge (DONE)
- 27-2.5 landed or in-flight (intake consumes cross-val output)
- evidence-bolster field name `evidence_bolster_active` pinned (done — D6)

### Vote record

- 🏗️ Winston: YELLOW → GREEN (after code location + D4 + additive-manifest riders)
- 💻 Amelia: YELLOW → GREEN (after module-level-constant + lazy-import + corroborate-only + task-order riders)
- 🧪 Murat: YELLOW → GREEN (after structural-shape-not-log-string + parametrize-via-table + doc-parity-test-mechanism riders)
- 📚 Paige: YELLOW → GREEN (after D4 + mapping ratified at party-mode)

**Unanimous GREEN → dev-story cleared to start** at position 4.

---

**Dev-story expansion triggered at:** green-light ratification (now). Posture scope (corroborate-only v1) + code location (`marcus/irene/intake.py`) + contract doc (new `retrieval-intake-contract.md`) + convergence-narration mapping all RATIFIED above; citation-style guidance bounded by mapping table.
