---
baseline_commit: d43eb53058403c9a2b3d1569044af138ba73ee13
---

# Story 38.3a: Research-packet consume side and 07W.1 demand handoff

Status: done

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

Three subsequent governed amendments are binding. First, a unanimous Winston/Murat reconciliation review authorized the terminal producer to call the canonical pure lesson-plan contribution-receipt builder; this is reconciliation-only and changes no terminal input or render behavior. Second, the two party-approved correct-course amendments in `sprint-change-proposal-2026-07-13.md` authorize Deep-Dive-only 32,000 completion tokens and the raw-JSON-schema adapter with `deep-dive-provider-normalizer.v1`. That normalizer may remove only later exact duplicates of independently strict-valid `{term: <string>}` metadata; it preserves the first occurrence/order, never trims, case-folds, Unicode-normalizes, or repairs any other value, and binds raw/normalized payloads, schema, records, and version into the journal/config identity. Third, the closure party (John, Winston, Amelia, and Murat; unanimous Option B) clarified the closed-authority boundary below: thin-but-valid authority persists typed output, while total required-authority absence is structurally unrepresentable by Story 37.2a and fails before any current brief write. These amendments supersede the conflicting terminal scope sentence, blanket strict-candidate wording, and blanket missing-authority persistence wording only.

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

### Review Findings

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

### Completion Notes List

- Activated the existing `workbook-brief.v1` reserved Deep Dive slot while preserving the canonical digest of real legacy-null artifacts and the original two-item Scene/Promise receipt tuple.
- Added exact manifest/slide/Promise authority assembly, live/offline writer injection, atomic call journaling, idempotency/replay checks, null upgrade, and split-brain handling without graph, runner, manifest, node-order, or `07W.2`-`07W.4` changes.
- Added strict digest-bound Ask-A demand projection with exact-coordinate envelope/sidecar reconciliation and honest typed non-ready states.
- A unanimous targeted Winston/Murat amendment approved one reconciliation-only terminal change: the terminal now calls the canonical pure lesson-plan contribution-receipt builder; render and input behavior are unchanged.
- Final exact-current deterministic verification is green: 246 passed, 7 skipped; scoped Ruff, all 18 import-linter contracts, `git diff --check`, and all six immutable live-evidence hashes pass.
- The bounded live close bar is met by `_bmad-output/implementation-artifacts/evidence/deep-dive-38-3a-live-cd98f7e5/verdict.json`: all 12 checks pass, including exactly one provider call, authored/pass-valid skeleton, nonempty terms, ready demand, terminal reconciliation, completed journal, zero-recall replay, and prior-failure preservation. Exact-current Blind/Edge/Acceptance review is clean; Cora block-mode lockstep and Audra closure-artifact audit both pass.

### File List

- `.gitattributes`
- `_bmad-output/implementation-artifacts/38-3a-research-packet-consume-side.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-07-13.md`
- `_bmad-output/implementation-artifacts/evidence/deep-dive-38-3a-live-7ed48f8a/`
- `_bmad-output/implementation-artifacts/evidence/deep-dive-38-3a-live-b6fc76ea/`
- `_bmad-output/implementation-artifacts/evidence/deep-dive-38-3a-live-cd98f7e5/`
- `app/marcus/lesson_plan/deep_dive_from_run.py`
- `app/marcus/lesson_plan/deep_dive_provider_contract.py`
- `app/marcus/lesson_plan/prework_artifact.py`
- `app/marcus/lesson_plan/research_demand.py`
- `app/marcus/orchestrator/workbook_prework_writers.py`
- `app/marcus/orchestrator/workbook_wiring.py`
- `app/specialists/workbook_producer/_act.py`
- `scripts/utilities/run_deep_dive_38_3a_live_evidence.py`
- `tests/integration/marcus/test_workbook_deep_dive_38_3a.py`
- `tests/integration/marcus/test_workbook_band_wiring.py`
- `tests/integration/marcus/test_workbook_brief_part2_36_4.py`
- `tests/integration/marcus/test_workbook_prework_writers_36_4.py`
- `tests/scripts/test_run_deep_dive_38_3a_live_evidence.py`
- `tests/unit/marcus/lesson_plan/test_research_demand_38_3a.py`
- `reports/dev-coherence/2026-07-13-1315/check-pipeline-manifest-lockstep.PASS.yaml`
- `reports/dev-coherence/2026-07-13-1315/evidence/ca-38-3a.md`

## Change Log

- 2026-07-13: Drafted with BMAD party amendment to close the missing `07W.1` Deep-Dive-to-Ask-A demand handoff.
- 2026-07-13: Implemented the deterministic consume-side handoff and targeted single-source receipt amendment; retained in-progress after the no-retry live attempt failed at the 4096-token reasoning ceiling.
- 2026-07-13: Implemented party-approved Deep-Dive-only 32k/effective-config correction; deterministic gates remained green, but the one fresh post-fix call failed strict duplicate-bold-term validation, so no further call was made and the story remains in-progress.
- 2026-07-13: Implemented party-approved raw-schema/exact-duplicate-normalizer correction and captured a passing single-call live witness; verification is complete and the story remains in-progress only for mandatory review and closure.
- 2026-07-13: Closed after exact-current Blind/Edge/Acceptance zero-finding review, 246-pass regression matrix, Cora block-mode lockstep PASS, and Audra four-artifact closure PASS.
