# Dev-Agent Anti-Patterns Catalog

**Audience:** BMAD dev agents (Amelia et al.) at T1 of any story.
**Source:** harvested from Dev Notes sections of Stories 27-0, 27-2, 31-1, and from G6 `bmad-code-review` findings across those stories.

Read this at T1 of every story. These are the traps dev agents have repeatedly walked into and that layered reviews have had to catch. If you see a pattern below matching your current approach, stop and reconsider.

---

## Category A — Schema & validator traps

### A1. Silent mutation (G6 MF-1/2/3 on 31-1)

**Trap:** Construct a Pydantic model with validators, then mutate a field via attribute assignment. Validators don't re-run.

**Fix:** Every model that can be mutated has `model_config = ConfigDict(validate_assignment=True)`. No exceptions.

### A2. Naive datetime from `datetime.utcnow()` (G6 MF-4 on 31-1)

**Trap:** `datetime.utcnow()` returns a tz-naive datetime. It's deprecated in Python 3.12. Passing it to a model with a timezone-aware field silently creates drift.

**Fix:** `datetime.now(tz=UTC)` always. Add a `field_validator` that rejects naive datetimes on every timestamp field.

### A3. `Field(exclude=True)` assumed overridable (31-1 Dev Agent Record)

**Trap:** Caller calls `instance.model_dump(exclude=set())` expecting to get the internal audit field back. Pydantic v2 does not allow `exclude=True` on Field to be overridden this way.

**Fix:** Expose an opt-in helper (31-1's `to_audit_dump()`). Don't try to build a flag that flips `exclude` at dump time.

### A4. Closed enum with only one rejection surface (G5 Murat on 31-1)

**Trap:** Closed-enum field has a Pydantic `Literal[...]` validator but no JSON Schema `enum` array check and no `TypeAdapter` round-trip test. External jsonschema validators accept values Pydantic would reject.

**Fix:** Three-layer rejection per `docs/dev-guide/pydantic-v2-schema-checklist.md` §4.

### A5. `min_length` on verbatim free-text fields (R2 rider S-2)

**Trap:** Adding `min_length=1` to a `rationale` or `commentary` field. This rejects Maya's valid empty-string decisions and violates the "stored verbatim" contract.

**Fix:** No `min_length`. No regex. No `.strip()`. Verbatim means verbatim.

### A6. State-machine transition via field assignment (R2 rider Q-5)

**Trap:** State machine uses per-field validators. An attacker/bug assembles the model with fields in an order that bypasses the intended transition rules.

**Fix:** `model_validator(mode="after")` bypass guard that inspects the final assembled state.

## Category B — Test-authoring traps

### B1. K-floor becomes K-ceiling-multiplier (31-1 shipped 131 tests against K=25)

**Trap:** The K test-floor in the story plan is treated as a starting minimum and the dev agent pads to 4-6× it. Large parametrized matrices expand cases but don't buy new correctness.

**Fix:** Target 1.2-1.5× K. Stop when the acceptance matrix is closed. Consolidate related parametrized cases into one test function rather than splitting across files. See `docs/dev-guide/story-cycle-efficiency.md`.

### B2. Tautological self-referential tests (G6 MF-6 on 31-1)

**Trap:** Test helper raises an exception; test asserts that the helper raises. The test passes trivially — it's testing its own helper, not the model behavior.

**Fix:** The behavior under test lives on the model (method or validator). The test exercises the model method, not a fixture helper.

### B3. Mocking the thing you're testing (recurring from 27-0, 27-1, 27-2)

**Trap:** Mocking the retrieval adapter in a test of the adapter ABC. Or mocking the file system in a test of a file-writer. The mock hides the behavior you need to verify.

**Fix:** Use real adapters or real temp files. If the real thing is expensive, use fixtures with committed canned output (27-2's pattern).

### B4. Batched shape-pin tests across families (R2 rider AM-1 on 31-1)

**Trap:** One `test_all_schemas_shape_stable.py` that pins LessonPlan + FitReport + ScopeDecision together. When any one changes, the whole file fails and you can't tell which family drifted.

**Fix:** One shape-pin file per shape family. Per-family SCHEMA_CHANGELOG entries track them.

### B5. One-directional required-optional parity (R2 rider AM-2 on 31-1)

**Trap:** Parity test asserts "Pydantic-required → JSON Schema required" but not the reverse. A field demoted in Pydantic drifts silently.

**Fix:** Bidirectional parity. Scaffold template `test_json_schema_parity.py.tmpl` has both directions wired.

### B6. Missing boundary values on numeric fields (G6 MF-5 on 31-1)

**Trap:** `Dials` field validated as `ge=0.0, le=1.0`. Test covers mid-range values but not 0.0, 1.0, NaN, +inf, -inf. Edge Case Hunter flagged the gap.

**Fix:** Parametrize every numeric range validator over its boundary values plus pathological floats.

## Category C — Review-ceremony traps

### C1. Treating every story as foundation-tier (R2 ceremony overhead on 31-1)

**Trap:** Full R2 party-mode → dev → G5 party-mode → G6 layered review for a 2-point peripheral story. The ceremony overhead exceeds the development cost.

**Fix:** Per `docs/dev-guide/story-cycle-efficiency.md`, single-gate review for non-foundation schema stories (31-3, 29-1, 29-3, 28-*, 30-2a, 30-5, 32-1, 32-2, 32-4). Dual-gate reserved for foundation or refactor stories (30-1, 30-3a/b, 30-4, 31-2, 31-4, 31-5, 29-2, 28-2, 32-3).

### C2. Triaging cosmetic NITs as carefully as MUST-FIXes (G6 on 31-1: 23 dismissed NITs)

**Trap:** Every finding gets a paragraph of triage rationale, including "rename this variable for clarity" and "add a trailing newline."

**Fix:** One-line DISMISS for cosmetic, DRY-refactor, pragma-style. Save the triage attention for MUST-FIX and SHOULD-FIX.

### C3. Re-deriving anti-patterns per story (31-1 Dev Notes authored its own anti-patterns section from scratch)

**Trap:** Each story spec has its own "anti-patterns dev agent will get wrong" section, re-authored per story. Duplicated knowledge, stale copies.

**Fix:** This document. Story specs reference it and add only story-specific anti-patterns on top.

## Category D — Refinement & iteration traps (inherited from Epic 27)

### D1. Cumulative iteration against a shrinking collection (G6 27-2 HIGH bug)

**Trap:** `drop_filters_in_order` was iterating over a `key_order` list AND mutating the underlying dict. The shrinking dict shifted the index on each iteration; `authority_tier_min` never got dropped.

**Fix:** Iterate over a frozen copy of the key_order at function entry. Never iterate over a mutating collection.

### D2. Filter that excludes the error path (G6 27-2 HIGH bug)

**Trap:** `_derive_overall_status_retrieval` filtered outcomes to `role == "primary"` before deriving overall status. Validation-role errors silently became invisible to the status aggregator.

**Fix:** Iterate all outcomes; branch on role inside the loop; apply role-specific severity rules. Never pre-filter by role when deriving aggregate status.

### D3. Writer with shared code path across two emission shapes (G6 27-2 SHOULD-FIX)

**Trap:** One writer function handles both "retrieval" and "locator" row shapes. A row tagged `code_path="locator"` lands in the retrieval branch because the discriminant is weak.

**Fix:** Strong `Literal["retrieval", "locator"]` discriminant on the writer signature; raise `ValueError` on row/code_path mismatch in BOTH directions.

### D4. Regression scrubber with brittle regex (G6 27-2 MH-1)

**Trap:** Scrubber regex matches hex strings of any length. In the wild, two-character hex substrings (file paths, timestamps) get incorrectly scrubbed.

**Fix:** Require hex length ≥16. Scope path-prefix patterns to known temp-dir roots.

## Category E — Marcus-duality surface traps (R1 amendment 17, R2 rider S-3)

### E1. Token leak in field descriptions

**Trap:** `Field(description="Marcus-Orchestrator emits this event at plan-lock")`. The internal duality leaks into the OpenAPI / JSON Schema doc that Maya eventually sees.

**Fix:** User-facing text says "Marcus". Scaffold's `test_no_intake_orchestrator_leak.py.tmpl` scans for this.

### E2. Token leak in error messages

**Trap:** `raise ValueError("only Marcus-Orchestrator may write to the lesson plan log")`. Maya sees this error and is confused.

**Fix:** "only Marcus may write to the lesson plan log". Internal code paths and module names can use the precise taxonomy; user-facing error strings cannot.

### E3. Token leak in SCHEMA_CHANGELOG

**Trap:** Changelog entries narrate the architecture: "Marcus-Intake handshake updated." The changelog is user-facing documentation.

**Fix:** Describe the behavioral change without naming the duality. "Pre-packet handshake updated" is fine.

---

## Category F — Handoff-integrity traps (P2-2 T11, party-mode 2026-06-20)

### F1. Mislabeling an in-scope regression as "pre-existing drift"

**Trap:** The dev handoff lists a RED test under "N unrelated pre-existing failures" without proving it. P2-2's handoff bucketed `test_33_1a_verbatim_extraction` among "15 unrelated contract failures" — but it was RED only on the P2-2 tree and GREEN on clean HEAD (the new 07G section broke it). It surfaced ONLY because the reviewer ran a clean-HEAD baseline diff. A mislabeled regression is worse than a bug: it misdirects the reviewer away from the defect.

**Fix (burden flips to dev):** any test the handoff labels "pre-existing / unrelated drift" MUST carry inline clean-HEAD evidence (`git stash`/checkout the baseline + run the node, showing RED there too). No attestation → the label is rejected and the failure is treated as in-scope by default. This is a T11-gate checklist item, not advisory. (Mirrors the Mary-A1 "annotate an exempted RED with proof, never assert it" discipline.)

### F2. Net-new `-gen` prose section vs a verbatim-extraction contract

**Trap:** Adding a brand-new generated section (07G) whose prose has no home in the frozen source pack silently breaks `test_33_1a_verbatim_extraction` (which requires every `-gen` section be verbatim-extractable from frozen v4.2). The green-light reasoned about schema-additivity and `-gen` regen but never asked "does this introduce a net-new `-gen` prose section?"

**Fix (green-light checklist question):** "Does this story add a net-new `-gen` prose section? If yes, register it in the verbatim-extraction closed allowlist (with its substitute invariant — L1 Check-9 determinism) BEFORE dev opens." Exclusion-list additions are party-mode governance; a meta-test must assert every excluded section is enrolled in Check-9 (the structural lock against a coverage hole).

---

## Category G — Liveness / evidence-integrity traps (vision-perceiver-real CLOSE, party-mode 2026-06-21)

### G1. Fixture-backed contract mistaken for live capability

**Trap:** A specialist ships a *contract* (Pydantic models + a provider seam) plus golden fixtures and a green test suite, and the closure record claims the capability is "real" — but no live model was ever wired. The vision specialist (P2-2) POSTed to a pinned `VISION_PROVIDER_ENDPOINT` that was never configured, defaulted to model id `vision-fixture-v1`, and carried a single hand-authored slide-01 golden artifact; P2-2 closed as "real PerceptionArtifact on disk." The literal claim ("artifact on disk") was true while the implied claim ("live perception capability") was false. The same root cause hit a *config* surface: the OpenAI catalog-snapshot test (`test_cascade_ids_in_openai_published_catalog`) was already RED on clean HEAD because `gpt-5.4` was added to the runtime config but never to the snapshot — a passing-elsewhere suite masking a stale tracker.

**Detection cue:** a passing test suite that never touches a live endpoint; a `-fixture-v*` model default; an unconfigured `_PROVIDER_ENDPOINT`/`_API_KEY` env var; golden-only on-disk artifacts cited as proof-of-live; a config/catalog snapshot that drifts from the runtime config it mirrors.

**Fix:** a closure claim of "real X" requires EITHER a key-gated live invocation with the response captured to disk, OR explicit wording that scopes it honestly ("contract + fixture; `<perceiver>` not yet live"). Sweep siblings for the signature (filed as deferred-inventory `believed-green-tracker-audit`). Live-API tests gate on key presence (`pytest.skip` when unreachable) but the production path itself must be live (operator directive: no mocks).

---

## Category H — Test-as-gate-integrity traps (P2-4c S1 T11, party-mode 2026-06-23)

### H1. Green test certifies a bug (shape-pin locks the wrong value)

**Trap:** A shape-pin / golden test that asserts the WRONG expected value is not a passing test — it is a *certified defect*. The suite goes green by encoding the bug as its own oracle, which inverts the purpose of the battery: green no longer means "correct," only "internally consistent with a wrong spec." Precedent: P2-4c S1 `derive_primary_name` collapsed `card_grid→top_down` (a correctly-detected layout silently becoming the DEFAULT, polluting the anti-vacuity ceiling) AND `test_reading_path_derivation.py` *pinned* `card_grid→top_down` as expected — so the bug was both shipped and test-locked.

**Detection cue:** a shape-pin whose expected value you cannot independently justify from the spec; a "stop over-claiming X" story whose battery has NO negative control asserting X is not emitted from non-X input (P2-4c S1 shipped green while over-firing `two_up_comparison`/`enumerated_process` on filler words — the suite was never capable of failing on the exact defect class the story targets).

**Fix:** HAND BACK — a compromised gate cannot certify its own repair (if the dev "just fixes the prod code," the fix either breaks the bad pin or is written to keep it green). Correct the assertion BUG-FIRST / RED-first: rewrite the pin to the correct value, prove it RED against the current tree, then fix the production code to green — this proves the pin has discriminating power and isn't re-locked to whatever the impl emits. For any "stop over-claiming" story, require negative-control fixtures as a binding pass-bar. A test that cannot fail on the bug it nominally guards is decorative.

---

## Meta-rule — Read this at T1, not at G6

If you find yourself hitting one of these traps during bmad-code-review, look back at T1. Did you read this document? If yes, did the trap you hit fit one of the categories above? If no, this catalog needs a new entry — flag it during review closure so it gets added.

The catalog exists to stop re-learning. When 31-1 landed, every finding here had been a surprise. They should not be surprises again.

---

## Changelog

| Version | Date | Source |
|---------|------|--------|
| v1 | 2026-04-18 | Initial harvest from 27-0 / 27-2 / 31-1 Dev Notes + G6 layered-review findings |
| v2 | 2026-06-20 | Category F (handoff-integrity) harvested from P2-2 T11 party-mode (F1 mislabeled-regression-as-preexisting-drift; F2 net-new-gen-section vs verbatim-extraction) |
| v3 | 2026-06-21 | Category G (liveness / evidence-integrity) harvested from vision-perceiver-real CLOSE party-mode (G1 fixture-backed-contract-mistaken-for-live-capability) |
| v4 | 2026-06-23 | Category H (test-as-gate-integrity) harvested from P2-4c S1 T11 HAND-BACK party-mode (H1 green-test-certifies-a-bug / shape-pin locks wrong value + missing negative controls) |
