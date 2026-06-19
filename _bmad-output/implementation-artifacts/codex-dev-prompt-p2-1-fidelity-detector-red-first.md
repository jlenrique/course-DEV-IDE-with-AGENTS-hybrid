# Codex dev-story prompt — P2-1 (Fail-loud fidelity detector — RED-first vs the $5.2T evidence)

**Cycle:** Claude spec (Tier-3 party green-lit 2026-06-19, AMENDMENTS LOCKED) → Codex T1-T9 + T10 self-review → Codex handoff at `_bmad-output/implementation-artifacts/_codex-handoff/p2-1-fidelity-detector-red-first.ready-for-review.md` → Claude T11 `bmad-code-review` → Claude commit + flip done.
**Epic:** P2 (Perception + Reading-Path Narrative-Grounding Restoration). **Story:** P2-1. **Gate-mode:** dual. **Tier:** Tier-3 (party green-light DONE — see spec §Tier-3 Green-Light Disposition).
**Authority:** `beta-phase-1-closure-ratification-2026-06-19.md §7`; `epics-perception-reading-path-fidelity.md` (Story P2-1).
**Dispatch ordering:** P2-1 is FIRST in Epic P2. It lands the detector RED; it does NOT make a run green (that's P2-3). Do NOT dispatch P2-2/P2-3 until P2-1 closes.

---

```
Run bmad-dev-story on Story P2-1 (Epic P2; dual-gate; fail-loud fidelity detector, RED-first).

Spec: `_bmad-output/implementation-artifacts/spec-p2-1-fidelity-detector-red-first.md`
The spec's <frozen-after-approval> Intent/Boundaries/Edge-Case Matrix AND the §Tier-3 Green-Light Disposition (binding amendments C1-C3, M1-M3, F1-F6, CL1, G2-G4) are CONTRACT. Honor them verbatim. The design is LOCKED by a unanimous 5/5 party green-light — do not re-litigate placement, the contract home, Class-A mechanics, or the green-corpus approach.

## Required reading (T1, before any code)
1. The spec (whole file) — especially §Tier-3 Green-Light Disposition (the binding amendments) and §Substrate findings.
2. `_bmad-output/planning-artifacts/epics-perception-reading-path-fidelity.md` — Story P2-1 ACs + the FR coverage map.
3. `beta-phase-1-closure-ratification-2026-06-19.md §7` — the WHY (detector RED-first, two-sided, Class-A, own non-folded story).
4. `skills/bmad-agent-content-creator/scripts/perception_contract.py` — the legacy perception artifact shape your `PerceptionArtifact` field names MUST match (no third vocabulary).
5. `app/specialists/quinn_r/_act.py:134-180` (`run_g5_checks`) — the G5 host; note `narration_segments` is `list[dict]` read via `seg.get(...)`.
6. `app/specialists/quinn_r/quality_control_dispatch.py:17-35` (`_content_error` factory + the dual-based G5 errors + tags).
7. `app/models/state/` (e.g. `run_state.py`) — the import pattern + Pydantic-v2 idioms to mirror for `app/models/perception/`.
8. `docs/dev-guide/pydantic-v2-schema-checklist.md` + `docs/dev-guide/scaffolds/schema-story/` — for the typed contract.
9. The evidence: `_bmad-output/implementation-artifacts/evidence/narration-hallucinates-illustration-slide01-2026-06-19.png` (rendered: $4.5T/74%/3x + building photo) and `runs/d7ad4dac-7e65-4bde-9cb2-88a13fed2adc/irene-pass1.md:8` (the $5.2T hallucination narration string).

## T1 hard checkpoints
- Baseline commit (see spec frontmatter `baseline_commit`) is an ancestor of HEAD; branch `fidelity-perception-arc-2026-06-19`.
- Run the L1 pipeline-manifest check (`scripts/utilities/check_pipeline_manifest_lockstep.py`) and CONFIRM exit 0. Per the spec, P2-1's paths are NOT in `block_mode_trigger_paths` (lockstep-clean); if your grep shows otherwise, STOP and surface.
- Confirm `_RETRYABLE_DISPATCH_TAGS` (in `app/marcus/orchestrator/production_runner.py`) is allowlist-based; you will NOT modify it.
- Confirm `runs/` is untracked (`git ls-files runs/` ≈ 1 file) — you MUST commit green-corpus fixtures into `tests/fixtures/...`, never point tests at `runs/`.

## Files in scope
**New:**
- `app/models/perception/perception_artifact.py` (typed contract — C1/C16; `extra="forbid"`; legacy-identical field names; provider-free).
- `app/specialists/quinn_r/fidelity_detector.py` (pure `detect_fidelity(narration_segments: list[dict], perception_artifacts) -> verdict`).
- `tests/specialists/quinn_r/test_fidelity_detector.py`.
- `tests/fixtures/specialists/quinn_r/fidelity/` — `slide01-red.json`, `green-corpus/*`, `green-corpus-manifest.json`, `seeded-defects/*` (ALL committed + content-hash frozen).
**Modified:**
- `app/specialists/quinn_r/quality_control_dispatch.py` (add `FidelityError` via `_content_error`; tags `quinn_r.g5.fidelity-orphan-reference` / `quinn_r.g5.fidelity-figure-contradiction`).
- `app/specialists/quinn_r/_act.py` (`run_g5_checks` invokes `detect_fidelity`; absent/low-confidence/not-covered perception ⇒ non-conformance).
- `pyproject.toml` (`[tool.importlinter]` forbidden contract; 13→14).
- `docs/trials/cross-trial-learnings.md` (P2-1 DoD harvest — see below).
**Do NOT modify:**
- `app/marcus/orchestrator/production_runner.py::_RETRYABLE_DISPATCH_TAGS` (non-retryable by absence).
- The vision producer / `sensory_bridges_dispatch` (P2-2 territory). Do NOT build a vision node. Do NOT repair Pass-2 (P2-3). Do NOT make a run green.
- The grounding-leg deferred-inventory entry — **do NOT strike it** (G4; strike waits for P2-3).

## Critical implementation notes (amendment-locked)
- **C1/C16 contract home:** `app/models/perception/perception_artifact.py`, NOT under `quinn_r/`. Field names byte-identical to `perception_contract.py` (`confidence, visual_elements, extracted_text, layout_description, slide_title, text_blocks, artifact_path, slide_id, card_number`) + a `coverage` enum (`perceived|low-confidence|not-covered`). `extra="forbid"`. A shape-pin test fixes the contract P2-2 will extend additively.
- **C3 ground-truth direction (deep):** perceived artifact = AUTHORITY (what the PNG renders: $4.5T/74%/3x/photo); narration = CLAIMANT. The `slide01-red.json` perceived leg derives from the PNG's rendered values — NEVER from `irene-pass1.md` (plan-text and narration can agree while both diverge from the render; sourcing ground-truth from plan-text reintroduces the blindness).
- **M1 Class-A mechanics:** `FidelityError` via the existing `_content_error` factory → dual base `(SpecialistDispatchError, ValueError)`. This gives a recoverable fail-loud error-pause (NOT a crash — a bare ValueError reintroduces the cycle-5 crash). Non-retryable = the tag is simply absent from `_RETRYABLE_DISPATCH_TAGS`. Do not touch that frozenset.
- **M3 idempotent re-eval:** the detector must hold no latched state — re-running on a corrected artifact returns clean. Pin with a test (this is P2-3's clearing contract).
- **F1/F3/F5 fixtures:** commit everything under `tests/fixtures/specialists/quinn_r/fidelity/`. `slide01-red.json` cites `runs/d7ad4dac.../irene-pass1.md:8` + the PNG path in a comment/metadata field. `green-corpus-manifest.json` records per-entry source run id + slide id + content hash + curator + faithful-criterion. The curator label is operator/party-owned — author the manifest with a `curator: "operator (pending sign-off)"` placeholder and FLAG in the handoff that operator sign-off on the faithful labels is required before T11 close.
- **F4 seeded defects:** generate programmatically as single-mutation injections (figure-swap, element-drop, magnitude-drift) over the frozen green corpus — not bespoke fixtures.
- **F6/AC-12:** a standing test asserts RED on the real committed evidence (cited narration string + PNG-derived perceived leg).
- **CL1/AC-14:** the fidelity-bearing-vs-non-visual classifier gets its own labeled two-sided test with asserted confusion counts.
- **G2 import-linter:** `forbidden` contract, source `app.specialists.quinn_r.fidelity_detector`, forbidden `app.specialists.quinn_r.sensory_bridges_dispatch`. The detector imports only `app.models.perception` + stdlib; the contract module is provider-free.
- **AC-11/AC-12 anti-trap:** P2-1 stays RED on the committed-evidence fixture; the green corpus stays GREEN; do NOT soften thresholds to make the evidence pass — that's the tuned-to-buggy-output trap the whole story exists to prevent.

## Verification (T9 self-G6)
- `pytest tests/specialists/quinn_r/test_fidelity_detector.py -q` — RED-first proven (incl. AC-12 real-evidence); two-sided green (FP 0); recall on seeded defects; classifier confusion-metric; idempotent re-eval; single-source (contradiction + second-inference-injection); determinism.
- `pytest tests/specialists/quinn_r/ tests/contracts/ -q -p no:randomly` — no G5-family regression.
- `lint-imports` → 14 kept / 0 broken. `check_pipeline_manifest_lockstep.py` → exit 0. `ruff check` clean on touched files.

## T10 ready-for-review handoff
Record: each new test's intent + result; confirmation the green corpus is committed (clean-clone reproducible) with manifest; the curator-sign-off-pending flag; lint-imports 14/0; lockstep exit 0; and an explicit statement that the detector is RED on the committed evidence and the suite did NOT make a production run green (AC-11 held).

## Cycle-close discipline
Claude T11 = `bmad-code-review` (3-lane) + commit + flip done + the P2-1 DoD harvest (cross-trial-learnings entry, NO inventory strike). After P2-1 closes, dispatch P2-2 (vision node + PerceptionArtifact producer + full schema richness) — which is where the Tier-3 pack/manifest version bump + lockstep regime actually apply.
```

---

**Authored 2026-06-19 by Claude orchestrator. Tier-3 party green-light COMPLETE (5/5 APPROVE-WITH-AMENDMENTS, applied). Ready for Codex dispatch — P2-1 is the first story of Epic P2; do not dispatch P2-2/P2-3 until P2-1 closes.**
