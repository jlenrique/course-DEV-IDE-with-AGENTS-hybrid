# Codex Dev Prompt — P2-4a (Reading-path native machinery — classifier + verify-node)

**Story:** `p2-4a-reading-path-native-machinery` · **Branch:** `fidelity-perception-arc-2026-06-19` · **Baseline:** `485662e` (P2-3 closed + AC-6 strike fired).
**Cycle:** NEW CYCLE — you run T1–T10 (dev + tests), then Claude runs T11 (review/commit/close). **Read first:** the spec `spec-p2-4a-reading-path-native-machinery.md` (Frozen Intent + ACs + §Scope Boundary + §Tier-3 Green-Light Disposition), and `docs/dev-guide/pipeline-manifest-regime.md` at T1 (pipeline-lockstep applies — manifest + `-gen` pack + schema are touched). Also `docs/dev-guide/pydantic-v2-schema-checklist.md` and the schema-story scaffold.

## The fix in one sentence
Restore the SEVERED reading-path leg natively: classify each slide's `reading_path` (closed enum, the 7 surviving patterns) **deterministically from perceived geometry** at the vision node onto the **rich** `PerceptionArtifact`; Pass-2 narrates in that scan order; a deterministic **fail-loud verify-node** (mirroring `_assert_narration_joins_roster`) checks conformance. **Machinery only** — NO repertoire growth, NO held-out real-slide ≥80% bar (those are P2-4b, operator-gated).

## Scope fence (read before coding)
- **IN:** FR17 field+classifier · FR18 verify-node · FR20 cadence · native four-file lockstep rebuild · anti-vacuity contradiction fixture · A8 re-pin · the §52 payload-tail rider (AC-8).
- **OUT (do NOT author):** FR19 new patterns (triptych/image-dominant-first); any ≥80% real-slide conformance test against operator-labeled ground truth (AC-9 — it does NOT exist; authoring a self-labeled version is a vacuous-pass violation and will FAIL T11). The enum ships with the **7 surviving patterns only**.

## Edit sites (verified at 485662e)
1. **`app/models/perception/perception_artifact.py`** — add `reading_path: Literal[<7 patterns>]` to the **RICH** model (NOT the minimal `pass_2_template.py` one — A1 trap). Triple-layer red-rejection + fail-loud default. If internal-audit: clone the `provenance` `SkipJsonSchema[...] + Field(exclude=True)` idiom; if public: it enters the JSON Schema + four-file lockstep.
2. **`app/specialists/vision/_act.py`** (or vision-adjacent post-processing over the rich artifact) — a **deterministic** classifier derives `reading_path` from perceived element geometry (bbox/positions/`visual_elements`). **No incremental LLM/model call.** Rebuild `scripts/utilities/reading_path_classifier.py` native (was severed). Field-compatibility contract test (A1-style).
3. **`app/specialists/irene/graph.py`** — `_act_pass_2` (`:538+`): add `_assert_reading_path_conformance` post-check after `_assert_narration_joins_roster` (`:575`), deterministic, raises a tagged `Pass2ReadingPathError` on order non-conformance. FR20: couple per-cluster cadence to the classified pattern. If scan-order data enters the prompt, re-pin the A8 cache-prefix fixture deliberately.
4. **Native four-file lockstep (rebuild):** `state/config/reading-path-patterns.yaml` (NEW registry) · `state/config/schemas/segment-manifest.schema.json` (`reading_path` enum) · `scripts/validators/pass_2_emission_lint.py` (NEW emission lint) · `tests/contracts/test_reading_path_parity.py` (NEW parity: registry ↔ schema ↔ worked-examples-doc headings agree on the 7; out-of-vocab rejected).
5. **Manifest/governance:** `data_plane_vocabulary_version` `dp-v1.4 → dp-v1.5` (additive); confirm at T1 whether `pack_version` stays `v4.2` (vision-adjacent classifier = dp-vocab bump, NOT a new pipeline node → no pack-family bump) per the regime doc; regenerate the `-gen` witness; update SCHEMA_CHANGELOG.

## Binding amendments (T11 re-fails without these)
- **A1 (rich-model only):** `reading_path` on the rich model; deterministic; fork-agnostic; field-compatibility contract test fails loud if the rich model drops a read field.
- **Anti-vacuity (Murat, non-negotiable):** a **contradiction fixture** (slide whose perceived scan order contradicts naive top-to-bottom/DOM default). Assert the classifier emits the correct **non-default** pattern AND the verify-node FAILS LOUD on wrong-order narration. **Two mutation runs RED:** M1 classifier→naive-default (conformance RED); M2 collapse the verify partition (known-wrong fixture passes → test RED). Evidence in Completion Notes. A presence-only "pattern field exists" assertion is REJECTED.
- **RED-first:** the wrong-order conformance case is committed RED pre-fix, GREEN post-fix.
- **Verify-node fail-loud:** deterministic, no-retry, no warning-level for the 7 in-scope patterns (mirror P2-1 detector + `_assert_narration_joins_roster`).
- **AC-9 operator-gate:** the ≥80% real-slide bar is OUT of T1–T10. Record it as an operator-gated Completion-Notes item with its precondition (operator scan-order harvest); do NOT self-label a corpus. Write the disconfirmation criterion ("verify-node green but operator scan-order complaint reproduces" = FAIL).
- **A8 (cache-prefix):** deliberate re-pin of the named stability fixture (canonical sorted-keys JSON, deterministic ordering, fixed-seam injection, one-line rationale; never `xfail`/skip).
- **§52 rider (AC-8):** gate/redact-or-frame the un-framed `## Envelope payload` brief tail for UNVERIFIED slides, scoped so it doesn't break the A8 pin without the deliberate re-pin. Strikes `pass2-envelope-payload-brief-unframed-in-prompt-tail` on close.

## Verification battery (T1–T10)
Focused irene + vision suites green; new classifier/conformance/mutation tests green; the contradiction fixture's RED-first + M1/M2 mutation RED evidence; native parity test green (registry↔schema↔doc); emission lint green; manifest lockstep L1 exit 0; frozen-pack-SHA discipline per regime; lint-imports 0-broken; ruff clean; sandbox-AC validator PASS; `git diff --check` clean. Re-pin the A8 fixture deliberately. Completion Notes carry: the mutation table, the RED-first baseline-diff, the dp-v1.5 governance note, and the AC-9 operator-gate statement.
