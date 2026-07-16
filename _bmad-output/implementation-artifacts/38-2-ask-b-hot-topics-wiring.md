---
id: 38-2
epic: 38  # re-homed to the Epic-39 wave 2026-07-15 (wave-3940 party record §D1); key kept verbatim
key: 38-2-ask-b-hot-topics-wiring
status: ready-for-dev
anchor_provenance: post-39-1b tree at commit 72e17a05
---

# Story 38.2: Ask B — hot-topics wiring (`ask_b_hot_topics@07W.4`)

Status: ready-for-dev

## Story

As the Marcus-SPOC workbook runtime,
I want `07W.4` to run one separate, LATE, narrowly-scoped hot-topics research pass bound to the beat-③ abilities (and the scene when possible) and mint the Ask-B packet with its own witnessed digest,
so that 39.2 can render a finely-focused, honest Door-Ajar — never a discipline survey, never model-prior forecasting theater, and never a smear of the Ask-A or generic `04.55` research.

## Dependency Position

`38.0 → 38.3b → {36, 37.1, 37.2a, 37.3, 37.4} → 38.3a → 38.1 → 37.2b → 39.1 → 38.2 → 39.2 → 40.1`

All predecessors are done (39-1 and 39-1b are `done-awaiting-live-witness` per the D3 status vocabulary; their full-run witness is owed by batch run A and does not gate this story's deterministic work). This story activates the last reserved model-free coordinate in the terminal workbook band. It blocks Story 39.2 (Door-Ajar re-point — the sole consumer) and therefore 40.1.

## Provenance & Dependencies

**Re-home riders (BINDING — wave-3940 kickoff party record §D1, ratified 2026-07-15):**

- **Key stays verbatim** `38-2-ask-b-hot-topics-wiring` — never renumbered. Re-home = the story executes under the Epic-39 wave grouping; it remains cross-referenced by this key in the ratified DAG, the Epic-38 retro, the Epic-38 closure record, and the deferred inventory.
- **FR re-point (Murat M-D1-1):** FR16's Ask-B leg + FR9 travel with this story and are asserted at the **Epic-39-wave close bar** (this story + 39.2 together deliver them). Epic 38's close claim remains "Ask-A + graph reorder delivered; Ask-B re-homed" — this story must never be cited as retroactively completing Epic 38's bar, and its own close never claims "FR9/FR16 fully delivered" (39.2 owns the render leg).
- **Contracts travel with specialist/node identity (Murat M-D1-2, Winston D1-1):** the binding contract keys are `specialist_id=ask_b_hot_topics`, `node_id=07W.4`, **own witnessed digest**, **39.2 sole consumer** — per the ratified Epic-38 graph-shape record. They key on specialist/node identity, not the story number. T1 MUST cite that record (see §T1 Readiness).
- **Original ACs travel intact:** separate LATE Tracy call scoped to the beat-③ abilities (and the scene when possible) · ungrounded/injected topics marked `unusable` via the existing `reject_model_prior_topic` idiom · empty-honesty (bounded, never fabricated; `known_losses` on thin results).
- **Tier-2 lockstep + regime doc:** the diff touches `block_mode_trigger_paths` rows; the Tier-2 consensus authority for this activation is the RATIFIED Epic-38 graph-shape record (party-mode 2026-07-12) — no fresh party round is required for the graph shape itself; this story's green-light round covers only the story spec.

**Paid-Run Economy Protocol (BINDING — wave-3940 party record §D3):** this story adds a NEW LLM/provider surface (the Ask-B dispatch). Therefore: component probe REQUIRED before boarding a governed run (`scripts/utilities/run_ask_b_38_2_live_evidence.py`, cloned from the `run_deep_dive_38_3a_live_evidence.py` pattern); **zero-witness rule** applies (probe → freeze → replay → spend — the probe output becomes the path's first witness fixture); a new `ask-b` witness family auto-enrolls in `tests/live_witness_replay/witnesses.yaml` **in this story's diff**; machine-asserted bars carry negative-witness pins; batch attribution + `done-awaiting-live-witness` vocabulary govern the run-B boarding (AC 9).

**Depends on (both landed and verified in the tree at `72e17a05`):**

- **38-0 resolvers:** `app/marcus/lesson_plan/research_packet.py` — `resolve_for_hot_topics(run_dir, require_usable=...)` exists (L345–355) and resolves exactly `ask_b_hot_topics@07W.4`; the three-digest distinctness pin already exists (`tests/unit/marcus/lesson_plan/test_research_packet_w1.py` L364).
- **38.3b band:** `app/marcus/orchestrator/workbook_wiring.py` — node `07W.4` is positioned LAST in the band (`WORKBOOK_BAND_NODE_IDS`, L124–129), currently backed by the honest-empty `_ask_b_stub` (L1198–1203); both production-runner walks already dispatch every band node with `dispatch_live=_research_dispatch_live()` (`production_runner.py` L3330–3336 and L4334–4340).
- **38.1 precedent:** `ask_a_enrichment@07W.2` activation — the direct structural precedent this story mirrors (journal, exclusive claim, replay, reconciliation table, exact-coordinate upgrade).

## Green-Light Round Record (2026-07-16)

**Verdict: 4/4 GREEN-WITH-AMENDMENTS** — Winston (architect), John (PM), Amelia (dev), Murat (test architect); orchestrator concurred. Party-consensus-=-approval per the CLAUDE.md solo-operator rule (fully-spawned party consensus + orchestrator agreement proceeds without a redundant human Checkpoint-1 hold; operator may override asynchronously). All amendments folded below; per-id fold map:

| Finding id(s) | Amendment | Folded at |
|---|---|---|
| W-1, J-1, M-6, M-8, A-2 (unanimous) | Strict-reader conditional → DECIDED MANDATE: strict Ask-B reader branch at exact `ask_b_hot_topics@07W.4` IS added this diff, with the declared 38-1 AC 4 pin flip; machine reason M-8 (AC 9 credibility-fields negative pin unsatisfiable under lax reader) | AC 3 (reader-side strictness bullet) |
| Murat ruling-d | Honest flip shape — named 5-item discipline block (conscious same-diff flips w/ rationale; mirrored strict-fail-loud tests; generic-`04.55` unchanged-leniency re-pin; lockstep row flip; 38-1 closure cross-ref note owed at close) | AC 3 (discipline block) |
| W-4 | `research_packet.py` lockstep row LIKELY-TOUCHED → **TOUCHED** | §Lockstep declaration table |
| W-2, M-4 | Resume-skip hardening: BOTH-direction pins (upgrade row + completed-resume no-op as its own matrix row); named set-membership pin (reconcile-not-skip set == exactly `{07W.2, 07W.3, 07W.4}`); upgrade test runs with `factories is None`, dispatch monkeypatched only at the owned `ask_b_research_wiring` seam | AC 6 (resume-skip hardening block) + I/O matrix rows 7/9 |
| W-3, A-1, A-5 | Demand-model completeness: scene-absent branch DECIDED (`ready` with recorded scope loss — optional enhancement, never blocking retryable); closed Ask-B loss→status lattice enumerated pre-dev (Ask-A's 6-loss map does not transfer); deterministic ability-association basis stated explicitly (new design, row → vow index/id association minted at intent-composition time, digest-covered) | AC 1 (three new bullets) |
| M-1, M-2, M-3 (+ M-4 row) | Matrix expansion: kill-switch-OFF, credentials-absent, `call_in_progress` ambiguous pause, completed-journal roll-forward, split-brain, demand-invalid, scope-overflow, barrier two-worker, completed-resume no-op | Deterministic I/O matrix rows 9–17 |
| M-5, J-2 | Probe verdict licensing: `completed_empty` = VALID seam witness, usable-mint half of the claim stays OPEN; run-B boarding on empty probe requires explicit governed acknowledgment line; operator note re empty-honest Door-Ajar at 39.2 | AC 9 (component probe, pre-declared verdict-class rule) |
| M-7, A-4 | Parity via PARAMETRIZING the existing 38-1 both-walks parity module over `{07W.2, 07W.4}` (never a hand-cloned suite); `reject_model_prior_topic`-vs-Ask-B pin in a NEW module (not `test_trends_w3.py`) so 39-2's re-point opens conflict-free | AC 7 (module-hygiene bullets) |
| A-3 | Traceability table declares band-wiring stub-pin flips (`test_workbook_band_wiring.py` L294 `ask_b_not_yet_wired` pin + `_ask_b_stub` identity assertions) as conscious enumerated flips | AC 9 (deterministic bullet) |
| A-6 | `ask-b-hot-topics-call.v1` = FIRST Scite-canonical band research-call family; expect a small shape delta from the three existing per-family modules, not a pure mirror | Dev Notes §Witness-family enrollment plan |
| J-3 | 39-2 handoff rider: closure record + deferred-inventory/39.2 grooming note name 39.2's inherited obligations (`trends_inputs_from_run` re-point, post-re-point `reject_model_prior_topic` pin, FR16/FR9 wave-close assertion) | AC 9 (handoff rider bullet) |
| Amelia (size) | Size honesty recorded: demand model+resolver = M (new lattice, not a mirror); story overall = L (full 38-1-scale replay at new coordinates) | Dev Notes §Size honesty |

## T1 Readiness (BINDING)

The dev agent MUST read, in order, before any code:

1. `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` — §"Epic 38 graph-shape decision (party-mode 2026-07-12) — RATIFIED" (node topology; the three-packets/three-digests table pinning `ask_b_hot_topics@07W.4` with 39.2 as sole consumer; layer boundary; lockstep surface) + §"Story 38.2" (the two original ACs) + §"Story 38.3" AC 2 (Ask B is a late narrowly-scoped Tracy pass **distinct from the upfront `04.55` mint**).
2. `_bmad-output/planning-artifacts/wave-3940-kickoff-party-record-2026-07-15.md` — §D1 (re-home riders) + §D3 (Paid-Run Economy Protocol: all six planks + seven amendments; the zero-witness rule, probe honesty contract, negative-witness pins, batch attribution, status vocabulary).
3. `docs/dev-guide/pipeline-manifest-regime.md` — the diff touches `block_mode_trigger_paths` rows (see §Lockstep declaration); Cora block-mode classification runs before closure.
4. `_bmad-output/implementation-artifacts/38-1-ask-a-enrichment-wiring.md` — the direct precedent story: mirror its AC shape (immutable pre-call scope vs post-call execution evidence; crash-safe journal; reconciliation table; exact-coordinate activation; both-walks visibility).
5. Landed substrate (real anchors, re-verify at T1):
   - `app/marcus/orchestrator/workbook_wiring.py` — `_ask_b_stub` (L1198–1203); `DEFAULT_WORKBOOK_BAND_FACTORIES` (L1206–1211); the exact-coordinate skip set at L1566–1571 + L1693 (**07W.4 is NOT in the reconcile-not-skip set today** — see AC 6); the Ask-A dispatch branch (L1832–1843) and Ask-A replace/reconcile blocks (L1737–1768, L1941–1978) to mirror.
   - `app/marcus/lesson_plan/research_packet.py` — `resolve_for_hot_topics` (L345–355); the Ask-A-only strict-validation branch (L195–207); `_empty_packet`/losses/status machinery.
   - `app/marcus/orchestrator/ask_a_research_wiring.py` — the whole module (journal/lock filenames L37–38; `_build_intent` L105–131; `_default_dispatch` L134–138; `run_ask_a_research` L388–493).
   - `app/marcus/lesson_plan/ask_a_enrichment.py` — the strict contract family to mirror (scope/receipt/intake/entry/output; dispositions).
   - `app/marcus/lesson_plan/research_demand.py` — `resolve_enrichment_demand` + `AskAResearchDemandV1` (L67–152): **there is NO Ask-B demand resolver today**; this story adds one (AC 1).
   - `app/marcus/lesson_plan/trends_projection.py` — `reject_model_prior_topic` (L173–212), `project_trends_from_packet` (L215–302), and `trends_inputs_from_run` (L305–319, still reading the generic `04.55` packet — 39.2 re-points it, NOT this story).
   - `app/marcus/orchestrator/production_runner.py` — both band walk sites (L3325–3354 start walk; L4334+ continuation walk) and the sole `_persist_envelope` writer.
   - `state/config/pipeline-manifest.yaml` — node `07W.4` (L1064+: `specialist_id: null`, `model_config_ref: null`, model-free) and edges `07W.3 → 07W.4 → 07W` (L1159–1160); `block_mode_trigger_paths` (L60–110).
   - `tests/live_witness_replay/witnesses.yaml` + `tests/live_witness_replay/registry.py` — the auto-enrolling registry the new `ask-b` family joins.
   - `scripts/utilities/run_deep_dive_38_3a_live_evidence.py` — the probe-script pattern to clone.

## Acceptance Criteria

1. **Beat-③ ability scope is the sole dispatch authority (separate LATE Tracy call)**
   - Add a strict disk-read Ask-B demand resolver (`resolve_hot_topics_demand(run_dir)` in `research_demand.py`, mirroring `resolve_enrichment_demand`'s strictness) that derives the scope from the ratified `07W.1` workbook-brief authority: the ordered beat-③ Promise ability vows (`pre_work.promise.vows` — `objective_id` + text) and, when available, the Scene identity (digest-bound), plus the workbook-brief payload digest. Ask-B does NOT bind bold terms or the deep-dive skeleton — it is ability/scene-scoped by design (narrower than Ask-A).
   - Dispatch only on a strict `ready` demand. Never reconstruct demand, scrape prose, infer keywords, use model priors, read another run, or fall back to `research_wiring@04.55` or `ask_a_enrichment@07W.2` — the Ask-B packet is minted by its own dispatch, distinct from the upfront `04.55` mint (epics §38.3 AC 2) and from Ask-A.
   - "Separate late Tracy call" binds to the landed substrate as: one NEW dispatcher invocation through the same Scite-canonical retrieval seam Ask-A uses (`_build_intent`-style `RetrievalIntent` + `dispatch_intent`), with its OWN journal, OWN lock, OWN idempotency key, and OWN scope digest — never reusing, reading, or mutating the Ask-A journal, the `04.55` bridge output, or their locks. It runs at `07W.4`, the LAST band node before the terminal render (manifest edges `07W.3 → 07W.4 → 07W`, already landed — no edge change).
   - Corrupt/forged/mismatched demand fails with `ask-b.demand-invalid`. Valid non-ready demand makes zero dispatcher invocations and emits a typed retryable output — never fabricated rows.
   - **Scene-absent branch is DECIDED (W-3/A-1):** an otherwise-complete brief without a Scene is `ready` WITH a recorded scope loss — visible in the demand receipt / packet `known_losses`. Per the original AC's "and the scene when possible," the scene is an optional enhancement, never a blocking retryable. No scene-absent demand ever emits `retryable_demand_not_ready` on that ground alone.
   - **Closed loss→status lattice enumerated pre-dev (A-1):** the dev agent enumerates the complete closed Ask-B demand-level loss→status lattice BEFORE implementation (which demand-level losses exist, and which map to `ready`-with-loss vs `retryable_demand_not_ready` vs `ask-b.demand-invalid`). Ask-A's 6-loss map at `research_demand.py` L131–138 is skeleton-digest-coupled and does NOT transfer — the Ask-B lattice is a new design, written down in the demand model, not inherited.
   - **Deterministic ability-association basis is explicit (A-5):** this is NEW design — there is no 38.1 precedent (the Ask-B demand carries vow text + optional scene, not bold terms/claim refs). The demand and packet MUST state the association rule the packet rows carry: each packet row carries a `supports_ability_ids` association minted from a row → vow index/id association established at intent-composition time (the intent's per-ability query segments are tagged with the vow `objective_id`; rows inherit the association from the segment that produced them), deterministic and digest-covered. If the dev agent finds a simpler deterministic rule consistent with the substrate, it may substitute it — but the rule must be SAID in the contract module docstring and covered by the scope digest, never left implicit.

2. **One deterministic Ask-B research pass, model-free coordinate preserved**
   - Exactly one dispatcher invocation per completed journal. Record dispatcher invocations separately from observable `ProviderResult.iterations_used`/refinement logs/receipts; never claim an unobservable HTTP-call count. No retry loop.
   - The canonical query and structured intent carry the complete ordered ability scope (+ scene identity when present). If the effective query limit cannot carry it, fail before dispatch with `ask-b.scope-overflow`; never truncate, drop, reorder, or silently partition scope.
   - Reuse the existing `dispatch_live` posture threaded by both runner walks (`_research_dispatch_live()`). Kill-switch OFF is a typed retryable zero-call output. `07W.4` remains manifest model-free (`specialist_id: null`, `model_config_ref: null` — verified in the manifest at L1064+): it owns no workbook-writer LLM configuration, and this story changes ZERO manifest lines.

3. **Strict, evidence-bearing Ask-B contract with its own witnessed digest**
   - Add frozen, extra-forbid lesson-plan models mirroring the Ask-A family (new `app/marcus/lesson_plan/ask_b_hot_topics.py`): retrieval scope (immutable, pre-call, digest-bound, no outcome fields), execution receipt (post-call), research intake (ordered covered/uncovered ability IDs for 39.2 honesty), knowledge entry, and a discriminated contribution output with dispositions `retryable_demand_not_ready` / `retryable_dispatch_disabled` / `retryable_credentials_unavailable` / `completed_empty` / `completed_degraded` / `completed_ready` and exact retryable loss codes (`ask_b_demand_not_ready`, `ask_b_dispatch_disabled`, `ask_b_credentials_unavailable`). No orchestrator or Texas implementation-type imports (M3 held).
   - Every usable entry carries the packet-required credibility fields (`REQUIRED_ENTRY_FIELDS`), evidence excerpt/truncation/body-hash bindings per the 38.1 idiom, `scope_digest`, ordered `supports_ability_ids`, association-basis evidence, and packet-namespaced citation IDs `ask-b-cite-###` (contiguous, first-wins deduped). An entry with no deterministic ability association is rejected into an indexed loss. No model summarization/classification call is added.
   - `resolve_for_hot_topics(run_dir, require_usable=True)` must read the resulting packet and witness the same stable `packet_digest` on reload. **One-witness-rule shape-pin:** every consumer of the Ask-B packet witnesses the SAME digest, and that digest is distinct from both the Ask-A digest and the generic `04.55` digest on the same run (extends the existing three-digest pin at `test_research_packet_w1.py` L364).
   - **Reader-side strictness — DECIDED MANDATE (green-light unanimous: W-1, J-1, M-6, M-8, A-2):** strict Ask-B reader validation IS added to `load_research_packet` at the exact `ask_b_hot_topics@07W.4` coordinate (mirroring the Ask-A branch at `research_packet.py` L195–207) IN THIS DIFF, with the pin flip that 38-1 AC 4 explicitly declared. This is no longer conditional. Machine reason (M-8): the AC 9 negative pin "entry missing credibility fields → REJECT" is unsatisfiable under the lax reader — the mandate is forced, not stylistic. Packet coordinates, `SCHEMA_VERSION`, digest algorithm, and `ProductionEnvelope` v2 remain unchanged.
   - **Honest flip shape (Murat ruling-d — named discipline block, all five items binding):**
     1. **Conscious same-diff flips** of the 38-1-pinned lenient-Ask-B tests — `test_research_packet_w1.py` L325–365 bare-fixture read + the L549-family parametrized fixtures — each flip carrying a one-line rationale citing 38-2 AC 3 and noting that 38-1 AC 4 scoped "current semantics" as interim. Never silent.
     2. **Mirrored strict-fail-loud tests** (a `test_ask_b_present_malformed_contract_fails_loud` analog of the Ask-A strict pin) land in the SAME diff.
     3. **Unchanged-leniency re-pin for generic `04.55`** proving the strictness flip is coordinate-exact — the generic packet's lenient read semantics are re-asserted untouched.
     4. **Lockstep table row for `research_packet.py` flips from LIKELY-TOUCHED to TOUCHED (W-4)** — reflected in §Lockstep declaration below.
     5. **Cross-ref note owed:** at story close, add a one-line cross-reference on the 38-1 closure record noting the interim-leniency pin was consciously retired by 38-2 AC 3.

4. **Empty-honesty is the packet's native idiom (FR9 honesty leg)**
   - Zero usable rows → `completed_empty` with typed `known_losses` (producer losses merged before reader losses, first-wins — the `load_research_packet` producer-loss machinery from 38.1 AC 4 already handles this; Ask-B emits well-formed single-line losses). Usable rows plus any loss → `completed_degraded`. Never fabricate rows, never pad, never "forecast" to fill.
   - Empty output still binds the exact Ask-B scope through validated `research_intake` and losses (auditable "we asked, honestly nothing usable came back").
   - **Ungrounded-topic marking:** the mint guarantees packet rows originate ONLY from the dispatch (never model-prior/injected topics). Consumer-side, a pinned test proves the existing `reject_model_prior_topic` (`trends_projection.py` L173) marks an ungrounded/injected topic `unusable` when grounded against an Ask-B-shaped packet — WITHOUT re-pointing `trends_inputs_from_run` (39.2 owns the re-point).

5. **Crash-safe call journal and exactly-once replay**
   - Mirror the 38.1 journal discipline at new coordinates: exclusive per-trial `ask-b-hot-topics-call.v1.lock` (create-if-absent; no automatic stale-lock reclamation), atomic pre-call journal `ask-b-hot-topics-call.v1.json` with `state="call_in_progress"` + canonical idempotency key (trial ID, demand digest, scope/query digest, non-secret provider/config fingerprint) + validated scope snapshot; completed journal stores raw rows with evidence bodies, normalization/filter/loss records, intake, output, receipts, digests.
   - Replay recursively validates and recomputes the exact output with zero network calls. `call_in_progress` is an ambiguous-call hard pause; completed honest-empty is terminal; neither ever recalls. Provider exceptions leave the claim intact (`ask-b.provider-execution-failed`; re-entry → `ask-b.call-ambiguous`).
   - Stable tags: `ask-b.demand-invalid`, `ask-b.scope-overflow`, `ask-b.dispatch-init-failed`, `ask-b.provider-execution-failed`, `ask-b.output-invalid`, `ask-b.persistence-failed`, `ask-b.call-ambiguous`, `ask-b.reconciliation-failed`, `ask-b.split-brain` — translated inside the Ask-B seam, never collapsed to `workbook.band.factory-failed`.
   - A barrier-controlled two-worker test proves exactly one dispatch; the loser makes zero calls.

6. **Exact-coordinate activation at `07W.4` — including the resume-skip fix**
   - Replace only the reserved `_ask_b_stub` factory (`workbook_wiring.py` L1198–1203) with an `_ask_b_factory` mirroring `_ask_a_factory` (L1162–1177: runtime_context + dispatch_live threading), and add the `07W.4` dispatch branch mirroring L1832–1843. Preserve `ask_b_hot_topics@07W.4`, specialist/node order, graph/manifest/pack/event/gate/HUD surfaces, and terminal `07W` behavior.
   - **Substrate fact (verified):** `run_workbook_band_node`'s exact-coordinate skip (L1566–1571 → return at L1693) currently includes only `{07W.2, 07W.3}` in the reconcile-not-skip set — a persisted `stub_status: not_yet_wired` Ask-B contribution would be skipped FOREVER on resume under default factories. This story MUST add `07W.4` to that set so a persisted stub/typed-retryable output upgrades at the same coordinate when prerequisites become ready (mirror 38.1 AC 6 same-coordinate upgrade), while completed outputs reconcile and are never recalled.
   - Reconciliation is exact (mirror the 38.1 AC 6 table at the `ask-b.*` tags): absent journal + stub/retryable → dispatch-or-typed-retryable; completed journal + absent/stub/retryable → roll forward from raw journal with zero dispatch; completed + exact-matching completed → no-op (zero persistence/projection/event effects); completed + conflicting completed → `ask-b.split-brain`; `call_in_progress` + anything → `ask-b.call-ambiguous`; completed contribution + no journal → `ask-b.split-brain`; digest mismatches → `ask-b.reconciliation-failed`/`ask-b.split-brain` before dispatch. Wrong-specialist/right-node and right-specialist/wrong-node contributions never satisfy the exact lookup.
   - Emit a node-specific deterministic execution marker (`deterministic-ask-b-hot-topics-wiring`), not the generic band marker (mirror L1918–1921).
   - **Resume-skip hardening (W-2 + M-4):**
     - **BOTH-direction pins:** (i) persisted stub + ready inputs → exactly-one-dispatch upgrade at the same coordinate (I/O matrix row 7); (ii) persisted COMPLETED contribution + resume → zero dispatch AND zero persistence/projection/event effects — promoted to its own I/O matrix row (row 9) paired with the upgrade row, not folded into it.
     - **Named set-membership pin (W-2):** a test asserts the reconcile-not-skip set equals EXACTLY `{07W.2, 07W.3, 07W.4}` — set equality, not membership-of-one. This trap has recurred once per band-node activation; the pin makes any future band-node omission fail loud at activation time instead of silently skipping forever.
     - **Upgrade test posture (M-4):** the same-coordinate upgrade test MUST run with `factories is None` (default registry; dispatch monkeypatched ONLY at the owned `ask_b_research_wiring` seam). Injecting a factories override would route around the `and factories is None` guard and leave the fixed branch never exercised — the test would pass while the fix stays dead.

7. **Both-walks parity via the landed uniform band seam**
   - Both runner walks already dispatch `07W.4` through `run_workbook_band_node` with `dispatch_live=_research_dispatch_live()` and persist actual band mutations through the sole `_persist_envelope` writer (L3330–3354; L4334+). Expected `production_runner.py` diff: ZERO. Parity tests prove `07W.3 → disk → 07W.4` visibility in both walks, identical Ask-B behavior in both, no extra persistence/projection/event emission on no-op resume, and preserved resume/learning-event/parity behavior. If a defect forces a runner change, it is declared in the lockstep table and reviewed as a trigger-path touch.
   - **Parity module hygiene (M-7):** two-walk parity lands by PARAMETRIZING the existing 38-1 both-walks parity module over band coordinates (`07W.2`, `07W.4`) — never a hand-cloned second suite. One module, one parametrized coordinate axis.
   - **Consumer-pin module hygiene (A-4):** the `reject_model_prior_topic`-vs-Ask-B consumer-side pin (AC 4) lands in a NEW test module — NOT in `tests/unit/marcus/lesson_plan/test_trends_w3.py` — so 39-2's `trends_inputs_from_run` re-point opens conflict-free (the DAG hard-serializes 38-2 → 39-2).

8. **Downstream boundary stays clean — 39.2 owns the re-point**
   - This story produces the Ask-B packet ONLY. It does NOT re-point `trends_inputs_from_run`/`resolve_for_trends_projector`, does not modify the Door-Ajar/trends render, References, glossary, Deep-Dive, Check/Reflection, Markdown/DOCX, or the terminal `07W` leaf. `trends_projection.py` line changes: ZERO.
   - No existing consumer of any packet is re-pointed; generic `04.55` and Ask-A behavior are proven unchanged by regression.

9. **Verification, D3 probe, and run-B boarding (close bar)**
   - **Deterministic:** hermetic tests inject the dispatch only at the owned seam, prohibit network, and cover: ready/non-ready/corrupt demand; scope ordering/overflow; ability association; evidence extraction/mutation; empty-honesty and loss ordering/status; provider exceptions; exclusive claim/two-worker; journal crash/replay; every reconciliation row incl. the resume-skip upgrade; all retryable dispositions; terminal empty; split-brain; wrong-coordinate collisions; both-walks parity; digest distinctness + one-witness shape-pin; `reject_model_prior_topic` against an Ask-B packet; unchanged `04.55`/Ask-A behavior. Maintain an AC-to-named-test traceability table. **Traceability of conscious flips (A-3):** the traceability table declares the existing band-wiring stub pins that flip on stub replacement — `tests/integration/marcus/test_workbook_band_wiring.py` L294 (the `ask_b_not_yet_wired` stub output pin) and any `_ask_b_stub` identity assertions — as CONSCIOUS ENUMERATED FLIPS, each with a one-line rationale, alongside the AC 3 reader-strictness flips. Run focused + dependency regressions, strict warnings, Ruff, import-boundary checks, manifest/graph/pack parity, and the Cora block-mode lockstep regime. Record the exact pre/post baseline command and per-failure node/exception/dependency signature for every inherited failure (a count alone is insufficient).
   - **Negative-witness pins (D3 M-D3-2b):** every machine-asserted Ask-B bar is fed known-bad artifacts (forged/mutated journal, completed-contribution-without-journal, stub-shaped output where completed is claimed, entry missing credibility fields) and must REJECT.
   - **Component probe (D3 plank 3 + M-D3-2a probe honesty contract) — REQUIRED before boarding any governed run:**
     - Script: `scripts/utilities/run_ask_b_38_2_live_evidence.py`, cloned from the `run_deep_dive_38_3a_live_evidence.py` pattern (immutable attempt dir; failed-evidence preservation pins; machine-readable verdict; first-run-stands).
     - The probe is REGISTERED BEFORE it runs: probe id `probe-38-2-ask-b-hot-topics-001`; the exact claim licensed = "the `ask_b_hot_topics@07W.4` seam, given a real ready beat-③ demand on the frozen Tejal Part-2 corpus, completes one dispatcher invocation and mints a strict Ask-B packet whose digest reloads stably and replays with zero calls" — and nothing broader (never "the pipeline works"); deterministic machine judge (asserts dispatcher count, journal state, entry/association/credibility fields, packet digest reload equality, zero-call replay); frozen evidence pack with input digests and raw outputs.
     - First-run-stands: a failed attempt is preserved immutably; no retry-to-green without a governed correction.
     - **Pre-declared verdict-class rule (M-5 + J-2):** `completed_empty` freezes as a VALID seam witness — the zero-witness rule is satisfied for the call path — but it leaves the usable-mint half of the registered claim OPEN (the claim's "mints a strict Ask-B packet with usable associated rows" leg is neither passed nor failed). Boarding run B on an empty probe requires an EXPLICIT governed acknowledgment line in the run-B authorization — never a silent pass, never retry-to-green. Operator note: a persistently-empty Ask-B yields an empty-honest Door-Ajar at 39.2 — that is the designed honest outcome, not a defect.
     - **Zero-witness rule:** the probe output becomes the `ask-b` family's first witness fixture — a new family `ask-b-hot-topics-call.v1` (node `07W.4`) is enrolled in `tests/live_witness_replay/witnesses.yaml` with a per-family replay module, IN THIS STORY'S DIFF (enrollment is automatic, not remembered).
   - **Run-B boarding rider (D3 M-D3-3 / John F1–F2):** this story boards governed batch run B (after 38-2 + 39-2 + 40-1) only after probe green. The run-B evidence pack carries a per-story verdict line keyed to `ask_b_hot_topics@07W.4`: REACHED+PASS = witness; NOT-REACHED = the claim stays OPEN (no-evidence — never pass, never fail); "aboard" ≠ tested. Only independently-greened fixes board. Pre-run-B status is exactly `done-awaiting-live-witness  # deterministic+review green; component probe probe-38-2-ask-b-hot-topics-001 green; full-run witness owed by batch run B` — the flip to `done` cites the witnessing run id. Never overload `in-progress`; never early-`done`.
   - **FR assertion note:** FR16's Ask-B leg + FR9 are asserted at the 39-wave close bar by this story + 39.2 together; this story's close records its half (packet minted + witnessed), not the rendered Door-Ajar.
   - **39-2 handoff rider (J-3):** at story close, the closure record AND the deferred-inventory/39.2 grooming note MUST name 39.2's inherited obligations — the `trends_inputs_from_run` re-point, the post-re-point `reject_model_prior_topic` pin, and the FR16/FR9 wave-close assertion — so the wave-close claim has a named owner.

### Deterministic I/O matrix (pre-dev floor — each row is a named test before implementation completes)

| # | Input condition | Required output |
|---|---|---|
| 1 | Ready beat-③ demand (brief authority present, ordered vows, digests bind) + dispatch live + credentials | Exactly 1 dispatcher invocation; completed journal; strict packet minted at `ask_b_hot_topics@07W.4` |
| 2 | Scoping input absent/legacy (no workbook brief / legacy stub / no promise vows) | Typed retryable `retryable_demand_not_ready` + `ask_b_demand_not_ready`; ZERO dispatcher invocations; no journal; no fabricated rows |
| 3 | Dispatch completes, zero usable rows survive filtering | `completed_empty` with typed `known_losses` (empty-honesty); scope still bound via intake; terminal — never recalled |
| 4 | Ungrounded/injected topic grounded against the minted Ask-B packet | `reject_model_prior_topic` marks it `unusable` (consumer-side pin; no trends re-point) |
| 5 | Packet reload (`resolve_for_hot_topics`, `require_usable=True` on usable mint) | Same `packet_digest` witnessed on reload; distinct from Ask-A + generic digests on the same run (one-witness-rule shape-pin) |
| 6 | Band reached in start walk vs continuation walk | Identical Ask-B behavior; disk-mediated `07W.3 → 07W.4` visibility; sole-writer persistence; no-op resume emits nothing |
| 7 | Persisted `not_yet_wired` stub at `07W.4` + prerequisites now ready | Same-coordinate upgrade fires (resume-skip fix, AC 6); completed output never recalled |
| 8 | Negative witnesses (forged journal / completed-without-journal / mutated raw body / missing credibility fields) | Machine bars REJECT with the exact stable `ask-b.*` tag |
| 9 | Persisted COMPLETED contribution at `07W.4` + resume (M-4, paired with row 7) | Zero dispatch; zero persistence/projection/event effects — exact no-op |
| 10 | Kill-switch OFF (dispatch disabled) (M-1) | `retryable_dispatch_disabled` + `ask_b_dispatch_disabled` loss; ZERO dispatcher invocations |
| 11 | Credentials absent (M-1) | `retryable_credentials_unavailable` + `ask_b_credentials_unavailable` loss; ZERO dispatcher invocations |
| 12 | `call_in_progress` journal found on entry (M-2) | `ask-b.call-ambiguous` hard pause; ZERO recall |
| 13 | Completed journal + absent/stub contribution (M-2) | Roll forward from raw journal; ZERO dispatch |
| 14 | Completed journal + conflicting completed contribution (M-2) | `ask-b.split-brain` |
| 15 | Corrupt/forged demand artifact (M-3) | `ask-b.demand-invalid`; ZERO dispatch |
| 16 | Scope exceeds effective query limit (M-3) | `ask-b.scope-overflow` — fail BEFORE dispatch; never truncate/reorder/partition |
| 17 | Barrier-controlled two workers race the claim (M-3) | Exactly one dispatch; the loser makes ZERO calls |

## Scope Fences

- **NO trends render re-point** — `trends_inputs_from_run` / `resolve_for_trends_projector` / Door-Ajar composition belong to 39.2. `app/marcus/lesson_plan/trends_projection.py`: zero lines changed.
- **NO `07W` terminal render change** — the model-free deterministic-consume leaf and its no-model-client pin stay untouched.
- **NO `07W.1` / `07W.3` writer changes** — SceneComposer/PromiseTransformer/DeepDiveWriter/enrichment writers and their journals are out of scope.
- **NO new learning-event types** (graph-shape record: held to zero for this band lineage).
- **NO pack-version bump** — the ratified graph-shape record authorizes v4.2-lineage refinement only, and the band + manifest nodes landed in 38.3b; this story's expected manifest/pack diff is ZERO. Any forced deviation is a stop-and-report, not a dev-authority call.
- **NO weakening** of the model-free pins (manifest `specialist_id: null` / `model_config_ref: null` at `07W.2`/`07W.4`), G2, the M-R3 LO shippability bar, `_assert_completed_workbook_deliverable`, or any existing machine bar. Bar modules touched by this story get Blind+Edge review on change (D3 M-D3-2b).
- **NO second `run.json` writer**; no envelope-schema, gate, HUD, node-order, or provider-adapter changes.

## Lockstep declaration (Tier-2 regime — consensus authority = the RATIFIED Epic-38 graph-shape record)

Verified against `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` (L60–110) in the tree at `72e17a05`:

| Scoped file | Trigger row? | Expected touch | Note |
|---|---|---|---|
| `app/marcus/orchestrator/workbook_wiring.py` | YES (L109) | **TOUCHED** | `_ask_b_stub` → `_ask_b_factory`; dispatch branch; reconcile-not-skip set + reconciliation blocks |
| `app/marcus/lesson_plan/research_packet.py` | YES (L110) | **TOUCHED** | strict Ask-B reader branch at `ask_b_hot_topics@07W.4` IS added (AC 3 decided mandate, mirror of L195–207; W-4 flip from LIKELY-TOUCHED); resolver already landed in 38-0 |
| `app/marcus/orchestrator/production_runner.py` | YES (L106) | **UNTOUCHED expected** | both walks already dispatch the full band uniformly (L3330–3336, L4334–4340); any forced touch is declared + reviewed |
| `state/config/pipeline-manifest.yaml` | YES (itself, L61) | **UNTOUCHED — verified** | node `07W.4` + edges `07W.3→07W.4→07W` already landed (L1064+, L1159–1160), model-free; expected manifest diff ZERO |
| `app/marcus/lesson_plan/ask_b_hot_topics.py` (new) | no | TOUCHED (new) | lesson-plan contract family, M3-safe |
| `app/marcus/orchestrator/ask_b_research_wiring.py` (new) | no | TOUCHED (new) | orchestrator adapter mirroring `ask_a_research_wiring.py` |
| `app/marcus/lesson_plan/research_demand.py` | no | TOUCHED | adds `resolve_hot_topics_demand` + Ask-B demand model |
| `app/marcus/lesson_plan/trends_projection.py` | no | **UNTOUCHED (fence)** | 39.2's surface |
| `tests/live_witness_replay/witnesses.yaml` (+ family module) | no | TOUCHED | `ask-b-hot-topics-call.v1` family enrollment (D3) |
| `scripts/utilities/run_ask_b_38_2_live_evidence.py` (new) | no | TOUCHED (new) | component probe script |

Because trigger rows are touched: read the regime doc at T1 (done, §T1 item 3); run `python scripts/utilities/check_pipeline_manifest_lockstep.py` (assert exit 0) before closure; Cora's block-mode pre-closure hook is the arbiter. Tier-2 consensus is already carried by the ratified graph-shape record — no new node, edge, pack section, or event type is introduced by this story, so no fresh Tier-2 round opens.

## Tasks / Subtasks

- [ ] Task 1: Ask-B demand + strict contract family (AC 1, 3, 4)
  - [ ] Add `resolve_hot_topics_demand` + strict demand model to `research_demand.py` (beat-③ vows + scene identity + brief digest; ready/non-ready shape rules mirroring `AskAResearchDemandV1`).
  - [ ] Add `app/marcus/lesson_plan/ask_b_hot_topics.py` (scope/receipt/intake/entry/output; digests; association algorithm; dispositions + loss codes).
  - [ ] Contract tests: ordering, association, evidence/hash binding, dispositions, digest binding, empty/degraded, malformed losses.
  - [ ] Strict Ask-B reader branch in `research_packet.py` at exact `ask_b_hot_topics@07W.4` (AC 3 decided mandate) + the full Murat ruling-d flip set: conscious flips of the 38-1 lenient pins (`test_research_packet_w1.py` L325–365 + L549 family) w/ one-line rationales, mirrored strict-fail-loud tests, generic-`04.55` unchanged-leniency re-pin.
- [ ] Task 2: Orchestrator Ask-B wiring + journal (AC 1, 2, 5)
  - [ ] Add `app/marcus/orchestrator/ask_b_research_wiring.py` mirroring `run_ask_a_research` at the `ask-b.*` coordinates (lock, pre-call/completed journal, replay, error translation, reconciliation).
  - [ ] Two-worker barrier, write-failure, collision, ambiguous-call, zero-recall tests.
- [ ] Task 3: Activate only `07W.4` (AC 2, 6)
  - [ ] `workbook_wiring.py`: `_ask_b_factory`, dispatch branch, reconcile-not-skip set fix, upgrade/replace/reconcile blocks, node-specific marker.
  - [ ] Focused band tests: stub upgrade (incl. persisted-stub resume row 7), completed replay no-op, marker identity, kill-switch posture, no graph/manifest drift.
- [ ] Task 4: Parity + downstream boundary (AC 7, 8)
  - [ ] Both-walks parity tests via the real `_persist_envelope` writer and disk-only demand reader; unchanged `04.55`/Ask-A/trends regressions; digest distinctness + one-witness shape-pins; `reject_model_prior_topic`-vs-Ask-B-packet pin.
- [ ] Task 5: Verification + D3 protocol (AC 9)
  - [ ] Full deterministic matrix, negative-witness pins, traceability table, baseline comparison, Ruff/import-linter/lockstep PASS.
  - [ ] Author + register `probe-38-2-ask-b-hot-topics-001`; write `run_ask_b_38_2_live_evidence.py`; witness-replay pre-flight (STRICT) before spend; execute the probe first-run-stands; freeze evidence; enroll the `ask-b-hot-topics-call.v1` family in `witnesses.yaml` + add the family replay module.
  - [ ] Set status `done-awaiting-live-witness` with the exact D3 vocabulary; record the run-B boarding verdict-line contract (incl. the M-5/J-2 `completed_empty` acknowledgment rule if applicable).
  - [ ] Close-time riders: one-line cross-ref note on the 38-1 closure record (AC 3 ruling-d item 5); 39.2 inherited-obligations note in closure record + deferred-inventory/39.2 grooming (J-3).

## Dev Notes

### Code map (anchors re-verified in the tree at `72e17a05`)

- `app/marcus/orchestrator/workbook_wiring.py`
  - L124–129 `WORKBOOK_BAND_NODE_IDS` — `07W.4` is last; L131–137 `WORKBOOK_BAND_SPECIALIST_IDS` maps it to `ask_b_hot_topics`.
  - L1162–1177 `_ask_a_factory` — the factory shape to mirror (lazy import; `runtime_context` + `dispatch_live` kwargs; `.model_dump(mode="json")`).
  - L1198–1203 `_ask_b_stub` — today's honest-empty stub: `{"research_entries": [], "stub_status": "not_yet_wired", "known_losses": ["ask_b_not_yet_wired"]}`. L1206–1211 registry.
  - L1566–1571 + L1693 — the exact-coordinate skip: `existing` found via `get_contribution` (else-branch L1567) and **skipped without reconciliation** because the reconcile-not-skip set is `{ASK_A_ENRICHMENT_NODE_ID, WORKBOOK_REVIEW_NODE_ID}` only. THE resume-blocking fact behind AC 6.
  - L1737–1768 prior-output validation + completed-without-journal split-brain (Ask-A) — mirror at `ask-b.*`.
  - L1832–1843 the Ask-A dispatch branch (context-missing guard + kwargs) — mirror for `07W.4`; today `_ask_b_stub` falls to the generic 2-arg call at L1851–1852.
  - L1918–1921 node-specific marker selection; L1941–1978 completed-reconcile / exact-coordinate replace — mirror.
- `app/marcus/orchestrator/ask_a_research_wiring.py` — whole-module precedent: L37–38 journal/lock names; L105–131 `_build_intent` (Scite-canonical `RetrievalIntent` via `research_wiring._import_retrieval`; posture + scope_digest in provider params; iteration_budget 3); L134–138 `_default_dispatch`; L141–144 `_credentials_present`; L388–493 `run_ask_a_research` (demand → limit/fingerprint → scope → journal replay → lock claim → pre-call write → dispatch → normalize → completed write). Note the Tracy naming: the "Tracy call" in the landed band substrate is this Scite-canonical dispatch seam — the `IreneTracyBridge` (L705–709 of `research_wiring.py`) belongs to the `04.55` path and is NOT imported here.
- `app/marcus/lesson_plan/research_packet.py` — L31–32 Ask-B literals; L195–207 the Ask-A-only strict branch (decision point for AC 3 reader-strictness); L221–237 producer-loss validation (38.1 AC 4 — already generic, Ask-B gets it free); L345–355 `resolve_for_hot_topics`.
- `app/marcus/lesson_plan/research_demand.py` — L67–152 `AskAResearchDemandV1` (shape discipline to mirror; note ready-demand completeness rules L94–117); L286 `resolve_enrichment_demand`. No Ask-B resolver exists.
- `app/marcus/lesson_plan/prework_artifact.py` — L291–298: Promise vows carry `(objective_id, text)` and are pinned equal to the deep-dive abilities; the beat-③ ability authority for the Ask-B demand.
- `app/marcus/lesson_plan/trends_projection.py` — L173–212 `reject_model_prior_topic` (grounds a topic against packet titles; returns `confidence="unusable"` when ungrounded); L305–319 `trends_inputs_from_run` still reads the generic packet (39.2's re-point). Existing consumer-side pin: `tests/unit/marcus/lesson_plan/test_trends_w3.py` L172.
- `app/marcus/orchestrator/production_runner.py` — L3325–3354 (start walk) and L4334+ (continuation walk): uniform band dispatch with `dispatch_live=_research_dispatch_live()` (L142) + sole-writer persistence + `_pause_at_error` with band specialist attribution. Expected diff ZERO.
- `state/config/pipeline-manifest.yaml` — L1036–1050 node `07W.2`; L1064+ node `07W.4` (`specialist_id: null`, `model_config_ref: null`, `sub_phase_of: "07W"` family, v4.2); L1156–1161 band edges. Expected diff ZERO.
- Shape-pins already standing: `tests/unit/marcus/lesson_plan/test_research_packet_w1.py` L314–364 (Ask-B constants, resolver, exact-coordinate resolution, three-digest distinctness), L395–397 (absent-contribution loss string), L463–466 (malformed entries fail loud).

### Probe script plan (`scripts/utilities/run_ask_b_38_2_live_evidence.py`)

Clone the `run_deep_dive_38_3a_live_evidence.py` skeleton (L92–101 unique-attempt allocation; failed-evidence preservation pins; machine-readable `verdict.json`): seed a run dir from the frozen Tejal Part-2 evidence lineage carrying a real ratified `07W.1` brief (the `a940c5eb`/`8b275e5b` closure lineage from 38.1 provides completed-band predecessors); register the probe (id, licensed claim, judge spec) in the verdict BEFORE dispatch; resolve the real Ask-B demand; one live dispatch through the production seam (`run_workbook_band_node` at `07W.4`, not a side-channel); judge deterministically (dispatcher count = 1, completed journal, ≥1 usable row associated to ≥1 exact beat-③ ability with credibility fields + provenance + receipt — or an honest `completed_empty` with typed losses, which the judge records as a DISTINCT verdict class, not a pass-by-default); prove reload digest equality + zero-call replay; freeze everything immutably. First-run-stands.

### Witness-family enrollment plan

New `witnesses.yaml` family block: `family: ask-b-hot-topics-call.v1`, `node_id: "07W.4"`, first witness = the probe attempt's journal (state `completed`, capture: idempotency key + provider/config fingerprint), disposition `enrolled`; failed attempts (if any) enroll as ambiguity-shape witnesses exactly like the `7ed48f8a`/`b6fc76ea` precedent rows. Add `tests/live_witness_replay/test_ask_b_hot_topics_call_v1.py` mirroring the existing per-family modules (replay pins + STRICT-mode participation). Enrollment lands in THIS story's diff (D3 M-D3-1a: automatic, not remembered).

**First-of-kind note (A-6):** the `ask-b-hot-topics-call.v1` replay module is the FIRST Scite-canonical band research-call family — `witnesses.yaml` holds only `07W.1`/`07W.3`/`07W` families today, and no ask-a family is enrolled yet (its witness is owed by run A). Expect a small shape delta from the three existing per-family modules (call-journal capture fields vs writer-output capture), not a pure mirror; do not force-fit the existing module shape where the call-family shape differs.

### Velocity tiers

The 38-1 precedent spec carries no `r_tier`/`t11_tier`/`files_touched`/`lookahead_tier` frontmatter (the Slab-7c amendment convention was not applied to the Epic-38 story family); this spec follows the precedent and omits them.

### Size honesty (Amelia, green-light round)

- Demand model + resolver = **M**, not S: the Ask-B loss→status lattice is a NEW design (AC 1), not a mirror of the skeleton-digest-coupled Ask-A map.
- Story overall = **L**: a full 38-1-scale replay at new coordinates (contract family + journal/replay + activation + parity + probe + witness enrollment), plus the AC 3 reader-strictness flip set.

### Guardrails

- Product work only: this activates the SPOC production seam; never add proofing-only behavior (CLAUDE.md design guardrail).
- `lesson_plan` may not import `marcus.orchestrator`; the M3 crossing stays disk/envelope-mediated.
- Baseline discipline: record the exact pre-story pytest command + failure signatures before any code (the 38.1 preflight-failure class at `production_runner.py` may recur; compare by node/exception/dependency signature, never by count).
- Live spend only after witness-replay pre-flight in STRICT mode (`WITNESS_REPLAY_STRICT=1`; skip ⇒ fail) with the drift-flag report (prompt/model/config identity vs capture-time values).

### References

- [Source: `_bmad-output/planning-artifacts/wave-3940-kickoff-party-record-2026-07-15.md` — §D1 re-home riders; §D3 Paid-Run Economy Protocol]
- [Source: `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` — §Epic 38 graph-shape decision RATIFIED; §Story 38.2; §Story 38.3 AC 2; FR coverage map rows FR16/FR9]
- [Source: `_bmad-output/implementation-artifacts/38-1-ask-a-enrichment-wiring.md` — direct precedent: AC shape, journal/reconciliation discipline, closure record]
- [Source: `_bmad-output/implementation-artifacts/38-0-two-packet-intake-contract.md` — packet identity, digest, resolver contracts]
- [Source: `_bmad-output/implementation-artifacts/38-3b-graph-topology-band-orchestrator.md` — fixed topology, model-free band, idempotency]
- [Source: `docs/dev-guide/pipeline-manifest-regime.md` — lockstep regime, pack-versioning policy]
- [Source: `app/marcus/orchestrator/workbook_wiring.py`; `app/marcus/orchestrator/ask_a_research_wiring.py`; `app/marcus/lesson_plan/research_packet.py`; `app/marcus/lesson_plan/research_demand.py`; `app/marcus/lesson_plan/ask_a_enrichment.py`; `app/marcus/lesson_plan/trends_projection.py`; `app/marcus/orchestrator/production_runner.py`; `state/config/pipeline-manifest.yaml`]
- [Source: `tests/live_witness_replay/witnesses.yaml`; `scripts/utilities/run_deep_dive_38_3a_live_evidence.py`]
