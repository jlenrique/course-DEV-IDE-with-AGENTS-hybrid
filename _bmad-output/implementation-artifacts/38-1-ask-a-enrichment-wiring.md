---
baseline_commit: 6ae42a5208bb4a9fcb5bee8668705d6c8b9dd1d7
---

# Story 38.1: Ask-A enrichment research wiring

Status: in-progress

## Story

As the Marcus-SPOC workbook runtime,
I want `07W.2` to consume the exact ready demand from `07W.1` and mint one cited, credibility-tiered Ask-A knowledge pool,
so that the Deep Dive and glossary can add real sourced depth without generic-research fallback, model-prior invention, or duplicate research.

## Dependency Position

`38.0 -> 38.3b -> {36, 37.1, 37.2a, 37.3, 37.4} -> 38.3a -> 38.1 -> 37.2b -> 39.1 -> 38.2 -> 39.2 -> 40.1`

All predecessors are done. This story activates the already-positioned model-free `ask_a_enrichment@07W.2` coordinate. It blocks Story 37.2b and therefore every later dependency-path story.

## Party Green-Light Record

On 2026-07-13, independent native BMAD seats John (PM), Winston (architect), and Murat (test architect) reviewed the story against current planning, predecessor contracts, code, and tests. Round 1 returned three GO-WITH-AMENDMENTS verdicts. The story folded every MUST: immutable pre-call scope versus post-call execution evidence; strict Ask-A entry/intake/output/journal validation; downstream ability/term coverage; exact retry/terminal dispositions; exclusive two-worker call ownership; reproducible evidence extraction; complete journal/contribution reconciliation; sole-writer outer-envelope persistence in both walks; exact inherited-failure attribution; and machine-readable live evidence. The exact-current confirmation round returned **FINAL GO 3/3**, and the orchestrating agent concurs. Per repository governance, this is authorization to implement without a redundant human hold.

## Acceptance Criteria

1. **Exact ready demand is the sole dispatch authority**
   - Call `resolve_enrichment_demand(run_dir)` and dispatch only when its strict `AskAResearchDemandV1.status == "ready"`.
   - Bind the exact demand digest, workbook-brief digest, skeleton authority/candidate digests, ordered ability IDs/text, ordered exact bold terms, and source-claim refs into the Ask-A scope.
   - Never reconstruct demand, scrape prose, infer keywords, substitute Scene terms, use model priors, read another run, or fall back to `research_wiring@04.55` or `ask_b_hot_topics@07W.4`.
   - Corrupt/forged/mismatched demand fails with `ask-a.demand-invalid`. Valid non-ready demand makes zero Texas calls and emits typed retryable honesty rather than fabricated rows.

2. **One deterministic Ask-A research pass**
   - Create one ordered `RetrievalIntent` jointly scoped to every authored ability and exact bold term, even when the research-detective flag is OFF. Source-claim refs are audit identities, not provider source refs.
   - One pass means exactly one Texas `dispatch_intent(intent)` invocation. Record dispatcher invocations separately from observable `ProviderResult.iterations_used`, refinement logs, and provider receipts; never claim an unobservable HTTP-call count. This story adds no retry loop.
   - The canonical query and structured intent must contain the complete ordered scope. If the effective provider/config query limit cannot carry it, fail before dispatch with `ask-a.scope-overflow`; never truncate, drop, or reorder scope and never silently partition it into extra dispatcher invocations.
   - Reuse `_research_dispatch_live()` as the sole research switch in both walks. Kill-switch OFF is a typed retryable zero-call output. `07W.2` remains manifest model-free (`specialist_id:null`, `model_config_ref:null`): it owns no workbook-writer LLM configuration.

3. **Strict, evidence-bearing Ask-A contract**
   - Add frozen, extra-forbid lesson-plan models `AskARetrievalScopeV1`, `AskAExecutionReceiptV1`, `AskAResearchIntakeV1`, `AskAKnowledgeEntryV1`, and a discriminated `AskAContributionOutputV1`. These contracts import no orchestrator or Texas implementation types.
   - The immutable pre-call scope binds demand/workbook/skeleton digests, ordered abilities, terms, claim refs, the complete exact query/query digest, posture, and a non-secret provider/adapter/config fingerprint. It contains no outcome or call count. The pre-call journal, idempotency key, and every entry bind `scope_digest`.
   - The post-call execution receipt binds the immutable scope snapshot/digest, dispatcher invocation count, provider iterations/refinement logs, outcomes, receipts, and its own digest. Store scope plus execution receipt under the existing `research_intake` key so both remain in the unchanged packet-digest domain. Never mutate the pre-call scope during completion/replay and never persist or hash credentials/tokens.
   - A usable entry retains all current packet-required fields plus `evidence_excerpt`, `evidence_truncated`, `evidence_body_sha256`, `scope_digest`, ordered `supports_ability_ids`, ordered `supports_bold_terms`, association-basis evidence, and packet-namespaced citation ID `ask-a-cite-###`.
   - Scope associations are deterministic and auditable: a bold-term association requires the exact demanded term under NFC+casefold+whitespace-collapse comparison in the raw title/body; an ability association requires persisted matching nontrivial tokens from the exact ability text under one committed fixed-token/stopword algorithm. The entry records the matched term/tokens and algorithm version. Reject a row with neither association. Intake exposes ordered covered/uncovered ability IDs and bold terms for 37.2b selection and 39.1 top-up.
   - Evidence extraction is exact: require `TexasRow.body.strip()` nonblank; preserve `evidence_excerpt = body[:2000]` by Python Unicode code points with no normalization or summarization; set truncation from `len(body) > 2000`; hash the full unmodified UTF-8 body separately and recompute the existing full-row `source_hash`. Replay must reproduce the excerpt exactly and fail on any raw-body, excerpt, body-hash, source-hash, or scope mutation.
   - Filtering order is strict: raw-row/source validation -> evidence extraction -> credibility admissibility -> scope association -> existing first-wins source dedupe -> contiguous `ask-a-cite-###` numbering. T1-T6 rows may be usable with their existing tier/peer-review caveats; T7/T8 are excluded from cited enrichment and recorded as indexed losses. Missing evidence, source identity/ref, admissible tier, provenance, or association records one stable indexed loss. Never add a model summarization/classification call.

4. **Producer losses participate in packet honesty and digest**
   - Update `load_research_packet()` to validate producer `known_losses` as an ordered list of nonblank single-line strings; malformed containers or entries fail loudly.
   - Merge producer losses before reader losses with deterministic first-wins deduplication. Usable rows plus any loss yield `degraded`; no usable rows yield `empty`.
   - At exact `ask_a_enrichment@07W.2`, the reader must validate strict Ask-A output, scope, intake, execution receipt, and every entry. Missing/mismatched scope/intake invalidates the whole Ask-A packet loudly; blank/malformed row evidence becomes its deterministic indexed row loss. Generic `04.55` and Ask B retain their current entry semantics.
   - Mutations cover null/string/mapping loss containers; non-string, blank, whitespace-only, multiline, and duplicate entries; producer-before-reader ordering; and deterministic deduplication.
   - Empty output still binds the exact Ask-A scope through validated `research_intake` and losses. Do not change packet coordinates, schema version, digest algorithm, or `ProductionEnvelope` v2.

5. **Crash-safe call journal and exactly-once replay**
   - Before the first external call, acquire an exclusive per-trial `ask-a-research-call.v1.lock` using create-if-absent semantics, then atomically write `ask-a-research-call.v1.json` with `state="call_in_progress"`, a canonical idempotency key binding trial ID, demand digest, immutable scope/query digest, and non-secret provider/config fingerprint, plus the validated scope snapshot. No automatic stale-lock reclamation is allowed; a stranded lock/journal is ambiguous.
   - A completed journal stores raw Texas rows including evidence bodies, exact normalization/filter/loss records, scope/intake, output, receipts, and all relevant digests. On replay, recursively validate and recompute the exact output; make zero network calls.
   - `call_in_progress` is an ambiguous-call hard pause and forbids automatic recall. Completed honest-empty is terminal and also forbids recall.
   - Provider exceptions leave the `call_in_progress` claim intact: the current invocation reports `ask-a.provider-execution-failed`; any re-entry reports `ask-a.call-ambiguous` with zero recall.
   - A barrier-controlled two-worker test must prove exactly one Texas dispatch; the losing worker makes zero calls and fails/pauses on the held claim. Mutate pre-call write failure, completed-write failure, temp collision, lock collision, and preserved `call_in_progress`.
   - Symlink/nonregular/path escape, invalid JSON/schema/digest, atomic-write failure, or split-brain state fails closed. Stable tags are `ask-a.scope-overflow`, `ask-a.dispatch-init-failed`, `ask-a.provider-execution-failed`, `ask-a.output-invalid`, `ask-a.persistence-failed`, `ask-a.call-ambiguous`, `ask-a.reconciliation-failed`, and `ask-a.split-brain`; translate inside the Ask-A seam so the outer factory does not collapse them to `workbook.band.factory-failed`.

6. **Exact-coordinate activation and retry disposition**
   - Replace only the reserved `07W.2` stub factory. Preserve `ask_a_enrichment@07W.2`, specialist/node order, graph/manifest/pack/event/gate/HUD surfaces, and terminal `07W` behavior.
   - `AskAContributionOutputV1.disposition` is one of `retryable_demand_not_ready`, `retryable_dispatch_disabled`, `retryable_credentials_unavailable`, `completed_empty`, `completed_degraded`, or `completed_ready`. Retryable states require empty entries, zero dispatcher invocations, and no journal; they carry exact loss codes `ask_a_demand_not_ready`, `ask_a_dispatch_disabled`, or `ask_a_credentials_unavailable`. Completed states require a validated completed journal and exactly one dispatcher invocation: empty has zero usable entries, degraded has usable entries plus losses, ready has usable entries and no losses.
   - An existing `stub_status:not_yet_wired` or typed retryable output may be replaced at the same coordinate when its prerequisite changes. Any completed output reconciles and is never recalled.
   - Reconcile journal and exact-coordinate envelope output before replacement. No duplicate coordinate, blind overwrite, or latest-specialist/any-node lookup.
   - Emit a node-specific deterministic execution marker such as `deterministic-ask-a-research-wiring`, not the generic workbook stub marker.

   Reconciliation is exact:

   | Journal | Exact contribution | Disposition |
   |---|---|---|
   | absent | absent, legacy stub, or typed retryable | dispatch/upgrade only when current prerequisites are ready; otherwise emit/no-op the exact retryable state |
   | completed | absent, legacy stub, or typed retryable | recompute from raw journal evidence and roll forward with zero dispatch |
   | completed | exact matching completed | no-op; zero dispatch and zero persistence/projection/event effects |
   | completed | conflicting completed | `ask-a.split-brain` |
   | `call_in_progress` | any state | `ask-a.call-ambiguous` |
   | absent | any completed state | `ask-a.split-brain` |
   | any mismatch of scope/idempotency/output digests | any state | `ask-a.reconciliation-failed` or `ask-a.split-brain` before dispatch |

   Wrong-specialist/right-node and right-specialist/wrong-node contributions never satisfy the exact lookup and remain untouched; the exact coordinate is independently resolved/created.

7. **Inter-node disk visibility in both production walks**
   - After an actual workbook-band mutation in both runner walks, update `run_state`, replace the outer envelope's `production_envelope`, and persist the outer `ProductionTrialEnvelope` through the existing sole `_persist_envelope` writer before `continue`. Exact no-op reconciliation does not rewrite.
   - Prove that `07W.1` becomes immediately visible to disk-only `resolve_enrichment_demand()` at `07W.2`. Persistence failure pauses with a stable typed tag; never introduce a second `run.json` writer.
   - Preserve the last durable `run.json` on failure. If atomic hardening is needed, harden `_persist_envelope` itself rather than adding a writer. Because that writer also emits operator projection, parity tests assert the intended mutation-time projection and prove no extra emission on no-op resume.
   - Preserve resume behavior, learning-event count, and parity between the two walks.

8. **Downstream boundary remains clean**
   - `resolve_for_enrichment_pool(run_dir, require_usable=True)` must read the resulting packet and witness the same stable packet digest on reload.
   - Story 38.1 produces upstream knowledge only. It does not write Deep-Dive prose, glossary entries, References/Further Reading, trends, Review/Check/Reflection content, Markdown/DOCX, or terminal render output.
   - Story 37.2b owns sentence-level citation coverage; Story 39.1 owns glossary coverage/top-up; Story 37.5 owns References rendering. This story's G2-equivalent check is source/citation resolvability, not a full semantic claim-support audit.

9. **Verification and live close bar**
   - Hermetic tests inject Texas only at the owned dispatch seam, prohibit network access, and cover ready/non-ready/corrupt demand; exact scope ordering/overflow; coverage association; evidence extraction/mutation; loss validation/order/status; provider exceptions; exclusive claim/concurrency; journal crash/replay; every reconciliation-table row; stub upgrade; all retryable dispositions; terminal empty; split-brain; wrong-coordinate collisions; both-walk visibility; and unchanged generic/Ask-B behavior. Maintain an AC-to-named-test traceability table.
   - Run focused plus dependency regressions, strict warnings, Ruff, import-boundary checks, manifest/graph/pack parity, and the applicable Cora block-mode lockstep regime.
   - Both runner-walk tests use the real `_persist_envelope` writer and disk-only demand reader. No-op resume proves no extra persistence/projection/event effects and no provider call.
   - Record the exact pre/post baseline command, node IDs, exception class, and dependency signatures for every inherited failure; a count alone is insufficient.
   - Before live dispatch, atomically allocate a fresh immutable attempt directory. Close only after one bounded first-run-stands live Tejal Part-2 production-seam attempt consumes a real ready `07W.1` demand and persists a non-vacuous Ask-A packet with at least one real usable row associated to at least one exact ability and one exact bold term, containing reproducible evidence text, a run-local G2-resolvable source ref and valid DOI where the provider supplies one, admissible credibility tier, peer-review posture, provenance, and receipt. Preserve any failed attempt immutably; no retry-to-green without a governed correction.
   - Reload must preserve exact digests, `resolve_for_enrichment_pool(require_usable=True)` must pass, and resume/re-entry must make zero provider calls. Generic `04.55` and Ask B remain unchanged.
   - Emit a machine-readable live verdict covering dispatcher invocation count, completed journal, coverage associations, evidence/body/source hashes, source-ref/DOI checks, credibility fields, execution receipt, packet/journal/envelope hashes, reload equality, and zero-call replay.

## Tasks / Subtasks

- [x] Task 1: Define strict Ask-A scope and evidence contracts (AC: 1-4)
  - [x] Add `app/marcus/lesson_plan/ask_a_enrichment.py` with strict scope/execution/intake/entry/output models, canonical digest helpers, fixed association/evidence algorithms, exports, and validation.
  - [x] Update `app/marcus/lesson_plan/research_packet.py` to validate/carry producer losses without changing packet schema or digest rules.
  - [x] Add contract tests for ordering, coverage association, evidence/body/source hash binding, output dispositions, digest binding, empty/degraded states, and malformed losses.

- [x] Task 2: Build orchestrator-owned Ask-A wiring and call journal (AC: 1-6)
  - [x] Add `app/marcus/orchestrator/ask_a_research_wiring.py` using the existing posture, Texas dispatch, citation, credibility, deduplication, and triangulation seams.
  - [x] Implement exclusive call claim, atomic pre-call/completed journaling, exact replay, stable error translation, strict disposition/reconciliation tables, and split-brain handling.
  - [x] Add barrier-controlled two-worker, write-failure, temp/lock collision, ambiguous-call, and zero-recall tests.
  - [x] If pure helpers must be extracted from `research_wiring.py`, preserve generic `04.55` bytes/semantics and cover them with regressions; do not duplicate provider clients.

- [x] Task 3: Activate only `07W.2` (AC: 2, 5, 6)
  - [x] Update `app/marcus/orchestrator/workbook_wiring.py` to inject runtime context for `07W.2`, replace legacy/retryable placeholders coherently, and preserve exact-coordinate idempotency.
  - [x] Add focused workbook-band tests for legacy upgrade, completed replay, marker identity, kill-switch posture, and no graph/manifest drift.

- [x] Task 4: Persist between band nodes in both walks (AC: 7)
  - [x] Update both workbook-band walk sites in `app/marcus/orchestrator/production_runner.py` to use the existing `_persist_envelope` writer after each local band mutation.
  - [x] Add two-walk parity tests proving `07W.1 -> disk -> 07W.2` visibility and stable pause/error behavior.

- [ ] Task 5: Prove downstream resolution and non-regression (AC: 8-9)
  - [x] Add unit/integration tests under `tests/unit/marcus/` and `tests/integration/marcus/` for the full Ask-A seam and public resolver.
  - [x] Run the focused/dependency/static/lockstep suites and record exact commands/results.
  - [x] Maintain an AC-to-test traceability table and exact inherited-failure comparison.
  - [ ] Execute one governed live Tejal Part-2 attempt; preserve raw evidence, coverage, receipts, packet/journal/envelope hashes, reload/replay checks, and machine-readable first-run verdict.

## Dev Notes

### Existing seams to reuse

- `resolve_enrichment_demand()` in `research_demand.py` is the sole disk-based authority and already validates the authored skeleton, Promise abilities, exact bold terms, claim refs, and digests.
- `research_wiring.py` already owns deterministic posture selection, Tracy bridge, Texas dispatch, Scite-canonical retrieval, citation minting, credibility tiers, optional triangulation, first-wins deduplication, source-ref fidelity, citation manifest, intake, and visible credential degradation. Extract only pure reusable pieces if necessary.
- `research_packet.py` already preserves extra entry keys and hashes entries, losses, intake, and triangulation receipt. Its current defect is ignoring producer losses.
- `workbook_wiring.py` already reserves `ask_a_enrichment@07W.2`; the current factory is an honest-empty stub. The runner already passes context to every band node, but the default factory currently receives it only for `07W.1`.
- Keep `07W.2` runtime input minimal (`run_dir`, dispatch-live posture, non-secret provider/config fingerprint). Do not make the writer-bearing `WorkbookBriefRuntimeContext` its architectural contract merely because the current factory seam uses that type.
- Both production-runner walks currently update only local `run_state.production_envelope` between band nodes. Disk-mediated demand therefore sees stale `run.json`; use the existing writer rather than memory fallback.
- `TexasRow.body` contains the evidence needed by downstream cited enrichment. Existing `CitedResearchEntry` drops it, so Ask A must retain a bounded verbatim excerpt with source-hash binding.

### Guardrails

- Product work only: fix the SPOC production seam, never add proofing-only behavior.
- `lesson_plan` may not import `marcus.orchestrator`; M3 crossing remains disk/envelope mediated.
- No terminal `_act.py`, renderer, provider-adapter, graph, manifest, node-order, gate, event, HUD, or envelope-schema changes.
- No `07W.3`, `07W.4`, glossary, References, Deep-Dive enrichment, or semantic-coverage implementation.
- Preserve unrelated ambient run/evidence files and the shadow monitor.
- Applicable lockstep trigger paths include `workbook_wiring.py`, `production_runner.py`, and `research_packet.py`; run Cora classification before closure.

### Baseline and known environment failures

- Exact pre-story baseline command: `./.venv/Scripts/python.exe -m pytest -q tests/unit/marcus/lesson_plan/test_research_packet_w1.py tests/unit/marcus/lesson_plan/test_research_demand_38_3a.py tests/integration/marcus/test_workbook_band_wiring.py tests/integration/marcus/test_braid_s3_research_wiring.py --tb=short` -> `4 failed, 140 passed, 3 skipped in 35.15s`.
- The four inherited failures occur at `production_runner.py:3069` before target behavior and must be compared by exact node/signature after implementation:
  - `test_ac_d2_two_walk_parity_fires_on_real_continuation` -> `PreflightGateFailed`, `openai=fail`.
  - `test_m1_kill_switch_threads_false_to_both_walks` -> `PreflightGateFailed`, `hud-server-healthz=fail, openai=fail`.
  - `test_m1_toggle_on_threads_true_to_continuation_walk` -> the same HUD/OpenAI signature.
  - `test_m2_fail_mode_gate_error_pauses_the_trial_walk` -> the same HUD/OpenAI signature.
- Isolate/pin preflight in new runner tests and do not misclassify these four as Story-38.1 regressions. Any changed node ID, exception class, or dependency signature requires investigation.
- Immediate predecessor close: Story 38.3a had 246 passed, 7 skipped, exact-current Blind/Edge/Acceptance zero findings, Cora block-mode lockstep PASS, Audra closure PASS, and a preserved 12/12 live witness.

### Project Structure Notes

- New lesson-plan contract: `app/marcus/lesson_plan/ask_a_enrichment.py`.
- New orchestrator adapter: `app/marcus/orchestrator/ask_a_research_wiring.py`.
- Update only `research_packet.py`, `workbook_wiring.py`, `production_runner.py`, and—if pure extraction is unavoidable—`research_wiring.py`.
- Tests follow existing `tests/unit/marcus/lesson_plan`, `tests/unit/marcus/orchestrator`, and `tests/integration/marcus` conventions. Live evidence belongs under a fresh immutable `_bmad-output/implementation-artifacts/evidence/` attempt directory.

### References

- [Source: `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` — Epic 38, Story 38.1, ratified graph decision and DAG]
- [Source: `_bmad-output/planning-artifacts/workbook-presentation-support-redesign-2026-07-12.md` — §§7.1, 8, 8.1, 13.5]
- [Source: `_bmad-output/implementation-artifacts/38-0-two-packet-intake-contract.md` — packet identity, digest, and resolver contracts]
- [Source: `_bmad-output/implementation-artifacts/38-3a-research-packet-consume-side.md` — ready-demand contract, exact coordinates, dependency handoff]
- [Source: `_bmad-output/implementation-artifacts/38-3b-graph-topology-band-orchestrator.md` — fixed topology, model-free band, idempotency]
- [Source: `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-13.md` — 38.1 unblocked only by ready demand; no scope broadening]
- [Source: `app/marcus/lesson_plan/research_demand.py` — exact current demand reader]
- [Source: `app/marcus/lesson_plan/research_packet.py` — exact current packet loader/digest]
- [Source: `app/marcus/orchestrator/research_wiring.py` — existing research service]
- [Source: `app/marcus/orchestrator/workbook_wiring.py` — reserved 07W.2 factory]
- [Source: `app/marcus/orchestrator/production_runner.py` — both workbook-band walk sites and sole persistence writer]

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Debug Log References

- Task 1 RED: missing `ask_a_enrichment` module; GREEN: strict contract/packet tests.
- Task 2 RED: missing orchestrator adapter; GREEN: exactly-once journal, replay, concurrency, mutation, and failure tests.
- Task 1-2 focused/dependency result: 119 passed; four inherited preflight failures retained exactly at `production_runner.py:3069` with the baseline exception/dependency signatures.
- Task 5 exact-current deterministic matrix: `171 passed, 3 skipped, 4 failed`; each failure remains the inherited `PreflightGateFailed` at the same node and dependency signature (the implementation moved the source line from 3069 to 3083). Focused strict-warning matrix: `84 passed`; post-correction isolated strict suites added `22 passed`; Ruff and `git diff --check` clean; import-linter `18 kept, 0 broken`; pipeline-manifest lockstep exit 0 with PASS trace `reports/dev-coherence/2026-07-13-1547/check-pipeline-manifest-lockstep.PASS.yaml`.
- Governed live attempt `9d2ab3f1-7e6c-4d9a-b835-12c7e8f46031`: delegated runner completed eight gates without operator keyboard input, then failed closed before Ask-A at `07W.1` with `workbook-brief.deep-dive-authority-invalid`. Read-only diagnosis found `resolve_promise_objectives()` degraded with `promise_ratified_lo_lineage_unverified`: `irene-pass1.lesson-plan.json` recorded a null `ratified_los_digest` while the actual authority SHA-256 was `a41a942dffeca6f3842cfca17f61a1717e690fd6642a29138c71f789006ffd9e`. The immutable verdict records dispatcher count zero and every unmet live close-bar field; no retry or run mutation occurred.
- Governed production correction RED/GREEN: `test_irene_pass1_runner_payload_binds_run_identity_for_both_aliases` first failed because the real shared runner seam omitted run identity, then passed after the seam began threading its existing `runs_root`/`run_id` to Irene pass-1. Existing planning-context/floor suites passed after their expected runner-context shape was updated. Fresh attempt `c8f17a24-9b63-4e10-a5d7-6f2043bc9812` proved the correction live: Irene's persisted digest exactly matched `ratified-los.json`, then `07W.1` failed independently because the 13-slide segment manifest reached `slide-07` while the declared Tejal slide authority contains only six files. The immutable verdict records the successful correction witness and unmet Ask-A close bar; no further retry occurred.
- Separate HUD/runtime follow-on: notifier-spawning inherited tests leaked 82 dummy-trial `python -m app.notify` processes rooted only under `.tmp/pytest-fixtures/.../12345678-...`, causing visible empty consoles. After verification they were selectively terminated (zero matched processes remain); no live trial or unrelated service was touched. This process/conhost lifecycle defect is not part of Story 38.1.

### AC-to-Test Traceability

| AC | Named witnesses |
|---|---|
| 1 | `test_scope_preserves_authority_order_and_binds_complete_query`; `test_nonready_and_disabled_are_typed_zero_call`; research-demand strictness suite |
| 2 | `test_one_dispatch_completed_journal_and_zero_call_replay`; `test_scope_overflow_fails_before_claim_or_dispatch`; braid kill-switch parity tests |
| 3 | `test_evidence_is_exact_unicode_slice_and_full_body_hash`; `test_association_requires_exact_term_or_nontrivial_ability_tokens`; `test_entry_rejects_no_scope_association_and_wrong_evidence_hash`; `test_duplicate_loss_uses_original_raw_row_index` |
| 4 | `test_producer_losses_precede_reader_losses_and_dedupe_first_wins`; `test_malformed_producer_losses_fail_loud`; `test_ask_a_present_malformed_contract_fails_loud`; `test_ask_a_strict_completed_packet_resolves_stably` |
| 5 | `test_barrier_two_workers_exactly_one_dispatch`; `test_precall_write_failure_preserves_lock_and_reentry_is_ambiguous`; `test_completed_write_failure_leaves_in_progress_and_reentry_is_ambiguous`; `test_temp_collision_fails_before_dispatch`; `test_completed_raw_body_mutation_fails_replay` |
| 6 | `test_retryable_dispositions_are_zero_call_and_journal_free`; `test_ask_a_default_factory_upgrades_legacy_and_retryable_is_exact_noop`; `test_ask_a_completed_envelope_without_journal_fails_split_brain`; `test_manifest_band_and_model_config_are_pinned` |
| 7 | `test_start_walk_reaches_07w1_with_persisted_normalized_context`; `test_real_start_then_continuation_reaches_band_in_order`; `test_atomic_outer_writer_preserves_last_durable_run_on_replace_failure` |
| 8 | `test_dual_consumers_share_digest`; `test_named_resolvers_require_usable_and_validate_rows`; `test_research_packet_has_no_orchestrator_import` |
| 9 | Strict-warning/focused/dependency matrices, Ruff, import-linter, lockstep PASS, and immutable live verdict `evidence/workbook-live-hil/9d2ab3f1-7e6c-4d9a-b835-12c7e8f46031/verdict.json` |

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Tasks 1-2 complete: immutable pre-call scope is separated from execution evidence; exact evidence and association rules are digest-bound; producer losses participate in packet honesty; the Texas call is exclusively claimed, atomically journaled, and replayed without recall.
- Task 3 complete: only `ask_a_enrichment@07W.2` is activated; legacy/retryable outputs upgrade at the exact coordinate, completed replay is zero-effect, the marker is node-specific, and both production walks thread the shared dispatch-live switch.
- Task 4 complete: both walks publish each actual workbook-band mutation through the sole outer-envelope writer before advancing; the real start and continuation tests prove disk-mediated `07W.1 -> 07W.2` visibility, no-op candidates do not write, and atomic writer failure preserves the last durable `run.json`.
- Task 5 deterministic/static work is complete and exact-current. Live closure remains open because the one first-run-stands Tejal attempt stopped at predecessor node `07W.1`; it neither reached nor disproved the Ask-A seam, and the failed attempt is preserved with a machine-readable failing verdict.
- The authorized product correction closed the first live predecessor defect without proofing accommodations, and its one fresh attempt proved that correction. Live closure still remains open at a second `07W.1` authority mismatch (`13` generated slide IDs versus `6` declared source-slide files), before Ask-A dispatch.

### File List

- app/marcus/lesson_plan/ask_a_enrichment.py
- app/marcus/lesson_plan/research_packet.py
- app/marcus/orchestrator/ask_a_research_wiring.py
- app/marcus/orchestrator/workbook_wiring.py
- app/marcus/orchestrator/production_runner.py
- tests/unit/marcus/lesson_plan/test_ask_a_enrichment_38_1.py
- tests/unit/marcus/lesson_plan/test_research_packet_w1.py
- tests/unit/marcus/orchestrator/test_ask_a_research_wiring_38_1.py
- tests/integration/marcus/test_workbook_band_wiring.py
- tests/integration/marcus/test_braid_s3_research_wiring.py
- tests/marcus/orchestrator/test_runner_planning_context_thread.py
- _bmad-output/implementation-artifacts/evidence/workbook-live-hil/9d2ab3f1-7e6c-4d9a-b835-12c7e8f46031/
- _bmad-output/implementation-artifacts/evidence/workbook-live-hil/c8f17a24-9b63-4e10-a5d7-6f2043bc9812/
- reports/dev-coherence/2026-07-13-1547/check-pipeline-manifest-lockstep.PASS.yaml
- tests/integration/marcus/test_braid_s3_research_wiring.py
