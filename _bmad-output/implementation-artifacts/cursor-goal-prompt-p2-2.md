# Cursor Goal Prompt — P2-2 (PNG-grounded PerceptionArtifact + vision node)

> Paste the block below into Cursor as a `/goal`. It drives the next story (P2-2) of Epic P2 from the current state through full implementation, testing, and validation, following the project's NEW CYCLE (Claude pre-author → Codex T1-T10 → Claude T11) and BMAD sprint-governance.

---

```
/goal Take Story P2-2 (PNG-grounded PerceptionArtifact + standalone vision node) of Epic P2 from current state through full implementation, testing, and validation. Use spawned bmad-party-mode for the mandatory Tier-3 pre-dev green-light and for any major decision/impasse. Pre-author the spec + Codex dev-prompt; hand dev+test creation to the Codex agent; then run Claude T11 (bmad-code-review 3-lane + remediation + commit + flip done). The goal is accomplished when P2-2 is committed done on branch fidelity-perception-arc-2026-06-19 with the validation gates below all green.

## Context to load first (do not re-derive)
- docs/STATE-OF-THE-APP.md (§3 the regression, §8 forward path)
- _bmad-output/planning-artifacts/beta-phase-1-closure-ratification-2026-06-19.md §7 (P2 structure)
- _bmad-output/planning-artifacts/prd-perception-reading-path-fidelity.md (FRs/NFRs + §Domain + §AI-Pipeline architecture)
- _bmad-output/planning-artifacts/epics-perception-reading-path-fidelity.md (Story P2-2 ACs)
- _bmad-output/implementation-artifacts/spec-p2-1-fidelity-detector-red-first.md (esp. §Tier-3 Green-Light Disposition + §T11 Review & Close — P2-2's binding inheritances)
- docs/dev-guide/pipeline-manifest-regime.md + docs/dev-guide/pydantic-v2-schema-checklist.md + docs/dev-guide/scaffolds/schema-story/
- skills/bmad-agent-content-creator/scripts/perception_contract.py (the legacy producer shape to converge on)

## What P2-2 builds (per §7 + the P2-1 disposition)
P2-2 is the PRODUCER half: a standalone vision node that perceives each rendered slide PNG into the PerceptionArtifact, wires perception into the production G5 path, and turns the P2-1 detector "partly green" (real produced artifacts replace the hand-authored RED fixture). It does NOT rewire Pass-2 grounding (that is P2-3).

## BINDING inheritances from the P2-1 green-light + T11 (do NOT relitigate)
1. TIER-3, pack/manifest change → THIS is where the pipeline-lockstep regime + pack-version bump actually bite (P2-1 was lockstep-clean; P2-2 is NOT). Party-mode green-light is MANDATORY BEFORE dev. The vision node touches state/config/pipeline-manifest.yaml (a block_mode_trigger_path) → full L1 lockstep regime + read pipeline-manifest-regime.md at T1.
2. Extend app/models/perception/perception_artifact.py STRICTLY ADDITIVELY — Optional/defaulted fields only; NO rename or make-required of P2-1 fields; keep extra="forbid"; P2-1 fixtures + shape-pin test must stay green. Add: per-claim provenance (source ∈ {png-grounded, brief-expectation, not-covered}) as Field(exclude=True)+SkipJsonSchema (absent from emitted JSON Schema); richer confidence/coverage. Four-file lockstep (model + emitted JSON Schema + shape-pin test + golden fixture); the lockstep test asserts the deliberate model-vs-schema divergence on provenance (NOT field-equality).
3. THE TRIPWIRE FLIP (load-bearing): wiring perception into the G5 manifest node WILL make tests/specialists/quinn_r/test_fidelity_detector.py::test_tripwire_g5_manifest_does_not_yet_supply_perception FAIL — that is BY DESIGN. P2-2 MUST: (a) add perception_artifacts to the G5 node's dependency_projections in the manifest; (b) flip app/specialists/quinn_r/_act.py::run_g5_checks from the dormant-skip branch to ENFORCE (delete the "perception-not-wired" dormant status; the detector now runs on real perception); (c) delete/replace the tripwire test with a positive test asserting perception IS now projected + enforced. Dormancy ends here.
4. ONE perception authority: the vision node is the SOLE owner of the vision-provider dependency; published as the authoritative production-envelope contribution threaded via ProjectionSpec / the A-R3 dependency-projection seam; any run-dir disk copy is audit-only. Per-slide addressable by slide identity; uncovered slides carry an explicit not-covered state (never a missing key). Import-linter: Pass-2 + the detector import only app.models.perception (never the provider); the vision node is the one module that imports the provider.
5. Vision-step robustness: pinned model id + deterministic decode + a golden-image repeatability test within per-field comparator tolerances (bbox IoU≥θ, element-set Jaccard=1.0, figure/text edit-distance≤d); silent-drift canary (out-of-CI, non-blocking); seam failure taxonomy (raised/timeout, low-confidence, schema-invalid → mapped outcomes, never silent fallback to brief); stated vision-step retry policy distinct from the detector's no-retry.
6. Two-lane CI: deterministic detector + schema tests = BLOCKING; live/golden vision repeatability = QUARANTINED, non-blocking, alert-only. Never relax the detector gate to absorb vision flake.
7. Sandbox-AC: live vision round-trip dev-agent ACs invoke the provider in-process via a shipped dep (prefer a thin pinned-endpoint httpx client over a vendor SDK) with pytest.skip when the key/service is unreachable; golden tests run offline against a recorded fixture (no skip). No operator CLIs in dev-agent ACs.
8. AC-12 follow-on: a standing test now proves the detector is RED on the REAL PRODUCED PerceptionArtifact for the $5.2T slide (not just the hand-authored fixture) — possible because the producer now exists.
9. DoD (§6): grounding-leg deferred-inventory entry `fidelity-metric-blind-to-perception-regression` STAYS OPEN (struck only at P2-3); file the P2-2 cross-trial harvest; sprint annotation.

## Task sequence (NEW CYCLE)
T1. Substrate-ground the spec: RUN the substrate (read the manifest G5 node, the existing perception_contract.py + sensory-bridges perceive(), the envelope/ProjectionSpec machinery, the irene §07/§08 seam, the P2-1 contract). Do NOT author spec-as-paper.
T2. Pre-author _bmad-output/implementation-artifacts/spec-p2-2-perception-artifact-vision-node.md (frozen-after-approval Intent / Boundaries / Substrate findings / Code Map / Tasks+AC / Verification), status: awaiting-party-green-light.
T3. MANDATORY Tier-3 party-mode green-light (spawn Winston/John/Murat/Mary/Amelia as real subagents) — validate the manifest/pack tier + the tripwire flip plan + the additive-schema contract + the seam/robustness design; reach consensus; apply ALL amendments into the spec; flip status: ready-for-dev. If impasse → Dr. Quinn → John tiebreaker → operator (CLAUDE.md chain).
T4. Author _bmad-output/implementation-artifacts/codex-dev-prompt-p2-2-perception-artifact-vision-node.md (required reading, T1 checkpoints incl. the lockstep regime, files-in-scope, the tripwire-flip instructions, do-not-modify list). Post both files in their canonical location.
T5. Hand off to Codex (operator runs it): Codex T1-T10 (dev + tests) → ready-for-review handoff.
T6. Claude T11: bmad-code-review 3-lane (Blind/Edge/Auditor) on the actual code; remediate must-fixes; run the FULL battery yourself (do not trust the handoff's test list — explicitly include tests/parity/, tests/integration/marcus/, tests/audit/, lockstep, lint-imports, ruff); verify the tripwire flip + additive-schema-keeps-P2-1-green; commit + flip P2-2 done; push.

## Validation gates (all must be green before done)
- New P2-2 suite + the full quinn_r + parity + audio + taxonomy + TW-7c-4 suites pass.
- tests/integration/marcus/ green (no new failures).
- The tripwire test is replaced by a positive enforce test; the detector is RED on the real produced $5.2T artifact (AC-12 follow-on) and GREEN on real faithful slides.
- P2-1 fixtures + shape-pin still green (additive extension proven).
- check_pipeline_manifest_lockstep.py exit 0 (L1 regime); lint-imports kept/0-broken (new provider-isolation contract); ruff clean on touched files.
- Pack version bumped per the regime; TW-7c-4 allowlist extended for P2-2 paths.
- Push at least once; do not merge to master (scoped branch).

## Guardrails
- Do NOT make a full production run green if real narration still hallucinates — P2-2 wires perception + enforcement, but the Pass-2 grounding REPAIR is P2-3. A real run may now legitimately FAIL fidelity (the detector finally sees the real defect) — that is the expected, honest state at P2-2 close, and is the whole point.
- Operator authority overrides at any gate.
```

---

**Authored 2026-06-19 by Claude orchestrator after P2-1 close (`43581d2`). P2-2 is the next story; it is where the Tier-3 pack/manifest governance and the tripwire flip activate.**
