# Spec — Braid S3 (Slice 1): Thin research wiring

**Status:** ready-for-dev
**Class:** S (substrate) · **Cycle:** NEW CYCLE (dev T1–T10 → Claude T11 `bmad-code-review` + close)
**Story key:** `braid-s3-research-wiring-thin`
**Authority:** `_bmad-output/planning-artifacts/braid-green-light-ratification-2026-06-24.md` (DP2(b), DP5, DP6, gates G2/G4/G6; Murat #5 named boundary) · strawman `braid-strawman-2026-06-24.md` (§3 DP2/DP7)
**Depends on:** Story 0 (stale Tracy registry line at `specialist-registry.yaml:130-136` — corrected; DP2(a)). **Does NOT block S1/S2.** S1 (collateral+research spec) and S2 (workbook producer) are the *upstream* and *downstream* of this wiring respectively; this story is the *connective tissue* and is sequenced after them in Slice 1 but is independently authorable.
**Defers:** Epic 17 (hypothesis-mode research) — explicitly out of scope; see §"v1-vs-v-next fence."

---

## 1. Problem (witnessed substrate gap)

The Irene→Tracy→Texas research-enrichment lane is **fully built and module-tested but integration-orphaned on the production trial path**. Confirmed by direct substrate read (2026-06-24):

- **The bridge exists and is exercised by tests.** `IreneTracyBridge.process_plan_locked` (`skills/bmad_agent_tracy/scripts/irene_bridge.py`) scans in-scope plan units for `IdentifiedGap`s and dispatches each to Tracy's posture selector; `emit_plan_lock_fanout` (`app/marcus/orchestrator/fanout.py`) calls it via the optional `bridge=` kwarg and records `bridge_results` onto the fanout envelopes. Contract tests: `tests/contracts/test_irene_tracy_bridge.py`, `tests/test_marcus_plan_lock_fanout.py`.
- **The facade exposes the seam but the trial path never feeds it.** `app/marcus/facade.py::run_4a` accepts `tracy_bridge: Any | None = None` (line 238) and threads it into `emit_plan_lock_fanout(..., bridge=tracy_bridge)` (line 305). **The production runner never calls `run_4a` and never constructs a bridge.**
- **The production runner has ZERO retrieval/Tracy references.** `app/marcus/orchestrator/production_runner.py` contains no `tracy`, no `IreneTracyBridge`, no `emit_plan_lock_fanout`, no bridge construction. The single Texas-adjacent line (1769-1770) is about the §02A directive-driven `dispatch_retrieval` re-fetch closing the trial-475 silent-bypass — **not** the gap-fill/enrichment lane.
- **Filed:** `tracy-gap-fill-lane-not-adopted-by-production-runner` (`_bmad-output/planning-artifacts/deferred-inventory.md:542-550`). This story is its reactivation. Per that entry's **"direction may flip if substrate evolves"** caveat, the attach-point decision is re-validated here (§3) rather than executed blindly.

**Net effect today:** no tracked trial can produce a cited research entry. Irene's research-enrichment goals (S1 content model) terminate at a fanout envelope with `bridge_status=None`; no Texas re-fetch ever fires on the trial path; the workbook (S2) has no cited entries to embed.

DP2 is **REFRAMED, not a rename** (ratification §2): exactly one Tracy (research-intent enricher), one Texas (retrieval dispatcher); the boundary is built. This story is **(b) wire the already-built bridge through `production_runner.py`** — the DP2(a) registry-line hygiene is Story 0 (done).

---

## 2. Deliverable

Pass the existing Irene→Tracy→Texas bridge through the production runner's node walk so that:

1. At plan-lock fanout on the trial path, Irene's in-scope research-enrichment gaps dispatch through `IreneTracyBridge` → Tracy posture selection → a `RetrievalIntent` (`skills/bmad-agent-texas/scripts/retrieval/contracts.py`).
2. The `RetrievalIntent` is dispatched to Texas (`dispatcher.py`) against the **live** Scite / Consensus retrieval adapters → `TexasRow`s with real `source_id` / `source_origin` / `provider`.
3. Each accepted `TexasRow` becomes a **cited research entry** carrying a `source_ref` (the canonical provenance handle mandatory across schemas) made available to the S2 workbook producer for embedding.
4. The run record is stamped with the **L2 fail-mode citation report** + a **citation→source_ref→source-hash manifest** (§G2).

### 2.1 The TWO-WALK constraint (BINDING — memory `project_production_runner_two_walks`)

`production_runner.py` has **two independent node walks**:

- **Start walk** — `run_production_trial` (~line 1751). Iterates `manifest.nodes`; **stops at the first gate, G1** (`_pause_at_gate`, line 1882). Reaches only pre-G1 nodes.
- **Continuation walk** — `_continue_production_walk` (~line 2259), shared by `resume_production_trial` (~2068, post-verdict) and `recover_production_trial` (~2181, post-error-pause). Handles **all gates after G1, including G2B and everything downstream.**

**Gate-pause side-effects added to only one walk silently never fire for later gates.** Live precedent is in-tree: the storyboard/chooser publishers had to be added to BOTH walks (start walk lines 1847-1859; continuation walk lines 2349-2366, comment at 2356-2360: *"G2B is ALWAYS reached via this continuation walk … MUST publish here too — not only in the start walk"*).

**Therefore:** the research-wiring hook (bridge construction + fanout-with-bridge dispatch + Texas re-fetch + cited-entry capture) MUST be attached at the **same logical node in BOTH walks**, OR provably reachable in exactly one walk with a test that proves it fires on a real continuation. The dev agent decides the attach-node in T1 (§3) and the AC-D2 parity test below enforces the both-walks invariant.

---

## 3. Build contract

### 3.1 Attach point (decide in T1, validate against substrate)

The designed trigger per Epic 28 is **plan-lock (§04.55 / G1.5-lock)** — the fanout point. Two viable attach mechanics; the dev agent picks one in T1 and records the rationale:

- **(A) Runner-wired at the fanout node.** The runner constructs the bridge and invokes the fanout-with-bridge at the existing plan-lock/fanout boundary on the trial path, mirroring `facade.py::run_4a`'s `emit_plan_lock_fanout(..., bridge=tracy_bridge)` call. Preferred if a fanout/plan-lock node is already in the manifest walk.
- **(B) Manifest Tracy node.** Add a node between §04.55 and §08 whose handler performs the dispatch. Heavier (manifest is a `block_mode_trigger_paths` member → lockstep regime + pack-version governance applies). **Only if (A) is not reachable** — and if chosen, this escalates to a Tier-2 pack bump requiring party consensus (see §Governance), so prefer (A).

**Whichever is chosen, the side-effect must be present in BOTH the start walk and the continuation walk** per §2.1 (or proven single-walk-reachable by test). Plan-lock/G1.5 sits at/near G1, so the attach node is plausibly reached differently across the two walks — this is exactly the trap §2.1 names. Verify empirically; do not assume.

### 3.2 Bridge → Texas dispatch path

- Construct `IreneTracyBridge(posture_dispatcher=...)` with the real Tracy posture dispatcher (`app/specialists/tracy/posture_dispatch.py` / `_act.py`), not a stub.
- Feed the locked plan via the existing `_plan_dict_for_bridge` shape (`fanout.py:67-93`) — already maps `LessonPlan` → bridge-expected `{"units": [...]}`. Reuse; do not re-derive.
- Tracy produces `RetrievalIntent` JSON (`tracy/_act.py` system message: *"Shape Irene Pass-2 research needs into Texas-compatible RetrievalIntent JSON"*). Each intent's `provider_hints` names live adapters (`scite`, `consensus`).
- Dispatch each `RetrievalIntent` through `dispatcher.py` against the registered live adapters (`scite_provider.py`, `consensus_provider.py`). Honor `iteration_budget` / `convergence_required` as authored — do not override.
- Collect accepted `TexasRow`s; each becomes a cited entry. The `source_ref` is derived from the row's stable identity (`source_id` + `provider`); see §3.3.

### 3.3 Cited-entry → source_ref → source-hash

- For each accepted `TexasRow`, mint a **cited research entry** record: `{citation_id, source_ref, provider, source_id, title, source_hash}`.
- `source_ref` = the canonical provenance handle the run already uses for corpus sources; for retrieved rows it is a deterministic function of `(provider, source_id)`. **No invented refs** — a citation with no backing `TexasRow` in this run's retrieval set is a hard failure (§G2).
- `source_hash` = a content hash over the retrieved row body/identity, recorded so the manifest is auditable and the L2 channel can classify retrieved figures.
- Make the accepted entries available to the **S2 workbook producer** via the run record (the producer consumes them as `research_supplements` per §3.4). The exact handoff key is a thin contract between S2 and S3 — name it `research_entries` on the run record and pin it with an AC-D test.

### 3.4 L2 wiring (citation channel — fail mode)

`app/specialists/_shared/source_fidelity_audit.py::audit_numeric_provenance` is **numeric-only + WARN-ONLY today** (confirmed: it only ever RETURNS a report dict, `status` ∈ {`AUDIT`, `FAIL`(zero-denominator only)}; it NEVER raises/gates on drift; the semantic leg is an explicit STUB, `SEMANTIC_TRIPWIRE = None`). The `research_supplements: set[str] | None` param is the **citation-acceptance channel**: figures present in declared supplements classify as `research_supplement` (legitimately-sourced), NOT as drift.

This story does **NOT** change the warn-only numeric engine. Instead it adds a **thin citation-fidelity check run in FAIL mode** at the run-record assembly point:

- Feed every retrieved cited entry's surfaced figures into `audit_numeric_provenance(..., research_supplements=<declared retrieved figures>)` so retrieved research figures classify as `research_supplement`, not `unsourced_numeric` drift. (This is the channel the L2 spec left open as a stub — S3 populates it for retrieved research only.)
- Separately compute **`unsourced_citations`** = count of workbook/run citations whose `source_ref` does NOT resolve to a `TexasRow` (or corpus source) in this run's retrieval set. **Gate: `unsourced_citations == 0` (FAIL mode — a single unsourced citation is RED).** This is a NEW, citation-facing check; it is NOT the numeric drift rate and must not be conflated with it.
- Attach to the run record: (1) the L2 numeric report (warn, unchanged) and (2) the **citation manifest** (`citation_id → source_ref → source_hash`) + the `unsourced_citations` count.

### 3.5 Frozen-Gamma reuse (DP6)

Research wiring is **slide-independent** (DP6: ratification §2). The dev-agent and the live run operate under the DP6 path-intersection gate: `fresh_gamma_required := (git diff --name-only <base>..<head>) ∩ slide_production_paths ≠ ∅`. This story touches `production_runner.py`, `fanout.py`-adjacent wiring, and the retrieval/L2 modules — **none in `slide_production_paths`** (v4.2 pack, generator, Pass-1 clustering, per-sub-slide A/B chooser, VO figure-grounding gate, Gamma adapter, numCards/text_mode). Therefore **frozen-Gamma reuse on `tejal-apc-c1-m1-p2-trends` is permitted**; the run record stamps `gamma: frozen, reuse_justified_by: empty-intersection@<sha>`. **Frozen-reuse runs are ineligible to assert deck no-regression** (recorded by construction). If T1 discovers the chosen attach mechanic touches a `slide_production_paths` file, DP6 flips to fresh-required — re-validate at T1.

---

## 4. Acceptance Criteria

ACs split **dev-agent** (verified via shipped Python deps, `pytest.skip(...)` when a live service is unreachable — per "verify via shipped deps, not operator CLIs") vs **operator-gated** (live-API evidence pasted into Completion Notes once). **No mocks; live APIs; first-run-stands; no retry-to-green** (G6).

### Dev-agent ACs (shipped-deps; skip-on-unreachable)

- **AC-D1 — Bridge constructed + dispatched on the trial path.** A test drives the runner's plan-lock/fanout step with a locked `LessonPlan` carrying ≥1 in-scope unit with a research-enrichment `IdentifiedGap`, and asserts `IreneTracyBridge.process_plan_locked` is invoked (bridge non-None on the fanout call) and produces ≥1 `bridge_result`. (No live API needed — bridge dispatch to the posture selector is local; use the real bridge + real posture dispatcher, not a mock.)
- **AC-D2 — TWO-WALK parity (BINDING).** A test proves the research-wiring side-effect is present in BOTH `run_production_trial` (start walk) AND `_continue_production_walk` (continuation walk), OR — if the attach node is reachable in exactly one walk — a test exercises a real continuation (resume/recover) and asserts the side-effect fires there. Mirror the storyboard/chooser publisher parity precedent (lines 1847-1859 vs 2349-2366). A grep-style structural assertion alone is insufficient; the test must execute the walk.
- **AC-D3 — RetrievalIntent shape conformance.** Tracy's emitted intents validate against `RetrievalIntent` (`provider_hints` non-empty, naming only registered live providers via `list_providers()`); a malformed intent raises `RetrievalIntentParseError` (no silent drop).
- **AC-D4 — Texas dispatch reached (skip-gated).** A test dispatches a Tracy-authored `RetrievalIntent` through `dispatcher.py` against the live Scite/Consensus adapters using the shipped MCP/HTTP client; `pytest.skip(...)` when `SCITE_USER_NAME`/`SCITE_PASSWORD`/`CONSENSUS_API_KEY` env unset or the service is unreachable. When it runs, asserts ≥1 `TexasRow` with non-empty `source_id` + `provider`.
- **AC-D5 — Cited-entry minting + source_ref derivation.** Given a `TexasRow`, the entry-minter produces `{citation_id, source_ref, provider, source_id, source_hash}` deterministically; `source_ref` is a pure function of `(provider, source_id)`; `source_hash` is stable across two calls on the same row.
- **AC-D6 — L2 citation channel: unsourced==0 in FAIL mode (the gate).** A test feeds a run record where every citation's `source_ref` resolves to a `TexasRow` in the retrieval set → `unsourced_citations == 0` → PASS; injecting one citation with a `source_ref` absent from the retrieval set → `unsourced_citations == 1` → the gate FAILS (raises/returns RED). This is the only NEW gating check; assert it is distinct from the warn-only numeric `drift_rate`.
- **AC-D7 — research_supplements channel populated, not drift.** Retrieved research figures passed as `research_supplements` to `audit_numeric_provenance` classify as `research_supplement` (counted in that bucket), NOT `unsourced_numeric`. Asserts `source_fidelity_audit.py` is called read-only (no signature change, no new state — frozen-engine discipline).
- **AC-D8 — Run-record handoff to S2.** The accepted cited entries are written to the run record under the agreed `research_entries` key in a shape the S2 workbook producer consumes; a contract test pins the shape.
- **AC-D9 — DP6 stamp.** When the diff∩`slide_production_paths` is empty, the run record stamps `gamma: frozen, reuse_justified_by: empty-intersection@<sha>` and is marked ineligible to assert deck no-regression. (Pure-Python predicate test on a fixture diff; no git invocation required in the dev-agent AC — see operator-gated AC-O3 for the live run.)
- **AC-D10 — No regression on the unwired path.** With no research-enrichment gaps (degenerate-empty / `collateral: none`), the runner behaves exactly as today: no bridge dispatch, no Texas call, no citation manifest beyond an empty-but-present section. Existing trial-path tests stay green.

### Operator-gated ACs (live-API; evidence → Completion Notes, first-run-stands)

- **AC-O1 — Live small-scale run produces ≥1 cited research entry (THE artifact witness).** On the frozen `tejal-apc-c1-m1-p2-trends` deck (frozen-Gamma reuse per AC-D9/DP6) with a predefined workbook spec + predefined research-enrichment goals (S1 content model), a live run dispatches through Tracy → Texas (live Scite/Consensus) → produces **≥1 cited research entry traced to a real `source_ref` linked to slide content.** Paste the entry + its `source_ref` + the linked slide reference into Completion Notes.
- **AC-O2 — L2 fail-mode citation report attached, `unsourced_citations == 0`.** The run record carries the L2 numeric report (warn) AND the citation manifest (`citation_id → source_ref → source_hash`) with `unsourced_citations == 0`. Paste the manifest + the count into Completion Notes. First-run-stands; a non-zero count is a real RED, not retried-to-green.
- **AC-O3 — DP6 stamp present on the live run record.** The live run record shows `gamma: frozen, reuse_justified_by: empty-intersection@<sha>`. Paste the stamp.
- **AC-O4 — Named operator spot-check (Murat #5 / G1 boundary).** See §5. Operator spot-checks claim↔source *support* faithfulness on the cited entry(ies). Record the verdict in Completion Notes.

---

## 5. Named boundary (Murat #5 / G1) — do NOT silently fold into L2

> **L2 proves the source EXISTS, not that it SUPPORTS the attached claim or grounds the named slide content.**

The `unsourced_citations == 0` gate (G2) is a **resolvability** check: every citation's `source_ref` resolves to a real retrieved row in this run's set. It does **NOT** verify that the cited source actually *substantiates* the claim it is attached to, nor that it grounds the slide content it is linked to. That claim↔source *support* faithfulness is, in v1, a **NAMED operator-gated spot-check** (AC-O4), explicitly held OUT of L2. The general semantic claim-citation audit is net-new/deferred (the L2 semantic leg is a documented stub, `SEMANTIC_TRIPWIRE = None`). **Do not claim L2 covers support faithfulness; do not silently extend the numeric/resolvability engine to assert it.** File the semantic claim↔citation audit as a deferred follow-on (§Deferred-inventory) rather than smuggling it into this gate.

---

## 6. v1-vs-v-next fence

| In scope (v1) | Deferred (v-next, in ink) |
|---|---|
| Wire the **already-built** Irene→Tracy→Texas bridge through `production_runner.py` (both walks). | **Epic 17 — hypothesis-mode research** (open-ended research generation). NOT this story. |
| Predefined research-enrichment goals (S1 content model) on frozen tejal. | Open-ended "state purpose → agents design the research" elicitation (Marcus interlocutor = S5, the arc finale). |
| Live Scite/Consensus dispatch; ≥1 cited entry; L2 fail-mode for **citation resolvability**. | **Semantic claim↔citation support audit** (the L2 semantic leg) — file as deferred follow-on; AC-O4 is the v1 stand-in (named operator spot-check). |
| `research_supplements` channel populated for retrieved figures. | Promotion of the warn-only numeric audit → gate (needs ≥3 runs per the L2 spec; untouched here). |
| Cited entries handed to the S2 workbook producer. | New retrieval providers / richer convergence. |

---

## 7. T1 Readiness (dev agent reads BEFORE any code)

Required readings at T1:
- **This spec**, the ratification (`braid-green-light-ratification-2026-06-24.md` DP2/DP5/DP6 + gates), and memory `project_production_runner_two_walks` (the TWO-WALK trap — load-bearing).
- `app/marcus/orchestrator/production_runner.py` — the two walks (`run_production_trial` ~1751, `_continue_production_walk` ~2259) and the storyboard/chooser publisher parity precedent (1847-1859 vs 2349-2366) as the template for both-walks side-effects.
- `app/marcus/orchestrator/fanout.py` (`emit_plan_lock_fanout`, `_plan_dict_for_bridge`) + `app/marcus/facade.py::run_4a` (lines 238/305 — the `tracy_bridge` kwarg seam to mirror).
- `skills/bmad_agent_tracy/scripts/irene_bridge.py` (`IreneTracyBridge`); `app/specialists/tracy/_act.py` + `posture_dispatch.py`.
- `skills/bmad-agent-texas/scripts/retrieval/` — `contracts.py` (`RetrievalIntent`/`TexasRow`/`ProviderInfo`), `dispatcher.py`, `provider_directory.py::list_providers`, `scite_provider.py`, `consensus_provider.py`.
- `app/specialists/_shared/source_fidelity_audit.py` (numeric-only + warn-only; `research_supplements` channel; semantic STUB).
- `state/config/pipeline-manifest.yaml::slide_production_paths` (DP6 predicate) and `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`; if the diff touches a `block_mode_trigger_paths` member, read `docs/dev-guide/pipeline-manifest-regime.md` (lockstep regime).

T1 decisions to record: attach mechanic (A runner-wired vs B manifest-node, §3.1) + both-walks plan; the `research_entries` run-record key shape (contract with S2); confirmation that the diff∩`slide_production_paths` is empty (DP6 reuse) or, if not, the fresh-Gamma plan.

**Velocity tiers (Slab-7c amendment carry):** `r_tier: R2` (wiring across an existing seam, no new schema family) · `t11_tier: standard` (cross-module integration touching the runner) · `lookahead_tier: 2` · `files_touched`: `production_runner.py`, a thin research-wiring module under `app/marcus/orchestrator/`, run-record assembly, a citation-manifest/L2-channel helper, tests. (Refine at T1 if the attach mechanic shifts the set.)

---

## 8. Governance + honesty gates (ride alongside)

- **G2 — Citation fidelity (PRIMARY gate here):** every workbook/run citation resolves to a real `source_ref` in this run's retrieval set; **L2 fail-mode, `unsourced_citations == 0`**; L2 report + citation→source_ref→source-hash manifest attached to the run record (AC-D6, AC-O2). Claim↔source *support* faithfulness = the named operator spot-check (§5/AC-O4), NOT silently assumed.
- **G4 — No reading-path halo:** this arc does **NOT** advance the reading-path fresh-naive-holdout. Close-out states so explicitly; no generalization claim rides on research-wiring work.
- **G6 — Believed-green discipline:** per-story acceptance is the **artifact witness** (AC-O1), never a green unit suite. No mocks; live APIs; first-run-stands; no retry-to-green.
- **Pipeline lockstep:** if the chosen attach mechanic (§3.1) edits any `block_mode_trigger_paths` member (e.g. the manifest under option B), the lockstep regime applies and a manifest/pack change is **governance, not technical** — a Tier-2 pack bump requires **party-mode consensus BEFORE dev opens.** Prefer option (A) to avoid this. If unavoidable, pause and convene party-mode.
- **Deferred-inventory bookkeeping:** on close, strike `tracy-gap-fill-lane-not-adopted-by-production-runner` (cite this spec) and **file the deferred semantic claim↔citation support audit** under §Named-But-Not-Filed Follow-Ons (the L2 semantic leg this story explicitly does not build).

---

## 9. NEW CYCLE handoff

Per ratification §5: party green-light (this doc, under the consolidated braid ratification) → **NEW CYCLE** (author `codex-dev-prompt-braid-s3-research-wiring-thin.md`; dev runs T1–T10 incl. T10 self-review; **Claude T11** runs `bmad-code-review` + commit + flips `done`) → small-scale live run (AC-O1..O4) → iterate. A light party concurrence pass confirms ready-to-implement before dev launch.
