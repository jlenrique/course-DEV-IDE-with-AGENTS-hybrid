# Strawman — Lesson-Component Composition + Curated Bundle Catalog (2026-06-25)

**Status:** STRAWMAN for party-mode GOVERNANCE RATIFICATION before any dev (mandated: the frozen-graph-ceremony change is an unanticipated drift class per `pipeline-manifest-regime.md`; motion is Tier-2; both gate dev on party consensus). Operator-set direction (this session, `/goal`). Supersedes the menu-registry `workflow-front-door-strawman` (that was the wrong abstraction).
**Authorities:** operator `/goal` 2026-06-25; conversation design lock; recon of compiler/manifest/kira/lesson_plan substrate; `pipeline-manifest-regime.md` §Pack Versioning + §Unanticipated Drift Class; braid S4 capability-overlay + S5 SPOC precedents; Lesson-Planner Epics 28–32 (ModalityProducer/registries, orphaned).

---

## 1. The locked architecture (operator-ratified direction; party refines specifics only)

A lesson is a **composition of components** (deck / motion / workbook / podcast / quiz), NOT a member of an enumerated workflow list. **Composition is a COMPILE-TIME act, before the freeze:** the settled lesson plan selects components → a deterministic composer assembles the selected fragments into ONE graph → that assembled graph is frozen per run (reuse `app/runtime/compiled_graph_digest.py`; add the component-selection to the digest payload). Freeze-after-assembly **preserves** the proven single-frozen-graph + tamper-evident replay invariant.

**Not** maximal-superset (produce-everything-then-discard — rejected on cost/latency/failure-coupling/hollow-selection) and **not** a free-form arbitrary assembler (over-engineered for a ~5-bundle reality). Target = a **SMALL CURATED CATALOG of blessed bundles (~3)**, each producing only its components.

Front door: Marcus-SPOC + Irene + operator(HIL) co-develop a lesson plan → settle components → Marcus confirms realistic vs PROVEN capabilities (capability-overlay tiers) → recommends one bundle → deterministic composed run.

---

## 2. Reuse map — mostly wiring + ONE engine generalization + ONE new producer

| Need | Exists | Gap |
|---|---|---|
| Motion clip leg | kira 07E → Kling proven (C1-M1-PRES .mp4); contracts intact | input STARVED: no motion-plan producer edge; silent `{"slides":[]}`; folded G2F |
| Component model | Lesson-Planner registries (`modality_registry`, `component_type_registry`, `ModalityProducer` ABC, `ProducedAsset.fulfills`) | ORPHANED — zero compiler/runner integration; motion absent from registry |
| Graph build | `compiler.py:compile_run_graph()` adds ALL manifest nodes unconditionally | no conditional/fragment inclusion |
| Freeze/replay | `compiled_graph_digest.py` hashes node_ids+edge_tuples+versions | doesn't capture a per-run component-selection |
| Workbook | producer mechanism (braid S2) emits a DOCX | never DESIGNED+produced as a real artifact |
| Capability honesty | braid S4 capability-overlay (`wired/partial/orphaned/shelf`) | needs a 4th tier: proven-but-regressed |
| Conversational front door | braid S5 SPOC gate REPL (deterministic guard) | no pre-run lesson-plan + component-selection turn |

---

## 3. DECISION POINTS the party must ratify (strawman recommendation in **bold**)

**DP1 — Governance tier + sequencing.** Strawman: **motion repair = Tier-2 branch-restore** (additive, restores a known-good motion-enabled path; party consensus, no v-bump if pack render unchanged); **the composer + frozen-graph-ceremony amendment = Tier-3/drift-class**, Epic-boundary, operator-ratified (already ratified in direction). **Sequence: motion-first (restore + bring under brick contract) → composer + digest → workbook brick → catalog + front-door → 3 live runs.** Motion first because it de-risks (restore-known-good isolates the Kling leg before the engine refactor) AND is the first brick.

**DP2 — Frozen-graph ceremony amendment (the load-bearing governance vote).** Strawman: amend the invariant from *"one blessed graph per version"* to *"blessed components + a deterministic composer; each run freezes its assembled composition."* Replay guarantee restated: **same component-selection + same component-versions + same composer → same graph → same digest.** Tamper-evidence preserved by hashing the selection into the digest. Requires explicit ratification (Cora block-mode + Audra/Murat lockstep+audit input).

**DP3 — Brick contract.** Strawman: each component is a fragment under the (de-orphaned) `ModalityProducer`/`component_type_registry`, declaring {nodes, spine join-points, dependency_projections, produced_assets}. Add a `motion`/`video` modality (absent today). **Motion is the first brick** — its repair doubles as the brick-contract proof.

**DP4 — Composer + digest.** Strawman: a deterministic composer assembles selected fragments into the StateGraph at declared join-points; `compiled_graph_digest` payload gains `component_selection` (canonical-JSON, sorted) so replay re-assembles identically. Compiler generalizes "add all nodes" → "add selected fragments' nodes."

**DP5 — The 3 bundles.** Strawman: **B1 narrated-deck** (proven), **B2 deck+motion** (post-repair), **B3 deck+motion+workbook** (full). Composes exactly {deck, motion, workbook}; podcast/quiz stay shelf (honestly greyed in the conversation).

**DP6 — Workbook = design first.** Strawman: design what the companion workbook IS for the tejal lesson (sections, exercises, depth, transcript, cited research) BEFORE wiring the producer as a brick. It's mechanism-without-artifact today.

**DP7 — Capability-overlay 4th tier.** Strawman: extend the overlay tiers to {proven-&-wired, **proven-regressed-repairable**, mechanism-only-never-produced, shelf} so Marcus's "realistic given proven capabilities" call is honest (motion = regressed→repaired; workbook = mechanism→designed).

---

## 4. Honesty / risk carry-forwards

- Compose-then-freeze MUST keep replay tamper-evident — the digest selection-hash is load-bearing (Murat to set the test floor: a tamper test that mutates the selection post-freeze → replay refuses).
- Motion repair is restore-known-good EXCEPT the in-graph motion-plan producer (historically an external YAML) — that one piece is genuinely new but small.
- Two-walk `production_runner` trap (`[[project_production_runner_two_walks]]`): resume/recover must read the frozen component-selection from the run, never re-default.
- NO MOCKS — real Kling/Gamma/ElevenLabs/DOCX; first-run-stands; frozen tejal corpus.

---

## 5. The question for the party

> Ratify the architecture + governance (DP1 tier/sequence; DP2 frozen-graph ceremony amendment; DP3 brick contract; DP4 composer+digest; DP5 the 3 bundles; DP6 workbook-design-first; DP7 overlay 4th tier) as GREEN / GREEN-WITH-AMENDMENTS, or surface an impasse. Then authorize the BMAD epics/stories decomposition. Pressure-test hardest: **DP2 (does compose-then-freeze truly preserve the proven replay invariant?)** and **DP1 (is motion-first the right de-risking sequence, and is the composer Tier-3 Epic-boundary work?)**.

---

## PARTY RATIFICATION — 2026-06-25 (3/4 returned; Murat reproducibility pending, folds into Phase-5 composer test-floors)

**Outcome: GREEN-WITH-AMENDMENTS. No impasse.** Winston / John / Amelia returned GREEN-WITH-AMENDMENTS; Murat (reproducibility/test-floors) pending and gates the COMPOSER story (Phase 5), not motion (Phase 3).

**Unanimous:**
- **Motion-first, restored + ALONE** (no composer code in the motion story) — a real `.mp4` from a de-stubbed producer BEFORE any engine refactor. (Winston/John/Amelia.) Tier-2 branch-restore; this ratification is the before-dev gate.
- Story spine: **S1 motion brick (restore) → S2 composer+digest → S3 workbook brick → S4 3-bundle catalog (schema-shape/scaffold) → S5 Marcus-SPOC front door** (Amelia). DP5 bundles = B1 deck / B2 deck+motion / B3 deck+motion+workbook.

**Blocking amendments (Winston) if/when the composer (S2) is built:**
1. Digest: canonicalize hash input (sorted node_ids + sorted edge_tuples) AND extend to {component_selection, per-component_version, composer_version} — version coverage is load-bearing for TAMPER, not just replay.
2. Resume AC: the continuation/resume walk REHYDRATES `component_selection` from the frozen record and NEVER re-composes (the two-walk trap — highest-risk item).
3. Composer FAILS CLOSED on unresolved dependency_projection or cycle; no partial graph reaches freeze.
4. DP3 reframe: not "independent fragments" — a **typed producer→consumer DAG** (motion consumes the deck's slides; workbook consumes deck+narration); composer topo-sorts on `dependency_projections` resolved against `produced_assets`.
5. + Amelia: byte-identity regression (deck-only selection → byte-unchanged deck artifact + unchanged deck-subset digest); no v4.3 render bump (Tier-2-without-render-change; re-confirm at S2 close).

**Scope/phasing finding (John, strong; Winston concurs via the "N static blessed manifests vs composer" boring-tech option):** the full 3-bundle + composer + workbook live proof is unlikely to fit 6h (it is ~3 epics). B3 cannot enter an HONEST front-door recommendation until the workbook is DESIGNED+proven (Marcus confirms vs *proven* capabilities). Working resolution: pursue the goal in the ratified sequence; treat **motion + front-door on B1/B2 as the high-confidence first milestone**; workbook/B3 + the general composer follow. Composer-vs-static-manifests is a **spike gate at S2 open** (Winston A5): overlay/DP7 is in the operator's locked scope → tips toward the composer, but if time-pressed the static-manifest path proves the same front-door thesis with far less risk. **Operator owns any reduction of the 3-bundle DONE bar** — surfaced, not silently dropped.

**AUTHORIZED:** motion-first dev (S1) opens now under NEW CYCLE. Composer (S2) opens after the S2-open spike gate.

### Murat (4th voice) — GREEN-WITH-AMENDMENTS (binding; closes the round 4/4, no impasse)
Composer/digest (Phase 5) binding floors:
1. Digest hashes the **content-addressed compile-input CLOSURE, two-part**: `input_closure_digest` = H(canonical(component_selection) ⊕ per-fragment **content-hashes (bytes, NOT version labels)** ⊕ composer_version ⊕ model_config closure ⊕ pack/frozen_graph_version ⊕ digest_schema_version) + the existing `composed_graph_digest` (node_ids ⊕ edge_tuples ⊕ versions ⊕ dispatch_snapshot). Composition is a pure function input_closure→composed_graph; same input_closure MUST yield same composed_graph (a test assertion).
2. RED-first floors before S2/S5 flip done: (a) determinism across ≥3 process-restarts × PYTHONHASHSEED∈{0,random}; (b) tamper-refusal ×3 incl. **fragment-byte mutation WITHOUT version bump → replay RAISES** (the proof of content-addressing); (c) differential composition B1/B2/B3 distinct on both digest parts + topology + structural assertions (motion-bundle contains motion nodes); (d) motion floors below.
3. Governance: `digest_schema_version` bump + ceremony change = Tier-2 party-consensus; add composer/catalog/fragment-dir/digest to block_mode_trigger_paths; replay-from-audit test (persist full input closure, re-resolve → recompute → equals recorded); extend frozen-at-ship from packs to fragments/bundles; two-walk side-effect assertions.

**MOTION (S1) binding floors (Murat d, usable now, NO MOCKS):** (d-i) BUG-REPRO RED: starved/empty motion_plan → kira RAISES (today silently returns {"slides":[]}); (d-ii) HAPPY: real motion_plan → real `.mp4` on disk, non-zero bytes, duration>0, valid container; (d-iii, post-composer) composition→motion contract: a motion-bearing bundle's motion node receives a non-empty plan or fails loud.
