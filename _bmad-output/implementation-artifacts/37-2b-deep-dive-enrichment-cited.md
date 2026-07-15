---
baseline_commit: c0811817
---

# Story 37.2b: Deep Dive enrichment — cited pool-grounded depth + A2 citation-COVERAGE gate

Status: draft  <!-- party green-light round precedes ready-for-dev; do not flip without it -->

## Story

As the Marcus-SPOC workbook runtime,
I want the Deep Dive read-prose enriched with net-new depth drawn ONLY from the Ask-A cited knowledge pool — inline-cited, coverage-gated, and rendered into the workbook deliverable,
so that the read-channel carries real sourced depth beyond the glance-deck without model-prior invention, phantom citations, or claimed enrichment the writer never used.

## Dependency Position

`38.0 ✅ -> 38.3b ✅ -> {36 ✅, 37.1 ✅, 37.2a ✅, 37.3 ✅, 37.4 ✅} -> 38.3a ✅ -> 38.1 ✅ -> **37.2b (this)** -> 39.1 -> 38.2 -> 39.2 -> 40.1`

Both hard deps are done: 38.0 (two-packet intake) and 38.1 (Ask-A pool live-proven at `ask_a_enrichment@07W.2`, closed 2026-07-15 on trials `a940c5eb` + `8b275e5b`). This story blocks 39.1 (glossary reads the terms this deep-dive bolds) and therefore the rest of the DAG. Batched governed **run A** (after 37-2b + 39-1) is this story's full-pipeline witness per the Paid-Run Economy Protocol.

## T1 Readiness (BINDING readings before any code)

1. **Ratified Epic-38 graph-shape record** — `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` §"Epic 38 graph-shape decision" (L243–293): 07W.3 hosts `DeepDiveWriter(enrich+cite+A2)` LEASHED with `model_config`; **37.2b reads Ask-A** via `resolve_for_enrichment_pool`; one digest per packet witnessed identically by every consumer; M3 wall crossed disk-mediated only.
2. **Wave party record (BINDING protocol)** — `_bmad-output/planning-artifacts/wave-3940-kickoff-party-record-2026-07-15.md`: D3 Paid-Run Economy Protocol (zero-witness rule probe→freeze→replay→spend; probe honesty contract; live-shape fixtures only; deliverable bar extended in the SAME story diff with negative-witness pins; batch attribution; `done-awaiting-live-witness` vocabulary) and **D2.4 MERGE authoring-time dedup input**: this story's deep-dive authoring receives the overlay's covered-LO/fact list as INPUT and flexes around it (John's seed duplicate pairs: admin-cost %, 73-day doubling, digital front door); residual duplication is an operator spot-check at governed run A, declared honestly, never claimed machine-caught.
3. **Pipeline-lockstep regime doc** — `docs/dev-guide/pipeline-manifest-regime.md`. **Lockstep APPLIES**: this diff touches `app/marcus/orchestrator/workbook_wiring.py`, a `block_mode_trigger_paths` entry (`state/config/pipeline-manifest.yaml:109`). Declared tier: **Tier-1 within-node activation** — the 07W.3 coordinate, specialist order, band topology, and manifest are UNCHANGED (manifest node `07W.3` already carries `model_config_ref: app/marcus/orchestrator/workbook_writer_model_config.yaml`, manifest L1050–1062); no new nodes, no new learning-event types, no pack bump. Run the lockstep checker + Cora block-mode classification before closure (38.1 precedent: `reports/dev-coherence/2026-07-13-1547/check-pipeline-manifest-lockstep.PASS.yaml`). If review finds the change exceeds Tier-1, STOP and take it to party per the regime doc.
4. **M-R2 BINDING rider (Epic-38 retro §Challenges 4)** — **checked: DOES NOT APPLY.** This story's authorized scope touches no path under `app/specialists/irene_pass1/` (the refinement-path normalization gap — `_validate_raw_refinement_identity` red-rejecting before `normalize_clusters` — rides the next Pass-1-touching story, not this one). Any mid-dev scope drift into `app/specialists/irene_pass1/` is a STOP: re-open T1 with the M-R2 reading before proceeding.
5. **Specialist state-threading contracts** — `docs/dev-guide/how-to-add-a-specialist.md` (anti-patterns 9 and 10, L216–217): no new node or specialist is added, but the 07W.3 factory reads run-dir artifacts, so the run-dir threading contract and the persisted-envelope-not-live-field rule apply verbatim (regression floor `tests/specialists/workbook_producer/test_run_dir_threading_503e54c1.py` stays green).
6. **Epic-38 retro doctrine** — `_bmad-output/implementation-artifacts/epic-38-retro-2026-07-15.md`: join through digest-bound run artifacts, never textual markers; normalize provably-empty live-variance shapes observably at deterministic seams; fail-loud on ambiguity.

## Acceptance Criteria

1. **Strict M3-safe enrichment contract (lesson_plan layer)**
   - **Given** the authored skeleton contract at `app/marcus/lesson_plan/deep_dive_projection.py` (`DeepDiveSkeletonResult` L385, `DeepDiveSkeletonClaim` L117, `BoldTermMarker` L146, gate receipt L301) **When** NEW `app/marcus/lesson_plan/deep_dive_enrichment.py` lands **Then** it defines strict, frozen, extra-forbid, JSON-safe models: an enrichment request binding (a) the authored skeleton result by `authority_digest` + `candidate_payload_digest`, (b) the Ask-A pool identity by packet digest + `scope_digest`, (c) the ordered usable pool rows (citation_id, evidence_excerpt, evidence_body_sha256, source_id/source_ref, tier, `supports_ability_ids`, `supports_bold_terms` — exactly the live `ask-a-knowledge-entry.v1` fields, no invented fields), (d) the D2.4 overlay-covered input (LO ids/statements + exercise-fact strings projected deterministically from `project_enrichment_to_workbook_inputs`, `app/marcus/lesson_plan/workbook_enrichment.py:561`; honest-empty when no enrichment card exists); an enriched result whose claims are **typed at the writer boundary**: every enriched-deep-dive claim carries either inherited skeleton `source_claim_refs` (role `skeleton`) or one-or-more pool `citation_refs` (role `enrichment`) — never neither, never both blank; and an inspectable A2 gate receipt (AC2). Mirrors 37.2a discipline: duplicate/blank/unknown IDs reject; constructed-model revalidation; authored/degraded/unavailable status↔payload↔loss reconciliation; imports `lesson_plan` only (import/AST guard).
2. **A2 citation-COVERAGE gate — deterministic matrix (the teeth)**
   - **Given** amendment A2 ("the deep-dive must not claim enrichment it didn't use") **When** the pure gate runs **Then** each row of this matrix is a pinned deterministic test:
     | # | Input condition | Verdict |
     |---|---|---|
     | a | enrichment-typed claim with zero citation_refs (uncited enrichment sentence) | **FAIL** |
     | b | citation_ref naming a citation_id absent from the bound pool (phantom citation) | **FAIL** |
     | c | citation_ref to a pool row whose `scope_digest`/packet digest disagrees with the request binding (cross-run/cross-packet citation) | **FAIL** |
     | d | pool empty or packet status `empty` → result is typed `degraded` with stable loss `deep_dive_enrichment_pool_empty`; zero enrichment claims, zero citations, skeleton prose intact (**empty-honesty**) | PASS-as-degraded |
     | e | pool non-empty + usable, writer used zero rows but claims `enriched` status | **FAIL** (cannot claim enrichment it didn't use) |
     | f | partial coverage: some usable rows cited, others not | PASS; receipt lists `used_citation_ids` and `unused_citation_ids` exactly (**unused-row honesty** — unused rows are reported, never counted as coverage) |
     | g | receipt's `used_citation_ids` ≠ the citation set actually appearing in prose markers | **FAIL** (coverage is measured from prose, not asserted by the writer) |
     | h | skeleton VO-claim coverage regression (any 37.2a `vo` claim missing from the enriched trace) | **FAIL** (enrichment may only ADD; the A3 proper-superset gate re-runs on the enriched claim set) |
   - The receipt exposes counts + ordered ID lists: available/used/unused pool rows, covered/uncovered ability IDs (joined against the pool's `covered_ability_ids` from `ask-a-research-intake.v1`), per-claim citation bindings, and pass/fail — never only a Boolean. **Honesty boundary declared verbatim in the module docstring:** the machine gate proves the claim-typing/citation-binding/coverage arithmetic; whether an enriched sentence *semantically follows from* its cited evidence_excerpt remains an **operator prose spot-check WARN** (per A2's fallback clause — this story does not call the semantic audit G2-enforced).
3. **Pool consumption is digest-bound and sole-sourced**
   - **Given** `resolve_for_enrichment_pool(run_dir, require_usable=False)` (`app/marcus/lesson_plan/research_packet.py:332`) **When** the enrichment request is built from a run dir **Then** the pool comes ONLY from the exact `ask_a_enrichment@07W.2` packet (never `research_wiring@04.55`, never Ask-B), the packet digest is bound into the request and witnessed identically on reload, and T7/T8 rows never appear (they were excluded upstream into `known_losses` — a fixture pinning this is required). `require_usable=False` deliberately: a thin/empty pool is a legitimate degraded path (matrix row d), not a dispatch failure.
4. **Bold-term continuity for 39.1 (glossary anchor stability)**
   - **Given** the skeleton's canonical `bold_terms` tuple (37.2a AC5) **When** the enriched result is authored **Then** the skeleton's bold term set is preserved EXACTLY (39.1's anchors never silently vanish); the writer MAY bold additional terms only when each new term is traced to a used pool citation; the 37.2a bold parity gate (`prose_bold_parity_is_valid`, `deep_dive_projection.py:678`) re-runs over the enriched prose; marker/metadata mismatch, nested/unmatched markup, and untraced new terms reject. Inline citation markers render as `[ask-a-cite-###]` immediately after the sentence they support and are excluded from bold-parity text.
5. **Exactly-once journaled live dispatch at `07W.3` (orchestrator layer)**
   - **Given** the reserved `_review_stub` factory (`app/marcus/orchestrator/workbook_wiring.py:1177–1196`, `WORKBOOK_REVIEW_NODE_ID = "07W.3"` L116) **When** the factory is activated **Then** it mirrors the proven 07W.1 deep-dive seam: a `LiveDeepDiveEnrichmentWriter` in `app/marcus/orchestrator/workbook_prework_writers.py` (mirror `LiveDeepDiveWriter` L363 — structured writer, provider schema digest, normalizer version, raw-payload capture) is instantiated live-mode-only via `runtime_context_for_run` (pattern at `workbook_wiring.py:1218–1243`); dispatch is journaled crash-safe exactly-once in a NEW journal family `workbook-deep-dive-enrichment-call.v1.json` mirroring `DEEP_DIVE_JOURNAL_FILENAME` (`prework_artifact.py:35`) and the 07W.1 reconciliation walk (`workbook_wiring.py:627–780`): `call_in_progress` = ambiguous hard pause, completed journal replays with zero provider calls, raw provider payload + normalization records + idempotency key (binding trial id, skeleton digests, pool packet digest, provider/config identity) stored in-journal; stable node-scoped error tags (`workbook-review.enrichment-*`), never collapsed to a generic factory failure.
   - Same-coordinate upgrade semantics mirror 38.1 AC6: the legacy `workbook_review_stub` contribution upgrades at the exact `07W.3` coordinate (introduce `LEGACY_WORKBOOK_REVIEW_SPECIALIST_ID`, activated id `workbook_review`, mapping at `workbook_wiring.py:129–134`); completed output reconciles and is never recalled; split-brain (journal↔envelope disagreement) fails closed. Offline mode composes via the deterministic offline stub (honest non-authored) so goldens run without a model.
   - **Check/Reflection stay honestly stubbed:** the activated 07W.3 payload carries typed `known_losses` (`check_writer_not_yet_wired`, `reflection_writer_not_yet_wired`) — this story wires ONLY the deep-dive-enrichment leg of the review node.
   - Both production walks already persist band mutations through the sole `_persist_envelope` writer (38.1 AC7); this story adds **no** `production_runner.py` change — a two-walk regression proves 07W.2 → disk → 07W.3 visibility using the existing seam. If any runner edit proves unavoidable, STOP: that expands the lockstep surface and requires a party check-in.
6. **Terminal render + References resolvability + deliverable bar extended in THE SAME DIFF**
   - **Given** the `presentation_support` render profile in `app/marcus/lesson_plan/workbook_producer.py` **When** an authored enriched deep-dive exists on disk **Then** the terminal (still deterministic-consume, model-free — the `_act.py` no-model-client pin is untouched) renders a new `## Deep Dive` section: per-ability subsections in ratified ability order, enriched prose with `**bold**` terms and inline `[ask-a-cite-###]` markers; the placeholder disclaimer "Traceable Deep Dive read-prose arrives in Story 37.2a and is not claimed here" (`workbook_producer.py:591–596`) is REMOVED and replaced with honest profile copy; on degraded/unavailable enrichment the section renders the skeleton-or-honesty note with the typed loss visible (mirror the `lo_overlay_loss` visible-degrade idiom, `workbook_producer.py:636–640`) — never a silent absence. The existing `## Depth-delta narrative` section (L653–664) is left byte-stable (it is the G0-card depth-deferral, a different authority).
   - Every inline `ask-a-cite-###` marker resolves: the used Ask-A rows render into the existing cited-references block (the `#### Live-research cited entries (DOI)` idiom seen in `runs/8b275e5b…/exports/workbooks/u01@1.md:248–253`) with citation_id, DOI/source_ref, tier, provenance. **Resolvability floor only** — full References assemble/dedupe/render ownership stays with 37.5 (amendment A8).
   - **Protocol plank 5 (same-diff bar):** extend `_assert_completed_workbook_deliverable` (`scripts/utilities/marcus_spoc_live_test_runner.py:1236`, call site L1311) with the deep-dive conformance bar, asserted off the **structured run artifacts first** (07W.3 contribution + gate receipt from `run.json`; Amelia-F2 idiom), then a minimal MD presence check: enriched claim in artifacts ⇒ MD carries the `## Deep Dive` heading, ≥1 inline `ask-a-cite-` marker, and every marker in the MD resolves to a rendered reference entry; degraded claim ⇒ MD carries the honest note and ZERO `ask-a-cite-` markers. **Negative-witness pins in the same diff:** the bar is fed known-bad artifacts (phantom-citation contribution; enriched-status-with-zero-citations; marker-in-MD-without-reference-entry; enriched-claim-with-missing-section) built from mutated copies of the frozen live shapes, and must REJECT each (`workbook-deliverable-nonconforming-despite-completed`). Bar-module change gets Blind+Edge review per protocol.
   - **Witness-replay registry enrollment:** when the AC8 probe freezes this path's first witness, enroll the `workbook-deep-dive-enrichment-call.v1` journal family in the standing replay suite `tests/live_witness_replay/` + `witnesses.yaml`. That suite does not exist yet at baseline (`c0811817`): this story CREATES the registry skeleton per the protocol amendment (auto-enrolling; one-line adds; `WITNESS_REPLAY_STRICT=1` skip⇒fail) and enrolls both this family and the existing 07W.1 `workbook-deep-dive-call.v1` witnesses (`_bmad-output/implementation-artifacts/evidence/deep-dive-38-3a-live-{7ed48f8a,b6fc76ea}/`) as the founding rows.
7. **Deterministic verification — live-shape fixtures ONLY**
   - **Given** protocol plank 2 **When** consume-side tests are authored **Then** every pool/journal/render fixture derives from the two real runs — the Ask-A journal/pool shapes from `runs/a940c5eb-1043-42c1-a2a4-8a6301b6bcf4/ask-a-research-call.v1.json` (real fields incl. `citation_id: ask-a-cite-001`, `evidence_excerpt`, `evidence_body_sha256`, `supports_ability_ids` (7), `supports_bold_terms` (1), tier `T4_peer_other`, covered/uncovered lists, `scope_digest`) and the rendered-workbook shape from `runs/8b275e5b-ed8a-4720-8217-8ddaca4c6627/exports/workbooks/u01@1.md` — no hand-invented shapes. Fixtures digest-bind to their `schema_version` with a bump tripwire (protocol drift-flags amendment). Mutation tests cover the full AC2 matrix, journal crash/replay/ambiguity, upgrade/no-op/split-brain reconciliation rows, bold-parity/term-trace rejects, D2.4 overlay-input presence/absence, and the negative-witness bar pins. Focused suite + dependency regressions (37.2a's 58-test suite, 37.1 frame, 38.1 Ask-A suites, workbook-band topology, run-dir threading floor), strict warnings, Ruff, import-linter, lockstep checker — all green; inherited failures compared by exact node/signature per the 38.1 idiom, never by count.
8. **Component-probe AC (registered HERE, before it runs — probe honesty contract)**
   - **Probe id:** `probe-37-2b-deep-dive-enrichment-001`.
   - **Exact claim licensed:** "the live deep-dive enrichment writer produces cited, bolded, pool-grounded prose on real inputs — the frozen Tejal Part-2 authored skeleton + the real `a940c5eb` Ask-A pool — passing the A2 gate first-run." It licenses NOTHING else (not "the pipeline works", not render, not the bar).
   - **Vehicle:** NEW `scripts/utilities/run_deep_dive_enrichment_37_2b_live_evidence.py`, a clone of `scripts/utilities/run_deep_dive_38_3a_live_evidence.py` (same one-shot, failed-evidence-preservation-pin, immutable-attempt-dir discipline).
   - **Deterministic machine judge:** the AC2 gate + AC4 parity gates over the probe output — no human vibes, no LLM judging itself.
   - **Evidence pack:** immutable attempt dir under `_bmad-output/implementation-artifacts/evidence/` with input digests (skeleton authority/candidate, pool packet, prompt-text digest, model id + config identity per the drift-flags amendment), raw provider payload, normalization records, journal, machine verdict JSON.
   - **First-run-stands.** A failed probe is preserved immutably and remediated under governance — no retry-to-green. On PASS the probe output **freezes as the path's first witness fixture** (zero-witness rule) and enrolls per AC6.
9. **Batch-run AC — governed run A (full-pipeline claim)**
   - **Given** protocol plank 4 **When** deterministic suite + probe + `bmad-code-review` are green **Then** this story flips to `done-awaiting-live-witness  # deterministic+review green; component probe probe-37-2b-deep-dive-enrichment-001 green; full-run witness owed by batch run A (after 39-1)`. Run A's pre-flight replays ALL enrolled witnesses in STRICT mode (skip ⇒ fail) and records "replay GREEN, N witnesses, 0 skipped". Run A's evidence pack carries this story's per-verdict line keyed to `07W.3` + the A2 gate: REACHED+PASS = witness → flip to `done` citing the run id; NOT-REACHED = claim stays OPEN (never pass, never fail). This story never crosses two batch boundaries unwitnessed.

## Scope Fences (hard NO)

- NO glossary rendering, entries, links/anchors, or top-up — 39.1 (this story only preserves/extends the bolded-term set 39.1 consumes).
- NO Ask-B / `07W.4` / trends / Door-Ajar — 38.2 + 39.2.
- NO `app/specialists/irene_pass1/` changes (M-R2 fence — see T1 item 4).
- NO Check/Reflection live wiring (typed known_losses only), NO References assemble/dedupe redesign (37.5), NO mode-parity work (37.6).
- NO manifest topology, node, pack-version, or learning-event changes; NO `production_runner.py` or `research_packet.py` edits (any of these = undeclared lockstep expansion → STOP, party-gate).
- NO new provider clients; the enrichment writer rides the existing `make_chat_model` / structured-writer stack.

## Lockstep declaration

| `block_mode_trigger_paths` entry | Touched? | Why |
|---|---|---|
| `app/marcus/orchestrator/workbook_wiring.py` (manifest L109) | **YES** | 07W.3 factory activation + journal reconciliation |
| `app/marcus/lesson_plan/research_packet.py` (L110) | no | resolver already exists; read-only consumer |
| `app/marcus/orchestrator/production_runner.py` (L106) | no | both-walk persistence landed in 38.1 |
| `state/config/pipeline-manifest.yaml` (L61) | no | 07W.3 node + model_config_ref already declared |

Tier-1 within-node activation (see T1 item 3); regime doc read at T1; lockstep checker + Cora classification at closure.

## Gate taxonomy (A9)

| Gate | Disposition | Witness | Owner |
|---|---|---|---|
| Enrichment claim-typing / citation binding / phantom-citation / cross-packet (AC2 a–c) | FAIL | automated mutation tests | 37.2b |
| Empty-pool empty-honesty (AC2 d) | DEGRADE (typed) | automated | 37.2b |
| Zero-use-claims-enriched / receipt-vs-prose coverage (AC2 e,g) | FAIL | automated | 37.2b |
| Unused-row honesty reporting (AC2 f) | REPORT | automated receipt pins | 37.2b |
| A3 proper-superset re-run on enriched claim set (AC2 h) | FAIL | automated (37.2a gate reused) | 37.2b |
| Bold parity + term-trace continuity (AC4) | FAIL | automated | 37.2b |
| Numeric fidelity over enriched prose (37.2a witnesses re-run) | FAIL | automated | 37.2b |
| Semantic claim↔evidence support | WARN | operator prose spot-check (run A) | 37.2b (declared) |
| D2.4 overlay-dedup residual duplication | WARN | operator spot-check at run A | 37.2b (declared) |
| Deliverable bar: deep-dive section conformance + negative pins (AC6) | FAIL | automated (test-harness side) | 37.2b |
| Journal exactly-once / replay / split-brain (AC5) | FAIL | automated | 37.2b |
| Glossary render / References dedup / Ask-B | NOT OWNED | downstream | 39.1 / 37.5 / 38.2 |

## Dev Notes

### Code map (anchors verified at baseline `c0811817`)

- NEW `app/marcus/lesson_plan/deep_dive_enrichment.py` — contracts + pure A2 gate (AC1–4).
- NEW `app/marcus/orchestrator/deep_dive_enrichment_wiring.py` (or fold into `workbook_wiring.py` if the diff stays coherent) — journaled dispatch (AC5).
- UPDATE `app/marcus/orchestrator/workbook_wiring.py:1177–1198` (`_review_stub` → activated factory; `DEFAULT_WORKBOOK_BAND_FACTORIES`), `:116–134` (ids), `:1218–1243` (live writer injection).
- UPDATE `app/marcus/orchestrator/workbook_prework_writers.py` — `LiveDeepDiveEnrichmentWriter` mirroring `LiveDeepDiveWriter` (L363–394) with its own provider contract mode/normalizer version (mirror `app/marcus/lesson_plan/deep_dive_provider_contract.py`, 87 lines).
- UPDATE `app/marcus/lesson_plan/workbook_producer.py:572–607` (Overview copy), NEW `## Deep Dive` block, References resolvability floor; `app/specialists/workbook_producer/_act.py` input threading only (its G2 sidecar idiom at `_act.py:1265` is precedent for surfacing counts).
- UPDATE `scripts/utilities/marcus_spoc_live_test_runner.py:1236` (`_assert_completed_workbook_deliverable`) — same diff, negative pins (AC6).
- NEW `tests/live_witness_replay/` + `witnesses.yaml` (AC6); NEW probe script (AC8); tests under `tests/unit/marcus/lesson_plan/`, `tests/unit/marcus/orchestrator/`, `tests/integration/marcus/`; fixtures under `tests/fixtures/deep_dive_enrichment_37_2b/` derived from the two real runs (AC7).

### Seams to reuse (do NOT re-derive)

- Skeleton authority + digests: `deep_dive_projection.py` (`compose_deep_dive_skeleton` L816, `deep_dive_authority_digest` L281, `_gate` L535); persisted skeleton lives in `WorkbookBriefArtifactV1.deep_dive_skeleton` (`prework_artifact.py:227`) with receipt reconciliation L254–288 — join by its digests, never by prose.
- Pool: `resolve_for_enrichment_pool` (`research_packet.py:332`); intake covered/uncovered lists (`ask_a_enrichment.py:299`); entry shape `AskAKnowledgeEntryV1` (`ask_a_enrichment.py:215`).
- Journal discipline: 07W.1 walk at `workbook_wiring.py:627–780` + 38.1's reconciliation table (`38-1-ask-a-enrichment-wiring.md` AC5–6) — same states, same zero-recall posture.
- Citation resolvability precedent: `app/marcus/orchestrator/research_citation.py` (G2 `unsourced_citations == 0`, L223–260) — A2 deliberately goes beyond it (coverage, not just resolvability); do not weaken G2.
- D2.4 input: `project_enrichment_to_workbook_inputs` (`workbook_enrichment.py:561`) → `WorkbookEnrichmentProjection.learning_objectives` + `spec` exercise prompts (L77–93).

### Guardrails

- Product work only (SPOC): every change earns its place in the production runtime — nothing lands "so the probe passes."
- M3: `lesson_plan` never imports `marcus.orchestrator`; the pool and skeleton cross the wall disk-mediated.
- Terminal `07W` stays deterministic-consume and model-free; semantic writing happens at 07W.3 only.
- First-run-stands on every live leg; cost is not the constraint — variance discipline is (signal per run).

### References

- `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` — Story 37.2 (L115–124), A1/A2/A3/A9 (L224–233), graph-shape record (L243–293), FR7/FR12/FR15
- `_bmad-output/planning-artifacts/wave-3940-kickoff-party-record-2026-07-15.md` — D2 §4/§7, D3 planks + amendments, wave run plan
- `_bmad-output/implementation-artifacts/37-2a-deep-dive-skeleton.md` — predecessor contracts, gate taxonomy, Dev Notes
- `_bmad-output/implementation-artifacts/38-1-ask-a-enrichment-wiring.md` — pool contract, journal/reconciliation idiom, live close-bar idiom
- `_bmad-output/implementation-artifacts/epic-38-retro-2026-07-15.md` — doctrine + M-R2/M-R3 riders
- `runs/a940c5eb-1043-42c1-a2a4-8a6301b6bcf4/ask-a-research-call.v1.json` · `runs/8b275e5b-ed8a-4720-8217-8ddaca4c6627/exports/workbooks/u01@1.md` — live shapes
- `docs/dev-guide/pipeline-manifest-regime.md` · `docs/dev-guide/how-to-add-a-specialist.md`

## Change Log

- 2026-07-15: Story authored from the ratified A1 split + A2 coverage-gate amendment + wave-3940 Paid-Run Economy Protocol; deterministic A2 matrix, probe registration (`probe-37-2b-deep-dive-enrichment-001`), same-diff deliverable-bar extension with negative pins, witness-registry founding, D2.4 dedup input, Tier-1 lockstep declaration (workbook_wiring.py), and M-R2 not-applicable verdict pinned. Status: **draft** pending party green-light round.
