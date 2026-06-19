# Claude Code Goal Prompt — P2-2 PREP (through Codex-ingestion boundary)

> Paste the block below into Claude Code as a `/goal`. It drives **the Claude-orchestrator half** of the NEW CYCLE for Story P2-2: substrate-ground reality → pre-author the spec → run the **mandatory spawned Tier-3 party-mode green-light** → author the Codex dev prompt. It terminates **exactly** at the point where the Codex agent can ingest fully-prepped files. It does **NOT** write production code — Codex T1–T10 (= NEW CYCLE T5) is operator-run; Claude T11 is a separate later pass.

---

```
/goal Prepare Story P2-2 (PNG-grounded PerceptionArtifact + standalone vision node) of Epic P2 for Codex ingestion. Run NEW CYCLE tasks T1–T4 only: substrate-ground reality, pre-author the spec, secure a MANDATORY Tier-3 spawned-party-mode green-light, and author the Codex dev prompt. The goal is ACCOMPLISHED when, on branch fidelity-perception-arc-2026-06-19, the spec file is frozen at status: ready-for-dev with party consensus recorded, the Codex dev prompt is posted in its canonical location, tracking/inventory are annotated, and a Codex agent could begin dev with zero further questions. DO NOT write production code, dev tests, or flip any story to done in this goal — that is Codex (T5) + Claude T11 (T6), out of scope here.

## Context to load first (do not re-derive)
- docs/STATE-OF-THE-APP.md (§3 the regression, §8 forward path)
- _bmad-output/planning-artifacts/beta-phase-1-closure-ratification-2026-06-19.md §7 (P2 structure)
- _bmad-output/planning-artifacts/prd-perception-reading-path-fidelity.md (FRs/NFRs + §Domain + §AI-Pipeline architecture)
- _bmad-output/planning-artifacts/epics-perception-reading-path-fidelity.md (Story P2-2 ACs verbatim)
- _bmad-output/implementation-artifacts/spec-p2-1-fidelity-detector-red-first.md (esp. §Tier-3 Green-Light Disposition + §T11 Review & Close — P2-2's BINDING inheritances)
- _bmad-output/implementation-artifacts/cursor-goal-prompt-p2-2.md (the prior framing of P2-2 scope — reconcile, do not blindly copy)
- docs/dev-guide/pipeline-manifest-regime.md + docs/dev-guide/pydantic-v2-schema-checklist.md + docs/dev-guide/scaffolds/schema-story/
- skills/bmad-agent-content-creator/scripts/perception_contract.py (legacy producer shape to converge on)
- app/models/perception/perception_artifact.py (the P2-1 consumed contract to extend STRICTLY ADDITIVELY)
- The live G5 manifest node + app/specialists/quinn_r/_act.py::run_g5_checks + the tripwire test in tests/specialists/quinn_r/test_fidelity_detector.py

## What P2-2 is (the PRODUCER half)
A standalone `vision` manifest node that perceives each rendered slide PNG into a per-slide-addressable PerceptionArtifact (provenance + confidence/coverage), publishes it as the authoritative production-envelope contribution, wires perception into the G5 path, and turns the P2-1 detector "partly green" (real produced artifacts replace the hand-authored RED fixture). It does NOT rewire Pass-2 grounding — that is P2-3.

## BINDING inheritances from the P2-1 green-light + T11 (the spec MUST encode these; do NOT relitigate)
1. TIER-3, pack/manifest change → the pipeline-lockstep regime + pack-version bump bite HERE (P2-1 was lockstep-clean; P2-2 is NOT). The vision node touches state/config/pipeline-manifest.yaml (a block_mode_trigger_path) → spec mandates full L1 lockstep regime + reading pipeline-manifest-regime.md at Codex-T1.
2. Extend app/models/perception/perception_artifact.py STRICTLY ADDITIVELY — Optional/defaulted fields only; NO rename or make-required of P2-1 fields; keep extra="forbid"; P2-1 fixtures + shape-pin test stay green. Add: per-claim provenance (source ∈ {png-grounded, brief-expectation, not-covered}) as Field(exclude=True)+SkipJsonSchema (absent from emitted JSON Schema); richer confidence/coverage. Four-file lockstep (model + emitted JSON Schema + shape-pin test + golden fixture); the lockstep test asserts the deliberate model-vs-schema divergence on provenance (NOT field-equality).
3. THE TRIPWIRE FLIP (load-bearing): wiring perception into the G5 manifest node WILL make tests/specialists/quinn_r/test_fidelity_detector.py::test_tripwire_g5_manifest_does_not_yet_supply_perception FAIL — BY DESIGN. The spec MUST instruct Codex to: (a) add perception_artifacts to the G5 node's dependency_projections in the manifest; (b) flip app/specialists/quinn_r/_act.py::run_g5_checks from the dormant-skip branch to ENFORCE (delete the "perception-not-wired" dormant status); (c) delete/replace the tripwire test with a positive test asserting perception IS now projected + enforced. Dormancy ends here.
4. ONE perception authority: the vision node is the SOLE owner of the vision-provider dependency; published via ProjectionSpec / the A-R3 dependency-projection seam; any run-dir disk copy is audit-only. Per-slide addressable by slide identity; uncovered slides carry an explicit not-covered state (never a missing key). Import-linter: Pass-2 + the detector import only app.models.perception (never the provider); the vision node is the one module that imports the provider.
5. Vision-step robustness: pinned model id + deterministic decode + a golden-image repeatability test within per-field comparator tolerances (bbox IoU≥θ, element-set Jaccard=1.0, figure/text edit-distance≤d); silent-drift canary (out-of-CI, non-blocking); seam failure taxonomy (raised/timeout, low-confidence, schema-invalid → mapped outcomes, never silent fallback to brief); stated vision-step retry policy distinct from the detector's no-retry.
6. Two-lane CI: deterministic detector + schema tests = BLOCKING; live/golden vision repeatability = QUARANTINED, non-blocking, alert-only. Never relax the detector gate to absorb vision flake.
7. Sandbox-AC: live vision round-trip dev-agent ACs invoke the provider IN-PROCESS via a shipped dep (prefer a thin pinned-endpoint httpx client over a vendor SDK) with pytest.skip when the key/service is unreachable; golden tests run offline against a recorded fixture (no skip). NO operator CLIs in dev-agent ACs. Run scripts/utilities/validate_migration_story_sandbox_acs.py mentally/structurally against the spec's AC blocks before freezing.
8. AC-12 follow-on: a standing test must prove the detector is RED on the REAL PRODUCED PerceptionArtifact for the $5.2T slide (not just the hand-authored fixture) — now possible because the producer exists.
9. DoD: grounding-leg deferred-inventory entry `fidelity-metric-blind-to-perception-regression` STAYS OPEN (struck only at P2-3); the spec names the P2-2 cross-trial harvest as a Codex deliverable; sprint annotation added.

## Task sequence (T1–T4 — Claude orchestrator only)
T1. SUBSTRATE-GROUND (run the substrate, do NOT author spec-as-paper): read the live manifest G5 node + dependency_projections machinery, the existing perception_contract.py + sensory-bridges perceive(), the envelope/ProjectionSpec / A-R3 seam, the irene §07/§08 seam, the P2-1 consumed contract + tripwire test, and the schema-story scaffold. Capture concrete file:line findings and the exact edit sites.
T2. PRE-AUTHOR _bmad-output/implementation-artifacts/spec-p2-2-perception-artifact-vision-node.md with the frozen-after-approval structure: Intent / Boundaries (in-scope vs P2-3) / Substrate findings (file:line) / Code Map / Tasks+AC (each AC tagged dev-agent vs operator-gated, sandbox-AC-clean) / Verification gates / the 9 binding inheritances encoded / r_tier+t11_tier+files_touched+lookahead_tier declared. Set frontmatter status: awaiting-party-green-light.
T3. MANDATORY Tier-3 PARTY-MODE GREEN-LIGHT — spawn Winston (architect), John (PM), Murat (test architect), Mary (analyst), Amelia (dev) as REAL subagents via bmad-party-mode with the full spec draft. They must validate: the manifest/pack version tier + bump; the tripwire-flip plan; the strictly-additive schema + four-file-lockstep contract; the single-authority/import-isolation seam; the vision robustness + two-lane CI + sandbox-AC design. Reach consensus; apply ALL amendments into the spec; record the green-light disposition (who/what/verdict) in a §Tier-3 Green-Light Disposition block; flip status: ready-for-dev. On impasse follow the CLAUDE.md chain: Dr. Quinn synthesis → John tiebreaker → operator.
T4. AUTHOR _bmad-output/implementation-artifacts/codex-dev-prompt-p2-2-perception-artifact-vision-node.md: required reading list, Codex-T1 checkpoints (incl. the lockstep regime + pydantic checklist + scaffold), files-in-scope, the explicit tripwire-flip instructions, the do-NOT-modify list (P2-1 fixtures, _RETRYABLE_DISPATCH_TAGS, etc.), the dev-agent-vs-operator AC split, and the RED-first ordering. Post both files in their canonical implementation-artifacts location.

## Definition of done for THIS goal (the Codex-ingestion boundary)
- spec-p2-2-...md exists, frozen at status: ready-for-dev, with the green-light disposition + all 9 binding inheritances + sandbox-clean AC split recorded.
- codex-dev-prompt-p2-2-...md exists, self-contained enough that Codex begins dev with zero further questions.
- Party-mode consensus is documented (or the impasse chain was run to resolution).
- Tracking annotated (sprint-status / next-session-start-here as applicable); deferred-inventory grounding-leg entry confirmed STILL OPEN.
- Commit the two prep docs (+ tracking) on the branch; push per cadence policy. Do NOT merge to master (scoped branch).

## Guardrails
- This goal STOPS at the Codex-ingestion boundary. Do NOT write app/ production code, do NOT author dev tests, do NOT flip P2-2 to done. If tempted to "just implement it," STOP — that breaks NEW CYCLE.
- Do NOT relitigate P2-1 ratified decisions (Edge-1 dormant posture, money-normalization, etc.) — inherit them.
- A real production run may legitimately FAIL fidelity after P2-2 wires perception+enforcement (the detector finally sees the real defect); the Pass-2 grounding REPAIR is P2-3. That honest-failure state is expected and is NOT a P2-2 bug.
- Operator authority overrides at any gate.

## Follow-on (do not start here)
After Codex lands P2-2 (T5) and Claude completes T11 (T6, separate goal), re-run this same goal pattern for Story P2-3 (Pass-2 consumes perceived visuals — the regression fix). P2-3 prep is BLOCKED until the producer exists, because its substrate-grounding reads the real emitted PerceptionArtifact at the irene/graph.py + pass_2_template.py edit sites.
```

---

**Authored 2026-06-19 by Claude orchestrator after P2-1 close (`43581d2`), per operator request for a Claude Code goal statement driving NEW CYCLE T1–T4 to the Codex-ingestion boundary. Companion to `cursor-goal-prompt-p2-2.md` (which is the Codex-side T5 driver).**
