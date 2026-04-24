# Research Knobs Guide

Purpose: define the operator-facing knobs that control Tracy evidence behavior, where each knob is authored, and how preflight enforces safe usage.

## Canonical Terms (Do Not Conflate)

- evidence_bolster: run-constants operator knob (layer 1), boolean, default false.
- evidence_bolster_active: Irene intake runtime state projection (layer 2), derived from run-constants and consumed by intake narration branching in the sibling intake story.
- cross_validate: Tracy RetrievalIntent mechanical action flag (layer 3), set by corroborate posture based on bolster state.

These three fields are related but not interchangeable. `evidence_bolster` is the operator-authored control, `evidence_bolster_active` is intake-layer state, and `cross_validate` is the retrieval action.

## Canonical Knobs

### 1) run-constants.yaml knob

- Name: evidence_bolster
- Type: boolean
- Default: false
- Location: bundle-root run-constants.yaml
- Owner: Marcus run-constants contract (PR-RC + run_constants parser)

Behavior:

- false: Tracy corroborate uses a single-provider path (scite only).
- true: Tracy corroborate requests cross-validation with provider hints scite + consensus.

Provider strategy policy (v1):

- bolster false: `cross_validate=false`, `provider_hints=[scite]`
- bolster true: `cross_validate=true`, `provider_hints=[scite, consensus]`

Safety gate:

- If evidence_bolster is true, Consensus credentials must be present in environment: CONSENSUS_API_KEY or CONSENSUS_USER_NAME + CONSENSUS_PASSWORD.
- APP readiness and preflight receipt fail closed when key is missing.

## Runtime Propagation Path

1. Run constants are parsed from run-constants.yaml.
2. Marcus fanout includes evidence_bolster in the Irene->Tracy bridge lesson-plan payload.
3. Bridge includes evidence_bolster in corroborate briefs.
4. Tracy posture dispatcher sets retrieval intent:
  - cross_validate: true when bolstered
  - provider_hints: [scite, consensus] when bolstered; [scite] otherwise
5. Intake-layer consumer state (`evidence_bolster_active`) is owned by the sibling intake story and is intentionally tracked separately from the run-constants knob.

## Validation Commands

- Readiness with bundle constants:
  - .venv/Scripts/python.exe -m scripts.utilities.app_session_readiness --with-preflight --bundle-dir <bundle-path>
- Preflight receipt:
  - .venv/Scripts/python.exe -m scripts.utilities.emit_preflight_receipt --output <bundle-path>/preflight-results.json --bundle-dir <bundle-path> --with-preflight

Exit semantics:

- Missing Consensus credentials (CONSENSUS_API_KEY or CONSENSUS_USER_NAME + CONSENSUS_PASSWORD) with evidence_bolster=true returns exit code 30.

## Authoring Rules

- Use canonical snake_case field name evidence_bolster.
- Keep evidence_bolster, evidence_bolster_active, and cross_validate naming synchronized in docs, tests, and run-constants parsing.
- Do not use these names as synonyms in docs or tests; each name maps to exactly one layer.
