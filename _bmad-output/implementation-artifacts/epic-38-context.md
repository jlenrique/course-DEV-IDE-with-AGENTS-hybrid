# Epic 38 Context: Research asks & pipeline reorder (Tracy + Texas)

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Make workbook research **demand-driven by the workbook's own abilities** instead of a generic upfront sweep. Two distinct research asks — never smeared together: **Ask A** (concept/narrative enrichment, inward-deepening) builds a cited, credibility-tiered knowledge pool on the lesson's own concepts, feeding both the deep-dive prose and the glossary from one shared pass; **Ask B** (hot-topics/trends, forward-expanding) is a separate, late, narrowly-scoped Tracy call feeding the Door-Ajar beat. The production graph is extended with a terminal "workbook band" of nodes so research follows the abilities (finest-grained last), while the existing generic upfront research mint stays untouched for its current consumers. This epic is **graph-topology + intake-contract surgery, not a simple reorder**, and it is the enabler for the deep-dive enrichment, glossary, and trends stories in Epics 37/39.

## Stories

Per binding amendments, Epic 38 was reshaped from the original 38.1–38.3 draft into:

- Story 38.0 (NEW): Two-packet intake contract — generalize `research_packet.py`, add both resolvers with witnessed digests (lands first)
- Story 38.1: Ask A — concept/narrative enrichment knowledge pool (fills node 07W.2)
- Story 38.2: Ask B — hot-topics / trends, late and scoped (fills node 07W.4)
- Story 38.3a: lesson_plan consume side — packet readers + cross-layer string-contract test (zero orchestrator diff)
- Story 38.3b: orchestrator side — the 4-node workbook band, 07W re-point, runner hooks, two-walk parity, lockstep additions

## Requirements & Constraints

- **Ask A** produces a cited, credibility-tiered knowledge pool scoped to the lesson's key concepts/terms, consumed by the deep-dive enrichment and available to the glossary — one pass, one shared SSOT via the research-packet intake idiom. Rows missing provenance/`source_ref` are skipped into `known_losses` (never invented); empty-honesty when no usable rows.
- **Ask B** is a **separate Tracy call, run last**, scoped to the promised abilities (and the pre-work scene when possible). Ungrounded/injected topics are marked `unusable` (existing `reject_model_prior_topic` mechanism). Trends must be bounded and honest — no forecasting theater; empty-honesty when thin.
- Runtime order: ratified LOs → pre-work scene/friction → deep-dive skeleton → Ask A → check → Ask B (last) → compose. Ask B is distinct from the upfront generic research wiring at node 04.55 — the generic mint is NOT the source for these consumers.
- **Anti-fabrication is non-negotiable:** research content only from credible sourced expert knowledge, never model priors; every enriched claim must be citable downstream (G2 gate: `unsourced_citations == 0`).
- **Pipeline lockstep applies:** any change to the graph order or `block_mode_trigger_paths` requires party consensus (already granted via the ratified graph-shape round) and the regime doc read at T1; the lockstep checker must pass.
- Goldens must run offline (deterministic stubs); evidence on the frozen tejal Part-2 deck.

## Technical Decisions

- **Ratified node topology — a terminal workbook band appended after node 15 (operator handoff):**
  - `07W.1` Pre-work + deep-dive skeleton (leashed LLM, `model_config`) — emits briefs + bolded term set
  - `07W.2` Ask A enrichment (orchestrator wiring, model-free) — Tracy+Texas scoped to 07W.1 terms → Ask-A packet
  - `07W.3` Enrichment + Check + Reflection (leashed LLM)
  - `07W.4` Ask B hot-topics (orchestrator wiring, model-free) — separate late Tracy call → Ask-B packet
  - `07W` terminal render leaf — **UNCHANGED**; its no-model-client pin is load-bearing and stays intact (deterministic-consume only)
- **Three packets, three digests, one witness rule each:** generic research at `04.55` (`research_wiring`, untouched) · Ask-A pool at `07W.2` (`ask_a_enrichment`, consumed by deep-dive enrichment + glossary) · Ask-B at `07W.4` (`ask_b_hot_topics`, consumed by Door-Ajar/trends). `research_packet.load_research_packet` is parameterized by `(specialist_id, node_id)` with today's `04.55` behavior as the default; add `resolve_for_enrichment_pool` (Ask A) and `resolve_for_hot_topics` (Ask B). Shape-pin tests assert each consumer witnesses its intended digest.
- **Layer boundary (M3 held):** `lesson_plan` (model-free) owns the `research_packet` generalization, resolvers, and consume-side readers; the **orchestrator layer** owns the manifest node band, runner hooks, Tracy+Texas dispatch, and live writer instantiation. Packets cross the M3 wall disk-mediated (same seam as 04.55). Story 38.3b is explicitly orchestrator-layer — NOT under the `lesson_plan` M3-safe blanket — with its own reviewer discipline.
- **Runner hooks keyed by node id, mirrored in BOTH production-runner walk bodies**, with a continuation-walk parity test (the band is reached only on the continuation walk, like 04.55).
- **Lockstep surface (Tier-2, new pipeline steps):** `pipeline-manifest.yaml` (4 node adds + 07W re-point) and `production_runner.py` are existing trigger paths; ADD the new orchestrator wiring module (e.g. `app/marcus/orchestrator/workbook_wiring.py`) and `app/marcus/lesson_plan/research_packet.py` to `block_mode_trigger_paths`. Pack tier = v4.2-lineage refinement (terminal-sidecar `sub_phase_of` nodes), NOT a v4.3 family bump; hold new learning-event types to zero; confirm at T1 with the regime doc.
- **Ownership boundary with Epic 37:** the `DeepDiveWriter(skeleton)` contract + deterministic stub is authored by Story 37.2a (lesson_plan); Story 38.3b only instantiates/positions it in node 07W.1. Skeleton creation = Epic 37; node positioning = Epic 38.
- Build 38.3b with deterministic stubs first to prove the topology offline; live writers land after.

## Cross-Story Dependencies

- **Build order (ratified DAG — sprint planning ingests this, not epic numbering):** `38.0 → 38.3b (band w/ stubs) → {36, 37.1, 37.2a, 37.3, 37.4 writers} → 38.3a → 38.1 → 37.2b → 39.1 → 38.2 → 39.2 → 40`.
- 38.1 (Ask A) must land before 37.2b (cited deep-dive enrichment) can enrich; Story 39.1 (glossary) re-points to the Ask-A digest.
- 38.2 (Ask B) runs last in the build order before render stories; Story 39.2 (trends/Door-Ajar) re-points to the Ask-B digest.
- 07W.1's leashed skeleton output scopes Ask A (leashed-on-leashed risk: a weak skeleton mis-aims Ask A — operator spot-check witness flagged).
- Any two agents touching the `workbook_producer/_act.py` render or the pipeline graph serialize by rule.
- Residual risks (non-blocking): two new live LLM calls in the workbook path (cost/latency; stubs keep goldens offline) · three-packet mis-resolution (digest shape-pins guard) · two-walk parity (both walk bodies + parity test).
