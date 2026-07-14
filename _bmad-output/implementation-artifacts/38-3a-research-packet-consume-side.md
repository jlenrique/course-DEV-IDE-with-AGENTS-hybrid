---
baseline_commit: d43eb53058403c9a2b3d1569044af138ba73ee13
---

# Story 38.3a: Research-packet consume side and 07W.1 demand handoff

Status: in-progress

## Story

As the Marcus-SPOC workbook runtime,
I want `07W.1` to persist the authored Deep Dive skeleton and expose one strict, digest-bound Ask-A research demand,
so that `07W.2` can research the workbook's actual abilities and marked concepts without scraping, guessing, falling back to generic research, or duplicating the Deep Dive contract.

## Dependency Position

`38.0 -> 38.3b -> {Epic 36, 37.1, 37.2a, 37.3, 37.4} -> 38.3a -> 38.1 -> 37.2b -> 39.1 -> 38.2 -> 39.2 -> 40.1`

Every predecessor is done. This story is the vertical handoff from the pure Story-37.2a skeleton contract to the authoritative demand that Story 38.1 will consume. It performs no research dispatch and does not own Review assembly/render.

## Party Amendment to the Ratified One-Line Scope

The original 38.3a shorthand said â€œlesson_plan consume side ... zero orchestrator diff.â€ Current code proves that a literal reading would be ceremonial: `WorkbookBriefPayloadV1.deep_dive_skeleton` remains `None`, and the existing `07W.1` factory never invokes `DeepDiveWriter`; therefore Story 38.1 has no authoritative term substrate.

On 2026-07-13, an independent stock-persona party of John (PM), Winston (architect), Amelia (developer), and Murat (test architect), with the orchestrating agent concurring, returned unanimous GO-WITH-AMENDMENTS on the vertical handoff. This decision supersedes exactly two earlier clauses: (a) 38.3a's literal â€œzero orchestrator diff,â€ and (b) 38.3b's assignment of future Deep-Dive live instantiation. All other ratified A5/topology/layering decisions remain binding.

For this story, **zero orchestrator diff** means no graph, manifest, runner-walk, node-order, event, gate, HUD, or `07W.2`â€“`07W.4` change. A surgical edit to the already-positioned `07W.1` factory/runtime-context seam is authorized solely to invoke the landed Story-37.2a writer, persist its typed result in the reserved brief slot, and reconcile that result on resume. No new story/node is introduced.

Four subsequent governed amendments are binding. First, a unanimous Winston/Murat reconciliation review authorized the terminal producer to call the canonical pure lesson-plan contribution-receipt builder; this is reconciliation-only and changes no terminal input or render behavior. Second, the two party-approved correct-course amendments in `sprint-change-proposal-2026-07-13.md` authorize Deep-Dive-only 32,000 completion tokens and the raw-JSON-schema adapter with `deep-dive-provider-normalizer.v1`. That normalizer may remove only later exact duplicates of independently strict-valid `{term: <string>}` metadata; it preserves the first occurrence/order, never trims, case-folds, Unicode-normalizes, or repairs any other value, and binds raw/normalized payloads, schema, records, and version into the journal/config identity. Third, the closure party (John, Winston, Amelia, and Murat; unanimous Option B) clarified the closed-authority boundary below: thin-but-valid authority persists typed output, while total required-authority absence is structurally unrepresentable by Story 37.2a and fails before any current brief write. Fourth, the live Story-38.1 validation run exposed that final manifest slide ordinals are not source-slide ordinals on a clustered deck. The unanimous 2026-07-13 correct-course party reopened this story and approved the explicit slide-authority-map amendment below. These amendments supersede only the conflicting clauses they name.

Amendment 7 is also binding. Governed trial `30850735-dea3-4444-bc7b-513239eae55b` returned one complete top-level JSON candidate plus exactly one surplus final `}`; the legacy parser discarded it and synthesized unanchored `unit-1`. The approved correction promotes new calls to `irene-pass1-response-processor.v2`, permits only the singular syntax-only final-brace correction after strict duplicate-key-rejecting decode, removes the current production synthetic fallback, and durably binds processing evidence before semantic gates. The failed trial remains immutable/nonpassing; only an external labeled offline counterfactual may use its bytes. See `sprint-change-proposal-2026-07-14.md` Amendment 7.

Amendment 8 is also binding. Governed trial `399bcd61-7779-4fa0-a592-186c3d4b4045` passed G2B, produced and published Storyboard A, completed high-confidence vision perception, and then safely error-paused at Irene Pass 2 because the shared figure-token neck classified the perceived OCR surface `$ 5% GDP` as `money-bare:5` while narration correctly emitted `percent:5`. An independent Winston/Amelia/Murat party returned GO-WITH-AMENDMENTS for the Marcus-SPOC product correction: the shared deterministic tokenizer recognizes dollar-prefixed percent and witnessed `+%` comparator surfaces as percentages before the ordinary money alternative, preserves raw perceived evidence, and leaves money/magnitude/range/tolerance and consumer policy unchanged. The frozen run remains immutable/nonpassing and is never resumed or retried. Signed and leading-decimal percentage behavior predates this amendment and is recorded as separate fidelity debt rather than broadened here.

### Correct-course Amendment 3: clustered final-to-source slide authority

This amendment supersedes AC2's direct `manifest slide_id -> slides/slide-<same ordinal>-*.md` join and its per-final-slide delta identity. Run `c8f17a24-9b63-4e10-a5d7-6f2043bc9812` produced 13 final slides from six authored source slides; the correct source ordinals are `[1,2,2,2,3,3,3,3,4,5,5,5,6]`. Existing suffix-derived helpers are forbidden here because live head IDs `u05`, `u09`, `u10`, and `u13` mean plan-unit identities, not source ordinals.

- Before any Deep Dive journal or provider action, mint `workbook-slide-authority-map.v1.json` exactly once with an exclusive, atomic, symlink-safe write. An existing map is never regenerated or overwritten; it is read and fully revalidated.
- The orchestrator supplies exactly one current Irene plan contribution, cross-checked against `irene-pass1.lesson-plan.json`, and exactly one node-06 `package_builder` slides contribution. A pure `lesson_plan` resolver joins final manifest slide -> package slide `source_ref` -> plan `unit_id` -> explicit source-slide file.
- Source identity is derived only from every nonblank plan-unit `source_refs` anchor occurring literally and case-sensitively in exactly one declared course slide file, with all anchors for the unit converging on the same file. CRLF/CR-to-LF comparison is the only permitted normalization if needed. No unit/final suffix, ordinal, position, head rank, title, cluster ID, fuzzy, case-fold, Unicode-normalization, whitespace-repair, or first/last-wins fallback is allowed.
- Every in-scope unit has nonempty anchors. Final IDs, unit IDs, package references, and map rows are unique and totally cover the ordered manifest roster. Every interstitial names an existing head parent and resolves to the same source file. Source paths remain under the declared `slides` root; missing, ambiguous, cross-file, stale, symlinked, escaping, or conflicting authority fails before provider spend.
- Each map row persists `final_slide_id`, `unit_id`, explicit `source_slide_id`, course-root-relative source path, original source-file SHA-256, exact matched anchors, and parent/cluster corroboration. The header binds schema/resolver version, ordered manifest identity/digest, selected plan sidecar and contribution digests, package-slides contribution/output digest, course-root-relative source inventory and hashes, and ordered rows. Canonical JSON is sorted, compact, UTF-8, `allow_nan=False`; machine-specific absolute paths are excluded.
- Revalidate the persisted map, its self-digest, every bound input, anchor match, source hash, and roster/order on initial, resume, upgrade, split-brain, and reconciliation paths. Divergence fails closed; persisted authority is never substituted with a newly reconstructed map.
- New 07W.1 requests require the map digest in their authority domain. Bind it into the request, authority digest, Deep Dive journal, idempotency key, execution receipt, and completed zero-call replay. An omitted-when-`None` field preserves legacy request/journal digest compatibility only; it is forbidden on new execution.
- Keep every VO span/claim in final manifest order. Group descendant VO by explicit source-slide identity, compare the full authored speaker note once against the ordered aggregate descendant narration, and admit at most one source-supported delta span/claim per unique source slide in first-descendant order. Delta IDs are source-keyed; the same full note is never duplicated for clustered descendants.
- Stable failures use the existing authority-invalid, persistence, reconciliation, ambiguous-call, and split-brain taxonomy. Carrier creation/read/mutation failures prove zero provider calls, zero brief write, and zero contribution minting.
- Scope remains surgical: no graph/node/order, provider family, Ask-A behavior, HUD, learning event, envelope schema, terminal render, or broad lineage harmonization change.

## Acceptance Criteria

1. **Reserved slot activation without a second Deep Dive contract**
   - Change `WorkbookBriefPayloadV1.deep_dive_skeleton` from pinned `None` to `DeepDiveSkeletonResult | None`; recursively revalidate the nested result and keep it inside the existing canonical workbook-brief payload digest.
   - This is a sanctioned activation of an already-serialized reserved field. Keep `workbook-brief.v1`: legacy artifacts containing exact `null` remain valid and retain their original canonical digest; no field is removed or renamed.
   - Add public `DeepDiveExecutionReceiptV1` without changing the required two-item Scene/Promise `writer_receipts` tuple. Its exact shape is: `schema_version: Literal["deep-dive-execution-receipt.v1"]`; `writer: Literal["deep_dive"]`; `mode: Literal["offline_stub", "live"]`; `calls: Literal[0, 1]`; `idempotency_key: sha256:<64-lower-hex>`; optional `prior_payload_digest`, `model`, `model_config_digest`, `request_id`, `latency_ms`, `input_tokens`, `output_tokens`, `cost_usd`, `cost_unavailable_reason`. Existing cost exclusivity/required-live-cost-posture rules apply. The receipt is exported.
   - Add `deep_dive_writer_receipt: DeepDiveExecutionReceiptV1 | None = None`. Legacy digest compatibility is exact: retain `deep_dive_skeleton:null` in the original digest domain; omit only `deep_dive_writer_receipt` when it is `None`; include it when present. A receipt is forbidden with a null skeleton and required with a non-null skeleton. A byte fixture from a real pre-38.3a null artifact must retain its original payload digest.
   - Do not duplicate Story-37.2a models, authority/candidate digests, gates, term extraction, or anti-forgery replay.

2. **Deterministic M3-safe request assembly**
   - Add one lesson-plan adapter that constructs `DeepDiveSkeletonRequest` from exactly `run_dir/exports/segment-manifest-storyboard-b.yaml::segments`, the explicit `course_source_root/slides/slide-*.md` authority, and the ordered authored Promise abilities already bound into the workbook brief.
   - VO spans are the nonblank manifest `narration_text` values in manifest order. Stable IDs are `vo:<segment_id>`; refs are `exports/segment-manifest-storyboard-b.yaml#segments/<segment_id>/narration_text`. Duplicate/blank IDs, absent/empty segments, wrong container, or missing narration are typed authority-invalid/unavailable per the pinned policy.
   - Source-supported delta authority is only SME-authored `Narration (Speaker Notes)` text from the course-root slide Markdown matched by manifest `slide_id` after canonical decimal-ordinal normalization (`slide-01` -> `slide-1`) to exactly one `slides/slide-<ordinal>-*.md`. Zero or multiple matches are typed authority-invalid/unavailable; no fuzzy filename match. Delta span IDs are `delta:<slide_id>`; claim IDs are `claim:delta:<slide_id>`; refs are `<course-root-relative-slide-path>#Narration (Speaker Notes)`.
   - Normalize only for the delta-presence decision: Unicode NFC, CRLF/CR to LF, collapse all whitespace runs to one ASCII space, and strip. Admit the full unmodified speaker-note textâ€”not a subtracted/reconstructed fragmentâ€”as both delta span text and delta claim text only when both normalized texts are nonblank and unequal and the note contains at least one case-folded alphanumeric token absent from the paired manifest narration. On-screen text, assessment answers, model inference, and unmatched files do not earn delta authority.
   - Ordering is exact: `source_spans` contains all VO spans in manifest order followed by admitted delta spans in the same manifest order; `source_claims` contains `claim:vo:<segment_id>` claims in manifest order followed by admitted delta claims in the same order. Every claim references exactly its corresponding span. Zero legitimate delta authority yields the Story-37.2a typed degraded path, never invented depth.
   - Abilities map exactly and in order from `WorkbookBriefPayloadV1.pre_work.promise.vows`: `DeepDiveAbilityInput.ability_id = PromiseVow.objective_id`, `text = PromiseVow.text`. The Promise must be authored; objective IDs/text/order must equal the persisted skeleton authority on reread.
   - Every narration/source span and claim has one stable ID and resolvable source ref. VO versus source-supported-delta role is decided only by the surfaces above, never by model inference.
   - The adapter performs no filesystem search, repository-wide guessing, research-packet read, glossary/trends read, model call, or orchestration import.

3. **Existing `07W.1` writer activation only**
   - Extend the explicit `WorkbookBriefRuntimeContext` injection seam with a `DeepDiveWriter`; invoke it at most once after eligible Scene/Promise/source authority is assembled, through `compose_deep_dive_skeleton`.
   - Offline mode uses Story-37.2a's deterministic unavailable stub. Live mode instantiates a bounded orchestrator-owned adapter using the existing workbook-writer model configuration and returns only the strict Story-37.2a writer candidate; the lesson-plan gate independently decides authored/degraded/unavailable.
   - `runtime_context_for_run()` must initialize the real Deep Dive writer in live mode. Missing live initialization fails loudly; live mode never silently falls back to the offline stub.
   - Before any live call, atomically persist `workbook-deep-dive-call.v1.json` with schema, deterministic idempotency key `sha256(canonical_json({trial_id: str(production_envelope.trial_id), node_id: "07W.1", authority_digest, model_config_digest}))`, `state="call_in_progress"`, the full validated `DeepDiveSkeletonRequest` authority snapshot, and no candidate/result. Canonical JSON uses sorted keys, compact separators, UTF-8, and `allow_nan=False`.
   - After the provider returns, recursively validate the full `DeepDiveWriterCandidate`, run `compose_deep_dive_skeleton`, then atomically replace the journal with `state="completed"`, the full validated authority snapshot, full candidate snapshot, full composed result, authority/candidate/result digests, idempotency key, and provider request/cost receipt. Before roll-forward, reload and recursively validate every snapshot, recompute every digest, require the current request authority/idempotency key to match, and replay the candidate through `compose_deep_dive_skeleton`; the replayed result must equal the journal result exactly. Only then may persistence resume without a provider call.
   - A resumed `call_in_progress` is an ambiguous-call hard pause and forbids recall; it is never retried automatically. A valid completed journal permits deterministic roll-forward without another provider call.
   - Stable `SpecialistDispatchError` tags are exact: authority corruption `workbook-brief.deep-dive-authority-invalid`; live init `workbook-brief.deep-dive-writer-init-failed`; provider exception `workbook-brief.deep-dive-writer-execution-failed`; wrong/constructed/invalid return `workbook-brief.deep-dive-writer-output-invalid`; journal/brief write `workbook-brief.deep-dive-persistence-failed`; digest/receipt mismatch `workbook-brief.deep-dive-reconciliation-failed`; unresolved in-progress journal `workbook-brief.deep-dive-call-ambiguous`; unlinked generation pair `workbook-brief.deep-dive-split-brain`. Translate these inside the `07W.1` seam so the outer factory wrapper cannot collapse them into `workbook.band.factory-failed`.
   - Contract-defined **thin-but-valid** authority means a recursively valid nonempty VO span/claim inventory, authored nonempty Promise abilities, exact slide matches, and zero eligible source-supported delta. It proceeds through unchanged Story 37.2a composition and persists the resulting typed degraded/unavailable output and receipt.
   - Total required request-authority absenceâ€”including absent course root/manifest/segments/narration/exact slide match or unavailable/empty Promiseâ€”cannot instantiate a truthful Story-37.2a request/result. It fails with `workbook-brief.deep-dive-authority-invalid` before writer call, journal creation, brief write, or contribution. No placeholder authority/result is invented. Current execution never mints `deep_dive_skeleton=null`; null is read-only pre-38.3a compatibility and may be replaced only by a successful targeted upgrade.

4. **Strict Ask-A demand contract and reader**
   - Add exported exception `ResearchDemandShapeError(ValueError)`, exported `AskAResearchDemandStatus = Literal["ready", "degraded", "unavailable"]`, and exported stable loss literal: `workbook_brief_absent`, `workbook_brief_legacy_stub`, `workbook_brief_legacy_null`, `deep_dive_skeleton_unavailable`, `deep_dive_skeleton_degraded`, `deep_dive_skeleton_terms_empty`.
   - Add exported frozen, strict, extra-forbid `AskAResearchDemandV1` with exact fields: `schema_version: Literal["ask-a-research-demand.v1"]`; `status`; `specialist_id: Literal["workbook_brief"]`; `node_id: Literal["07W.1"]`; optional `workbook_brief_payload_digest`; optional `skeleton_authority_digest` and `skeleton_candidate_digest`; `abilities: tuple[DeepDiveAbilityInput, ...]`; `bold_terms: tuple[BoldTermMarker, ...]`; `source_claim_refs: tuple[str, ...]`; `known_losses: tuple[ResearchDemandLoss, ...]`; `demand_digest: sha256`. Export `resolve_enrichment_demand(run_dir: Path) -> AskAResearchDemandV1`.
   - `demand_digest` is SHA-256 over canonical sorted compact UTF-8 JSON of every field except itself. `workbook_brief_payload_digest is None` iff the sole loss is `workbook_brief_absent`; it is non-null for every present valid brief, including legacy-null. Ready requires all digests present, nonempty abilities/terms/source refs, no losses, and exact replay/reconciliation. Degraded/unavailable require empty abilities/terms/source refs and exactly one stable loss; skeleton digests are present only when a valid non-ready skeleton supplied them.
   - A ready demand contains exact `workbook_brief@07W.1` coordinates, workbook-brief payload digest, skeleton authority and candidate digests, ordered ability IDs/text, ordered deduplicated bold terms, and stable source/claim refs required to audit scope.
   - Ready requires an authored, passing, replay-valid skeleton with at least one exact bold term; exact Promise ability IDs/text/order must equal the skeleton authority. Terms come only from canonical `bold_terms` metadata and are never reparsed, case-folded, heuristically recovered, or reordered. `None`, unavailable/degraded skeleton, failed gate, empty terms, unavailable Promise, corrupt brief, or digest/reference mismatch cannot produce a dispatchable demand.
   - Honest non-ready states carry stable typed status/losses. The reader never extracts keywords from prose, substitutes Scene terms, uses model priors, reads generic `04.55`, or falls back to another run/artifact.

   Exact non-ready/error disposition:

   | Condition | Status / exception | Sole loss |
   |---|---|---|
   | no `run.json` and no workbook brief | `unavailable` | `workbook_brief_absent` |
   | only legacy `workbook_brief_stub@07W.1` contribution | `unavailable` | `workbook_brief_legacy_stub` |
   | valid real brief with `deep_dive_skeleton=null` | `unavailable` | `workbook_brief_legacy_null` |
   | valid skeleton status `unavailable` | `unavailable` | `deep_dive_skeleton_unavailable` |
   | valid skeleton status `degraded` | `degraded` | `deep_dive_skeleton_degraded` |
   | authored/pass-valid skeleton with zero bold terms | `degraded` | `deep_dive_skeleton_terms_empty` |
   | corrupt JSON/schema/coordinates/digest; contribution mismatch; forged/failed gate replay; Promise ability mismatch; unknown/duplicate/reordered refs; invalid constructed model; or cross-run substitution | raise `ResearchDemandShapeError` | none |

5. **Contribution, sidecar, and resume reconciliation**
   - The `07W.1` contribution receipt witnesses the brief path/digest and Deep Dive status/digest summary without changing its `workbook_brief@07W.1` identity.
   - Existing contribution plus matching digest-valid sidecar and activated skeleton resumes with zero writer calls. Missing/corrupt/substituted sidecar, forged nested skeleton, contribution/sidecar mismatch, or mutated term/digest evidence fails loud before downstream execution.
   - Legacy contribution compatibility is exact: `workbook_brief_contribution_receipt()` emits the original old shape when `deep_dive_skeleton is None`; only activated artifacts add Deep Dive status/authority/candidate/execution summary. Validate the original old-shape receipt against the old null sidecar before entering the upgrade path.
   - A valid matching real `workbook_brief@07W.1` contribution/sidecar with `deep_dive_skeleton=null` has one explicit upgrade path at targeted `07W.1` re-entry: preserve the entire validated pre-work payload, call only the Deep Dive writer once, write a transition-linked replacement payload/receipt, and replace the same envelope coordinate coherently. Scene and Promise calls remain zero; a second resume makes all calls zero. A null brief read outside this upgrade path is typed non-dispatchable honesty, never Ask-A-ready.
   - Split-brain policy is exact. `new sidecar + old/null envelope` rolls forward without recall only when the new sidecar validates, its receipt `prior_payload_digest` equals the old envelope receipt digest, and a completed call journal matches its candidate/idempotency digest; then replace the contribution. `old/null sidecar + new envelope` always fails `workbook-brief.deep-dive-split-brain` because the envelope claims bytes absent from disk. `new sidecar + no contribution` rolls forward only from a matching completed journal; otherwise fails. Any unlinked pair fails loud. Never duplicate a live call or silently overwrite an unlinked generation.
   - Legacy stub coordinates, no brief, legacy real-null brief, degraded/unavailable skeleton, authored-zero-term skeleton, corrupt artifact, and receipt mismatch have distinct typed dispositions. Corruption is never downgraded to legacy/null honesty.

6. **Cross-layer identity and serialized-fixture witness**
   - A committed fixture uses a real serialized `ProductionTrialEnvelope`/`run.json` plus its workbook brief; direct model injection is not sufficient evidence.
   - Test-only cross-layer assertions pin `workbook_brief@07W.1`, `ask_a_enrichment@07W.2`, and `ask_b_hot_topics@07W.4` against `workbook_wiring.WORKBOOK_BAND_SPECIALIST_IDS` and the public research-packet constants.
   - Production `lesson_plan` modules import no orchestrator module. Exact-coordinate tests include wrong-specialist/right-node and right-specialist/wrong-node collisions and never use any-node/latest-specialist lookup.

7. **Packet-consumer contracts stay single-source**
   - Reuse Story-38.0's `resolve_for_enrichment_pool` and `resolve_for_hot_topics`; do not create another envelope loader, digest implementation, packet schema, or coordinate-selection path.
   - If intent-specific facades are needed for later consumers, they must delegate through the existing resolver path and preserve the current generic defaults. `glossary_inputs_from_run` and `trends_inputs_from_run` remain on generic `04.55` until Stories 39.1 and 39.2.
   - Stub Ask-A/Ask-B packets remain honestly empty. Coordinates remain outside `ResearchPacket.packet_digest`; identical packet payloads may legitimately hash equally.

8. **Ownership and scope fences**
   - No Tracy/Texas call, Ask-A minting, Ask-B behavior, cited enrichment, References, glossary/trends repoint, `07W.3` activation, Review sidecar, terminal render, Markdown/DOCX, graph/runner/manifest/lockstep change, learning event, HUD/operator-surface change, or proofing accommodation.
   - Story 38.1 consumes the ready demand and mints Ask A. Story 37.2b consumes Ask A for cited depth. Story 37.5 assembles/renders Review. Story 39.1/39.2 repoint glossary/trends.

9. **Gate taxonomy**

   | Condition | Disposition | Witness |
   |---|---|---|
   | Invalid source/ability authority or invalid writer candidate | FAIL-to-author | automated adapter/gate mutations |
   | Thin-but-valid authority or honest offline stub over a valid request | persist non-dispatchable unavailable/degraded | automated status/loss tests |
   | Required request authority absent/empty | fail-loud `workbook-brief.deep-dive-authority-invalid`; no writer/journal/new brief/contribution | source/Promise absence mutations |
   | Forged skeleton, digest/term/ref mutation, sidecar substitution | fail-loud | replay + contribution/sidecar tests |
   | Empty term set or non-authored skeleton | zero Ask-A readiness | automated demand tests |
   | Cross-layer coordinate drift or wrong-coordinate collision | FAIL | serialized fixture + string-contract tests |
   | Full prose depth/faithfulness beyond automated proxies | WARN | later live operator spot-check |

10. **Verification and close bar**
    - RED/GREEN tests cover request assembly, exactly-once writer invocation, offline/live injected behavior, nested strict round-trip, old-file readability, targeted null upgrade with zero Scene/Promise recalls, digest stability, causal mutations, contribution/sidecar resume, both split-brain directions, exact-coordinate collisions, M3/import fences, and a ready demand that Story 38.1 can consume without fallback.
    - Mutation tests independently alter payload, payload digest, skeleton authority/candidate snapshots and digests, gate receipt, Promise ability identity/order, bold terms, contribution receipt, coordinate identity, and cross-run sidecar. Constructed-model, wrong-return, extra-field, and coercion bypasses fail closed. Unicode and term order survive disk round-trip exactly.
    - Run focused 38.3a tests plus complete 36.4, 37.2a, 38.0, workbook-band, terminal-brief, composition/topology, and glossary/trends compatibility regressions; Ruff and `git diff --check` pass.
    - No paid run is required to create the story. Before `done`, complete one bounded live `07W.1` Deep Dive call on the frozen Part-2 substrate. The witness must record the model/config digest, request ID when supplied, latency/token/cost posture, passing Story-37.2a gate, nonempty terms, and ready demand. First-run-stands; no retry-to-green. This does not replace the final full Marcus-SPOC workflow gate.
    - Fresh dev, Blind/Edge/Acceptance review, remediation, Cora lockstep classification, and exact-current closure are mandatory.

## Tasks / Subtasks

- [x] Activate the reserved skeleton field with legacy-null and canonical-digest compatibility (AC: 1, 5)
- [x] Build the explicit narration/source/Promise-to-skeleton request adapter (AC: 2)
- [x] Extend the existing `07W.1` injection/factory and bounded live writer adapter without graph/runner changes (AC: 3, 5)
- [x] Add the durable live-call journal, exact error-tag translation, and pinned split-brain roll-forward/fail policy (AC: 3, 5)
- [x] Add the strict Ask-A demand projection/reader (AC: 4)
- [x] Add serialized fixtures, cross-layer identity pins, mutation/resume/M3 tests (AC: 5-7, 9-10)
- [x] Run focused/dependency/static verification and bounded live evidence (AC: 10)
- [x] Complete mandatory three-layer review, remediation, and closure audit (AC: 10)
- [x] Reproduce the serialized live `u01`-`u13` 13-final/6-source RED and pin the expected source map `[1,2,2,2,3,3,3,3,4,5,5,5,6]` (Amendment 3)
- [x] Add the pure exact-anchor authority-map resolver and immutable digest-bound sidecar persistence/revalidation (Amendment 3)
- [x] Replace direct-final-ordinal source lookup with total final->unit->source authority and grouped once-per-source delta assembly (Amendment 3)
- [x] Add corruption, ambiguity, stale-input, parent-conflict, no-fallback, legacy-digest, and zero-call replay mutation coverage (Amendment 3)
- [x] Build a pure digest-bound exact-source-span catalog from authenticated Pass-1 source sections, with stable IDs, exact text/offset/source identity, uniqueness, and mutation rejection (Amendment 6)
- [x] Change Irene's model-visible authority contract to ordered `source_ref_ids` and deterministically project them to literal `source_refs` before the existing independent exact-authority validator; forbid free-text/fuzzy/repair fallback (Amendment 6)
- [x] Version Pass-1 temporal authority so selected IDs, projected bytes, source identity, and catalog digest are bound, with explicit read-only legacy-v1 handling and no silent equivalence upgrade (Amendment 6)
- [x] Add a generation-lock-protected Irene call journal that persists pre-dispatch request/model/catalog identity and post-return raw response/provider evidence before parsing or validation; unresolved calls remain ambiguous and forbid automatic recall (Amendment 6)
- [x] Include every Irene provider attempt in local economics with known usage/cost or explicit unavailable posture, including post-provider validation failures (Amendment 6)
- [x] Add reconstructable per-file governed-preflight identity evidence with narrow declared writable exclusions and separate output inventory (Amendment 6)
- [x] Prove the witnessed near-paraphrase RED plus unknown/duplicate/reordered/stale/cross-source IDs, temporal substitution, crash/ambiguity, concurrency, failed-validation cost, and input-vs-output identity cases (Amendment 6)
- [ ] Run focused/dependency/static verification, mandatory BMAD code review, and one fresh governed live 38.1/workbook attempt only after deterministic GREEN (Amendment 3)
- [x] Implement Amendment 7 processor v2: strict-first exact one-surplus-final-`}` normalization, no general repair, and fail-loud removal of the current synthetic production fallback
- [x] Persist and validate the digest-bound v2 processing receipt before downstream semantic gates/publication; prove crash-safe idempotent zero-recall replay and receipt tamper rejection
- [x] Preserve allowlisted v1 journal audit/economics behavior without runtime upgrade, and bank a labeled offline counterfactual while all frozen-trial bytes/hashes remain unchanged
- [x] Complete Amendment 7 adversarial dependency/static review and fresh Blind/Edge/Acceptance ZERO FINDINGS before requesting any new live authorization
- [x] Correct the live-exposed dollar-prefixed percentage classification in the shared deterministic figure neck, replay the frozen evidence locally, and preserve money/percent type separation at both Irene and Quinn gates (Amendment 8)
- [x] Complete Amendment 8 party review, focused/dependency/static verification, and mandatory Blind/Edge/Acceptance review without retrying the frozen run

### Review Findings

#### Amendment 8 live-finding review

- [x] [Review][Patch] Record the shared product-level figure-token correction as a governed Story 38.3a amendment rather than silently folding it into the earlier G2B economics correction [\_bmad-output/implementation-artifacts/38-3a-research-packet-consume-side.md:29]
- [x] [Review][Defer] Preserve sign semantics for signed percentages before fidelity comparison [app/specialists/\_shared/figure_tokens.py:18] — deferred, pre-existing
- [x] [Review][Defer] Preserve leading-decimal percentage magnitude instead of suffix-matching `.5%` as `5%` [app/specialists/\_shared/figure_tokens.py:18] — deferred, pre-existing

- [x] [Review][Patch] Preserve the complete baseline legacy-null digest domain, including serialized empty `scene_receipt.introduced_terms` [app/marcus/lesson_plan/prework_artifact.py:240]
- [x] [Review][Patch] Reconcile the Deep Dive receipt mode and call posture with aggregate workbook execution mode [app/marcus/lesson_plan/prework_artifact.py:207]
- [x] [Review][Patch] Require completed journal state and fully reconcile provider receipt provenance [app/marcus/orchestrator/workbook_wiring.py:245]
- [x] [Review][Patch] Compare the authoritative replayed journal receipt with the persisted sidecar receipt on every roll-forward path [app/marcus/orchestrator/workbook_wiring.py:813]
- [x] [Review][Patch] Bind ready Ask-A demand authority to the current trial and completed execution evidence [app/marcus/lesson_plan/research_demand.py:137]
- [x] [Review][Patch] Fail loud on wrong-specialist/right-node and right-specialist/wrong-node contribution collisions [app/marcus/lesson_plan/research_demand.py:153]
- [x] [Review][Patch] Reject a real sidecar planted beside an otherwise honest legacy stub [app/marcus/lesson_plan/research_demand.py:155]
- [x] [Review][Patch] Enforce the exact status/loss/skeleton-digest table in constructed non-ready demand models [app/marcus/lesson_plan/research_demand.py:92]
- [x] [Review][Patch] Persist typed non-authored Deep Dive output for contract-defined missing or thin authority [app/marcus/orchestrator/workbook_wiring.py:558]
- [x] [Review][Patch] Restore targeted null-sidecar upgrade after production re-entry drops the old contribution [app/marcus/orchestrator/workbook_wiring.py:852]
- [x] [Review][Patch] Translate workbook-brief persistence failures to the required stable Deep Dive tag [app/marcus/orchestrator/workbook_wiring.py:565]
- [x] [Review][Patch] Preserve the preexisting Scene/Promise writer-init error tag while separately tagging Deep Dive initialization [app/marcus/orchestrator/workbook_wiring.py:650]
- [x] [Review][Patch] Reject segment-manifest and slide authority symlinks or resolved paths outside their declared roots [app/marcus/lesson_plan/deep_dive_from_run.py:70]
- [x] [Review][Patch] Parse only the exact full speaker-note field and treat absent notes as zero delta rather than aborting request assembly [app/marcus/lesson_plan/deep_dive_from_run.py:22]

#### Exact-current re-review findings

- [x] [Review][Patch] Reject symlinked or run-root-escaping completed Deep Dive journals before reconciliation [app/marcus/orchestrator/workbook_wiring.py:236]
- [x] [Review][Patch] Validate the decoded journal root as a mapping under the stable reconciliation tag [app/marcus/orchestrator/workbook_wiring.py:239]
- [x] [Review][Patch] Preserve colon-bearing continuation lines in the full unmodified speaker-note authority [app/marcus/lesson_plan/deep_dive_from_run.py:91]
- [x] [Review][Patch] Reject a legacy-null sidecar with no matching contribution instead of self-authorizing an upgrade [app/marcus/orchestrator/workbook_wiring.py:933]
- [x] [Review][Patch] Do not delete a pre-existing journal temporary file when exclusive creation fails [app/marcus/orchestrator/workbook_wiring.py:122]
- [x] [Review][Patch] Treat a broken workbook-brief symlink as corruption rather than honest absence [app/marcus/lesson_plan/research_demand.py:287]
- [x] [Review][Patch] Reject duplicate exact `workbook_brief@07W.1` contributions in serialized envelopes [app/marcus/lesson_plan/research_demand.py:295]
- [x] [Review][Patch] Reject simultaneous real and legacy `07W.1` contributions at the terminal reconciliation seam [app/specialists/workbook_producer/_act.py:768]
- [x] [Review][Patch] Reject duplicate YAML mapping keys before segment authority can be overwritten [app/marcus/lesson_plan/deep_dive_from_run.py:155]
- [x] [Review][Patch] Reconcile the sprint-ledger header with the final governed passing live attempt [\_bmad-output/implementation-artifacts/sprint-status.yaml:2]

#### Exact-current closure round 2 findings

- [x] [Review][Patch] Reject symlinked runtime-context authority before presence detection or live-writer initialization [app/marcus/lesson_plan/prework_artifact.py:389]
- [x] [Review][Patch] Preserve explicit zero token and cost metadata instead of treating zero as absence [app/marcus/orchestrator/workbook_prework_writers.py:139]
- [x] [Review][Patch] Give metadata-minimal injected live writers an honest cost posture and preserve the Deep-Dive output-invalid tag on receipt failure [app/marcus/orchestrator/workbook_wiring.py:166]
- [x] [Review][Patch] Require the canonical Deep-Dive candidate schema identity at the orchestration seam [app/marcus/orchestrator/workbook_wiring.py:194]
- [x] [Review][Patch] Refuse tuple/coercion input before the exact-duplicate provider normalizer canonicalizes it [app/marcus/lesson_plan/deep_dive_provider_contract.py:43]
- [x] [Review][Patch] Reject blank or multiline source-claim references in constructed ready demands [app/marcus/lesson_plan/research_demand.py:89]
- [x] [Review][Patch] Replace, rather than retain, a lone legacy-stub coordinate when 07W.1 successfully authors the real contribution [app/marcus/orchestrator/workbook_wiring.py:1111]
- [x] [Review][Patch] Translate absent course-source authority on split-brain roll-forward to the required reconciliation tag [app/marcus/orchestrator/workbook_wiring.py:982]
- [x] [Review][Patch] Make evidence-attempt directory allocation atomic across concurrent creators [scripts/utilities/run_deep_dive_38_3a_live_evidence.py:92]
- [x] [Review][Patch] Preserve a failure verdict even when the residual journal is malformed or unreadable [scripts/utilities/run_deep_dive_38_3a_live_evidence.py:222]

#### Exact-current closure round 3 findings

- [x] [Review][Patch] Reject dangling and non-regular runtime-context coordinates before legacy-default fallback [app/marcus/orchestrator/workbook_wiring.py:735]
- [x] [Review][Patch] Recompute the canonical provider-schema digest during completed-journal replay [app/marcus/orchestrator/workbook_wiring.py:327]
- [x] [Review][Patch] Refuse tuple/coercion input in the live provider path before raw-payload canonicalization [app/marcus/orchestrator/workbook_prework_writers.py:307]
- [x] [Review][Patch] Reject surrounding whitespace in constructed ready-demand source-claim references [app/marcus/lesson_plan/research_demand.py:109]
- [x] [Review][Patch] Translate unbounded numeric slide ordinals into the stable Deep-Dive authority-invalid family [app/marcus/lesson_plan/deep_dive_from_run.py:91]
- [x] [Review][Patch] Remove a legacy-stub coordinate during journal-backed sidecar roll-forward replacement [app/marcus/orchestrator/workbook_wiring.py:813]

#### Exact-current closure round 4 findings

- [x] [Review][Patch] Reject exact empty-string source-claim references in constructed ready demands [app/marcus/lesson_plan/research_demand.py:109]
- [x] [Review][Patch] Stop unbolded on-screen/assessment slide fields from entering speaker-note delta authority [app/marcus/lesson_plan/deep_dive_from_run.py:25]
- [x] [Review][Patch] Persist raw provider/digest/schema/normalizer evidence when normalization fails after mapping parse [app/marcus/orchestrator/workbook_prework_writers.py:307]

#### Exact-current closure round 5 findings

- [x] [Review][Patch] Replace the partial unbolded-field allowlist with a closed slide-field label grammar [app/marcus/lesson_plan/deep_dive_from_run.py:31]
- [x] [Review][Patch] Persist an ordered normalization-record list even when normalization fails before a normalized digest exists [app/marcus/orchestrator/workbook_wiring.py:230]
- [x] [Review][Patch] Reject a successful candidate that coexists with stale provider-normalization error state [app/marcus/orchestrator/workbook_wiring.py:230]

#### Exact-current closure round 6 findings

- [x] [Review][Patch] Use exact governed slide-field labels so colon-bearing narration prose is never truncated [app/marcus/lesson_plan/deep_dive_from_run.py:31]
- [x] [Review][Patch] Recognize a literal Unicode bullet before bold slide-field boundaries [app/marcus/lesson_plan/deep_dive_from_run.py:30]
- [x] [Review][Patch] Prove composed/decomposed Unicode terms remain distinct through normalization and workbook-brief disk round-trip [tests/integration/marcus/test_workbook_prework_writers_36_4.py:155]

#### Exact-current closure round 7 findings

- [x] [Review][Patch] Complete independent replay mutations for normalization records, normalized digest, candidate snapshot, and candidate digest [tests/integration/marcus/test_workbook_deep_dive_38_3a.py:600]
- [x] [Review][Patch] Accept a literal Unicode bullet on the exact Narration (Speaker Notes) header [app/marcus/lesson_plan/deep_dive_from_run.py:25]
- [x] [Review][Patch] Apply governed-label matching to bold colon-bearing fields so bold narration prose is preserved [app/marcus/lesson_plan/deep_dive_from_run.py:31]

#### Exact-current closure round 8 findings

- [x] [Review][Patch] Update stale exact-current verification evidence to the post-remediation result [\_bmad-output/implementation-artifacts/38-3a-research-packet-consume-side.md:275]
- [x] [Review][Patch] Exclude exact bold and unbolded `Answer` assessment fields from narration authority [app/marcus/lesson_plan/deep_dive_from_run.py:36]

#### Exact-current closure round 9 findings

- [x] [Review][Patch] Reconcile the sprint-ledger comment with resolved review status [\_bmad-output/implementation-artifacts/sprint-status.yaml:1805]
- [x] [Review][Patch] Translate typed Promise authority corruption to the stable Deep-Dive authority-invalid tag [app/marcus/orchestrator/workbook_wiring.py:602]

#### Exact-current closure round 10 findings

- [x] [Review][Patch] Translate corrupt persisted run-envelope lineage to the stable Deep-Dive authority-invalid tag and prove the causal malformed-file path [app/marcus/orchestrator/workbook_wiring.py:605]

#### Exact-current closure round 11 result

- [x] [Review][Blind Hunter] ZERO FINDINGS on the exact-current worktree.
- [x] [Review][Edge Case Hunter] ZERO FINDINGS on the exact-current worktree.
- [x] [Review][Acceptance Auditor] ZERO FINDINGS on the exact-current worktree.

#### Amendment 3 review findings

- [x] [Review][Patch] [HIGH] Require the slide-authority map on every current new 07W.1 execution and permit mapless compatibility only from positive persisted legacy evidence [app/marcus/orchestrator/workbook_wiring.py:174]
- [x] [Review][Patch] [HIGH] Resolve, persist, and revalidate the slide-authority carrier before any Scene, Promise, or Deep-Dive writer call [app/marcus/orchestrator/workbook_wiring.py:628]
- [x] [Review][Patch] [HIGH] Require the workbook receipt map digest to equal the skeleton request authority map digest [app/marcus/lesson_plan/prework_artifact.py:218]
- [x] [Review][Patch] [HIGH] Parse speaker notes from the exact source bytes whose hash was verified instead of reopening the path [app/marcus/lesson_plan/deep_dive_from_run.py:272]
- [x] [Review][Patch] [MEDIUM] Fully self-validate source-inventory digest/identity and row-to-inventory correspondence, with canonical paths strictly below slides/ [app/marcus/lesson_plan/slide_authority.py:97]
- [x] [Review][Patch] [MEDIUM] Reject authority identifier coercion and canonically duplicate final slide ordinals before carrier persistence [app/marcus/lesson_plan/slide_authority.py:369]
- [x] [Review][Patch] [MEDIUM] Preserve the stable persistence-failed taxonomy for carrier write, fsync, link, and temporary-cleanup failures [app/marcus/lesson_plan/slide_authority.py:209]
- [x] [Review][Patch] [MEDIUM] Reject target/temporary hard-link coexistence before accepting an existing carrier [app/marcus/lesson_plan/slide_authority.py:219]
- [x] [Review][Patch] [MEDIUM] Bank the live 13-to-6 structural witness and complete bound-input, carrier-mutation, path, legacy-digest, and zero-call failure coverage [tests/unit/marcus/lesson_plan/test_slide_authority_38_3a.py:1]

Remediation verification (2026-07-13): focused Story 38.3a plus inherited 36.4/37.2a and workbook-band regression battery passed `172 passed, 3 skipped`; scoped Ruff, compileall, and `git diff --check` passed. No live provider call was made.

#### Amendment 3 exact-current re-review findings

- [x] [Review][Patch] [HIGH] Forbid a legacy-null brief upgrade from making a new mapless Deep-Dive request; mapless compatibility belongs only to replay of a positively persisted pre-map request/journal [app/marcus/orchestrator/workbook_wiring.py:985]
- [x] [Review][Patch] [HIGH] Require an existing mapped carrier on resume/reconciliation/split-brain paths instead of silently reconstructing a deleted carrier [app/marcus/orchestrator/workbook_wiring.py:1089]
- [x] [Review][Patch] [HIGH] Eliminate the unchecked post-persistence carrier reread that can substitute a different internally valid map after reconciliation [app/marcus/orchestrator/workbook_wiring.py:238]
- [x] [Review][Patch] [HIGH] Bind map construction and request VO authority to one immutable manifest-byte snapshot rather than three independent filesystem reads [app/marcus/orchestrator/workbook_wiring.py:224]
- [x] [Review][Patch] [MEDIUM] Close path-swap/symlink races by validating and reading authority bytes through the same opened regular-file handle [app/marcus/lesson_plan/slide_authority.py:334]
- [x] [Review][Patch] [MEDIUM] Enforce unique row unit IDs plus parent existence, head role, source identity, and cluster agreement when validating a persisted map [app/marcus/lesson_plan/slide_authority.py:123]
- [x] [Review][Patch] [MEDIUM] Replace the tautological live-row summary with sanitized serialized live manifest/plan/package/source inputs that execute through the resolver [tests/fixtures/marcus/lesson_plan/slide_authority_live_witness_c8f17a24.json:1]

#### Amendment 3 exact-current closure round 2 findings

- [x] [Review][Patch] [HIGH] Revalidate every bound authority input after Scene/Promise authoring and before Deep-Dive provider dispatch [app/marcus/orchestrator/workbook_wiring.py:812]
- [x] [Review][Patch] [MEDIUM] Reject missing, malformed, or unknown plan-unit scope decisions instead of defaulting them in-scope [app/marcus/lesson_plan/slide_authority.py:460]
- [x] [Review][Patch] [HIGH] Preserve positively proven pre-map replay even when the legacy envelope retains Irene/package contributions [app/marcus/orchestrator/workbook_wiring.py:169]
- [x] [Review][Patch] [MEDIUM] Validate an existing mapped carrier without invoking any create-capable persistence path [app/marcus/orchestrator/workbook_wiring.py:239]
- [x] [Review][Patch] [HIGH] Hold a cross-process dispatch lock from final authority validation through Deep-Dive journal completion [app/marcus/orchestrator/workbook_wiring.py:146]
- [x] [Review][Patch] [MEDIUM] Fail pre-map replay when a carrier or carrier-temporary coordinate conflicts with the persisted pre-map evidence [app/marcus/orchestrator/workbook_wiring.py:174]
- [x] [Review][Patch] [MEDIUM] Bind the executable sanitized witness to hard-coded fixture and captured-live provenance digests [tests/unit/marcus/lesson_plan/test_slide_authority_38_3a.py:96]

Closure-round-2 verification (2026-07-13): focused Story 38.3a plus inherited 36.4/37.2a and workbook-band regression battery passed `182 passed, 3 skipped`; compileall and `git diff --check` passed. Scoped Ruff passed after the final lock-cleanup style correction. No live provider call was made.

#### Amendment 3 exact-current closure round 3 findings

- [x] [Review][Patch] [HIGH] Replace the crash-persistent dispatch sentinel with an OS advisory lock that releases automatically on process death [app/marcus/orchestrator/workbook_wiring.py:155]
- [x] [Review][Patch] [MEDIUM] Attempt dispatch-lock unlock and descriptor close independently, then translate either cleanup failure to the stable persistence taxonomy [app/marcus/orchestrator/workbook_wiring.py:190]

Closure-round-3 verification (2026-07-13): focused Story 38.3a plus inherited 36.4/37.2a and workbook-band regression battery passed `183 passed, 3 skipped`; scoped Ruff, compileall, and `git diff --check` passed. No live provider call was made.

#### Amendment 3 exact-current closure round 4 finding

- [x] [Review][Patch] [MEDIUM] Reject non-regular or multiply linked advisory-lock coordinates before writing the lock byte [app/marcus/orchestrator/workbook_wiring.py:167]

Closure-round-4 verification (2026-07-13): focused Story 38.3a plus inherited 36.4/37.2a and workbook-band regression battery passed `184 passed, 3 skipped`; scoped Ruff, compileall, and `git diff --check` passed. No live provider call was made.

#### Amendment 3 exact-current closure round 4 result

- [x] [Review][Blind Hunter] ZERO FINDINGS on the exact-current worktree.
- [x] [Review][Edge Case Hunter] ZERO FINDINGS on the exact-current worktree.
- [x] [Review][Acceptance Auditor] ZERO FINDINGS apart from the intentionally gated live task.

#### Amendment 4 - full-scale Deep-Dive timeout

- [x] Bind Deep Dive alone to a validated 300-second request timeout while Scene and Promise remain at 120 seconds and every workbook writer retains zero nonselectable retries.
- [x] Bind the normalized timeout and zero-retry posture into the Deep-Dive effective configuration digest, journal identity, and idempotency domain.
- [x] Prove completed replay rejects timeout drift and a timeout remains one-call/fail-loud with no brief or Ask-A side effects; preserve the prior `e08c3fef-eed3-42fa-94d5-f7e58989389e` evidence hashes.
- [x] Exact-current Blind, Edge, and Acceptance reviews returned ZERO FINDINGS after remediation.

Amendment-4 verification (2026-07-13): focused/dependency regression passed `197 passed, 3 skipped`; scoped Ruff, compileall, and `git diff --check` passed.

#### Amendment 5 - upstream Pass-1 authority correction

- [x] Reject blank/duplicate and temporally recycled plan-unit identities before Pass-1 sidecar/contribution/package persistence.
- [x] Require exact ordered literal source-anchor authority at Pass-1 using the same no-fuzzy semantics as the downstream resolver.
- [x] Prove package source-reference totality/uniqueness, resume parity, purity/no-repair, zero downstream spend/effects, and frozen-run preservation.
- [x] Complete deterministic/static/adversarial review. No fresh live attempt is authorized by Amendment 5.

#### Amendment 5 exact-current code-review findings

- [x] [Review][Patch] [HIGH] Reject missing or unknown scope decisions before exact-anchor authority and package projection can disagree [app/marcus/lesson_plan/pass1_authority.py:83]
- [x] [Review][Patch] [HIGH] Keep every retired unit ID permanently inactive, including attempts to restore the identical authority tuple [app/marcus/lesson_plan/pass1_authority.py:237]
- [x] [Review][Patch] [HIGH] Require a supplied cumulative receipt to bind the actual prior lesson plan before it governs a refinement [app/specialists/irene_pass1/_act.py:152]
- [x] [Review][Patch] [HIGH] Reject a present malformed prior receipt instead of silently rebuilding lineage from only the immediately prior plan [app/specialists/irene_pass1/_act.py:1167]
- [x] [Review][Patch] [HIGH] Reject current-format package resumes that omit their authority receipt instead of downgrading them to the legacy path [app/marcus/orchestrator/package_builders.py:272]
- [x] [Review][Patch] [HIGH] Fail when source provenance metadata is absent rather than collapsing all slide files into synthetic aggregate authority [app/specialists/source_bundle.py:81]
- [x] [Review][Patch] [MEDIUM] Derive prompt text and exact per-slide authority sections from one immutable read of the extracted corpus [app/specialists/irene_pass1/_act.py:1053]

Amendment-5 remediation verification (2026-07-13): all Irene Pass-1 tests passed `181 passed`; package-builder integration passed `23 passed`; the focused inherited workbook/authority regression battery passed `168 passed, 3 skipped`; scoped Ruff, compileall, all 18 import-linter contracts, and `git diff --check` passed. No live provider call was made.

#### Amendment 5 exact-current closure-round-2 findings

- [x] [Review][Patch] [HIGH] Delimit slide authority at every emitted source boundary so adjacent non-slide content cannot be attributed to a slide [app/specialists/source_bundle.py:107]
- [x] [Review][Patch] [HIGH] Bind every active receipt row's role, parent, and ordered anchors to the exact plan unit, not only its digest and ID [app/marcus/lesson_plan/pass1_authority.py:266]
- [x] [Review][Patch] [HIGH] Revalidate existing package contributions and their authority inputs before idempotent resume [app/marcus/orchestrator/package_builders.py:256]
- [x] [Review][Patch] [HIGH] Require cumulative authority receipts on every newly dispatched refinement so retirement history cannot reset [app/specialists/irene_pass1/_act.py:1053]
- [x] [Review][Patch] [HIGH] Enforce interstitial parent-source and cluster agreement during Pass-1 finalization before downstream spend [app/marcus/lesson_plan/pass1_authority.py:223]
- [x] [Review][Patch] [HIGH] Join the Pass-1 receipt's source identity to the final slide-authority resolver's source path [app/marcus/lesson_plan/slide_authority.py:621]
- [x] [Review][Patch] [HIGH] Persist and consume Texas's explicit emitted section title rather than reconstructing boundaries from filenames [skills/bmad-agent-texas/scripts/run_wrangler.py:1345]
- [x] [Review][Patch] [MEDIUM] Fail source-bundle refinement errors before invoking Irene's LLM when exact authority cannot possibly validate [app/specialists/irene_pass1/_act.py:1075]
- [x] [Review][Patch] [MEDIUM] Reject malformed serialized matched-anchor collections under the stable slide-authority taxonomy [app/marcus/lesson_plan/slide_authority.py:317]
- [x] [Review][Patch] [MEDIUM] Replace the predictable receipt temporary coordinate with an exclusively created regular file and reject symlinked sidecars [app/specialists/irene_pass1/_act.py:920]

Amendment-5 closure-round-2 verification (2026-07-13): Irene Pass-1 passed `185 passed, 1 skipped` (the skip is Windows symlink capability); package and exact-authority focus passed `79 passed, 1 skipped`; the inherited workbook/authority battery passed `172 passed, 3 skipped`; Texas's complete local runner suite passed `21 passed`; scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` passed. No live provider call was made.

#### Amendment 5 exact-current closure-round-3 findings

- [x] [Review][Patch] [HIGH] Run the post-shaping authority gate before planning-context coverage can persist a diagnostic sidecar or substitute a different failure taxonomy [app/specialists/irene_pass1/_act.py]
- [x] [Review][Patch] [HIGH] Reject anchors that become duplicates after the contract's CRLF/CR-to-LF normalization [app/marcus/lesson_plan/slide_authority.py]
- [x] [Review][Patch] [HIGH] Bind Pass-1 source identities to the Texas content digest and require the final source inventory to match it, so same-path source drift fails closed [app/specialists/source_bundle.py; app/marcus/lesson_plan/slide_authority.py]
- [x] [Review][Patch] [HIGH] Parse metadata with duplicate-key rejection and read both metadata and corpus through contained, stable, regular-file snapshots [app/specialists/source_bundle.py]
- [x] [Review][Patch] [MEDIUM] Treat only primary provenance rows as extracted-corpus boundaries so supporting headings cannot truncate a slide's authority body [app/specialists/source_bundle.py]
- [x] [Review][Patch] [MEDIUM] Upgrade the inherited serialized terminal-workbook fixture to current 05B/06 authority without discarding its authored workbook collateral [tests/helpers/workbook_slide_authority.py; tests/specialists/workbook_producer/test_workbook_producer_brick.py]

Amendment-5 closure-round-3 remediation verification (2026-07-13): Irene Pass-1 passed `188 passed, 1 skipped`; package and exact-authority focus passed `55 passed`; the broad inherited workbook battery passed `550 passed, 5 skipped`; Texas's complete local runner suite passed `99 passed, 1 skipped`; the new edge-case focus passed `73 passed, 1 skipped`. Scoped Ruff, compileall, all 18 import-linter contracts, repository-wide `git diff --check`, and frozen-run hashes/file count passed. The frozen run remains 67 files with `error-pause.json` SHA-256 `4d9bc6f4c1c4ef5f662f6607326402dc741f1e845dd5ec1034f49283cc4fa6bc` and `run.json` SHA-256 `3935b017d343bfd5c8bcdd1b7998d07ef82238ab74fa5031b6a1df60b90bc50f`. No live provider call was made.

#### Amendment 5 exact-current closure-round-4 findings

- [x] [Review][Patch] [HIGH] Treat an Irene `05B` contribution as positive current-format evidence so deleting every receipt marker cannot downgrade corrupted current work to legacy packaging [app/marcus/orchestrator/package_builders.py]
- [x] [Review][Patch] [HIGH] Emit a separate Texas source-authority record and verify each normalized extracted primary-slide section against it before Pass-1 anchor matching; use the same canonical content digest at final source resolution [skills/bmad-agent-texas/scripts/run_wrangler.py; app/specialists/source_bundle.py; app/marcus/lesson_plan/slide_authority.py]
- [x] [Review][Patch] [HIGH] Accept unused nonlocal/supporting source rows without requiring local paths or primary-only titles, while rejecting duplicate primary refs and conflicting bundle coordinates [app/specialists/source_bundle.py]
- [x] [Review][Patch] [HIGH] Read package authority sidecars through a contained stable-file handle and reject duplicate JSON keys before resume/build acceptance [app/marcus/orchestrator/package_builders.py]
- [x] [Review][Patch] [HIGH] Roll back all current Pass-1 plan/receipt coordinates if artifact publication fails after validation [app/specialists/irene_pass1/_act.py]
- [x] [Review][Patch] [HIGH] Add a copied-frozen-run regression that replays the actual malformed 05B plan through the Pass-1 seam, bombs downstream seams, proves the stable upstream tag and zero new plan/package/map/Deep-Dive/brief/Ask-A artifacts, and rechecks all 67 frozen files plus protected hashes [tests/specialists/irene_pass1/test_pass1_authority_amendment5.py]

Amendment-5 closure-round-4 remediation verification (2026-07-13): Irene Pass-1 passed `194 passed, 1 skipped`; package and exact-authority focus passed `56 passed`; Texas's complete local runner suite passed `99 passed, 1 skipped`; the broad inherited workbook battery passed `550 passed, 5 skipped`; scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` passed. The frozen-run regression passed and no live provider/network call was made. A separately included forensic Texas subprocess test stopped at its pre-existing fixture-SHA guard (`eec3f293...` present versus `351a57fb...` pinned) before executing product code; that dirty fixture is outside Amendment 5 and was not changed.

#### Amendment 5 exact-current closure-round-5 findings

- [x] [Review][Patch] [HIGH] Distinguish current authority-aware packages with a durable builder model marker while preserving completed legacy `05B` packages under the prior marker; node identity alone is not a format discriminator [app/marcus/orchestrator/package_builders.py]
- [x] [Review][Patch] [MEDIUM] Bind source identity with newline normalization only, preserving leading/trailing whitespace drift, while keeping a separate extraction-framing digest for Texas's stripped presentation section [skills/bmad-agent-texas/scripts/run_wrangler.py; app/specialists/source_bundle.py; app/marcus/lesson_plan/slide_authority.py]
- [x] [Review][Patch] [HIGH] Preserve raw local Markdown/Notion-export text separately from normalized extracted text so an unchanged source reconciles at both Pass-1 and final inventory [skills/bmad-agent-texas/scripts/run_wrangler.py]
- [x] [Review][Patch] [MEDIUM] Accept only canonical top-level `slides/slide-N-name.md` refs as slide authority, matching the final inventory grammar [app/specialists/source_bundle.py]
- [x] [Review][Patch] [HIGH] Stage and fsync the plan generation, remove the prior receipt commit marker, atomically replace plan projections, and publish the matching receipt last; rollback uses replacement files rather than following target links [app/specialists/irene_pass1/_act.py]
- [x] [Review][Patch] [MEDIUM] Hash and recheck every one of the frozen run's 67 files and explicitly bomb socket/provider plus package/workbook downstream seams [tests/specialists/irene_pass1/test_pass1_authority_amendment5.py]

Amendment-5 closure-round-5 remediation verification (2026-07-13): Irene Pass-1 passed `195 passed, 1 skipped`; package and exact-authority focus passed `58 passed`; Texas's complete local runner suite passed `100 passed, 1 skipped`; the broad inherited workbook battery passed `550 passed, 5 skipped`; the consolidated new close-bar focus passed `110 passed, 1 skipped`. Scoped Ruff, compileall, all 18 import-linter contracts, repository-wide `git diff --check`, all-67-file frozen hashing, and provider/network bombs passed. No live provider call was made.

#### Amendment 5 exact-current closure-round-6 findings

- [x] [Review][Patch] [HIGH] Permit receiptless Pass-1 only when replaying an already completed package carrying the durable legacy marker; a new `04A` contribution can no longer mint a legacy package [app/marcus/orchestrator/package_builders.py]
- [x] [Review][Patch] [HIGH] Require current package replay to retain or upgrade the current builder marker, including migration of a matching completed legacy package once current receipt authority is present [app/marcus/orchestrator/package_builders.py]
- [x] [Review][Patch] [HIGH] Capture local Markdown authority and extraction from one stable source snapshot, rejecting a file changed during extraction [skills/bmad-agent-texas/scripts/run_wrangler.py]
- [x] [Review][Patch] [HIGH] Preserve Texas's normalized Markdown/Notion extraction contract for ordinary documents while using raw bytes only at canonical `slides/slide-N-name.md` authority coordinates [skills/bmad-agent-texas/scripts/run_wrangler.py]
- [x] [Review][Patch] [HIGH] Reject a delivered authority-receipt path unless it is exactly the canonical run coordinate [app/marcus/orchestrator/package_builders.py]
- [x] [Review][Patch] [HIGH] Flush the containing directory between receipt-marker removal, each plan projection replacement, and receipt-last commit/rollback [app/specialists/irene_pass1/_act.py]
- [x] [Review][Patch] [MEDIUM] Read completed Deep-Dive journals only through a contained, regular, duplicate-key-free snapshot [app/marcus/orchestrator/workbook_wiring.py]

Amendment-5 closure-round-6 remediation verification (2026-07-13): the combined Irene/authority/package slice passed `257 passed, 1 skipped`; package-builder integration passed `29 passed`; Texas's complete local runner suite passed `161 passed, 1 skipped`, including mid-extraction mutation rejection and retained Notion normalization. Scoped Ruff, compileall, all 18 import-linter contracts, repository-wide `git diff --check`, and the frozen run's 67-file count plus protected hashes passed. A deliberately wider Marcus sweep recorded `1750 passed, 7 skipped, 64 failed`; all 64 failures are inherited runner fakes that attempt to mint a new package from receiptless Irene output, the unsafe compatibility path this amendment now rejects. Per the operator's no-full-repository-harmonization boundary, those unrelated legacy fixtures were not mass-rewritten. No live provider call was made.

#### Amendment 5 exact-current closure-round-7 findings

- [x] [Review][Patch] [HIGH] Reconcile the canonical Pass-1 receipt commit-marker sidecar again at the workbook authority seam so a resume after node 06 cannot spend after marker deletion or corruption [app/marcus/orchestrator/workbook_wiring.py]
- [x] [Review][Patch] [MEDIUM] Upgrade only the recognized legacy package marker; reject unknown or future markers instead of laundering them into current authority [app/marcus/orchestrator/package_builders.py]
- [x] [Review][Patch] [HIGH] Fsync the Deep-Dive journal directory entry after every atomic replacement and fail before provider dispatch when durability cannot be established [app/marcus/orchestrator/workbook_wiring.py]
- [x] [Review][Patch] [MEDIUM] Fsync the authority-map directory after hard-link publication and temporary cleanup [app/marcus/lesson_plan/slide_authority.py]
- [x] [Review][Patch] [HIGH] Make rollback itself receipt-last: withdraw/fsync the current marker, durably restore each plan projection, and restore/fsync the prior receipt last [app/specialists/irene_pass1/_act.py]
- [x] [Review][Patch] [HIGH] Eliminate Markdown ABA split snapshots by deriving both normalized extraction and raw authority from one identity-checked regular-file byte capture [skills/bmad-agent-texas/scripts/run_wrangler.py; skills/bmad-agent-texas/scripts/source_wrangler_operations.py]

Amendment-5 closure-round-7 remediation verification (2026-07-13): the combined Irene/authority/package slice passed `260 passed, 1 skipped`; Texas's complete local runner suite passed `161 passed, 1 skipped`; the focused package/rollback/map/Deep-Dive slice passed `158 passed, 4 skipped`. New regressions cover ABA coherence, rollback after current-receipt publication, unknown markers, deleted downstream receipt markers, authority-map dual directory flush, and journal-flush failure before provider spend. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` passed. No live provider call was made.

#### Amendment 5 exact-current closure-round-8 findings

- [x] [Review][Patch] [HIGH] Serialize cooperating Pass-1 generation publishers and workbook authority consumers with one per-run lock so overlapping resume/publication cannot mix generations or remove a marker after validation but before provider dispatch [app/pass1_generation_lock.py; app/specialists/irene_pass1/_act.py; app/marcus/orchestrator/workbook_wiring.py]
- [x] [Review][Patch] [MEDIUM] Recover a crash-left authority-map temporary only when it is the same hard-linked inode as the fully validated expected target; otherwise retain split-brain failure [app/marcus/lesson_plan/slide_authority.py]
- [x] [Review][Patch] [MEDIUM] Reconcile crash-left Deep-Dive journal temporaries: remove only an orphan pre-dispatch marker, or promote only a same-call completed/failure-evidence temporary over its committed in-progress record [app/marcus/orchestrator/workbook_wiring.py]
- [x] [Review][Patch] [MEDIUM] Read the captured Markdown handle twice and require identical bytes in addition to stable file identity/metadata, rejecting same-size torn transient content [skills/bmad-agent-texas/scripts/run_wrangler.py]

Amendment-5 closure-round-8 remediation verification (2026-07-13): the combined Irene/authority/package/Texas suite passed `422 passed, 2 skipped`; the focused concurrency/recovery slice passed `137 passed, 4 skipped`; the Deep-Dive/workbook resume slice passed `151 passed, 6 skipped`. New regressions cover overlapping Pass-1 publication refusal, workbook provider refusal under the shared generation lock, same-inode map cleanup recovery, and completed-journal temporary promotion. Scoped Ruff, compileall, all 18 import-linter contracts, repository-wide `git diff --check`, and the frozen run's 67-file count plus protected hashes passed. No live provider call was made.

#### Amendment 5 exact-current closure-round-9 findings

- [x] [Review][Patch] [HIGH] Acquire the shared generation lock before Irene reads authority or invokes its provider and hold it through receipt-last publication, preventing overlapping calls from spending on and later overwriting the same prior generation [app/specialists/irene_pass1/_act.py]
- [x] [Review][Patch] [HIGH] Hold the same generation lock from the workbook's first authority preflight through Scene, Promise, and Deep-Dive effects; retain the dispatch lock for Deep-Dive duplication control [app/marcus/orchestrator/workbook_wiring.py]
- [x] [Review][Patch] [MEDIUM] Make §06 a cooperating Pass-1 authority consumer by acquiring the generation lock around its complete sidecar/receipt validation and package projection [app/marcus/orchestrator/package_builders.py]
- [x] [Review][Patch] [MEDIUM] Reject hard-linked generation-lock coordinates before initialization can mutate an external alias; place the persistent lock beside rather than inside the run directory [app/pass1_generation_lock.py]
- [x] [Review][Patch] [MEDIUM] Require bundle carrier reads to match opened size and an identical second handle read, complementing the existing per-section metadata digest join [app/specialists/source_bundle.py]
- [x] [Review][Dismiss] A process crash during Pass-1 publication already leaves the run fail-closed behind a missing/mismatched receipt marker and requires explicit Pass-1 recovery/re-entry; auto-promoting partial staging would be deterministic repair and conflict with Amendment 5's no-repair rule. No false acceptance or downstream spend path was shown [app/specialists/irene_pass1/_act.py]

Amendment-5 closure-round-9 remediation verification (2026-07-13): the combined Irene/authority/package/Texas suite passed `425 passed, 2 skipped`; the focused generation-lock/package/workbook slice passed `164 passed, 4 skipped`; the Deep-Dive/workbook resume slice passed `151 passed, 6 skipped`. New regressions prove provider-zero lock contention for Irene and all three workbook writers, §06 contention refusal, hard-link lock safety, and retained crash-temporary recovery. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` passed. No live provider call was made.

#### Amendment 5 exact-current closure-round-10 verdict

Fresh independent Blind Hunter, Edge Case Hunter, and Acceptance Auditor reviews each returned `ZERO FINDINGS` against the exact post-round-9 working tree. Amendment 5's deterministic/static/adversarial review bar is complete. Story 38.3a remains `in-progress` because the separately governed live validation/closure work has not been authorized or performed; code-review cleanliness does not waive that product acceptance step. No live provider call was made.

#### Amendment 5 live-finding correction review

- [x] [Review][Patch] [HIGH] Require and stably recheck a valid manifest commit marker whose sizes and hashes bind every consumed bundle artifact [app/specialists/source_bundle.py:414]
- [x] [Review][Patch] [HIGH] Withdraw the newly installed manifest if its final directory durability flush fails [app/specialists/texas/_act.py:380]
- [x] [Review][Patch] [HIGH] Make interrupted hardening recoverable only through an owned transaction marker, using unique same-directory staging files that cannot be blocked by crash residue [app/specialists/texas/_act.py:318]
- [x] [Review][Patch] [HIGH] Harden every dispatched bundle carrying a valid directive instead of trusting the caller-controlled optional `command` receipt field [app/specialists/texas/_act.py:649]
- [x] [Review][Patch] [HIGH] Authenticate the incoming bundle against its manifest and prove hardening performs only the owned evidence transformation before resealing [app/specialists/texas/_act.py:398]
- [x] [Review][Patch] [HIGH] Validate the extracted digest of every primary section before filtering slide coordinates returned to Irene [app/specialists/source_bundle.py:385]
- [x] [Review][Patch] [MEDIUM] Enforce canonical local primary paths and a closed source-ID grammar before either value can enter evidence syntax [app/specialists/source_bundle.py:79]
- [x] [Review][Patch] [MEDIUM] Reject evidence-marker spelling variants and avoid modifying Markdown literal/code structures while anchoring claims [app/specialists/texas/_act.py:213]
- [x] [Review][Patch] [HIGH] Require at least one validated claim per primary section and derive the G0 pass receipt from checked predicates instead of unconditional booleans [app/specialists/texas/_act.py:446]
- [x] [Review][Patch] [MEDIUM] Count retrieval scope from bounded primary bodies rather than headings and wrapper/preamble text [app/specialists/texas/_act.py:435]
- [x] [Review][Patch] [MEDIUM] Reject duplicate YAML mapping keys in directives, reports, and results before they can be resealed [app/specialists/texas/_act.py:101]

Review triage merged 21 raw reports into 11 actionable patches and dismissed 2 duplicates: the preamble-authentication report is covered by whole-artifact manifest validation, and the fixed temporary-name report is covered by owned transaction recovery plus unique staging. No review layer failed and no item requires an operator design decision.

#### Amendment 5 live-finding correction exact-current re-review

- [x] [Review][Patch] [HIGH] Require a provable pre-hardening primary projection digest, including normalizing the wrangler's emitted line endings so the original digest can match exactly before owned evidence markers are added [skills/bmad-agent-texas/scripts/source_wrangler_operations.py; app/specialists/texas/_act.py]
- [x] [Review][Patch] [HIGH] Independently reconcile the wrangler's initially unmanifested `result.yaml` identity and status against authenticated report/metadata authority before resealing it [app/specialists/texas/_act.py]
- [x] [Review][Patch] [HIGH] Give each hardening transaction exclusive ownership, bind it to the withdrawn manifest generation, require the exact original/target artifact sets, and semantically validate recovered targets before manifest publication [app/specialists/texas/_act.py]
- [x] [Review][Patch] [HIGH] Treat a present hardening transaction marker as unpublished at every consumer, including when failed manifest withdrawal leaves a visible marker [app/specialists/source_bundle.py; app/specialists/texas/_act.py]
- [x] [Review][Patch] [MEDIUM] Use a shared CommonMark-aware scanner for primary boundaries and evidence anchoring so nested/blockquote fences, indented and inline code, HTML code, and tables are preserved without allowing foreign rendered evidence [app/specialists/source_bundle.py; app/specialists/texas/_act.py]
- [x] [Review][Patch] [MEDIUM] Restrict per-primary G0 claim counting to substantive prose/list claims, excluding rules, comments, images, references, owner-marker-only lines, and other structural Markdown [app/specialists/texas/_act.py]
- [x] [Review][Patch] [MEDIUM] Reject drive-qualified local paths and require canonical slide primaries to use a recognized local kind with matching path authority [app/specialists/source_bundle.py]
- [x] [Review][Patch] [MEDIUM] Close and remove every uniquely staged descriptor/file when permission hardening fails immediately after creation [app/specialists/texas/_act.py]

Exact-current triage merged 18 raw Blind/Edge/Acceptance reports into 8 actionable patches. Duplicate reports on fence length, transaction trust, result authentication, and failed manifest withdrawal were consolidated. No layer failed, no item was deferred, and no operator design decision is required.

#### Amendment 5 live-finding correction final deterministic verdict

All 19 live-finding correction items are implemented. The final exact-current Story 38.3a regression gate passed `383 passed, 3 skipped, 1 deselected`; scoped Ruff, compileall, the six Marcus import-linter contracts, and repository-wide `git diff --check` passed. Follow-on adversarial rounds also closed directive semantic binding, dispatch-receipt reconciliation, transaction recovery, CommonMark boundary handling, corpus-relative containment, and local-source identity/ABA races. The exact captured source bytes are now digest-bound before Markdown consumption or private PDF/DOCX/text snapshot parsing. Fresh independent Blind Hunter, Edge Case Hunter, and Acceptance Auditor reviews each returned `ZERO FINDINGS` on this same tree. No live provider call was made during remediation. Story 38.3a remains `in-progress` solely because a separately governed fresh live acceptance run has not yet been authorized or performed.

The single Amendment-4 live attempt `a28aa15a-fc80-46ae-b05a-09ac864829bb` completed all eight delegated HIL actions and 11/11 Enrique segments, then stopped before map or provider dispatch because `u06` was duplicated and one claimed exact anchor used `shape` where the source says `shaping`. The failed run is frozen; Story 38.3a and Story 38.1 remain in progress under party-approved Amendment 5.

#### Amendment 6 mandatory code-review findings

- [x] [Review][Patch] Pin one canonical Irene call coordinate per trial and manifest node so identity drift cannot recall an ambiguous provider call [app/marcus/lesson_plan/pass1_call_journal.py:22]
- [x] [Review][Patch] Reprocess completed-call raw evidence through deterministic projection and authority validation, and reconcile published artifacts before zero-call replay [app/specialists/irene_pass1/_act.py:1374]
- [x] [Review][Patch] Reject a different completion candidate when a call journal is already completed [app/marcus/lesson_plan/pass1_call_journal.py:338]
- [x] [Review][Patch] Require a digest-bound effective model configuration in every Pass-1 call identity [app/specialists/irene_pass1/_act.py:1357]
- [x] [Review][Patch] Validate refinement unit/source/role/parent identity before cluster normalization can repair model-authored drift [app/specialists/irene_pass1/_act.py:884]
- [x] [Review][Patch] Fail catalog construction when any declared source has no uniquely selectable exact span [app/marcus/lesson_plan/pass1_source_span_catalog.py:210]
- [x] [Review][Patch] Bound catalog entry count and serialized size before provider dispatch [app/marcus/lesson_plan/pass1_source_span_catalog.py:210]
- [x] [Review][Patch] Enforce the advertised one-to-six source-span selection limit [app/marcus/lesson_plan/pass1_source_span_catalog.py:317]
- [x] [Review][Patch] Include closing quotes and brackets in exact punctuation-bounded sentence spans [app/marcus/lesson_plan/pass1_source_span_catalog.py:153]
- [x] [Review][Patch] Allowlist provider evidence and scrub secrets from retained exception metadata [app/marcus/lesson_plan/pass1_call_journal.py:105]
- [x] [Review][Patch] Read call journals through a stable non-following file handle [app/marcus/lesson_plan/pass1_call_journal.py:209]
- [x] [Review][Patch] Reconcile Irene journal attempts to trace attempts by durable request/response identity while preserving unmatched trace cost and correct per-model totals [app/runtime/economics.py:584]
- [x] [Review][Patch] Recompute budget status and drift alerts after journal-cost reconciliation [app/runtime/economics.py:622]
- [x] [Review][Patch] Bind journal pricing to the cost report pricing-table digest [app/runtime/economics.py:563]
- [x] [Review][Patch] Persist cost JSON, Markdown, and attempt ledger as one recoverable artifact set [app/runtime/economics.py:771]
- [x] [Review][Patch] Read economics journal evidence with duplicate-key rejection and stable non-following file identity [app/runtime/economics.py:456]
- [x] [Review][Patch] Include production runtime, runner, delegation policy, and governance inputs even when the selected course input is external [scripts/utilities/marcus_spoc_live_test_runner.py:458]
- [x] [Review][Patch] Narrow writable exclusions to the fresh trial, inventory both output trees, and persist a post-run immutable-input comparison without masking the original run result [scripts/utilities/marcus_spoc_live_test_runner.py:484]
- [x] [Review][Patch] Hash governed input files through stable non-following handles and explicitly exclude generated bytecode caches [scripts/utilities/marcus_spoc_live_test_runner.py:177]

#### Amendment 6 exact-current closure review

The fresh Blind Hunter, Edge Case Hunter, and Acceptance Auditor reported 26 raw observations. Triage consolidated duplicates into 12 product-relevant patches and implemented all 12 under the operator's standing apply-all-review-patches direction. The Edge suggestion to execute the whole application from a content-addressed clone, solely to detect an input mutation that is perfectly reverted between observations, is dismissed as a new runtime-sandbox architecture requirement: Amendment 6 promises reconstructable before/after governed identity, not a hermetic copied-runtime executor. No proofing-only behavior was added.

- [x] [Review][Patch] Consume trace attempts one-to-one, reject duplicate reuse and unjournaled trace calls, and fail closed instead of double-counting ambiguous correlation [app/runtime/economics.py]
- [x] [Review][Patch] Treat zero provider usage as untrusted and carry unavailable-attempt count plus lower-bound cost posture in the strict machine report [app/models/runtime/trial_economics_report.py; app/runtime/economics.py]
- [x] [Review][Patch] Serialize economics persistence, require complete transaction artifact sets, fsync directory entries, and hide transaction-in-progress reports from every product reader [app/runtime/economics.py; app/marcus/orchestrator/production_runner.py; app/marcus/orchestrator/operator_surface_assembler.py]
- [x] [Review][Patch] Scrub Basic auth, password, client-secret, access-token, refresh-token, and signed-query credential forms from retained provider exceptions [app/marcus/lesson_plan/pass1_call_journal.py]
- [x] [Review][Patch] Reject duplicate JSON keys in both the Irene envelope payload and model candidate before deterministic validation [app/specialists/irene_pass1/_act.py]
- [x] [Review][Patch] Refuse a registered production-model dispatch when the conservative UTF-8 byte-token upper bound exceeds the resolved context budget [app/specialists/irene_pass1/_act.py]
- [x] [Review][Patch] Canonically join supported provider text blocks and reject unsupported/non-text response shapes [app/specialists/irene_pass1/_act.py]
- [x] [Review][Patch] Constrain run IDs to one contained coordinate and bind registered production-model calls to the RunState UUID and approved production runs roots [app/specialists/irene_pass1/_act.py]
- [x] [Review][Patch] Reconcile completed replay against the current cache entry count instead of returning stale accounting [app/specialists/irene_pass1/_act.py]
- [x] [Review][Patch] Double-read governed input handles and require identical bytes in addition to stable file identity and metadata [scripts/utilities/marcus_spoc_live_test_runner.py]
- [x] [Review][Patch] Reserve the run coordinate before preflight publication, verify the persisted manifest, and retain the trial lock through output inventory and postflight comparison [scripts/utilities/marcus_spoc_live_test_runner.py]
- [x] [Review][Patch] Require a present output root and make attach/resume close any retained preflight with fresh postflight and output evidence [scripts/utilities/marcus_spoc_live_test_runner.py]

The first closure re-review then exposed a second-order cost/recovery boundary. Those reports were consolidated and closed without a live call: all-Irene-traces-with-no-journals now fails; unknown cost cannot become under-budget, exact-median, Irene drift, or an exact operator-surface value; crossed request/response identifiers fail; unsupported returned content is durably terminal; cost and runner locks are alias-safe advisory locks recoverable after process death; stale ledgers are transactionally deleted; cost posture is internally validated; retained preflight evidence is digest-revalidated; and attach inventories the state-config output root. The runner's persistent advisory lock is explicitly excluded from output inventory.

The next exact-current pass closed the serialized-aggregate/no-journal bypass, write/delete transaction conflicts, legacy reports that omitted explicit cost posture, additional AWS credential forms, returned-response evidence-normalization failure, and attach-before-preflight ordering. A retained current-run lock now requires valid preflight evidence before the resume engine can act; legacy pre-Amendment-6 attaches remain readable without manufacturing a baseline.

The final shared Blind/Edge observation removed the last proxy inference: the persistent advisory lock now retains an explicit `preflight_required` origin bit. Current governed starts keep the requirement across crash/recovery; legacy runs remain legacy across repeated attaches and are not accidentally made unrecoverable.

The origin bit was then separated from the in-place advisory-lock body into an immutable, atomically published `codex-hil-runner-origin.v1` sidecar. A new run may initialize it; every pre-existing malformed, mismatched, or downgraded origin fails closed. A crash while refreshing diagnostic lock-holder metadata can no longer erase the governed-preflight requirement.

Post-remediation deterministic evidence is `408 passed, 2 skipped`; scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No live provider call was made.

#### Amendment 6 live-finding dual-digest correction review

- [x] [Review][Patch] Validate a completed Irene replay before publishing the reconstructed plan and authority receipt, so a mismatching replay cannot replace the last committed artifact generation [app/specialists/irene_pass1/_act.py:1767]
- [x] [Review][Patch] Reject multiple authenticated source records that claim the same source path with different raw digests in one source-span catalog [app/marcus/lesson_plan/pass1_source_span_catalog.py:239]
- [x] [Review][Patch] Recursively enforce receipt row role, parent, source, and projected-reference invariants before accepting a rehashed persisted temporal-authority receipt [app/marcus/lesson_plan/pass1_authority.py:289]
- [x] [Review][Patch] Require every deserialized source-span offset range to have the same length as its exact text [app/marcus/lesson_plan/pass1_source_span_catalog.py:94]

All four exact-current findings were patched under the operator's apply-all choice. Causal RED was `6 failed, 41 passed`; focused GREEN is `47 passed`; the expanded dependency matrix is `670 passed, 10 skipped`. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No provider call or live-run launch occurred. Story status remains `in-progress` pending a fresh exact-current closure review and a separately authorized governed live workbook attempt.

#### Amendment 6 dual-digest correction closure-round-2 findings

- [x] [Review][Patch] Reconcile every prior current-v2 plan and receipt against the newly authenticated source-span catalog before journal creation or provider dispatch [app/specialists/irene_pass1/_act.py:1534]
- [x] [Review][Patch] Reject noncanonical receipt activity ordering and any active interstitial whose required head parent is retired; revalidate supplied plan cluster topology during receipt reconciliation [app/marcus/lesson_plan/pass1_authority.py:357]

Fresh Blind Hunter, Edge Case Hunter, and Acceptance Auditor review produced three reports consolidated into two actionable findings. The stale-catalog dispatch defect was independently reproduced by Blind and Acceptance; the active-child/retired-parent defect was independently reproduced by Blind and Edge. No layer failed, no finding was dismissed or deferred, and neither fix requires an operator design decision. No live call occurred during root verification or remediation.

Both findings were patched under the operator's apply-all choice. Causal RED was `3 failed, 15 passed`; focused GREEN is `90 passed, 1 skipped`; the expanded dependency matrix is `674 passed, 10 skipped`. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. The stale/rehashed current-v2 witness now fails before journal creation with zero provider calls; receipt activity history and plan cluster corroboration fail closed. No live execution occurred.

#### Amendment 6 dual-digest correction closure-round-3 finding

- [x] [Review][Patch] Reconstruct and exactly compare the entire canonical Irene completed output and result/cache shape before returning a zero-call replay or republishing its artifacts [app/specialists/irene_pass1/_act.py:305]

Final exact-current Blind Hunter and Acceptance Auditor returned `ZERO FINDINGS`. Edge Case Hunter reproduced one rehashed-journal case in which the four individually checked output bindings remained valid while another cached-output field was changed and returned. Triage rates this high and patchable: deterministic reprocessing already reconstructs every legitimate output field, so exact canonical equality is required. No layer failed, and no item was deferred or dismissed. No live call occurred.

The finding was patched under the operator's apply-all choice. Causal RED proved a fully rehashed extra graph-output field was accepted; focused GREEN is `91 passed, 1 skipped`; the expanded dependency matrix is `675 passed, 10 skipped`. Replay now requires exact result/cache shape and exact canonical full-output reconstruction. The sole nondeterministic event timestamp is restricted to one canonical UTC value shared by both otherwise exactly reconstructed learning events. Valid zero-call replay remains green. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No live call occurred.

#### Amendment 6 dual-digest correction closure-round-4 finding

- [x] [Review][Patch] Compare reconstructed completed output as canonical JSON bytes rather than Python object equality so numeric `0`/`1` cannot substitute for JSON booleans [app/specialists/irene_pass1/_act.py:367]

Sealing Acceptance and Edge reviews returned `ZERO FINDINGS`. Blind Hunter reproduced one type-confusion bypass: Python considers `0 == False` and `1 == True`, so rehashed lock fields could retain object equality while changing canonical JSON type. Triage rates this high and patchable with type-strict canonical serialization comparison. No layer failed, and no item was deferred or dismissed. No live call occurred.

The finding was patched under the operator's apply-all choice. Causal RED reproduced numeric-zero substitution for all three canonical `locked:false` projections; exact canonical JSON comparison now rejects it. The expanded dependency matrix is `676 passed, 10 skipped`; scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No live call occurred.

#### Amendment 6 dual-digest correction closure-round-5 finding

- [x] [Review][Patch] Require the completed replay `result_identity` to contain exactly the canonical plan, authority, and output digest keys before any zero-call return or artifact publication [app/specialists/irene_pass1/_act.py:313]
- [x] [Review][Patch] Recursively validate completed provider evidence against its allowlisted schema, including nonnegative integer token usage, before using it to reconstruct or return replay output [app/marcus/lesson_plan/pass1_call_journal.py:350]

Final-seal Edge and Acceptance reviews returned `ZERO FINDINGS`. Blind Hunter reproduced (a) a rehashed completed journal with an extra `result_identity` field and (b) a fully rehashed provider-evidence/output chain carrying negative token usage. Both passed zero-call replay. Triage rates both high and patchable with an exact identity key-set guard plus recursive provider-evidence schema validation before replay reconstruction. No layer failed, and no item was deferred or dismissed. No live call occurred.

Both findings were patched under the operator's apply-all choice. Causal RED reproduced both accepted rehashed variants; exact identity shape and canonical provider-evidence variants now fail closed, including nonnegative type-strict usage totals/details. The focused journal suite is `15 passed`; the expanded dependency matrix is `678 passed, 10 skipped`. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No live call occurred.

#### Amendment 6 dual-digest correction closure-round-6 findings

- [x] [Review][Patch] Validate normalized provider evidence before first persistence/use so initial execution cannot complete with evidence that deterministic replay rejects [app/marcus/lesson_plan/pass1_call_journal.py:467]
- [x] [Review][Patch] Require the exact canonical journal top-level key set for each call state before resume or zero-call replay [app/marcus/lesson_plan/pass1_call_journal.py:404]
- [x] [Review][Patch] Apply the same canonical provider-evidence validator before economics treats Irene journal usage as known and priceable [app/runtime/economics.py:598]
- [x] [Review][Patch] Enforce the one-to-six selected-span limit while independently revalidating current-v2 plan/receipt authority, including rehashed prior authority [app/marcus/lesson_plan/pass1_authority.py:211]

Lock Acceptance returned `ZERO FINDINGS`. The first Blind attempt was interrupted by an automated classifier and was rerun successfully as a correctness audit. Blind and Edge independently converged on first-execution provider-evidence validation; Edge additionally reproduced unknown journal fields, economics consumption of malformed evidence, and seven-span rehashed v2 authority. Triage consolidates five raw reports into four high, patchable findings. No layer remains failed, and no item was deferred or dismissed. No live call occurred.

All four findings were patched under the operator's apply-all choice. Focused GREEN is `56 passed`; the exact-current dependency matrix is `1724 passed, 10 skipped`. A deliberately wider sweep additionally produced `1751 passed, 10 skipped, 4 failed`; the four failures are pre-existing legacy package-builder fixtures carrying invalid receipt/source pairings and are outside this closure patch and the operator's no-harmonization boundary. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No provider call or live-run launch occurred.

#### Amendment 6 dual-digest correction closure-round-7 findings

- [x] [Review][Patch] Validate the exact current journal state envelope before every response, exception, and completion transition so first execution cannot launder or complete bytes that replay rejects [app/marcus/lesson_plan/pass1_call_journal.py]
- [x] [Review][Patch] Apply one shared whole-journal validator in economics before any Irene attempt is treated as known and priceable [app/runtime/economics.py]
- [x] [Review][Patch] Persist a nonempty canonical fallback when a provider exception has an empty string representation [app/marcus/lesson_plan/pass1_call_journal.py]
- [x] [Review][Patch] Add causal all-state exact-envelope coverage plus a rehashed seven-span prior-authority production witness proving zero journal creation and zero provider calls [tests/specialists/irene_pass1]

Fresh exact-current Blind Hunter reproduced a high state-transition laundering defect. Edge independently found the whole-envelope economics gap and empty-exception-message boundary. Acceptance Auditor found two causal-coverage gaps: all three journal states and the rehashed-prior-authority/pre-provider path. These are consolidated into four patchable items; no item is dismissed or deferred. No live call occurred.

All four findings were patched under the operator's apply-all choice. The focused causal suite is `64 passed`; the exact-current dependency matrix is `1732 passed, 10 skipped`. Every journal state transition, replay consumer, and economics consumer now shares whole-envelope validation; all three state shapes, empty exception evidence, malformed pricing evidence, transition laundering, and rehashed seven-span prior authority have direct regression witnesses. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No provider call or live-run launch occurred.

#### Amendment 6 dual-digest correction closure-round-8 findings

- [x] [Review][Patch] Enforce canonical persisted call-identity semantics—not merely rehashable self-consistency—including exact schema/processor versions, coordinates, digest fields, and system/user message shape before any consumer accepts a journal [app/marcus/lesson_plan/pass1_call_journal.py]
- [x] [Review][Patch] Forbid any response or second exception transition after durable dispatch-exception evidence has made the provider outcome ambiguous [app/marcus/lesson_plan/pass1_call_journal.py]
- [x] [Review][Patch] Reject impossible completed journals carrying terminal error/unsupported provider evidence or noncanonical Pass-1 result/result-identity/cache shape in the shared validator [app/marcus/lesson_plan/pass1_call_journal.py]
- [x] [Review][Patch] Rejoin every populated retired current-v2 authority row to the rebuilt catalog so rehashed unknown retired span IDs cannot become permanent history [app/marcus/lesson_plan/pass1_authority.py]

Final fresh Acceptance Auditor returned `ZERO FINDINGS`. Blind and Edge independently converged on rehashed noncanonical identity semantics being accepted by economics; Blind reproduced a changed processor version with a recomputed request digest being priced as known. Edge additionally found three fail-closed boundaries around durable ambiguity, completed error/result semantics, and retired v2 authority history. Triage consolidates the reports into four high, patchable findings; none is dismissed or deferred. No live call occurred.

All four findings were patched under the operator's apply-all choice. Focused causal GREEN is `73 passed`; the exact-current dependency matrix is `1741 passed, 10 skipped`. Persisted call identities now enforce canonical semantics, dispatch-exception ambiguity is irreversible, completed journals require normal provider evidence plus exact result/cache semantics, and every populated current-v2 history row is rejoined to the authenticated catalog. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. The operator subsequently granted standing authority to apply any further deterministic review findings without another confirmation stop until the pre-live readiness point. No provider call or live-run launch occurred.

#### Amendment 6 dual-digest correction closure-round-9 finding

- [x] [Review][Patch] Derive and validate completed plan, authority, and output identities from the canonical cached Irene output and its embedded validated authority receipt before allowing completion or resume [app/marcus/lesson_plan/pass1_call_journal.py]

Fresh Acceptance and Edge reviews returned `ZERO FINDINGS`. Blind reproduced one remaining high causal-binding gap: arbitrary digest-shaped values plus a canonical but empty cache object could be marked completed by the shared journal transition even though deterministic Irene replay would reject them. Under the operator's standing apply-all authority, the shared validator now requires the canonical Irene output envelope, validates its embedded plan/receipt binding and events, binds usage/model/run semantics, and derives all three result identities from those bytes. Focused GREEN is `76 passed`; the exact-current dependency matrix is `1744 passed, 10 skipped`. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No live call occurred.

#### Amendment 6 dual-digest correction closure-round-10 findings

- [x] [Review][Patch] Require exact equality among the dispatched journal catalog digest, completed projected-plan catalog digest, and embedded authority-receipt catalog digest [app/marcus/lesson_plan/pass1_call_journal.py]
- [x] [Review][Patch] Make completed locked-scope and usage comparisons canonical/type-strict, constrain both Irene artifact coordinates to the same run directory and canonical filenames, and reject empty plans or malformed optional planning projections [app/marcus/lesson_plan/pass1_call_journal.py]
- [x] [Review][Patch] Add the exact structurally valid outer cache with canonical `{}` prefix witness so the new inner output-binding guard is exercised directly [tests/specialists/irene_pass1/test_pass1_call_journal_amendment6.py]

Blind reproduced a high cross-catalog completion; Edge independently confirmed it and supplied type, coordinate, empty-plan, and optional-projection boundaries. Acceptance identified the missing exact `{}` causal witness. Under standing authority these were consolidated and patched immediately. Focused GREEN is `77 passed`; the exact-current dependency matrix is `1745 passed, 10 skipped`. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No live call occurred.

#### Amendment 6 dual-digest correction closure-round-11 findings

- [x] [Review][Patch] Bind completed artifact coordinates to the actual journal directory, not merely a same-named run directory under an arbitrary root [app/marcus/lesson_plan/pass1_call_journal.py]
- [x] [Review][Patch] Require planning-provenance presence parity and exact strict schema equality between the plan and top-level output projection [app/marcus/lesson_plan/pass1_call_journal.py]
- [x] [Review][Patch] Validate optional planning-context coverage through the strict canonical `PlanningContextCoverageReceipt` round-trip and reject empty or coerced mappings [app/marcus/lesson_plan/pass1_call_journal.py]

Blind reproduced one-way planning-provenance omission; Acceptance independently found malformed optional coverage; Edge confirmed both and the same-name/different-root artifact path gap. Under standing authority all three were patched with direct causal tests. Focused GREEN is `80 passed`; the exact-current dependency matrix is `1748 passed, 10 skipped`. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No live call occurred.

#### Amendment 6 dual-digest correction closure-round-12 findings

- [x] [Review][Patch] Require planning coverage, plan provenance, and top-level provenance to co-occur; reject present-null provenance and reconcile provenance coverage status with the strict coverage receipt [app/marcus/lesson_plan/pass1_call_journal.py]
- [x] [Review][Patch] Require every non-null planning provenance digest to have its canonical companion path [app/marcus/lesson_plan/pass1_call_journal.py]

Blind reproduced provenance without its production-created coverage companion; Acceptance found present-null plan provenance; Edge confirmed both plus digest/path parity. Under standing authority the three projection presences are now identical by contract, null cannot masquerade as absence, coverage status reconciles, and digest/path pairs are exact. Focused GREEN is `82 passed`; the exact-current dependency matrix is `1750 passed, 10 skipped`. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No live call occurred.

#### Amendment 6 dual-digest correction closure-round-13 findings

- [x] [Review][Patch] Require `framing_only` provenance to pair specifically with coverage `present` and empty objective-ID lists [app/marcus/lesson_plan/pass1_call_journal.py]
- [x] [Review][Patch] Enforce provenance digest-to-path implication without rejecting the valid path-with-null-digest shape; prove both directions causally [app/marcus/lesson_plan/pass1_call_journal.py]
- [x] [Review][Patch] Build Irene planning provenance from the already-resolved production run directory so omitted optional `runs_root` cannot create a false no-directory posture [app/specialists/irene_pass1/_act.py]

Blind reproduced contradictory framing-only/absent coverage. Acceptance caught that the previous parity rule rejected the producer's valid path-with-null-digest shape. Edge traced that shape to `_act` consulting raw optional payload instead of the already-resolved run directory. Under standing authority all three were corrected with positive and negative witnesses. Focused GREEN is `85 passed`; the exact-current dependency matrix is `1753 passed, 10 skipped`. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No live call occurred.

#### Amendment 6 dual-digest correction closure-round-14 findings

- [x] [Review][Patch] Add direct success and fail-loud witnesses proving omitted optional payload `runs_root` still uses the resolved run directory for provenance digests and coverage-receipt persistence [tests/specialists/irene_pass1/test_planning_context_handoff.py]
- [x] [Review][Patch] Persist LO-ignore coverage evidence under the already-resolved run directory instead of consulting raw optional payload `runs_root` [app/specialists/irene_pass1/_act.py]

Acceptance found the resolved-root success fix lacked its exact omitted-payload causal witness. Edge found the same raw-payload error in the LO-coverage failure receipt branch. Blind's first review turn was interrupted by an automated classifier and is rerun in the next exact-current seal. Under standing authority both resolved-root paths now have direct success/failure witnesses. Focused GREEN is `100 passed`; the exact-current dependency matrix is `1755 passed, 10 skipped`. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No live call occurred.

#### Amendment 6 dual-digest correction closure-round-15 findings

- [x] [Review][Patch] Use `_act_locked`'s already-resolved `run_id` argument for both planning-provenance companion lookup and fail-loud coverage-receipt persistence; prove raw payload and resolved runtime IDs cannot split coordinates [app/specialists/irene_pass1/_act.py]
- [x] [Review][Patch] Make planning coverage intrinsically honest: context is necessarily present, `present` has no weak objectives, `partial` has at least one weak objective, and `absent` has no supported plus at least one weak objective [app/marcus/lesson_plan/planning_context.py]
- [x] [Review][Patch] Add completion-journal causal witnesses rejecting every impossible planning-coverage state identified by Blind and Edge [tests/specialists/irene_pass1/test_pass1_call_journal_amendment6.py]

Acceptance found both resolved-directory paths still recomputed run identity from payload/state instead of honoring the resolved argument. Blind reproduced coverage receipts that deterministic Irene cannot emit, and Edge independently confirmed `context_present=false` was accepted. Under standing authority the coordinate split and intrinsic receipt semantics were corrected with direct adversarial witnesses. Focused GREEN is `105 passed`; the exact-current dependency matrix is `1760 passed, 10 skipped`. Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. No live call occurred.

Fresh independent Blind Hunter, Edge Case Hunter, and Acceptance Auditor reviews each returned `ZERO FINDINGS` against the exact post-round-15 working tree. Amendment 6's deterministic/static/adversarial review bar is complete. Story 38.3a remains `in-progress` only because the one fresh governed live workbook validation has not yet run; no live/provider call occurred during remediation or sealing.

#### Amendment 7 live G2B economics correction findings

- [x] [Review][Patch] Preserve fail-closed missing-journal detection while removing fabricated Irene provider spans; a non-billable execution marker must prove Irene ran without competing with the digest-bound call journals [app/marcus/orchestrator/production_runner.py:705]
- [x] [Review][Patch] Reconcile non-billable Irene execution markers to journal node coordinates so partial journal loss fails closed rather than claiming complete accounting [app/runtime/economics.py:446]

The fresh governed v2 trial reached G2B with completed Irene journals for `04A`, `05`, and `05B`, then stopped while recording segment economics. The production runner had projected each multi-call Irene node contribution as a fabricated billable span, which could not correlate one-to-one with the real provider-attempt journals. The correction emits zero-token, node-coordinate execution markers and leaves the journals as the sole billable authority. Missing or partially missing journal coverage now fails closed; rejected-attempt journals without a completed contribution remain admissible. Frozen-evidence replay reconciles marker nodes and journal nodes exactly with zero Irene billable trace spans, exact cost posture, and total cost `$0.8165095`. Focused economics verification is `29 passed`; scoped Ruff, compileall, and diff checks pass. Fresh Blind, Edge, and Acceptance reviews each returned `ZERO FINDINGS`. No retry or provider call occurred.

## Dev Notes

### Expected production/test scope

- `app/marcus/lesson_plan/prework_artifact.py`
- NEW `app/marcus/lesson_plan/deep_dive_from_run.py` (or one equivalently narrow M3-safe adapter)
- NEW `app/marcus/lesson_plan/research_demand.py`
- `app/marcus/orchestrator/workbook_wiring.py`
- `app/marcus/orchestrator/workbook_prework_writers.py` or one narrowly named Deep Dive writer adapter
- focused unit/integration fixtures and tests
- this story and sprint ledger

`production_runner.py`, pipeline manifest, composition topology, generated/frozen prompt packs, workbook renderer, and `07W.2`â€“`07W.4` factories are not authorized. Terminal `_act.py` is authorized only for the binding reconciliation-only canonical-receipt delegation above.

The later G2B live finding narrowly supersedes the `production_runner.py` exclusion only for truthful non-billable Irene execution markers at the existing cost-trace seam; it changes no graph, node, gate, modality, or proof-run behavior.

### Existing contracts to reuse

- `deep_dive_projection.py`: `DeepDiveSkeletonRequest`, `DeepDiveSkeletonResult`, `DeepDiveWriter`, `compose_deep_dive_skeleton`, authority/candidate digests, gate replay, and deterministic offline stub.
- `prework_artifact.py`: atomic brief read/write and canonical payload digest; the reserved field already serializes as `null`.
- `workbook_wiring.py`: real `workbook_brief@07W.1`, exact contribution/sidecar reconciliation, explicit runtime-context injection, and existing workbook-writer model config.
- `research_packet.py`: exact Ask-A/Ask-B coordinates and packet readers. Consume; do not duplicate.

### Git intelligence

- `d43eb530` closed Story 37.4 and is this story's baseline.
- `36ada1ef`, `6b64ef06`, `490158ec`, and `f82dddf9` closed the remaining writer/pre-work prerequisites.
- Ambient shadow-monitor, run, workbook, recording-deconstruction, and notifier files are outside story scope and must not be staged.

### Latest technical information

No external library/provider/API upgrade is introduced. Repository-pinned Python/Pydantic/pytest/model-config patterns are authoritative; web research is unnecessary for this local contract/integration story.

### References

- `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` â€” amendments A1/A4/A5/A9 and ratified Epic-38 graph shape
- `_bmad-output/planning-artifacts/workbook-presentation-support-redesign-2026-07-12.md` â€” sections 7, 8, 11, and 13
- `_bmad-output/implementation-artifacts/38-0-two-packet-intake-contract.md`
- `_bmad-output/implementation-artifacts/38-3b-graph-topology-band-orchestrator.md`
- `_bmad-output/implementation-artifacts/36-4-wire-prework-part2-golden.md`
- `_bmad-output/implementation-artifacts/37-2a-deep-dive-skeleton.md`
- `app/marcus/lesson_plan/deep_dive_projection.py`
- `app/marcus/lesson_plan/prework_artifact.py`
- `app/marcus/orchestrator/workbook_wiring.py`
- `docs/project-context.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story creation research found that a verification-only consume-side story would not unblock 38.1 because no runtime artifact carries the 37.2a term set.
- RED established missing consume-side modules and an inactive reserved slot; GREEN reached 192 dependency/focused passes plus static/import fences.
- The authorized first-run-stands live attempt `7ed48f8a-0b01-4c80-a068-d2e152a5e8d6` exhausted the explicit 4096 completion-token ceiling entirely on provider reasoning and returned no parseable candidate. The durable journal remains `call_in_progress`; no retry occurred.
- Party-approved direct correction pinned Deep Dive alone to 32,000 completion tokens and bound that ceiling into the effective pre-handle model config identity; Scene/Promise remain at 4,096 and their base digest.
- The one authorized fresh post-fix attempt `b6fc76ea-94a2-4e51-bf04-ca626cb30ee0` used new shared outer/nested trial ID `15d265a9-0a33-4192-9e87-c731b4e60fcb`, new idempotency key `sha256:a0ac1ea3e7340f6650fb29fe499bf09b99f8e3b2d4e120925766470bf0de6fb6`, and no copied journal. It returned structured content, but strict candidate validation rejected duplicate bold-term metadata (`burnout`). Its journal remains `call_in_progress`; no additional call occurred.
- Party-approved Amendment 2 moved Deep Dive alone to the provider raw-JSON-schema path, bound schema/adapter/normalizer identity into the effective model-config digest, and added a deterministic normalizer that removes only exact repeated valid `bold_terms` entries while preserving unsafe variants for strict rejection.
- The final authorized fresh attempt `cd98f7e5-d89d-4a4c-ad22-83a584ac0617` used fresh shared outer/nested trial ID `929b5907-c2d1-48a2-a245-5fb7c046c10d` and idempotency key `sha256:8a5cd8811aa6bf06ee90c93733784ef441af1638226fafb42159dcb933745b79`. Its single `gpt-5` provider call completed in 58.45 seconds with 3,488 input and 6,609 output tokens at recorded cost $0.07045; the authored skeleton passed the 37.2a gate, exposed six nonempty terms, produced a ready demand, reconciled terminally, and replayed from the completed journal with zero additional provider calls.
- Governed trial `4cee7689-0f97-424b-bd6d-adfc9e63b37c` stopped at Irene Pass-1 because the model authored near-paraphrase `cannot rely on static training` instead of literal source text `We can no longer rely on static training.` The exact validator correctly rejected it. The four-seat 2026-07-14 correct-course party unanimously approved Amendment 6: deterministic exact-span IDs/projection, crash-safe rejected-candidate evidence, truthful failed-attempt cost posture, and reconstructable preflight identity. No retry or new live authorization was granted.

### Completion Notes List

- Activated the existing `workbook-brief.v1` reserved Deep Dive slot while preserving the canonical digest of real legacy-null artifacts and the original two-item Scene/Promise receipt tuple.
- Added exact manifest/slide/Promise authority assembly, live/offline writer injection, atomic call journaling, idempotency/replay checks, null upgrade, and split-brain handling without graph, runner, manifest, node-order, or `07W.2`-`07W.4` changes.
- Added strict digest-bound Ask-A demand projection with exact-coordinate envelope/sidecar reconciliation and honest typed non-ready states.
- A unanimous targeted Winston/Murat amendment approved one reconciliation-only terminal change: the terminal now calls the canonical pure lesson-plan contribution-receipt builder; render and input behavior are unchanged.
- Final exact-current deterministic verification is green: 246 passed, 7 skipped; scoped Ruff, all 18 import-linter contracts, `git diff --check`, and all six immutable live-evidence hashes pass.
- The bounded live close bar is met by `_bmad-output/implementation-artifacts/evidence/deep-dive-38-3a-live-cd98f7e5/verdict.json`: all 12 checks pass, including exactly one provider call, authored/pass-valid skeleton, nonempty terms, ready demand, terminal reconciliation, completed journal, zero-recall replay, and prior-failure preservation. Exact-current Blind/Edge/Acceptance review is clean; Cora block-mode lockstep and Audra closure-artifact audit both pass.
- Historical close evidence above remains valid for its one-to-one substrate. The later clustered production run `c8f17a24-9b63-4e10-a5d7-6f2043bc9812` disproved the direct-final-ordinal assumption before Ask-A, so Story 38.3a is reopened under Amendment 3 and Story 38.1 remains in-progress behind it.
- Amendment 4 is deterministically complete and exact-current review-clean. Its single live confirmation `a28aa15a-fc80-46ae-b05a-09ac864829bb` exposed upstream duplicate-unit/nonliteral-anchor defects before Deep-Dive dispatch; Amendment 5 now owns that correction and authorizes no further live run yet.
- Amendment 6 corrects the remaining leaky deterministic neck exposed by trial `4cee7689-0f97-424b-bd6d-adfc9e63b37c`: Irene will select digest-bound source-span IDs and deterministic code will project literal authority before the unchanged independent validator. It also closes rejected-call forensics/cost and governed-preflight identity gaps. Implementation and review are authorized; a new live attempt is not.
- Amendment 6 task 1 GREEN: `pass1_source_span_catalog.py` builds a canonical path/digest/offset/text-bound catalog from authenticated sections, excludes cross-slide duplicate text, and projects only valid same-source ordered IDs. The witnessed exact sentence is selectable while its near-paraphrase is absent; 13 focused tests pass.
- Amendment 6 task 2 GREEN: Irene receives the digest-bound catalog, emits ordered stable IDs only, and deterministic code projects exact source bytes before the unchanged authority validator. Model-authored literals, unknown/stale IDs, and free-text repair paths fail closed. The full Irene suite passes 202 tests with 1 skip; the focused catalog/projection slice passes 16 tests and scoped Ruff is clean.
- Amendment 6 task 3 GREEN: `pass1-plan-authority.v2` binds the catalog digest plus ordered selected IDs, exact projected bytes, source identity, role, parent, and active/retired identity. It independently rebuilds the catalog before receipt emission. Legacy v1 remains readable against legacy plans but production refinement refuses it pre-provider instead of silently upgrading. Irene passes 210 tests with 1 skip; Amendment-5/6 authority passes 47 with 1 skip; downstream slide/package/workbook consumers pass 84 tests; scoped Ruff is clean.
- Amendment 6 task 4 GREEN: the generation lock now encloses a crash-safe Irene call journal. It commits exact request/model/catalog identity before dispatch, raw response and provider metadata before parsing, and result identity after artifact publication. Returned-but-rejected responses and completed calls replay with zero provider recall; thrown/unknown outcomes remain explicitly ambiguous and fail closed. The focused journal slice passes 3 tests, the full Irene suite passes 213 with 1 skip, and scoped Ruff is clean.
- Amendment 6 task 5 GREEN: local economics scans every Irene call journal and emits `irene-pass1-provider-attempts.v1.json`. Complete durable usage is priced and reconciled into the cost report even after candidate validation fails; missing usage and ambiguous dispatches are counted with explicit unavailable reasons; matching trace rows are not double-counted. The focused and existing economics regression set passes 16 tests and scoped Ruff is clean.
- Amendment 6 task 6 GREEN: governed runner starts now retain `preflight-input-identity.v1.json` with a canonical per-file path/size/SHA-256 manifest across runtime/config/prompt and selected source roots, excluding only the declared `state/config/runs` output namespace. `output-inventory.v1.json` records the run tree separately after execution. Mutation and reconstruction tests pass; the full runner suite passes 45 tests with 1 skip and scoped Ruff is clean.
- Amendment 6 task 7 GREEN: one 276-pass/2-skip matrix proves the witnessed near-paraphrase is unselectable; unknown, duplicate, reordered, stale, and cross-source IDs fail; temporal substitution fails; returned, crashed, ambiguous, replay, and generation-lock paths forbid unintended calls; failed-validation economics is retained; and run outputs cannot perturb immutable input identity.
- Amendment 7 deterministic GREEN: new Irene calls bind `irene-pass1-response-processor.v2` before dispatch. The processor rejects duplicate keys and every prefix/suffix/internal/root-shape variant except exactly one surplus final `}` after one complete top-level object; the legacy synthetic `unit-1` path is removed. A `candidate_decoded` journal state now binds raw-response digest, both processor identities, action, removed byte/offset, and canonical candidate digest before semantic validation. Reprocessing and completed replay are zero-call and receipt replacement/tampering fails closed.
- Amendment 7 compatibility/evidence GREEN: legacy processor-v1 journals remain independently valid for audit and economics but mismatch current runtime identity and cannot be resumed/upgraded. The frozen run's 34-file SHA-256 manifest is unchanged. Its external `NONPASSING/COUNTERFACTUAL` witness records the one-byte framing action, eight original unit IDs, source-ref counts, five research goals, and six workbook sections without publishing any run artifact.
- Amendment 7 first review round closed seven consolidated findings: completion now requires a preexisting `candidate_decoded` receipt; the sole allowance targets exactly the final non-RFC-whitespace `}`; NBSP and non-JSON constants fail; the receipt addresses the removed raw UTF-8 byte across leading whitespace/fences/non-ASCII; v1 economics and predispatch-v2 timing have direct witnesses; and an external 34-entry pre-change hash manifest makes frozen immutability independently reproducible.
- Amendment 7 focused GREEN: the Irene plus journal-economics suite passes `326 passed, 1 skipped`; the clean direct changed-file/dependency sweep passes `744 passed, 7 skipped`. The broader changed-file diagnostic additionally passes `813` tests and exposes only eight documented inherited failures outside Amendment 7 (four stale legacy package-builder authority fixtures and four older live-preflight tests). Scoped Ruff, compileall, all 18 import-linter contracts, and repository-wide `git diff --check` pass. The intentionally over-broad full-repository sweep is not a closure gate under the operator's no-harmonization boundary.
- Amendment 7 exact-current closure seal: after the seven first-round findings were patched, fresh Blind Hunter, Edge Case Hunter, and Acceptance Auditor reviews each returned `ZERO FINDINGS` on the same tree. Deterministic/static/adversarial readiness is complete. Story 38.3a remains `in-progress` only for one newly authorized fresh v2 governed live workbook attempt; the frozen v1 run remains immutable and nonpassing.
- Amendment 6 live-finding correction GREEN: raw source-file and transformed extracted-body identity are separately preserved and bound. The review patches additionally validate completed replay before artifact publication, reject same-path split source identity, recursively validate temporal-receipt relationships, and bind span offset length to exact text. Causal RED was 6 failures over 41 passes; exact-current deterministic GREEN is 670 passed/10 skipped with all static and architecture gates clean. No live call occurred.
- Amendment 6 closure-round-2 GREEN: current-v2 refinements now rejoin the prior plan/receipt to the newly authenticated catalog before any journal or provider action; rehashed stale authority produces zero calls. Receipt activity is canonical, active interstitials require active heads, and supplied plan cluster topology is independently revalidated. Causal RED was 3 failures/15 passes; exact-current deterministic GREEN is 674 passed/10 skipped with all static and architecture gates clean.
- Amendment 6 closure-round-3 GREEN: completed replay now accepts only the exact canonical reconstructed Irene output and exact result/cache shape before artifact publication or return. A rehashed forged graph-output field fails; valid replay remains zero-call. Exact-current deterministic GREEN is 675 passed/10 skipped with all static and architecture gates clean.
- Amendment 6 closure-round-4 GREEN: completed replay compares canonical JSON serialization rather than Python object equality, so JSON booleans cannot be substituted by equal-valued numbers. Exact-current deterministic GREEN is 676 passed/10 skipped with all static and architecture gates clean.
- Amendment 6 closure-round-5 GREEN: completed replay requires the exact three-field result identity and validates provider evidence against canonical normal/error/unsupported variants with type-strict nonnegative usage. Exact-current deterministic GREEN is 678 passed/10 skipped with all static and architecture gates clean.

- G2B live-finding correction GREEN: Irene node contributions now emit non-billable, node-coordinate journal-authority markers instead of fabricated provider spans. Zero or partial journal loss fails closed; the frozen run reconciles `04A`/`05`/`05B` exactly with zero Irene billable trace spans and exact `$0.8165095` total cost. Focused verification is 29 passed and fresh three-way review is clean. No retry occurred.

### File List

- `.gitattributes`
- `_bmad-output/implementation-artifacts/38-3a-research-packet-consume-side.md`
- `_bmad-output/implementation-artifacts/deferred-work.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-13.md`
- `_bmad-output/implementation-artifacts/evidence/deep-dive-38-3a-live-7ed48f8a/`
- `_bmad-output/implementation-artifacts/evidence/deep-dive-38-3a-live-b6fc76ea/`
- `_bmad-output/implementation-artifacts/evidence/deep-dive-38-3a-live-cd98f7e5/`
- `_bmad-output/implementation-artifacts/evidence/workbook-live-hil/30850735-dea3-4444-bc7b-513239eae55b/amendment-7-counterfactual.json`
- `_bmad-output/implementation-artifacts/evidence/workbook-live-hil/30850735-dea3-4444-bc7b-513239eae55b/frozen-run-sha256-manifest.v1.json`
- `_bmad-output/implementation-artifacts/evidence/workbook-live-hil/399bcd61-7779-4fa0-a592-186c3d4b4045/`
- `app/marcus/lesson_plan/deep_dive_from_run.py`
- `app/marcus/lesson_plan/deep_dive_provider_contract.py`
- `app/marcus/lesson_plan/prework_artifact.py`
- `app/marcus/lesson_plan/research_demand.py`
- `app/marcus/lesson_plan/pass1_source_span_catalog.py`
- `app/marcus/lesson_plan/planning_context.py`
- `app/marcus/lesson_plan/pass1_authority.py`
- `app/marcus/lesson_plan/pass1_call_journal.py`
- `app/marcus/orchestrator/workbook_prework_writers.py`
- `app/marcus/orchestrator/workbook_wiring.py`
- `app/marcus/orchestrator/production_runner.py`
- `app/specialists/workbook_producer/_act.py`
- `app/specialists/irene_pass1/_act.py`
- `app/runtime/economics.py`
- `app/specialists/_shared/figure_tokens.py`
- `scripts/utilities/run_deep_dive_38_3a_live_evidence.py`
- `scripts/utilities/marcus_spoc_live_test_runner.py`
- `tests/_helpers/pass1_catalog_response.py`
- `tests/integration/marcus/test_workbook_deep_dive_38_3a.py`
- `tests/integration/marcus/test_workbook_band_wiring.py`
- `tests/integration/marcus/test_workbook_brief_part2_36_4.py`
- `tests/integration/marcus/test_workbook_prework_writers_36_4.py`
- `tests/integration/runtime/test_irene_pass1_journal_economics_amendment6.py`
- `tests/scripts/test_run_deep_dive_38_3a_live_evidence.py`
- `tests/unit/scripts/test_marcus_spoc_live_test_runner.py`
- `tests/unit/marcus/lesson_plan/test_research_demand_38_3a.py`
- `tests/unit/marcus/lesson_plan/test_pass1_source_span_catalog_38_3a.py`
- `tests/unit/marcus/orchestrator/test_irene_trace_economics_authority.py`
- `tests/unit/specialists/shared/test_figure_tokens_dollar_percent.py`
- `tests/specialists/irene_pass1/test_pass1_source_span_projection_38_3a.py`
- `tests/specialists/irene_pass1/test_pass1_authority_amendment6.py`
- `tests/specialists/irene_pass1/test_pass1_call_journal_amendment6.py`
- `tests/specialists/irene_pass1/test_cluster_floor_act_consumption.py`
- `tests/specialists/irene_pass1/test_irene_pass1_lesson_plan_authoring.py`
- `tests/specialists/irene_pass1/test_irene_pass1_collateral_emission.py`
- `tests/specialists/irene_pass1/test_irene_pass1_cluster_emission.py`
- `tests/specialists/irene_pass1/test_pass1_llm_payload_strip.py`
- `tests/specialists/irene_pass1/test_planning_context_handoff.py`
- `reports/dev-coherence/2026-07-13-1315/check-pipeline-manifest-lockstep.PASS.yaml`
- `reports/dev-coherence/2026-07-13-1315/evidence/ca-38-3a.md`

## Change Log

- 2026-07-13: Drafted with BMAD party amendment to close the missing `07W.1` Deep-Dive-to-Ask-A demand handoff.
- 2026-07-13: Implemented the deterministic consume-side handoff and targeted single-source receipt amendment; retained in-progress after the no-retry live attempt failed at the 4096-token reasoning ceiling.
- 2026-07-13: Implemented party-approved Deep-Dive-only 32k/effective-config correction; deterministic gates remained green, but the one fresh post-fix call failed strict duplicate-bold-term validation, so no further call was made and the story remains in-progress.
- 2026-07-13: Implemented party-approved raw-schema/exact-duplicate-normalizer correction and captured a passing single-call live witness; verification is complete and the story remains in-progress only for mandatory review and closure.
- 2026-07-13: Closed after exact-current Blind/Edge/Acceptance zero-finding review, 246-pass regression matrix, Cora block-mode lockstep PASS, and Audra four-artifact closure PASS.
- 2026-07-13: Reopened by unanimous correct-course party after a live clustered 13-final/6-source deck proved final slide ordinals are not source-slide authority; approved immutable exact-anchor slide-authority-map correction, RED-first review, and one later fresh live witness.
- 2026-07-13: Implemented and review-closed Amendment 4 (Deep Dive 300 seconds, zero retries, digest-bound posture); its one governed live attempt stopped pre-provider on duplicate `u06` identity and a nonliteral `shape`/`shaping` anchor. Party-approved Amendment 5 moves strict rejection upstream and authorizes deterministic work only.
- 2026-07-14: Governed trial `4cee7689-0f97-424b-bd6d-adfc9e63b37c` froze on a new nonliteral Pass-1 anchor; unanimous John/Winston/Murat/Amelia correct-course consensus approved Amendment 6 deterministic source-span ID projection plus rejected-call and preflight-evidence truthfulness. No new live attempt is authorized.
- 2026-07-14: Corrected the live-exposed raw-vs-extracted digest integration defect, applied all four exact-current review patches, and reached 670-pass/10-skip dependency GREEN plus clean Ruff, compileall, 18-contract import-linter, and diff checks. Story remains in-progress pending fresh closure review and separately authorized live validation.
- 2026-07-14: Closed the second-order stale-v2 pre-dispatch and retired-parent temporal-authority findings; reached 674-pass/10-skip dependency GREEN plus clean static gates. No live call occurred; final exact-current closure review and fresh live authorization remain pending.
- 2026-07-14: Closed the final rehashed completed-output replay finding with full canonical reconstruction; reached 675-pass/10-skip dependency GREEN plus clean static gates. No live call occurred; exact-current zero-finding review and fresh live authorization remain pending.
- 2026-07-14: Closed the sealing review's JSON boolean/numeric type-confusion finding with canonical serialization equality; reached 676-pass/10-skip dependency GREEN plus clean static gates. No live call occurred.
- 2026-07-14: Closed completed result-identity extension and rehashed provider-evidence usage findings; reached 678-pass/10-skip dependency GREEN plus clean static gates. No live call occurred.
- 2026-07-14: Closed resolved run-ID coordinate splitting and impossible planning-coverage receipt states; reached 1760-pass/10-skip exact dependency GREEN plus clean static and architecture gates. No live call occurred; fresh exact-current three-way closure review remains pending.
- 2026-07-14: Exact-current Blind/Edge/Acceptance seal returned ZERO FINDINGS after round 15. Deterministic Amendment 6 is ready for the separately authorized governed live workbook attempt; no provider call occurred during the seal.
- 2026-07-14: Implemented Amendment 7 processor v2 and its digest-bound `candidate_decoded` receipt, retired current synthetic fallback behavior, preserved read-only v1 audit/economics, and banked a labeled external counterfactual with all 34 frozen-run hashes unchanged. Fresh three-way review remains before the next pre-live report; no provider call occurred.
- 2026-07-14: Closed seven consolidated first-round Amendment-7 findings and reached 326-pass/1-skip focused plus 744-pass/7-skip direct dependency GREEN, clean Ruff/compileall/18-contract import-linter/diff gates, exact 34-file frozen-hash proof, and fresh Blind/Edge/Acceptance `ZERO FINDINGS`. Ready for a new pre-live authorization decision; no provider call occurred.
- 2026-07-14: The fresh governed v2 run proved all three Irene calls and reached G2B, then exposed fabricated contribution-level Irene cost spans. Replaced them with non-billable node-coordinate markers, preserved zero/partial missing-journal fail-closed behavior, reconciled exact cost from the three journals, and closed two review findings with a fresh three-way zero-finding seal. The failed run remains frozen and was not retried.
- 2026-07-14: Governed trial `399bcd61-7779-4fa0-a592-186c3d4b4045` advanced through Storyboard A publication and high-confidence perception before a false Pass-2 figure contradiction on perceived `$ 5% GDP`. Amendment 8 corrected the shared deterministic token class, replayed the exact frozen evidence locally, and passed party plus mandatory adversarial review without retrying the run. Signed and leading-decimal percent handling remains separately deferred pre-existing debt.
