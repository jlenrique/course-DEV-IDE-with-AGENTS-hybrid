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
