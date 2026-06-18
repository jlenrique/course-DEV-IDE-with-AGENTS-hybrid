---
title: 'Arc 2 — membership wake of the variant-pick (G2B) + voice-pick (G4A) HIL gates'
status: ready-for-dev
arc: 2
supersedes_task: 'Arc 1b (membership-only wake) folded into this spec for the G2B+G4A gates'
parent: spec-arc1a-manifest-gate-split.md
gate_mode: dual-gate
execution_mode: claude-direct (operator override 2026-06-18 — NOT Codex dev-story; BMAD party-mode for reviews/approvals)
r_tier: R3
t11_tier: cross-agent
files_touched: ~10 (live-path production_runner + 2 new card models + manifest + schema predicate + tests)
lookahead_tier: 3
pack_tier: 'Tier-2 gate-semantics change — party green-light APPROVE-WITH-CONDITIONS 2026-06-18 (Winston BLOCK→conditions, Amelia + Murat APPROVE-WITH-CONDITIONS, John PM scope+process). Pack-NEUTRAL by design (AC-2 keeps woken gates pack-invisible → witness unchanged).'
---

## Purpose

Wake the two long-awaited human-in-the-loop content picks for Trial 4: the **variant pick** (G2B @ `07B-gate`) and the **voice pick** (G4A @ `11-gate`). Arc-1a split these into `[content specialist node] + [content-free folded gate node]` so a woken pause lands AFTER content; this arc flips them from folded (inert) to surfaced (pausing) via `production_gate_ids` membership and builds the decision-card path the runner needs to pause there without crashing.

**Design is binding, not open:** standalone membership wake per `spec-arc1a-manifest-gate-split.md` line 31 (John PM tiebreaker: "path (i) topology split → membership wake"). A9 of Arc-1a already proved the pause mechanism (forced-membership fixture pauses at the content-free gate after its content node ran). This arc closes the gaps the green-light review found: the runner's decision-card builder has no G2B/G4A branch (hard crash), and clearing `fold_with` would un-exclude the gate from the pack (L1 RED) without a predicate fix.

## Scope

**In:** wake G2B (`07B-gate`) + G4A (`11-gate`). **Out (deferred — `deferred-inventory.md`):** G4B (`11B-gate`, Input Package HIL — stays folded; `g4b-input-package-hil-wake`, post-Trial-4); any generalized/runtime wake-toggle (`generalized-membership-wake-toggle`); rich poll-surface (http/mcp transport) integration of `section_05_5`/`section_11` (Trial 4 is a CLI trial — the CLI decision-card flow is the surface; transport-parity wiring is a follow-on).

## Green-light conditions → Acceptance Criteria

### Wake mechanism (manifest + predicate)

- **AC-1. Manifest wake (membership).** Clear `fold_with` on `07B-gate` (was `G2C`) and `11-gate` (was `G4`) in `state/config/pipeline-manifest.yaml`. `11B-gate` (G4B) keeps `fold_with: G4` (stays folded). After: `production_gate_ids(manifest)` returns `{G1, G2B, G2C, G3, G4, G4A}` (G2B + G4A newly present; G4B absent). No other manifest field changes.

- **AC-2. Pack-invisibility of woken content-free gates (Murat §5 — KEYSTONE).** Introduce `is_content_free_gate(node) := node.specialist_id is None and node.gate and node.gate_code is not None` in `app/manifest/schema.py`, and redefine `is_pack_excluded := is_orchestration_only or is_content_free_gate`. Rationale: a woken HIL gate is a *runtime pause point*, not pack/HUD prose — it must stay pack-excluded whether folded OR woken, so clearing `fold_with` does NOT add a `07B-gate`/`11-gate` section to the rendered pack. `is_folded_gate` (fold_with-specific) is UNCHANGED — it remains the inert-when-folded predicate. Consumers of `is_pack_excluded` (generator, L1 `_orchestration_only_node_ids`, dc2 test) inherit the fix in lockstep.

- **AC-3. Pack-neutral + L1 green (no regen, no HUD rows).** Because AC-2 keeps the woken gates pack-excluded: the regenerated `-gen` witness is **byte-identical** to its committed form (assert via `render_pack` diff == empty), and `check_pipeline_manifest_lockstep.py` exits 0 with all 10 checks (set-equality #1, gate-bitmap #4, regeneration #9, frozen-SHA #10) green. No HUD `PIPELINE_STEPS` rows added; no pack section added. Confirms the wake is a runtime-plane-only change.

### Decision-card path (the hard crash — Winston/Amelia/Murat BLOCKER)

- **AC-4. `G2BCard` + `G4ACard` models.** Author `app/models/decision_cards/g2b.py::G2BCard` and `.../g4a.py::G4ACard` per the Pydantic-v2 schema checklist (`docs/dev-guide/pydantic-v2-schema-checklist.md`): `schema_version: Literal["v1"]`, UUID4 `card_id`/`trial_id`, `gate_id: Literal["G2B"]`/`["G4A"]` discriminator, tz-aware `created_at`, closed `verb: DecisionCardVerb` (approve|edit|reject), and the pick payload — `G2BCard.variant_candidates: list[VariantCandidate]` + `selected_variant_id` (from node `07B` quinn-r output); `G4ACard.voice_candidates: list[VoiceCandidate]` + `selected_voice_id` (from node `11` elevenlabs output). Register both in `decision_cards/__init__.py` + `_frozen_hashes.py`/`vocabulary.py` as the existing cards are.

- **AC-5. `_build_decision_card` branches.** Add `gate_id in {"G2B","G4A"}` branches to `production_runner.py::_build_decision_card` (currently raises `RuntimeError("unsupported production gate id")` for them). Each branch reads the preceding content node's output from run state (07B variants / 11 voices) and constructs the typed card. A woken pause at `07B-gate`/`11-gate` MUST emit a valid card, not raise.

- **AC-6. Pause presents the pick + verdict round-trips (CLI surface).** When the runner pauses at a woken gate, the emitted decision card carries the candidate list; the operator verdict (`approve` default / `edit` with a `selected_*_id`) is captured and `resume_from_verdict` (or the resume walker) advances past the gate (G2B→07C, G4A→11B). `storyboard_publisher` correctly no-ops for G2B/G4A (not in `STORYBOARD_GATES`) — pin it (AC-9).

### Tests (Murat §1–§2)

- **AC-7. Re-narrow folded-state pins (do NOT delete).** Update `tests/unit/manifest/test_folded_gate_split.py`: `test_folded_gates_are_inert_no_pause` keeps asserting **G4B/`11B-gate`** inert (drop G2B/G4A); `test_is_folded_gate_is_content_free_only` repoints the True assertions from `07B-gate`/`11-gate` (now woken, `is_folded_gate`=False) to `11B-gate` (still folded); add positive assertions that `is_content_free_gate(07B-gate)` and `is_pack_excluded(07B-gate)` stay True after waking. Flip `test_production_gate_ids_derived.py` expected sets and `test_gate_fold_manifest_emit.py` (`G2B`/`G4A` → `pause_point`).

- **AC-8. New woken-runner integration coverage.** Add tests: (a) pause-lands-after-content (predecessor of `07B-gate` is `07B`, of `11-gate` is `11` — confirm woken gates in the A2 structural population); (b) woken-runner pauses at G2B + G4A returning a paused envelope with a valid `G2BCard`/`G4ACard` (NOT `RuntimeError`, NOT `GateBypassError`); (c) resume-from-woken-gate advances past each; (d) the verdict round-trip selects a candidate.

- **AC-9. Storyboard-non-membership pin.** One test asserting G2B/G4A are intentionally NOT in `storyboard_publisher.STORYBOARD_GATES`, so a future roster edit can't silently demand a Gary pack at a variant/voice pick.

### Governance

- **AC-10. TW-7c-4 allowlist + scope fence green.** Add to `PERMITTED_PYTHON_DIFFS`: `app/marcus/orchestrator/production_runner.py` (already present), `app/models/decision_cards/g2b.py`, `g4a.py`, `app/manifest/schema.py` (already present), and the touched test files. The audit must stay green.

- **AC-11. Close gate (party-mode, per operator).** Before done: (i) full `tests/unit/manifest/` + `check_pipeline_manifest_lockstep.py` exit 0 + section_05_5/section_11 suites still green; (ii) **3-lane `bmad-code-review`** (Blind Spot + Edge Case + Acceptance Auditor) reaching ACCEPT; (iii) **party-mode close-review** (live-path Tier-2 — same ceremony Arc-1a got, not solo sign-off) confirming the wake behaves as specified + no fold regression on G4B; (iv) commit + push per cadence policy.

## Anti-goals

- **No G4B wake** (stays folded). **No** generalized wake-toggle. **No** http/mcp poll-surface transport wiring (CLI card is the Trial-4 surface). **No** change to `is_folded_gate` semantics (only `is_pack_excluded` gains the content-free-gate arm). **No** pack regeneration expected (AC-3 asserts byte-identical witness) — if the witness changes, AC-2 is wrong and must be fixed, not the pack re-committed.

## Design notes / T1 readiness

- **Card data source:** node `07B` (quinn-r, "Variant Selection Gate") and node `11` (elevenlabs, "Voice Selection HIL") run BEFORE their gate nodes (Arc-1a positioning) and emit variant/voice candidates into run state. `_build_decision_card` reads that state. Confirm the exact state keys the two content `_act`s emit at implementation T1 (grep their summary writers); if the content nodes do not yet emit a candidate list, the minimal Trial-4 card carries the content node's available output + a single default-selectable candidate (weed-clearing posture: the pick must function; rich candidate fidelity is a postmortem-harvest concern, not an at-gate blocker).
- **Existing poll surfaces** (`section_05_5` alias_of G2C, `section_11` alias_of G4) are generic shims re-presenting parent-card fields; they are NOT wired to the runner and are out of scope here (transport-parity follow-on). Do not delete them.
- **Verdict model:** reuse the `OperatorVerdict` / `DecisionCardVerb` machinery the existing gates use; G2B/G4A verdicts carry the `selected_*_id` on `edit`.
- **Required readings (T1):** `docs/dev-guide/pydantic-v2-schema-checklist.md`, `docs/dev-guide/pipeline-manifest-regime.md` (manifest is a block_mode_trigger_path), `docs/dev-guide/dev-agent-anti-patterns.md`, this spec's parent (`spec-arc1a-manifest-gate-split.md`).
- **Lockstep:** `state/config/pipeline-manifest.yaml` is a block_mode_trigger_path → run `check_pipeline_manifest_lockstep.py` after AC-1/AC-2; AC-3 asserts it stays green pack-neutral.

## Completion notes (AC-11 close gate, 2026-06-18)

3-lane `bmad-code-review` executed. Acceptance Auditor + Edge Case Hunter returned ACCEPT (no blockers). **Blind Spot Hunter caught 3 live-only-path gaps the offline/fake-key test posture hid** — all remediated:
- **BLOCKER #1 (live pause crash):** added `docs/conversational-gates/g2b.j2` + `g4a.j2` (the pre-gate-marcus render raised `FileNotFoundError` under the real-API condition Trial 4 runs in). + a structural guard `test_every_surfaced_gate_has_a_pre_gate_template` so a future woken gate without a template is caught.
- **MUST-FIX #2 (no operator CLI):** added `g2b_shim.py` + `g4a_shim.py`; extended `ACTIVE_TERMINAL_GATES`. + guard `test_every_surfaced_gate_has_a_cli_shim`.
- **MUST-FIX #3 (no pick content):** added `pick_context` to G2BCard/G4ACard, populated from the adjacent specialist evidence; card tests assert it is non-empty.
- **SHOULD-FIX #4 (m3_trial divergence):** documented `SUPPORTED_GATES` is not the live gate-coverage oracle (frozen M3 baseline; behavior unchanged by design).
- **Edge Case SHOULD-FIX (inverted comment):** corrected the pause-order comment to G1→G2B→G2C→G3→G4→G4A (G4 fidelity gate precedes the G4A voice pick by node index).
- **NIT #5 (GateFamilyId omits G2B/G4A):** benign now (transport-parity `alias_of` is deferred); flagged for the transport-parity follow-on so it isn't rediscovered by a validation crash.
- **NIT #6 (AC-4 named `_frozen_hashes.py`/`vocabulary.py`):** AC text overreached — those hold only the 4 legacy migrated hashes / token enums, NOT per-gate card types (g0/g2a/g5/g6 were never added either). The real registration (union + `__all__` in `__init__.py`) is complete; no action.

Verification: L1 exit 0 (pack-neutral, witness byte-identical); TW-7c-4 fence green; ruff clean; zero genuine regressions (only the pre-existing ambient `test_schema_pin` 2 fail, identical on clean HEAD). The live HIL path (pre-gate template → pause → G2B/G4A card with pick_context → operator CLI shim → resume) is now end-to-end complete for Trial 4.
