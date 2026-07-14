# Sprint Change Proposal — Story 38.3a live Deep-Dive budget correction

Status: party-approved-minor-direct-adjustment
Date: 2026-07-13
Trigger: Story 38.3a first-run-stands live witness

## 1. Issue Summary

Story 38.3a's single authorized live `07W.1` Deep-Dive call failed before producing a parseable structured candidate. Attempt `7ed48f8a-0b01-4c80-a068-d2e152a5e8d6` used a 4,096 completion-token ceiling; provider usage shows all 4,096 tokens were consumed as reasoning, leaving no visible structured output. The runtime correctly raised `workbook-brief.deep-dive-writer-execution-failed`, retained `workbook-deep-dive-call.v1.json` in `call_in_progress`, and prohibited automatic recall. No retry occurred.

Evidence: `_bmad-output/implementation-artifacts/evidence/deep-dive-38-3a-live-7ed48f8a/verdict.json`.

This is a technical limitation discovered during implementation: the new adapter inherited `_StructuredWriter`'s 4,096-token default even though repository precedent explicitly documents that GPT-5 reasoning models consume completion budget on hidden reasoning first. Existing live paths use 8,000–32,000 ceilings; G0 extraction pins 32,000 after the same failure mode.

## 2. Impact Analysis

### Epic and story impact

- Epic 38 remains viable; no epic, story, or DAG resequencing is required.
- Story 38.3a cannot move to review until the live adapter can produce a candidate and the demand/terminal continuation is witnessed.
- Stories 38.1 and later remain correctly blocked on a ready Ask-A demand.
- The failed first-run evidence remains permanent and is not relabeled as a pass.

### Artifact impact

- PRD/redesign: no requirement change; the correction restores NFR3/NFR8 live reproducibility.
- Architecture/topology: no graph, runner, manifest, event, gate, HUD, packet, or render change.
- UX: not affected.
- Code: only the Deep-Dive live adapter's named completion ceiling and its tests.
- Story record: AC10/live evidence must record both the failed pre-fix attempt and the one authorized post-fix confirmation.

## 3. Options Evaluated

1. **Direct adjustment — recommended.** Pin a named Deep-Dive-only ceiling of 32,000 completion tokens, preserve 4,096 for Scene/Promise, and run one fresh post-fix confirmation in a new contained run. Effort low; risk low-to-medium; product scope unchanged.
2. **Rollback.** Revert 38.3a live integration. Not viable: it would strand the authoritative Ask-A demand and invalidate the ratified workflow.
3. **Reduce/defer the live gate.** Not viable: it would claim production readiness from hermetic tests after a real provider failure.

## 4. Detailed Change Proposal

### Story 38.3a — live-writer budget and evidence

Old effective behavior:

- `LiveDeepDiveWriter` inherits `max_completion_tokens=4096`.
- AC10 permits one first-run-stands live call but does not state how a product defect revealed by that call is re-witnessed.

New behavior:

- Add `WORKBOOK_DEEP_DIVE_MAX_COMPLETION_TOKENS: Final[int] = 32000` with the documented reasoning-model rationale.
- Override only `LiveDeepDiveWriter` construction to bind that ceiling through the existing `make_chat_model(..., max_completion_tokens=...)` path.
- Derive the Deep-Dive effective `model_config_digest` before model-handle construction from canonical sorted compact JSON containing the base workbook-writer config digest, `adapter="LiveDeepDiveWriter"`, and the effective `max_completion_tokens`. Pass it as the handle's `system_prompt_hash` and expose it through the existing attribute so it binds model/cache resolution identity, the idempotency key, call journal, execution receipt, and live evidence. Explicit test overrides must change the digest. Scene/Promise retain their existing base-config identity.
- Scene and Promise retain the existing 4,096 ceiling; no global adapter or model-registry change.
- Add a test that the default Deep-Dive handle binds 32,000 and that injected explicit overrides remain testable; pin Scene/Promise unchanged.
- Preserve the failed run and its ambiguous journal exactly. Do not clear, mutate, or resume it.
- Pre-fix preservation pins are binding after the evidence record's one-time factual augmentation. The original immediately-written verdict was 888 bytes/SHA-256 `d31b4e9e7c04399f6bfc502823414af27fd6a434a09055ffba979b0e83e318c2`; during the same dev evidence pass it was augmented with journal identity, usage, cost, latency, and runtime-configuration facts. The original bytes were not preserved and must not be claimed as preserved. The authoritative frozen augmented verdict is now `verdict.json` SHA-256 `d46681f0402c8f9d280a933f9584773dade6b5a7d84880ae3fd324c2d10ca5cb`, size 1872 bytes. The ambiguous `workbook-deep-dive-call.v1.json` pin is SHA-256 `1dafe2196a97a2262dd59c3d8d802ea93be6a7ee1ab11f77748ae9a2f857768a`, size 7123 bytes, state `call_in_progress`, idempotency key `sha256:de31a3f58b4987fbb87e88df8f72acc04de1e564a454ed6c13e584137027f32f`. Recompute and require exact current hash/size/state equality before and after all tests and the fresh run; no further augmentation is permitted.
- After code/tests pass, authorize exactly one fresh post-fix live confirmation in a new run directory. This is a validation of a materially corrected candidate, not a retry of the failed ambiguous call. No further retry-to-green is authorized.
- The fresh run starts without a copied journal and must have distinct run/trial/attempt IDs and a distinct idempotency key. A copy-based fixture driver must replace both `ProductionTrialEnvelope.trial_id` and nested `ProductionEnvelope.trial_id` with the same new UUID4 before the call. No command may resume or invoke a provider against the failed run.
- Story closure evidence must present both attempts: pre-fix FAIL and post-fix result, with separate run/attempt IDs and costs. A post-fix failure blocks closure and requires a new correction decision.

## 5. Implementation Handoff

Classification: **Minor direct adjustment** within Story 38.3a.

- Amelia/developer: implement the named Deep-Dive-only budget, tests, story evidence, and at most one fresh post-fix live witness.
- Murat/test architect: verify the budget pin, failed-journal preservation, no-call retry prohibition, separate-run identity, and evidence honesty.
- Winston/architect: confirm no global model/graph/render scope expansion.
- John/PM: confirm the correction preserves the product outcome and does not disguise retry-to-green.

Success criteria:

1. Failed attempt and ambiguous journal remain byte-preserved.
2. Deep-Dive alone binds 32,000 and an effective config digest that includes the ceiling; Scene/Promise remain 4,096 with unchanged config identity.
3. All deterministic/dependency/static checks pass.
4. At most one fresh post-fix live call occurs.
5. A passing post-fix witness yields a replay-valid skeleton, nonempty terms, ready Ask-A demand, matching terminal reconciliation, and zero-call resume.
6. If the post-fix witness fails, Story 38.3a stays open and no additional call is made without another governed change.

## Checklist Disposition

- Trigger/evidence: done.
- Epic/future-story impact: done; no resequencing/new epic.
- PRD/architecture/UX impact: done; no product or UX scope change.
- Direct adjustment: viable and recommended; rollback/MVP reduction not viable.
- Handoff/success criteria: defined.
- Approval: fully spawned BMAD party consensus recorded 2026-07-13. John: GO-WITH-AMENDMENTS (preservation SHA pins); Winston: GO-WITH-AMENDMENTS (effective config identity + preservation audit); Amelia: GO-WITH-AMENDMENTS (fresh nested trial identity + effective digest before handle construction); Murat: GO-WITH-AMENDMENTS (verdict discrepancy provenance + deterministic/live evidence gates). Every MUST amendment is folded above; the orchestrating agent concurs. Under repository governance, consensus plus agent concurrence authorizes the minor direct adjustment without a redundant human hold.

---

## Amendment 2 — Exact duplicate provider-metadata normalization

Status: party-approved-with-amendments

### Trigger and evidence

The one authorized post-budget-fix run used the corrected 32,000 ceiling and returned structured content, proving the truncation defect fixed. Strict Pydantic validation then rejected the provider payload because `bold_terms` repeated the exact string `burnout`. No additional call occurred. Story 38.3a remains `in-progress`.

- Attempt: `b6fc76ea-94a2-4e51-bf04-ca626cb30ee0`
- Trial ID (outer and nested): `15d265a9-0a33-4192-9e87-c731b4e60fcb`
- Verdict: SHA-256 `acb3e3f98f26c3563412f1a49f9c73ca0913594a4b1c3bb52de8059536bd801f`, 9408 bytes
- Ambiguous journal: SHA-256 `212d48f9dfcf0ac9f769d11571036eaa4e0c097cbdd6d917f0f687a602da4dcf`, 7105 bytes, `call_in_progress`
- Idempotency key: `sha256:a0ac1ea3e7340f6650fb29fe499bf09b99f8e3b2d4e120925766470bf0de6fb6`

Both failed runs and journals remain immutable; pre/post checks must pin all four hashes/sizes/states.

### Impact and options

- Epic/DAG/PRD/UX/topology/render: unchanged.
- Prompt-only correction is not sufficient: the prompt already says metadata once, and the provider violated it.
- Weakening `DeepDiveSkeletonWriterResult` uniqueness/parity is rejected.
- Recommended direct adjustment: normalize only redundant exact metadata at the provider boundary, then enter the unchanged strict Story-37.2a candidate/gate.

### Proposed implementation

1. `LiveDeepDiveWriter` alone requests the provider using exactly `DeepDiveSkeletonWriterResult.model_json_schema()` as a raw JSON-schema contract so the provider payload can be observed before Pydantic model validators run. The schema digest is canonical sorted compact UTF-8 JSON of the exact dict passed to `with_structured_output`, not a regenerated lookalike. Generic `_StructuredWriter`, Scene, and Promise remain on their current Pydantic structured-output path.
2. Treat provider `parsed` as untrusted JSON: require a plain mapping, canonical JSON round-trip/deep-copy it, retain the untouched raw mapping, and never normalize in place. Add one pure normalizer version `deep-dive-provider-normalizer.v1` returning `(normalized_mapping, ordered_records)`. For top-level `status == "authored"` and a JSON-list (not tuple/coerced container) `bold_terms`, consider only entries whose keyset is exactly `{term}`, whose term is a string, and for which `BoldTermMarker.model_validate(entry, strict=True)` passes. Stable-deduplicate only later eligible entries against earlier eligible exact case-sensitive, codepoint-sensitive strings, preserving first occurrence and order. Record one ordered item per removed occurrence, e.g. `deduplicated_exact_bold_term:burnout`.
3. Do not Unicode-normalize, case-fold, trim, rewrite, infer, add, remove, or reorder any unique term. Do not modify prose, sections, claims, refs, status, losses, or marker. Every ineligible malformed/extra-field/unsafe/whitespace-altered/non-string entry is preserved structure-equivalent so unchanged strict validation fails. Case/Unicode variants, duplicate claims/IDs, parity mismatch, unsafe Markdown, extra fields, and every other defect still fail strict validation. Deep-equality tests must prove `bold_terms` is the only possibly changed field.
4. Validate the normalized mapping into the unchanged `DeepDiveSkeletonWriterResult`, then run the unchanged `compose_deep_dive_skeleton` replay/gates.
5. Keep normalization evidence out of `DeepDiveExecutionReceiptV1` and the workbook-brief semantic payload. Extend completed-journal/live evidence with distinct fields: `raw_provider_payload`, `raw_provider_payload_digest`, `provider_schema_digest`, `provider_normalizer_version`, ordered `provider_normalizations`, `normalized_provider_payload_digest`, existing strict `candidate`, and existing semantic `candidate_digest`.
6. Completed replay verifies the raw digest, reruns the named normalizer from raw, requires exact normalization records and normalized digest, strictly validates the recomputed mapping, requires equality with the stored candidate, and then runs the unchanged composer/gate/result-digest replay. Any raw/list/digest/candidate mutation fails reconciliation before returning the saved result.
7. Bind the Deep-Dive effective configuration digest to base config digest, adapter name, 32,000 ceiling, provider contract mode `raw-json-schema`, the canonical digest of the exact JSON schema supplied, and normalizer version. Schema/normalizer/ceiling changes therefore alter handle identity, idempotency key, journal, and evidence.
8. Capture and canonical-digest the parsed raw mapping before normalization/strict validation. If normalization or strict validation fails after a mapping was parsed, atomically enrich the still-`call_in_progress` journal with raw payload/digest, schema digest, normalizer version/records, normalized digest when available, and typed failure before raising; the verdict may project this journal evidence. Never fabricate raw evidence for transport/parse failures, discard returned evidence, or authorize recall.
9. Tests prove: one/two removed exact duplicates and ordered records; repeated prose terms still derive one canonical metadata term; case/Unicode/whitespace variants do not normalize; unsafe duplicate pairs and eligible-after-ineligible ordering; list-versus-tuple/coercion refusal; malformed/extra/unsafe/non-string markers remain and fail; non-authored terms, duplicate claims/sections/abilities, parity, refs, and unsafe Markdown still fail; raw/normalized/candidate/record/digest mutations fail replay; stored normalized/candidate snapshots are never trusted over recomputation; strict candidate/gate source is unchanged; no generic `_StructuredWriter`, Scene, Promise, receipt, workbook-brief digest, or contribution behavior changes.

### Live authorization requested

Before and after all tests/call, pin all four prior files: first verdict `d46681f0402c8f9d280a933f9584773dade6b5a7d84880ae3fd324c2d10ca5cb`/1872 and journal `1dafe2196a97a2262dd59c3d8d802ea93be6a7ee1ab11f77748ae9a2f857768a`/7123/`call_in_progress`/key `de31…f32f`; second verdict `acb3e3f98f26c3563412f1a49f9c73ca0913594a4b1c3bb52de8059536bd801f`/9408 and journal `212d48f9dfcf0ac9f769d11571036eaa4e0c097cbdd6d917f0f687a602da4dcf`/7105/`call_in_progress`/key `a0ac…6fb6`.

After deterministic/dependency/static checks and immutable evidence-pin checks pass, authorize exactly one fresh post-normalization live run with `max_retries=0`, new run/attempt/idempotency identities, one new UUID4 applied equally to outer/nested trial IDs, and no copied journal. It validates materially changed adapter code; it does not resume either ambiguous call. If it fails, Story 38.3a remains open and no further provider call is authorized without a new decision. If it passes, require ready demand, terminal reconciliation, completed-journal replay with zero provider calls, and all earlier failure evidence visible beside the pass.

### Amendment 2 approval

Fully spawned party, 2026-07-13: John GO; Winston GO-WITH-AMENDMENTS; Murat GO-WITH-AMENDMENTS; Amelia GO-WITH-AMENDMENTS. Every MUST is folded above, including untrusted-mapping copy semantics, exact safe-entry eligibility, effective schema/normalizer identity, raw-to-normalized journal replay, failure evidence, receipt compatibility, four-file preservation, negative matrix, and fresh identity/call guard. The orchestrating agent concurs. Under repository governance, Amendment 2 is approved without a redundant human hold; no provider call may begin before all deterministic gates pass.

---

## Amendment 3 - Clustered final-to-source slide authority

Status: party-approved-minor-direct-adjustment; Story 38.3a reopened

### 1. Issue Summary

The second Story-38.1 live-validation run, `c8f17a24-9b63-4e10-a5d7-6f2043bc9812`, reached `07W.1` after eight delegated HIL gate actions and failed before any Ask-A dispatch with `workbook-brief.deep-dive-authority-invalid: slide authority for slide-07 matched 0 files`.

The run has six authored source-slide Markdown files but 13 final manifest slides after Irene's cluster expansion. Story 38.3a incorrectly interpreted final presentation ordinals as authored source ordinals. The intended mapping is `[1,2,2,2,3,3,3,3,4,5,5,5,6]`. Existing suffix-based lineage helpers are also unsafe on this live shape: `u05`, `u09`, `u10`, and `u13` are plan-unit identities and would be misread as source ordinals 5, 9, 10, and 13.

Concrete exact authority exists: all 58 persisted Irene `source_refs` anchors are literal, case-sensitive substrings of exactly one of the six declared source-slide files, and every interstitial agrees with its parent source.

### 2. Impact Analysis

- Epic 38 and the dependency DAG remain viable. Story 38.3a is reopened; Story 38.1 remains in-progress and cannot close until the predecessor correction is reviewed and live-proven.
- No new epic/story, resequencing, graph node, runner-walk, provider family, Ask-A contract, HUD, render, learning event, or envelope-schema change is required.
- The prior 38.3a close remains historically valid for its one-to-one live substrate, but it did not prove clustered production correctness.
- PRD intent is strengthened: the correction makes prose-depth authority follow the authored source from which each clustered final slide actually descends. UX is unaffected.
- The existing 38.1 attempts remain immutable evidence and are not relabeled or resumed.

### 3. Options Evaluated

1. **Direct adjustment - selected.** Reopen 38.3a and add an explicit immutable authority-map carrier derived from exact anchors. Effort medium; risk medium; product scope unchanged.
2. **Reuse suffix/ordinal/positional lineage.** Rejected: it silently miskeys the live `uNN` shape and can select a wrong but existing file.
3. **Title or fuzzy-content matching.** Rejected: it weakens authority and makes ambiguity nondeterministic.
4. **Change Pass-1 schema upstream.** Not required for this correction. A dedicated canonical sidecar supplies explicit source identity without broad upstream migration; a future harmonization is outside this pass.
5. **Skip source-note deltas and continue VO-only.** Rejected: it would evade a required authority contract and reduce the specified workbook depth.

### 4. Detailed Change Proposal

1. Add pure strict models/resolver in `app.marcus.lesson_plan` for `workbook-slide-authority-map.v1`. The orchestrator extracts exactly one current Irene plan contribution, cross-checks `irene-pass1.lesson-plan.json`, and extracts exactly one node-06 package-builder slides contribution.
2. Join final manifest slide -> package slide `source_ref` -> plan unit -> source slide using every unit's complete nonblank literal anchor set. Every anchor must occur in exactly one declared slide file and all anchors for a unit must converge. Interstitials must agree with a valid head parent. No suffix, ordinal, order, rank, title, cluster-ID, fuzzy, case-fold, Unicode, whitespace-repair, or first/last-wins fallback.
3. Before any Deep Dive journal/provider action, exclusively and atomically write `workbook-slide-authority-map.v1.json`. Rows explicitly carry final/unit/source identities, relative source path and byte hash, anchors, and parent/cluster corroboration. Header identity binds schema/resolver version, ordered manifest, plan sidecar/contribution, package slides, relative source inventory/hashes, and ordered rows. Existing sidecars are never overwritten and must fully revalidate.
4. Bind the map digest into the new request authority domain, journal, idempotency key, receipt, completed replay, upgrade, and split-brain checks. Preserve legacy digest compatibility with an omitted-when-null field, but require a non-null map digest for every new 07W.1 execution.
5. Preserve all final VO spans in manifest order. Group descendant narration by explicit source slide and compare the source speaker note once against the ordered aggregate; emit at most one source-keyed delta span/claim per unique source slide in first-descendant order.
6. Fail before provider spend on missing/duplicate/stale/conflicting authority, anchor zero/multi/cross-file matches, invalid parentage, roster/order mismatch, symlink/escape/non-regular paths, source hash drift, sidecar mutation, or map/journal digest mismatch. Use the existing stable error taxonomy.
7. RED-first coverage includes the serialized live `u01`-`u13` fixture and exact 13-to-6 map; wrong-suffix traps; missing/duplicate/conflicting rows; dangling units/parents; ambiguous/missing anchors; final-07-to-source-3 no-fallback trap even if source slide 7 exists; reordered/reclustered stability; symlink/escape; legacy digest pins; resume under changed map digest; zero writer/journal/brief/contribution on authority failure; exactly one delta per source slide.
8. After deterministic, dependency, Ruff, import-linter, diff, and BMAD code-review gates pass, authorize one fresh run with a new trial/idempotency lineage and no copied journal/map/brief/contribution. Require exactly one Deep Dive call, one Ask-A/Texas dispatch, completed journals, zero-call replay, and conforming workbook evidence. Any failure returns to governed correction; no retry-to-green.

### 5. Handoff and Success Criteria

Classification: minor direct adjustment to a closed predecessor contract; implementation complexity is medium because replay identity changes.

- Developer: implement resolver, sidecar, request/journal binding, grouped delta semantics, and RED-to-GREEN tests.
- Murat/test architecture: verify the serialized 13-to-6 trap, no-fallback mutations, zero-call failures, and replay drift rejection.
- Winston/architecture: verify M3 placement, single-write sidecar authority, compatibility domain, and no graph/provider expansion.
- John/product: verify the change repairs the Marcus-SPOC product rather than the proofing vehicle and preserves the workbook outcome.

Success requires: exact total 13-to-6 authority; immutable digest-bound replay; no inference fallback; once-per-source delta authority; all deterministic/review gates green; prior attempts immutable; one fresh full live path reaching Ask-A and emitting a conforming workbook; zero-call replay.

### Checklist Disposition and Approval

- Trigger/evidence, epic/future impact, PRD/architecture/UX impact, alternatives, handoff, and success criteria: complete.
- Selected path: direct adjustment. Rollback, MVP reduction, and scope deferral are not viable.
- Sprint ledger: Story 38.3a reopened to `in-progress`; Story 38.1 remains `in-progress`; no epic/DAG change.
- Fully spawned BMAD party reconciliation: John GO-WITH-AMENDMENTS, Winston GO-WITH-AMENDMENTS, Murat GO-WITH-AMENDMENTS; all remaining MUSTs are folded above. The orchestrating agent concurs. Under repository governance, party consensus plus agent concurrence is operator approval; no redundant human checkpoint is required.

---

## Amendment 4 - Full-scale Deep-Dive request timeout

Status: party-approved-minor-direct-adjustment

### Trigger and evidence

Fresh delegated Marcus-SPOC attempt `e08c3fef-eed3-42fa-94d5-f7e58989389e` proved Amendment 3's clustered authority correction live: the 13-final/6-source carrier persisted and validated with map digest `sha256:a080a3b0db00da790982564a86dbc3736f2312babe56b53e2c15ff56e1d560e9`. The full production request then reached `LiveDeepDiveWriter` with 12 VO spans, six grouped source deltas, and 11 Promise abilities. The provider hit the inherited generic 120-second request ceiling and returned `APITimeoutError: Request timed out.` With `max_retries=0`, the runtime correctly paused at `07W.1` under `workbook-brief.deep-dive-writer-execution-failed`; Ask-A and workbook output were not produced.

The failed attempt is frozen. Binding pins include:

- Deep-Dive journal: 25,870 bytes, SHA-256 `9e7798e2dfa874a2dcff800ab1b100252fd6ee630befcb6078a6ee4b3513c2d0`, state `call_in_progress`.
- Slide-authority carrier: 8,536 bytes, SHA-256 `ac8dde3c50921b60249485f51b6534279dd38685d253d2944fa90b71e97486c5`.
- Delegated HIL journal: 6,547 bytes, SHA-256 `e037f6f863e29c692e0d21783aa38c950108cbf45ce6cd9cd81250f836640656`.
- Delegated summary: 804 bytes, SHA-256 `302844af8de5ad1240263e4c47940773b36148834051ca2f38329bcf38af0fd9`.

### Impact and options

- Epic/DAG/PRD/UX/topology/request shape/provider family/Ask-A/render: unchanged.
- Direct adjustment is viable, low effort, and low-to-medium risk. It restores the intended full-scale production call without multiplying calls.
- Rollback is not viable because it would restore the disproven ordinal authority behavior.
- Scope reduction is not viable because the live production request is the specified workload.

### Approved correction

1. Add named `WORKBOOK_DEEP_DIVE_REQUEST_TIMEOUT_S = 300.0`, matching the existing G0 large reasoning-extraction precedent.
2. Parameterize the shared structured-writer constructor with an effective request timeout that defaults to 120 seconds. Pass 300 only from `LiveDeepDiveWriter`; Scene and Promise remain exactly 120 seconds.
3. Keep `max_retries=0` for every workbook writer.
4. Bind the effective request timeout and retry posture into the Deep-Dive effective model-config digest before handle construction, journal identity, and idempotency-key derivation. A timeout change must change execution identity; completed replay must reject drift.
5. Add RED/GREEN construction and orchestration tests for Deep-Dive 300/zero-retry, Scene/Promise 120/zero-retry, digest/idempotency drift, and the unchanged one-call fail-loud timeout path.
6. Run focused/dependency/static verification and mandatory adversarial review before live spend.
7. Preserve the failed run and journal exactly. Never resume, repair, rewrite, delete, or reuse its ambiguous call.
8. After deterministic and review GREEN, authorize exactly one fresh UUID production-seam attempt under the existing delegated HIL policy. The outer controller retains its four-hour budget, safely above the 300-second provider ceiling. Any failure stops without retry and requires a new party decision.

### Handoff and approval

Classification: minor direct adjustment within Story 38.3a; route to Amelia/developer, followed by Blind/Edge/Acceptance review and the single governed confirmation.

Fully spawned native BMAD party, 2026-07-13: John GO-WITH-AMENDMENTS; Winston GO-WITH-AMENDMENTS; Murat GO-WITH-AMENDMENTS; Amelia GO-WITH-AMENDMENTS. Every MUST is folded above. The orchestrating agent concurs. Under repository governance, Amendment 4 is approved without a redundant human hold.

---

## Amendment 5 - Pass-1 identity and literal-anchor authority

Status: party-approved-with-amendments; no fresh live attempt authorized

### Trigger and evidence

The single Amendment-4 live attempt, `a28aa15a-fc80-46ae-b05a-09ac864829bb`, completed all eight delegated HIL actions, both storyboards, Irene Pass 2, and 11/11 Enrique segments. At `07W.1`, the strict slide-authority resolver stopped before map persistence or Deep-Dive provider dispatch with `workbook-brief.deep-dive-authority-invalid: unit u06 anchor must match exactly one source slide file`.

The failed run proves two upstream authority defects:

1. Temporal and same-plan identity collision: `u06` identified the interstitial `Knowledge Now Outpaces Static Training` under `u05`, then was reused for the head `Part 2 Summary & Knowledge Check`.
2. Nonliteral source authority: the summary head claimed the anchor `shape the future of care`, while the declared source contains `shaping the future of care`. The other five summary anchors match exactly one source file. The resolver correctly rejected the near match; it must not be weakened.

Frozen evidence pins at stop:

- `runs/a28aa15a-fc80-46ae-b05a-09ac864829bb/error-pause.json`: 581,762 bytes, SHA-256 `4d9bc6f4c1c4ef5f662f6607326402dc741f1e845dd5ec1034f49283cc4fa6bc`.
- `runs/a28aa15a-fc80-46ae-b05a-09ac864829bb/run.json`: 553,548 bytes, SHA-256 `3935b017d343bfd5c8bcdd1b7998d07ef82238ab74fa5031b6a1df60b90bc50f`.
- delegated HIL journal: 6,522 bytes, SHA-256 `d40966f13073d815e183a5d94d46d33de192363fe89672cff4c8e23f4e29b091`.
- delegated HIL summary: 804 bytes, SHA-256 `63101565b9767044650098e939d4d71ca62cd3951b1e1668257fa99904075e2d`.
- No slide-authority map, Deep-Dive journal, workbook brief, Ask-A journal, or workbook was produced.

### Impact and decision

- This is a Marcus-SPOC production defect surfaced by the live workflow, not a proof-run accommodation.
- Epic/DAG/PRD/UX/provider/render scope remains unchanged. Story 38.3a and 38.1 remain in progress.
- A 07W-only repair, fuzzy/stemmed/case-folded matching, first/last-wins identity collapse, or in-place repair of the failed run is rejected.
- The selected correction moves the existing exact authority contract to the Pass-1 authority-finalization boundary so malformed plans fail before package construction and paid downstream production.

### Approved correction

1. Add one canonical pure Pass-1 authority validator/finalizer and invoke it on every newly dispatched 04A/05/05B result after cluster-floor shaping but before sidecar, learning-event, contribution, or package persistence. Add an earlier duplicate/blank-ID guard before cluster normalization so normalization cannot conceal ambiguity.
2. Treat `unit_id` as durable run identity. Reject duplicates within a candidate. Across refinement, a retained ID must preserve its exact ordered source-anchor tuple and authority/role identity; removed IDs remain retired and cannot be recycled for different content. Do not silently renumber or repair model output.
3. Require every in-scope unit to carry nonblank, unique literal anchors. Using the same shared exact matcher as the 07W resolver, every anchor must be a case-sensitive literal substring of exactly one declared source-slide file after newline normalization only, and all anchors for a unit must converge on one file. No fuzzy matching, stemming, punctuation/whitespace repair, anchor dropping, restoration, or paraphrase acceptance.
4. Project only the validated canonical plan to JSON/Markdown sidecars, locked scope, learning events, contribution output, and package input. Immediately validate package slide IDs/source refs as unique, total, ordered one-to-one projections of the validated in-scope plan-unit identities; never collapse through a dict.
5. Apply the same checks to newly dispatched and resumed current-format work before downstream execution. Preserve completed legacy runs without in-place migration.
6. Fail with a stable upstream plan/package-authority tag before persistence/spend. Tests must prove zero package contribution, paid producer call, slide-authority carrier, Deep journal, workbook brief, Ask-A journal, or Ask-A contribution.
7. Bank sanitized independent fixtures for duplicate `u06` and `shape` versus `shaping`, plus valid control, temporal A-to-B-to-C ID retirement/reuse, malformed parent, zero/multiple/cross-file anchor matches, package drift, resume, purity/no-repair, and exact upstream/downstream classifier parity.
8. Preserve the entire failed run and evidence exactly; tests use copies under temporary paths and bomb all provider/network factories.
9. Run focused Pass-1/package/authority/workbook suites, the established deterministic gate, Ruff/static/diff checks, and exact-current adversarial review.
10. This decision authorizes only deterministic implementation and verification. A fresh live attempt requires a separate post-green party authorization; no retry is currently authorized.

### Handoff and approval

Classification: direct production correction with upstream enforcement; medium implementation risk because identity persists across refinements.

Fully spawned BMAD party, 2026-07-13: John/PM GO-WITH-AMENDMENTS; Winston/architect GO-WITH-AMENDMENTS; Murat/test architect GO-WITH-AMENDMENTS; Amelia/orchestrating developer GO-WITH-AMENDMENTS. The orchestrator resolves the one disagreement in favor of strict rejection: malformed IDs and anchors are never automatically rewritten, restored, or dropped. All accepted MUSTs are folded above. Under repository governance, party consensus plus agent concurrence authorizes the deterministic correction without a redundant human checkpoint, but does not authorize another live run.
