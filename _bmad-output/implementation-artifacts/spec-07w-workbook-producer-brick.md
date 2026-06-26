# Spec — 07W In-Graph Workbook Producer Brick (composition-catalog B3)

**Status:** ready-for-dev (NEW CYCLE: dev T1–T10 → Claude T11 → live B3 re-run → party re-concurrence).
**Class:** S (substrate — pipeline-manifest topology + new specialist + composer fragment). Tier-2 *within-lineage* (witness-regen, NOT v4.3). **Mirrors the just-shipped 07D.5 motion brick exactly.**
**Branch:** `fidelity-perception-arc-2026-06-19`.
**Mandate:** the party's UNANIMOUS binding caveat on B3 (Murat C2 / Winston / John / Marcus) + operator directive 2026-06-26: *the workbook must be produced IN-GRAPH as part of a composed B3 run.* Today 07W is a no-op stub (`specialist_id=None`); the real workbook is only produced out-of-band by `scripts/utilities/produce_tejal_workbook.py`.

## 1. Goal & scope
Replace the composer's synthetic 07W stub with a REAL in-graph workbook specialist node that runs `WorkbookProducer.produce()` from the running run's graph state and **emits the DOCX + canonical MD in-graph** (a `ProducedAsset` on RunState + files under `_bmad-output/artifacts/workbooks/`). A composed `ComponentSelection(deck,motion,workbook)` B3 run must produce the workbook inside the pipeline.

**In scope (v1 — closes the binding caveat):** new `workbook_producer` specialist (9-node scaffold, deterministic, NO LLM); 07W as a real manifest node; composer fragment owns 07W (remove synthetic stub); registration + witness; the node's `_act` ports the PROVEN input-assembly from `scripts/utilities/produce_tejal_workbook.py` adapted to read the *running* run's state; RED-first tests.

**Out of scope (named follow-ons, do NOT claim):** word-form-numeral audit (`braid-workbook-wordform-numeral-gap`, Gap 6 — symbol-only tokenizer; tejal is word-form-heavy → DO NOT over-claim G1 numeric coverage); fully general arbitrary-corpus spec authoring (v1 reuses the proven tejal/corpus-assessment assembly; generalizing the lesson-plan→WorkbookSpec adapter to any corpus is a follow-on); S3 live-research `research_entries` (deferred).

## 2. Design — deterministic in-graph adapter over the PROVEN recipe
The node is **deterministic, NO LLM** (mirror motion_planner). Its `_act` REUSES the proven assembly in `scripts/utilities/produce_tejal_workbook.py` (`build_tejal_workbook_inputs` + `_load_segments` + `_exercises` + further_reading/objectives/answer_keys assembly), **re-pointed to read the CURRENT run** instead of a hardcoded B1 run:
- `segments` ← the running run's segment manifest (`exports/segment-manifest-storyboard-b.yaml` / irene_pass2 node 08 output) via `load_transcript_segments`.
- `source_text` / corpus ← the running run's `bundle/extracted.md` (+ delivered narration).
- `spec` (WorkbookSpec) + `learning_objectives` + `answer_keys` + `further_reading` + `citations`/`source_ref_manifest` ← assembled deterministically from the corpus assessments (`assessments/chapter-*-knowledge-check.md`) + lesson plan, as the proven script does (Gap 3 KC-ingest + Gap 7 spec-authoring reused).
- Then `WorkbookProducer.produce(...)` → `compose_workbook` → MD + DOCX + G1/G2/AC audits → `WorkbookSidecar`.
Output: write MD+DOCX (producer already does, output-root contained) + put the `ProducedAsset`/sidecar refs on RunState. **Terminal leaf** — no downstream consumer (does not feed compositor; emits sidecar artifacts only).

## 3. Manifest change (`state/config/pipeline-manifest.yaml`)
Add a REAL node `07W` (07W must be a manifest node, NOT synthetic, so dispatch routes to it). Mirror 07D.5/07G:
```yaml
  - id: "07W"
    label: "Companion Workbook Producer"
    specialist_id: "workbook_producer"
    scaffold_node: "act"
    model_config_ref: null            # deterministic, NO LLM
    dependency_projections:
      segment_manifest: { from: irene, key: segment_manifest }   # irene pass-2 / node 08
      lesson_plan:      { from: irene-pass1, key: lesson_plan }
      bundle_reference: { from: texas, key: bundle_reference }    # corpus locator
    gate: false
    sub_phase_of: "07"
    insertion_after: "15"             # terminal sidecar, after operator handoff
    hud_tracked: true
    pack_section_anchor: "7W)"
    pack_version: "v4.2"
    rationale: >-
      In-graph companion-workbook producer (braid S2). Deterministic (no LLM):
      reads the run's segment manifest + lesson plan + corpus, runs WorkbookProducer
      to emit the DOCX + canonical MD as a terminal sidecar (does not feed
      downstream). Internal producer→sidecar; topology refinement within the v4.2
      lineage (witness regenerates; frozen v4.2 untouched) — mirrors 07D.5/07G.
```
`<<DEV: confirm the exact upstream keys for segments/lesson_plan/corpus from the run state — verify against the running run's actual contribution shapes (the motion brick taught us live shapes differ from fixtures; instrument if needed). Edges: attach 07W after node 15 per the composer attach_after.>>`

## 4. Composer change (`app/marcus/lesson_plan/composition.py`)
- `workbook` ComponentFragment: `manifest_node_ids=frozenset({"07W"})`; **remove `synthetic_nodes=(_workbook_stub_node(),)`** and the `_workbook_stub_node()`/`WORKBOOK_STUB_NODE_ID` stub (07W is now a real manifest node owned by the fragment). Keep `depends_on=("deck",)`, `attach_after`/insertion handled via manifest `insertion_after: 15`.
- Deck-only / deck+motion selections must still prune 07W (workbook deselected) and stay **byte-identical** to baseline. If 07W's dependency_projections name producers in always-present components (irene/texas), pruning works because 07W itself is removed when workbook is deselected. Confirm OPTIONAL_PROJECTION_KEYS not needed (07W is removed as a unit, not a kept node reading an absent producer).

## 5. Specialist scaffold + registration (mirror motion_planner)
- New `app/specialists/workbook_producer/{__init__,graph,state,_act,payload_contract,model_config.yaml,config.yaml}` — 9-node scaffold; `plan()` records the trail (no LLM call); `_act` = the §2 adapter; `payload_contract.CONSUMED_PAYLOAD_KEYS`.
- `state/config/dispatch-registry.yaml`: `workbook_producer: app.specialists.workbook_producer.graph:build_workbook_producer_graph`.
- `app/models/state/specialist_summary_artifacts.py`: add `"workbook_producer"` to `CANONICAL_SPECIALIST_IDS` + `DISPLAY_NAMES["workbook_producer"]="Workbook Producer"` (the emit_spans roster — motion_planner hit this; DO NOT skip).
- `skills/bmad-agent-marcus/references/specialist-registry.yaml`: add a `workbook_producer` row.
- Regenerate `state/config/capability-overlay.yaml` (`workbook_producer: wired`) + the `-gen` witness; L1 lockstep checks 9+10 green. Same commands as the motion brick (see `spec-07d5-motion-planner-producer.md §6`).

## 6. RED-first test floors
1. **In-graph production** — given fixture run-state (segment manifest + corpus + lesson plan), the `workbook_producer` node `_act` emits a real DOCX + MD + a `ProducedAsset` on state (no LLM client touched — assert).
2. **Composer prune symmetry** — workbook deselected ⇒ 07W absent; deck-default + deck+motion compositions **byte-identical** to baseline (mirror the motion floor).
3. **Manifest/registration parity** — 07W in manifest with `specialist_id=workbook_producer`; dispatch-registry + capability-overlay + CANONICAL_SPECIALIST_IDS all carry it (emit_spans won't crash).
4. **Terminal-leaf** — 07W has no outgoing edge (does not feed downstream); failure is recoverable (dispatch-family error).
5. **Producer reuse** — the node calls the real `WorkbookProducer.produce()` (not a reimpl); the existing producer AC suite stays green.
6. **L1 lockstep** checks 9 + 10 green; within-lineage witness regen; frozen v4.2/v5 untouched. pack_version uniform.

## 7. Definition of done (goal gate)
A fresh composed **B3** run (`--bundle narrated-deck-with-workbook`) reaches `completed` AND **produces the workbook DOCX in-graph** (the run's RunState carries the workbook `ProducedAsset`; the DOCX exists, written during the run, not out-of-band). Then the fully-spawned party **re-concurs on a clean completion decision** (the binding 07W caveat closed). Honest caveats recorded: word-form-numeral gap (Gap 6) named-deferred; general arbitrary-corpus spec authoring is a follow-on.

## 8. Landmines (from the surface map)
- **Live upstream shapes differ from fixtures** (the motion brick's #1 lesson — the producer's resolver had to match quinn_r's real `selections` shape). Instrument the workbook node's inputs on the first live B3 run; expect to fix the segment/corpus/lesson-plan resolution to the REAL run-state keys.
- **07W must be a real manifest node** (not synthetic) or dispatch won't route to it.
- **emit_spans roster** — add `workbook_producer` to CANONICAL_SPECIALIST_IDS (the exact crash motion_planner hit live).
- **Reuse stamp (DP6)** — workbook-only diff justifies reuse; ensure the node's diff_files handling doesn't force a spurious fresh-gamma.
- **Do NOT over-claim G1 numeric fidelity** — symbol-only audit; tejal is word-form-heavy.
