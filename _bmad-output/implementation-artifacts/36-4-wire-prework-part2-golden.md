---
baseline_commit: dab32211699e6c294d8fb259e9537b6c18653598
---

# Story 36.4: Wire pre-work into 07W.1 and terminal workbook — Part-2 golden

Status: done

## Story

As the Marcus-SPOC workbook runtime,
I want the source-grounded Scene, deterministic Friction Scale, and ratified-LO Promise persisted at `07W.1` and rendered through the canonical workbook path,
so that a real Part-2 run produces a presentation-support Markdown and DOCX workbook with honest gates, delivery-mode parity, and none of the prohibited proofing payload.

## Dependency and Epic-Close Position

`38.0 -> 38.3b -> 36.1 -> {36.2 || 36.3} -> 36.4`

All predecessors are done. Story 36.4 is the Epic-36 integration/close node. It does not unlock later DAG work until mandatory review/remediation, Cora/Audra closure, bounded live Part-2 evidence, and Epic-36 close are complete.

## Binding Integration Decisions

1. **Real coordinate:** transition `07W.1` from legacy `workbook_brief_stub` to `specialist_id="workbook_brief"`. A legacy stub contribution at `07W.1` is non-authoritative and may be replaced once; an existing real `workbook_brief@07W.1` is idempotent and may never be overwritten or duplicated.
2. **Uninterrupted handoff:** `07W.1` atomically persists `<run_dir>/workbook-brief.v1.json`. The terminal `07W` reads that strict sidecar, not a potentially stale mid-walk `run.json`. The corresponding contribution output carries the exact relative path, digest, schema version, status summary, and coordinate.
3. **Extensible payload, narrow semantics:** the versioned payload contains required `pre_work` and a reserved optional `deep_dive_skeleton=None`. Story 36.4 must not author or interpret the reserved field; Story 37.2a owns it.
4. **Explicit runtime context:** the factory receives a strict `WorkbookBriefRuntimeContext` containing `run_dir`, explicit resolved `course_source_root`, `encounter_mode`, injected Scene/Promise writers, and writer execution evidence. Never repo-global-search or infer delivery mode from course names. Legacy missing encounter mode may default only to `recorded` with `encounter_mode_defaulted_recorded` loss/WARN; new contexts are strict.
5. **Two evidence axes:** `encounter_mode` (`recorded|live`) describes the learner encounter. It is not `RunState.llm_execution_mode` and does not prove a live model call. Writer execution evidence separately records `offline_stub|live`.
6. **Presentation-support render profile:** production `07W` selects a closed `presentation_support` profile. Legacy direct callers retain an explicit legacy default until migrated. No content branch may use course name or encounter mode.
7. **Persisted ingress:** new starts accept `course_source_root` and `encounter_mode` through the Marcus-SPOC/trial start surface and persist data-only `<run_dir>/workbook-runtime-context.v1.json` before walking. Continue/recover reconstruct from that artifact and reject conflicting overrides. Writer objects are instantiated from persisted config at runtime, never serialized.
8. **Legacy context discriminator:** absence of the runtime-context artifact identifies a pre-36.4 run. On first `07W.1` re-entry, persist `context_origin="legacy_default"`, `encounter_mode="recorded"`, `course_source_root=null`, and visible compatibility losses. It may render only honest unavailable pre-work unless the operator supplies the missing root through the explicit migration command; never guess.
9. **Digest domain:** `WorkbookBriefArtifactV1` is an envelope of `payload` plus `payload_digest`. Digest input is canonical JSON of `payload` only (`sort_keys=True`, separators `(',', ':')`, `ensure_ascii=False`, UTF-8, no trailing newline). The file may end in one newline; the digest excludes envelope/digest/newline. Contribution and reader compare this exact `payload_digest`.

## Acceptance Criteria

1. **Strict versioned workbook-brief artifact**
   - Add frozen/extra-forbid lesson-plan contracts for `WorkbookBriefArtifactV1`, `WorkbookBriefRuntimeContext`, encounter mode, writer execution mode, gate/warning summaries, and artifact receipt.
   - Artifact payload fields include exact schema/version, node/specialist coordinates, `PreWorkBrief`, complete Scene/Promise receipts, selected seed/ref/classification, Promise authority refs, encounter mode, writer execution evidence, deduped warnings/losses, reserved `deep_dive_skeleton=None`; its envelope carries the binding `payload_digest` defined above.
   - Aggregate invariants reconcile nested statuses/losses/refs. JSON strict round-trip and canonical digest are pinned. Authored sub-results cannot coexist with failure claims.
   - Atomic write + M3-safe reader verify schema, coordinate, digest, and reserved-field posture. Present corrupt/mismatched data fails loud; no arbitrary dict fallback.

2. **Real `07W.1` composition and idempotency**
   - Replace only the `07W.1` stub factory with a real factory that uses the explicit runtime context, reuses `SceneProjectionRequest.from_raw_candidates`/`compose_scene_projection`, `resolve_promise_objectives`/`compose_promise_projection`, and aggregates the existing strict `PreWorkBrief`.
   - Eligible Part-2 calls each injected writer exactly once. Pre-gate failures call the respective writer zero times. One beat may honestly degrade without manufacturing prose for it.
   - Unexpected writer/factory/persistence errors become tagged recoverable `SpecialistDispatchError` at `07W.1`. Contract-defined degradation persists honest output.
   - Existing real contribution + valid matching sidecar resumes without writer calls. Real contribution + missing/corrupt/mismatched sidecar fails loud.
   - Legacy stub history is retained but non-authoritative; after re-entry the envelope contains at most one legacy stub and exactly one real contribution. A serialized run already positioned after `07W.1` with only the stub must error-pause at `07W` with `workbook-brief.legacy-reentry-required`; operator recovery explicitly targets `07W.1`. No automatic pre-terminal migration or silent overwrite. Repeated recovery/resume is idempotent.
   - `07W.2`, `07W.3`, and `07W.4` stubs/semantics remain byte-unchanged.

3. **Real source adapter and non-vacuous Part-2 authority**
   - Add one deterministic run-source adapter using only the explicit `course_source_root` and run artifacts. It normalizes eligible assessment scenarios first, then slide narration/body; never model priors or repo-wide guessing.
   - The Part-2 primary Scene seed resolves to the actual Chapter-2 Q5 scenario in `course-content/courses/tejal-apc-c1-m1-p2-trends/assessments/chapter-2-knowledge-check.md`; payoff targets resolve to actual Part-2 slide files; the independent forbidden span resolves from that source's Correct Answer.
   - Exact source paths/anchors/spans are integrity-tested. Missing root/path/anchor yields honest unavailable/degraded evidence; fabricated coordinates cannot pass by self-declaration.
   - Promise authority remains the exact-byte `ratified-los.json` path/digest contract from 36.3. No unresolved-objective fallback supplies Promise prose.

4. **Both runner walks and pipeline lockstep**
   - Extend the workbook-band hook/factory signature with keyword-only runtime context and pass the same resolved context at both production-runner walk sites.
   - Start, continuation, recover/error, and serialized-resume tests prove identical arguments, exact-once `07W.1`, sidecar availability before `07W`, and recoverable error pause.
   - `workbook_wiring.py` and `production_runner.py` are existing trigger paths: run the pipeline-lockstep regime, manifest checker, composition-topology tests, and v4.2-lineage witness. No node/edge/order/config/event/pack-version change is authorized.
   - Add strict start ingress for `course_source_root` and `encounter_mode` to the Marcus-SPOC/trial start path **only when the resolved composed graph contains the workbook band / `07W.1`**. Persist `workbook-runtime-context.v1.json` before that workbook-selected run walks, using a contained existing directory and resolvable source root. Continue/recover enforce it only for persisted/composed workbook runs; supplied overrides must byte/enum-match or fail. Path must resolve, exist, be a directory, and remain under the workspace/course-content authority root unless an operator-explicit external-root allowance already exists.
   - Workbook-selected new-start missing root/mode is rejected at ingress. A non-workbook start that supplies workbook-only options is rejected as an invalid option combination and does not persist the context artifact. Existing deck-only and motion-only start/continue/recover behavior remains byte/behavior compatible and is regression-tested.
   - Only the explicit pre-36.4 **legacy workbook** migration path may carry `course_source_root=null`; supplying a root writes a migrated context with `context_origin="operator_migrated"` before re-entry. `WorkbookBriefRuntimeContext.course_source_root` is nullable only when `context_origin="legacy_default"`; `new_start` and `operator_migrated` require a resolved directory.

5. **Canonical front-matter render**
   - Extend strict `WorkbookInputs`, `WorkbookProducer.produce`, and `compose_workbook` to consume the validated artifact and render one pre-work front-matter region before Overview.
   - Render Scene -> Friction Scale -> Promise exactly once. Markdown remains canonical and DOCX derives from the same `_ComposedDoc`/block model; no text splice after Markdown render and no parallel DOCX path/dependency.
   - Avoid nested-heading corruption: the canonical model carries proper heading/body blocks, and parsed DOCX contains headings/bullets rather than raw Markdown tokens.
   - Degraded/unavailable beats show existing honest markers; detailed losses/warnings stay in receipt/sidecar rather than fabricated learner prose.

6. **FR17 presentation-support cut**
   - Under the production `presentation_support` profile, omit from both canonical Markdown and DOCX: `Transcript-narrative`, `Transcript of Record`, Figures/slide screenshots or embedded slide media, and key-figures/claim-table blocks. Update stale Overview copy claiming they are included.
   - Raw narration may remain internal input for later Deep-Dive/fidelity work but may not render. Existing deck figures remain deck assets, not DOCX relationships/media.
   - Negative tests inspect MD headings/body plus DOCX paragraphs, relationships, and media—not merely source block names.
   - Do not retain hidden transcript to satisfy legacy AC-5 segment coverage or AC-8 superset/depth. Under `presentation_support`, legacy segment coverage returns a typed `not_applicable_pre_deep_dive` receipt with claim fence `No transcript-segment completeness claim until Story 37.2a supplies traceable read-prose`; it is neither PASS nor FAIL and cannot be summarized as coverage. The superset/depth gate evaluates only actual remaining read-prose and records honest unavailable/degraded evidence when none exists. Story 37.2a owns reactivation against the Deep Dive.

7. **Encounter-mode parity**
   - Closed `encounter_mode` values are `recorded` and `live`. Mode controls only one deterministic encounter-label line: recorded `Before you watch the recorded presentation`; live `Before the live presentation`.
   - Mode never enters Scene/Promise semantic requests, source/LO selection, gates, status, section order, or contribution digest other than its explicit provenance/label field.
   - With identical semantic artifact, normalized Markdown differs exactly in the label line; parsed DOCX paragraph model differs exactly in that text node. Headings, styles, paragraph order, media/relationships, gates, refs, and semantic payload are identical.
   - Unknown mode fails strict. Legacy missing mode defaults to recorded only with visible `encounter_mode_defaulted_recorded` compatibility loss/WARN.

8. **Part-2 structural golden and gate taxonomy**
   - Byte-pin deterministic portions only: heading/order shell, full Friction Scale copy, encounter label, and canonical serialized receipts excluding declared volatile metadata.
   - Leashed Scene/Promise prose is never byte-goldened. Structural/gate assertions pin: real Q5 selected seed/ref; `fresh_pain -> external_friction`; payoff proxy PASS; Scene provenance/faithfulness clean; Promise IDs/cardinality/order equal authority; required posture delivered; no unresolved placeholder; numeral gate clean; Q5 answer copy WARNs while a capability vow does not false-positive.
   - Markdown headings occur once/in order; vows map 1:1; parsed DOCX carries the same semantic order/text with no raw Markdown artifacts.
   - Fixture separates structured inputs, deterministic expected receipt, semantic assertion manifest, and any recorded-live writer response. Never bless a whole LLM-authored workbook blob.

9. **Artifact fidelity, persistence, and terminal sidecar**
   - A frozen Part-2 run produces nonempty `.md` and valid `.docx` under a contained output root. Terminal sidecar/RunState refs include both plus workbook-brief path/digest/status/warning summary.
   - Parse DOCX for exact heading order, three beat bodies, deterministic instrument, mode label, and FR17 absences. Existence-only is insufficient.
   - Persist/reload `ProductionTrialEnvelope`; resumed `07W` consumes the same serialized brief and yields semantically identical artifacts/receipts. Normalize unavoidable DOCX container metadata; do not require ZIP-byte identity.
   - Terminal `07W` remains model-free; AST/import tests prohibit provider/model clients and orchestrator imports from lesson-plan/terminal consumer layers.

10. **Gate taxonomy and operator spot-checks**

   | Gate | Disposition | Witness |
   |---|---|---|
   | missing brief contribution/source/seed/objective substrate | FAIL-to-author -> unavailable | automated |
   | ambiguous type, unsupported scope, payoff/provenance/faithfulness failure | FAIL-to-author -> degraded | automated |
   | Promise authority/mapping/structure/placeholder/numeral failure | FAIL-to-author -> degraded | automated |
   | corrupt sidecar/run authority, invalid factory output, writer exception, render/write failure | fail-loud -> recoverable `07W.1`/`07W` pause | automated |
   | actual payoff sufficiency / Scene semantics beyond proxy | WARN | operator spot-check |
   | LO-vow fidelity, pertinent ability, half-rhyme, mastery overclaim, true no-spoiler | WARN | operator spot-check |
   | thin/gap adequacy, word-digit equivalence, negation scope | WARN | automated receipt + operator |
   | exact Scene/Promise wording | no gate / never byte-match | structural gates only |

   Sidecar preserves WARNs without presenting them as PASS claims.

11. **Offline and bounded live evidence**
   - Offline close battery: real Part-2 sources/ratified authority with injected authored writers; both runner walks; exact-once/resume/error; sidecar reader; terminal consumer; MD+parsed DOCX; encounter parity; FR17 negatives; all 36.1–36.3 tests; workbook producer/generalization/remediation suites; topology/manifest lockstep; Ruff/diff check.
   - Add named orchestrator adapters in `app/marcus/orchestrator/workbook_prework_writers.py`: `LiveSceneComposer` and `LivePromiseTransformer`. Each loads the existing pinned `07W.1` workbook-writer model config through the established model-config/client resolver, issues one structured-output provider call, validates into the closed `SceneBrief`/`PromiseProjection` contract, and then re-enters 36.2/36.3 gates. The terminal producer imports none of this.
   - Mandatory bounded live witness: one real `07W.1` node/factory execution on Part-2, containing exactly **two provider calls** (one Scene, one Promise; never combine contracts merely to reduce count), followed by deterministic `07W` render to real MD+DOCX. Record model/config digest, request IDs when supplied, latency, token/cost evidence, per-call timeout, and total bounded spend. First-run-stands; do not retry-to-green.
   - Record operator prose spot-check verdicts for provenance, actual payoff, semantic faithfulness, pertinent ability, LO fidelity, half-rhyme, mastery overclaim, and no-spoiler. Any MUST failure blocks story/Epic close.
   - `encounter_mode="live"` is not live-model evidence. A full paid Marcus-SPOC traversal remains the overall Epics 36–40 close gate, not Story 36.4's bounded witness.

12. **Epic 36 close and scope fence**
   - Mandatory fresh dev, three-layer code review/remediation, Cora block-mode/lockstep verification, Audra closure, bounded live witness, and operator spot-check all PASS before Story 36.4 and Epic 36 move to done.
   - Story owns only pre-work artifact/composition/front matter, presentation-support FR17 cut, encounter parity, and Part-2 evidence.
   - It must not implement DeepDiveWriter/skeleton, Review beats, Ask-A/B, `07W.2/.3/.4` semantics, research, glossary/trends promotion, Cover, HUD/events, or any proofing-only accommodation.

## Tasks / Subtasks

- [x] Define strict workbook-brief artifact/runtime-context/receipt contracts and M3-safe atomic reader/writer (AC: 1, 7, 9-10)
- [x] Implement explicit-root Part-2 source adapter with real Q5/payoff/answer integrity (AC: 2-3, 8)
- [x] Replace legacy 07W.1 stub with real exact-once factory and reserved future payload field (AC: 1-4, 12)
- [x] Thread identical runtime context through both runner walks and error/recover/resume paths (AC: 2, 4, 9)
- [x] Extend terminal inputs/canonical composition for pre-work front matter and strict sidecar consumption (AC: 5, 9)
- [x] Add presentation-support render profile and substantive FR17 removals (AC: 6)
- [x] Add recorded/live encounter label and semantic parity tests (AC: 7)
- [x] Add Part-2 structured golden, sidecar, runner, terminal, MD/DOCX, negative, and regression evidence (AC: 1-10)
- [x] Run lockstep/topology, focused regression, Ruff, and diff checks (AC: 4, 11)
- [x] Execute first-run-stands bounded live Part-2 07W.1->07W witness and operator spot-check (AC: 11)
- [x] Complete mandatory review/remediation, Cora/Audra closure, and Epic-36 close ledger (AC: 12)

## Authorized Scope

- `app/marcus/lesson_plan/prework_projection.py` additive artifact/encounter contracts if needed
- New `app/marcus/lesson_plan/prework_artifact.py` and/or `prework_from_run.py`
- `app/marcus/lesson_plan/scene_extraction.py` and its Story-36.2 regression tests, only under the live-defect scope amendment below
- `app/marcus/orchestrator/workbook_wiring.py`
- `app/marcus/orchestrator/production_runner.py` only for identical context injection at both existing call sites
- New `app/marcus/orchestrator/workbook_prework_writers.py` for the two live structured-output adapters
- Marcus-SPOC/trial start, continue, recover, and explicit legacy-migration call surfaces required to ingest/persist/reconcile workbook runtime context
- Existing pinned workbook-writer model config only if required without model-value drift
- `app/specialists/workbook_producer/_act.py`
- `app/marcus/lesson_plan/workbook_producer.py`
- Focused unit/integration/workbook producer tests and `tests/fixtures/prework_36_4/**`
- Evidence driver/artifacts, story, sprint ledger, Epic-36 status/retrospective

No manifest topology/order/config change, new events, `07W.2/.3/.4` semantics, research packets, DeepDive/Review, glossary/trends, Cover, HUD, unrelated course assets, or proofing-only behavior.

### Live-defect scope amendment — Scene authority (ratified at closure)

The bounded live evidence surfaced product defects inside the closed Story-36.2 Scene authority: the writer lacked the deterministic faithfulness constraints, the Part-2 Q5 seed included its question/answer tail, diagnostic completion could leak a resolution, and generic lexical novelty was initially over-promoted from operator WARN to automatic failure. These defects directly affected the Marcus-SPOC production workbook and were fixed on product merits, not to accommodate a proofing vehicle.

Story 36.4 therefore explicitly authorizes the narrow corrective changes in `app/marcus/lesson_plan/scene_extraction.py` and `tests/unit/marcus/lesson_plan/test_prework_projection_36_2.py`: expose the existing gate's prompt constraints; carry setup-only/forbidden-resolution inputs; keep answer-overlap and diagnostic completion as FAIL-to-author; preserve overlap/numeral/negator gates; and record non-diagnostic introduced terms as the original semantic operator WARN. No threshold was loosened to bless a failed attempt, and every change is mutation-tested against the leaked live sentences plus valid near-extractive controls. The immutable failed packs and adjudications remain evidence of the pre-fix behavior.

## Existing Seams to Reuse

- `scene_extraction.py` and `promise_projection.py` are semantic authorities; reuse them rather than forking their gates. The only authority changes permitted here are the ratified live-defect corrections above.
- `prework_projection.py::render_prework_markdown` is the deterministic beat renderer; canonical workbook blocks must preserve its semantics.
- `workbook_wiring.run_workbook_band_node` owns exact-coordinate idempotency/error normalization.
- `production_runner.py` contains two mirrored workbook-band walk sites; both must stay parallel.
- `workbook_producer.py` owns canonical `_ComposedDoc` -> Markdown/DOCX.
- `app/specialists/workbook_producer/_act.py` remains deterministic/model-free and reads only lesson-plan contracts/run artifacts.

## Dev Agent Record

### Agent Model Used

GPT-5 Codex (Amelia developer workflow)

### Debug Log References

- RED: new 36.4 tests initially failed on absent `prework_artifact` and `prework_from_run` modules.
- Focused offline close battery: 239 passed, 1 skipped in 18.89s.
- Pipeline manifest lockstep: exit 0; PASS trace `reports/dev-coherence/2026-07-13-0142/check-pipeline-manifest-lockstep.PASS.yaml`.
- Ruff changed-file check and `git diff --check`: PASS.
- Legacy migration/re-entry follow-up smoke: 20 passed in 11.36s; lockstep exit 0 (`2026-07-13-0147` PASS trace).
- Mandatory review remediation battery: 254 passed, 2 skipped in 20.73s; post-format changed-scope smoke 93 passed, 1 skipped in 16.65s; Ruff/diff clean; lockstep exit 0 (`2026-07-13-0202` PASS trace).
- Final offline remediation battery: 255 passed, 2 skipped in 20.56s; post-format focused smoke 32 passed, 1 skipped; Ruff/diff clean; lockstep exit 0 (`2026-07-13-0209` PASS trace).
- Final integrated-evidence battery: 257 passed, 2 skipped in 23.15s; targeted acceptance 17 passed in 14.29s; Ruff/diff clean; lockstep exit 0 (`2026-07-13-0216` PASS trace).
- Bounded-driver/scope-hygiene smoke: 18 passed in 14.43s; Ruff/diff clean; lockstep exit 0 (`2026-07-13-0222` PASS trace). No provider call and no live-attempt pack created.
- First bounded live attempt is immutably recorded at `evidence/prework-36-4-live-20260713T022531Z-12ccd755/` (attempt `12ccd755-592b-45c2-8fd2-b3fbe51df2b9`) with `pass=false`: the provider returned a mixed Scene shape (`status=authored` plus losses/marker). The failed pack was not modified.
- Post-failure local remediation smoke: 6 passed; live writer and recovery-driver Ruff checks passed. No recovery/live provider execution was performed.
- Recovery P0 preflight battery: 9 passed; labeled recovery dry-run passed with zero provider calls and no evidence pack; Ruff/diff/lockstep passed. The preventive bound prices two calls at configured-model input/output ceilings before adapter construction.
- Final recovery safety battery: 14 passed, including parameterized CLI rejection of NaN, positive/negative infinity, zero, and negative caps before pack/adapter/provider construction; Ruff and diff checks passed. No provider call or evidence pack was created.
- Second-attempt adjudication remediation: 72 focused Scene-gate/writer/driver tests passed. The original `380ecd47` pack remains unchanged; separate adjudication hashes it and records machine transport/render PASS but semantic/operator FAIL. No provider call was made.
- Fresh-clone safety remediation: 20 focused driver/writer tests passed. A manifest-bound production-shaped pre-07W.1 clone was created separately and the actual labeled `380ecd47` dry-run passed with zero calls and no pack.
- Third live-defect offline remediation: original `5ff7db47` pack preserved byte-for-byte; separate digest-bound adjudication records machine PASS/operator semantic FAIL. Setup-only Q5 authority, Scene-innocence gate, pending-operator evidence semantics, and third recovery chaining were added without a provider call.
- Evidence-state P0 validation: 91 focused tests passed; 172 broad relevant tests passed with 1 skipped; Ruff/diff/lockstep clean. Mutation coverage rejects every missing/extra check, wrong story/attempt/path/digest, and PENDING/FAIL mutation for PASS adjudication. No clone or live call was created.
- Final adjudication P0 adds a non-overridable machine-green prerequisite beneath operator PASS: exact pending tri-state, machine transport and primary acceptance true, no error key, two receipts/calls, artifact digest/paths, and all machine assertions true. Missing or failed machine evidence cannot be operator-overridden; finalized FAIL recovery semantics remain intact.
- Prepared a new separate manifest-bound pre-07W.1 clone for labeled recovery of `5ff7db47-62af-48d0-8b67-fa300c04aa4d`; exact dry-run passed with zero calls and no pack. Bound output `_bmad-output/artifacts/workbooks-36-4-recovery-5ff7db47` remains unused. No live run was executed.
- Fourth-attempt remediation preserves `b90fb3f6` unchanged and records a separate exact nine-check FAIL adjudication. Invented Scene terms now remain authored as `scene_invented_terms_operator_check` with introduced-term receipt evidence; forbidden-resolution overlap and diagnostic completion remain automatic failures. No recovery clone or live run was created.
- Prepared a new separate manifest-bound pre-07W.1 clone for labeled recovery of adjudicated `b90fb3f6-8951-4dcc-abff-66036576d89f`; exact dry-run passed with zero calls/no pack. Bound output `_bmad-output/artifacts/workbooks-36-4-recovery-b90fb3f6` remains unused; no live run was executed.
- Final `ba470ff2` evidence is machine-green/pending by construction and separately adjudicated `9/9 PASS`; `operator_adjudication_state` returns `pass`. Known recorded cost across the four receipt-bearing attempts is `$0.12621750` (the first parse-failure pack has no complete receipt cost). DOCX structural evidence passes; visual page rendering is explicitly not claimed because `soffice` was unavailable.
- Final closure-artifact validation: broad relevant battery 189 passed, 1 skipped; operator predicate/driver battery 44 passed; Ruff/format/diff clean; Cora BLOCK lockstep PASS trace `reports/dev-coherence/2026-07-13-0325/check-pipeline-manifest-lockstep.PASS.yaml`. No live call, staging, commit, or status promotion was performed.
- Broader topology command included five pre-existing environment-dependent `test_real_cd_graph_walk_pin.py` preflight failures (`openai`/HUD health); unaffected focused topology/manifest tests remained green.

### Completion Notes List

- Added strict payload-only canonical digest envelope, atomic sidecar/runtime-context persistence, reserved `deep_dive_skeleton=None`, and strict reader failure posture.
- Replaced `workbook_brief_stub@07W.1` with real `workbook_brief@07W.1`, exact-coordinate idempotency, sidecar reconciliation, real Part-2 Q5/payoff/answer source resolution, and 36.2/36.3 gate reuse.
- Threaded reconstructed context through both production-runner walks and added strict workbook-only start ingress.
- Added operator-facing `trial recover --course-source-root ... --encounter-mode ...` migration: legacy-workbook-only, `operator_migrated`, idempotent exact-match, conflict/real-context/non-workbook rejection, automatic `07W.1` re-entry, and retained legacy-stub history.
- Added `LiveSceneComposer` and `LivePromiseTransformer` over the pinned workbook-writer config; offline tests prove one structured call each without invoking a provider.
- Review remediation added digest-bound Scene classification/gate/extraction receipts, Promise gate/authority receipts, per-writer call/model/config/request/latency/token/cost receipts, aggregate validators, and honest contribution model identity.
- Terminal 07W now requires and exactly reconciles the real `workbook_brief@07W.1` contribution before presentation-support activation; legacy-only, planted, missing, corrupt, and receipt-mutation states error-pause with stable tags.
- Centralized persisted source-root and child containment, hardened atomic writes against planted temp/target symlinks, limited live-writer construction to 07W.1, and made missing/thin source substrate an honest zero-call unavailable result.
- Bounded payoff targets now name the relevant leadership-gap slide while retaining a distinct full inventory and deterministic slide-body fallbacks.
- DOCX projection now renders list/bold/heading semantics without raw Markdown; FR17 tests inspect paragraphs, relationships, and media, and recorded/live parity differs at exactly one label in both MD and DOCX.
- Existing real 07W.1 contributions now always require a sidecar and full receipt match, including blank/missing artifact paths. Writer calls are measured wrappers rather than inferred; live structured output retains raw request/usage/cost metadata with an explicit unavailable reason only when needed.
- Added separated `tests/fixtures/prework_36_4/` structured input, deterministic receipt shell, and semantic assertion manifest; presentation-support copy now explicitly fences Deep Dive/read-prose until 37.2a.
- Added executable no-pre-band-gate start-walk and continuation-walk witnesses that capture equivalent persisted runtime-context identity and prove the brief sidecar exists after 07W.1.
- Added an integrated serialized-authority terminal witness that loads all three separated fixtures, reloads `ProductionTrialEnvelope`, invokes the actual 07W producer, parses real MD+DOCX, and checks beat order/text, receipt refs, terminal artifact refs, depth fence, and FR17 negatives.
- Added `run_prework_36_4_live_evidence.py`, a bounded first-run-stands driver with explicit course/run/output inputs, credential/config/authority preflight, exactly-two-call enforcement, spend cap, real 07W.1 plus deterministic terminal 07W, parsed artifact assertions, immutable evidence pack, operator spot-check template, and a non-consuming `--dry-run`.
- Hardened both live structured-writer prompts with exact authored-vs-degraded cross-field invariants and request-specific Scene/Promise facts. Added strict malformed-shape coverage and established-pricing calculation from actual model/token usage when the provider omits cost.
- Recovery attempts now require `--recovery-of 12ccd755-592b-45c2-8fd2-b3fbe51df2b9` (or another existing `pass=false` attempt), refuse an unlabeled/unknown second attempt, create a new immutable pack, and record the chained causal-fix evidence in the new verdict.
- Replaced dirty-worktree-sensitive diff evidence with an allowlisted causal-fix manifest over current bytes (including untracked remediation files): per-file repo-relative SHA-256, canonical aggregate digest, named cause/fix, base commit, and prior failed-verdict path/SHA-256. Unrelated dirty files cannot change the manifest.
- Made the spend cap preventive: preflight loads the configured model and pricing-table digest, enforces bounded serialized inputs, prices two calls at the fixed input ceiling and enforced `max_completion_tokens`, and rejects an insufficient CLI cap before pack or adapter creation. The post-call actual-cost assertion remains.
- The spend preflight now also requires a finite value strictly greater than zero, closing IEEE-754 NaN/infinity and nonpositive bypasses before any recovery-side construction.
- Exposed the deterministic Scene faithfulness prompt constraints from the exact gate tokenizer/stopwords (meaningful anchors, shared-count/recall thresholds, digit and negator multisets) and embedded them in the live prompt with explicit Correct-Answer-copy and fabricated-resolution prohibitions. Mutation witnesses bind prompt facts to gate behavior.
- Tightened primary Part-2 acceptance to require authored Scene + authored Promise + empty Scene/Promise gate failures. Honest degradation remains a machine transport/render success but cannot pass the golden witness.
- Preserved the immutable `380ecd47-7491-42ab-a3d8-a68c1afbb078` pack and added separate `prework-36-4-adjudication-380ecd47/` evidence with finalized spot checks, semantic FAIL, defect statement, and original-verdict digest. Re-recovery recognizes the adjudication and chains both verdict and adjudication SHA-256 values; it requires a fresh pre-07W.1 input clone because the consumed input is mutated.
- Added strict `prework-36-4-fresh-clone.v1` manifest verification over source/origin labels, creation timestamp, run/LO/segment/extracted companion digests, and explicit no-contribution/no-sidecar assertions. Re-recovery also rejects any stale sidecar and any already-existing output root, and binds the manifest plus companion digests and unique output path into its verdict inputs.
- Narrowed the Part-2 Q5 Scene seed to only the attending-physician/complex-workflow and recurring patient-transport-delay setup sentences. The question tail and Correct Answer remain separate typed forbidden-resolution evidence with source spans and never enter the live writer request.
- Added generic setup-only assessment contracts and deterministic Scene innocence gates for forbidden-answer exact/near overlap, diagnostic completion, and invented meaningful claim terms. The gate runs after unchanged overlap/digit/negator faithfulness checks; the exact leaked leadership-gap sentence degrades while a near-extractive scenario remains authored.
- Three-layer review closure: Blind Hunter, Edge Case Hunter, and Acceptance Auditor findings were deduplicated into receipt authority, terminal reconciliation, containment/atomicity, source/payoff, DOCX/FR17, runner-walk, integrated-terminal, bounded-live-driver, recovery evidence-state, setup-only innocence, and operator-adjudication workstreams. Every MUST/HIGH/P1 finding was remediated and re-run through focused plus broad relevant batteries; final operator evidence is 9/9 PASS. Parent Cora/Audra closure remains the only reason status stays `review`.
- Live setup-only prompts now prohibit answers, causes, barriers, reasons, solutions, diagnoses, ownership/authority gaps, and fabricated resolution; payoff slides are explicitly coverage targets rather than content authority.
- Machine-green evidence packs remain unresolved with `evidence_status=pending_operator`; they return successfully for adjudication without claiming Story acceptance.
- Evidence-state P0 tightened machine-green to tri-state `pass=null` with `evidence_status=pending_operator`. The exact nine-key operator-check contract is now identity-bound to Story 36.4, attempt ID, repo-relative verdict path, and verdict digest. Only exact all-PASS adjudication closes; only exact finalized FAIL adjudication grants retry; pending or malformed evidence grants neither.
- Preserved `5ff7db47-62af-48d0-8b67-fa300c04aa4d` unchanged and added separate adjudication naming the invented `leadership gap—unclear cross-department ownership and decision rights` plus the prior PENDING/pass driver bug. Third recovery chains its verdict and adjudication digests and requires another fresh clone/output; none was created in this remediation.
- Cora BLOCK-mode lockstep traces remained PASS throughout remediation, including `2026-07-13-0202`, `0209`, `0216`, `0222`, `0230`, `0235`, `0245`, `0250`, `0259`, `0305`, and `0315`. Final parent Cora/Audra close is still open.
- Scope hygiene: formatter-only `production_runner.py` churn was removed; its diff is narrowed to the two workbook runtime-context call sites plus legacy-stub preservation during explicit 07W.1 migration recovery.
- Added canonical pre-work blocks, presentation-support FR17 transcript/figure cut, typed pre-deep-dive N/A coverage fence, encounter label, and terminal workbook-brief refs.
- Paid live witness, mandatory multi-layer remediation, and operator prose spot-check are complete. Parent Cora/Audra closure and Epic-36 ledger close remain intentionally open; story status remains `review`.

### Immutable Live Evidence Chronology

- `12ccd755-592b-45c2-8fd2-b3fbe51df2b9` — verdict SHA `95f5de089498baf14c31a85c8ebb784fd5f65613e09cfa62bef86c34d117ca4b`; structured Scene mixed authored state with losses/marker. Prompt invariants and strict parsing were fixed. Receipt cost unavailable because failure preceded complete receipt persistence.
- `380ecd47-7491-42ab-a3d8-a68c1afbb078` — verdict SHA `8e3bc69b123657b0a0b867d0c5fe5d7058dc512d10f23c99b3da04d7b5c60b45`; cost `$0.02003625`; artifact `18ff9bd63ec0af1938e2b8b4e645cd5cbe1ce2b4ae4ba5459b9e7c3fb318717e`. Machine transport passed, but degraded Scene failed semantic adjudication.
- `5ff7db47-62af-48d0-8b67-fa300c04aa4d` — verdict SHA `3545fcc83e15c6badaf3512a61c05e1f831bbcbcf1b95b5df9d34d7b01a9a00e`; cost `$0.03455250`; artifact `bbbd7c922768fc2dfe20a1d266c7f8b508d87023f2fcc30ba124a5fdf03f3207`. Authored Scene leaked/invented a leadership-gap diagnosis; exact nine-check FAIL adjudication drove setup-only authority and innocence gates.
- `b90fb3f6-8951-4dcc-abff-66036576d89f` — verdict SHA `9ec5ddd2cea9161813af04dc825dddf04023d6ef0ad65514b0bd40cafaacf0be`; cost `$0.03546625`; artifact `b87a837429f4c6e18736000f18c86ab352a2d5e781660cc935a16f95ebd90dd5`. Machine rejected an otherwise reviewable Scene due over-strict invented-term automation; FAIL adjudication drove WARN+receipt calibration.
- `ba470ff2-4c0c-44a0-af7b-0f01360d19da` — verdict SHA `ed509d1959d730f830bbc58e99b49d3644d7f286502866d81176e16f8f5795eb`; cost `$0.03616250`; artifact `a5fefb80599c4bc11fd7c55b81a70ba6b7f35a0388a042b42db4ed6b13ce9016`. Machine-green evidence correctly remained `pass=null/pending_operator`; two independent reviews supported exact `9/9 PASS`, recorded in a separate digest-bound adjudication.

These were not retries until green: each immutable attempt surfaced a distinct product defect, received an explicit FAIL adjudication, and authorized a separately labeled recovery with a fresh input clone/output. The final pack itself remains pending; acceptance exists only in its separate operator PASS adjudication.

### File List

- `_bmad-output/implementation-artifacts/36-4-wire-prework-part2-golden.md`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-adjudication-380ecd47/adjudication.json`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-adjudication-380ecd47/PROOF.md`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-380ecd47/run/fresh-clone-manifest.json`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-380ecd47/run/run.json`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-380ecd47/run/ratified-los.json`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-380ecd47/run/exports/segment-manifest-storyboard-b.yaml`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-380ecd47/run/bundle/extracted.md`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-adjudication-5ff7db47/adjudication.json`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-adjudication-5ff7db47/PROOF.md`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-5ff7db47/run/fresh-clone-manifest.json`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-5ff7db47/run/run.json`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-5ff7db47/run/ratified-los.json`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-5ff7db47/run/exports/segment-manifest-storyboard-b.yaml`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-5ff7db47/run/bundle/extracted.md`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-adjudication-b90fb3f6/adjudication.json`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-adjudication-b90fb3f6/PROOF.md`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-adjudication-ba470ff2/adjudication.json`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-adjudication-ba470ff2/PROOF.md`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-live-20260713T022531Z-12ccd755/{attempt-id.txt,verdict.json,PROOF.md}`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-live-20260713T023935Z-380ecd47/{attempt-id.txt,verdict.json,PROOF.md}`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-live-20260713T025318Z-5ff7db47/{attempt-id.txt,verdict.json,PROOF.md}`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-live-20260713T031142Z-b90fb3f6/{attempt-id.txt,verdict.json,PROOF.md}`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-live-20260713T031924Z-ba470ff2/{attempt-id.txt,verdict.json,PROOF.md}`
- `_bmad-output/artifacts/workbooks-36-4-rerecovery-b90fb3f6/u-intrapreneur-01@1.md`
- `_bmad-output/artifacts/workbooks-36-4-rerecovery-b90fb3f6/u-intrapreneur-01@1.docx`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-b90fb3f6/run/fresh-clone-manifest.json`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-b90fb3f6/run/run.json`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-b90fb3f6/run/ratified-los.json`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-b90fb3f6/run/exports/segment-manifest-storyboard-b.yaml`
- `_bmad-output/implementation-artifacts/evidence/prework-36-4-fresh-input-b90fb3f6/run/bundle/extracted.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/marcus/cli/trial.py`
- `app/marcus/lesson_plan/prework_artifact.py`
- `app/marcus/lesson_plan/prework_from_run.py`
- `app/marcus/lesson_plan/prework_projection.py`
- `app/marcus/lesson_plan/scene_extraction.py`
- `app/marcus/lesson_plan/workbook_producer.py`
- `app/marcus/orchestrator/production_runner.py`
- `app/marcus/orchestrator/workbook_prework_writers.py`
- `app/marcus/orchestrator/workbook_wiring.py`
- `app/specialists/workbook_producer/_act.py`
- `tests/integration/marcus/test_trial_cli.py`
- `tests/integration/marcus/test_trial_plan_json_selection.py`
- `tests/integration/marcus/test_trial_legacy_workbook_migration_36_4.py`
- `tests/integration/marcus/test_workbook_band_wiring.py`
- `tests/integration/marcus/test_workbook_brief_part2_36_4.py`
- `tests/integration/marcus/test_workbook_prework_writers_36_4.py`
- `tests/fixtures/prework_36_4/part2-structured-input.json`
- `tests/fixtures/prework_36_4/deterministic-expected-receipt.json`
- `tests/fixtures/prework_36_4/semantic-assertion-manifest.json`
- `scripts/utilities/run_prework_36_4_live_evidence.py`
- `tests/scripts/test_run_prework_36_4_live_evidence.py`
- `tests/specialists/workbook_producer/test_workbook_producer_brick.py`
- `tests/marcus/lesson_plan/test_prework_artifact_36_4.py`
- `tests/marcus/lesson_plan/test_prework_from_run_36_4.py`
- `tests/marcus/lesson_plan/test_workbook_s0_s7.py`
- `tests/unit/marcus/lesson_plan/test_prework_projection_36_2.py`

### Change Log

- 2026-07-13: Implemented Story 36.4 offline scope and moved to review; live and closure gates remain open.
- 2026-07-13: Recorded immutable failed live attempt `12ccd755-592b-45c2-8fd2-b3fbe51df2b9`; hardened structured-output invariants/cost telemetry and added explicitly labeled immutable recovery semantics. Recovery live run remains open and was not executed.
- 2026-07-13: Closed recovery-preflight P0s with allowlisted causal/verdict digest chaining and a preventive two-call spend proof. Labeled dry-run is SAFE; paid recovery remains unexecuted.
- 2026-07-13: Adjudicated `380ecd47` outside the immutable pack as transport/render PASS but golden semantic FAIL; closed the prompt/gate drift and driver-overacceptance defects. A fresh-input labeled re-recovery remains open and was not executed.
- 2026-07-13: Adjudicated immutable `5ff7db47` as machine PASS/operator semantic FAIL; added setup-only assessment innocence and pending-operator evidence governance. Third labeled recovery remains open; no clone or live run was created.
- 2026-07-13: Final bounded recovery `ba470ff2` produced authored, gate-clean Scene and Promise plus real MD/DOCX; separate digest-bound operator adjudication PASS 9/9. Three-layer review, Cora BLOCK lockstep, Audra closure, and O/I/A audit all PASS; Story 36.4 and Epic 36 marked done.
