# Codex dev-handoff — Arc 1a: manifest gate-split (Tier-2 pack bump)

**Story spec (authoritative — read fully first):** `_bmad-output/implementation-artifacts/spec-arc1a-manifest-gate-split.md`
**Status:** ready-for-dev · party-RATIFIED Tier-2 pack bump (Winston/Amelia/Murat unanimous; D2 resolved by PM tiebreaker).
**Cycle:** Codex runs T1–T10 (self-review); Claude does T11 (bmad-code-review + commit + flip done). Per NEW-CYCLE hand-off + John's binding routing for this substrate-impacting party-ratified story.

## What you are building
Decompose the THREE co-located voice/variant HIL gates so each becomes [content specialist node, `gate_code`+`fold_with` REMOVED] → [a NEW separate content-free gate node carrying `gate_code`+`fold_with`, FOLDED/no-op by default]:
- node `11` (elevenlabs, G4A, fold_with G4) → `11` content + new `11-gate` (G4A)
- node `11B` (elevenlabs, G4B, fold_with G4) → `11B` content + new `11B-gate` (G4B)
- node `07B` (quinn-r, G2B, fold_with G2C) → `07B` content + new `07B-gate` (G2B)
**Folded default behavior MUST be byte-identical to today on the content/decision plane.** This arc does NOT wake anything (that's Arc 1b) and does NOT touch the compiler's `production_gate_ids` derivation (the new folded gate node is auto-excluded — pin that it stays so).

## Acceptance contract
**All of A1–A14 in the spec are binding.** Highest-attention items:
- **A2 (Murat, escalation-closing):** the positional pin is STRUCTURAL over the manifest graph — "every node with a gate_code is content-free AND its sole immediate predecessor is a content-producing specialist" — NOT enumerated over today's 3 pairs.
- **A5 (Winston C1 + Murat C, non-negotiable):** define the folded-equivalence ORACLE explicitly — content/decision-plane byte-identity + an enumerated/frozen expected-delta set (node-count/HUD/telemetry), OR pin "folded gate nodes are telemetry-silent." Do not leave "byte-identical" ambiguous.
- **A6 (Murat B):** folded-equivalence golden + a DEMONSTRATED kill-the-mutant (a non-pass-through gate-node mutation reds the golden — show it).
- **A9 (Murat D):** a forced-membership replay fixture that pauses at a content-free gate node — proves the single-control-plane invariant LIVE before Arc 1b.
- **A11 (Winston C3 + Amelia):** per-slide cardinality — new gate node instantiated at the SAME per-slide cardinality; multi-slide equivalence test.
- **A12 (Winston C4, non-negotiable):** HUD/progress_map/L1 must key off gate_code/membership not node position/count; patch any structural consumer in this batch.
- **A13 (Amelia hard line):** resolve generator disposition at T1 — the new gate node renders via the generator's `if step.gate:` M→O path (NOT orchestration-only since gate=True). Confirm `pack.md.j2` + the gate-section template render a `specialist_id=None` content-free gate WITHOUT crash/malformed output. If a content-free-gate template branch is needed, that widens the bump → record it + bring the generator into frozen-at-ship discipline.

## T1 readings (mandatory)
`docs/dev-guide/pipeline-manifest-regime.md`; the manifest region (nodes 07/07B/07C, 10/11/11B incl. `insertion_after`/`sub_phase_of`/`dependency_projections`); `scripts/generators/v42/manifest.py` (`_audience`, `_orchestration_only_ids`) + `pack.md.j2` gate-section template; `app/manifest/{schema,compiler}.py` (`is_orchestration_only`, `production_gate_ids`); HUD/progress_map gate consumption.

## Verification (T9/T10)
`pytest tests/unit/manifest/ tests/integration/marcus/ tests/generators/ -q`; `check_pipeline_manifest_lockstep.py` (Tier-2 — pack-version-bump lockstep engages); `lint-imports`; `ruff check`. Retain the frozen prior-version pack (A14).

## T1 RESOLVED + the one design sub-decision (read the spec's "Implementation execution plan")
- **Manifest edit is mechanically specified** in the spec (node splits + exact edge reroutes; 07B/11/11B are single nodes — per-slide fan-out is the `0.6` subgraph's job, verified by a multi-slide run, NOT manifest replication).
- **A13 generator: the bump WIDENS into the v4.2 generator/pack.** A `gate=True` node is not `is_orchestration_only`, and `pack.md.j2` includes `step.template_name` per step — so a missing template crashes the renderer + lockstep. The new gate node inherits the original `pack_section_anchor` + gate section template. **THE ONE DESIGN SUB-DECISION:** the SPLIT CONTENT node (e.g. 07B-content = quinn-r eval, now gate=false but specialist_id set → NOT orchestration-only → still demands a template) — decide how it renders: (a) give it its own minimal content section, (b) broaden the orchestration/skip classification for specialist gate-content nodes (changes the shared predicate + L1 — higher blast radius), or (c) another disposition. This is atomically coupled to the manifest edit (lockstep-gated) and is NOT mechanical — resolve it (party input if it touches `is_orchestration_only`) BEFORE landing the manifest split.

## Ordering
Arc 1a ships + A5/A6/A9 green BEFORE Arc 1b (membership wake) opens. Arc 1b is a separate spec.
