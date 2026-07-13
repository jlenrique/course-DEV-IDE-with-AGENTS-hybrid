---
baseline_commit: 83df9e9ceffaa0f5a084835e0c322343ac281067
---

# Story 38.3b: Graph topology band — orchestrator and deterministic stubs

Status: done

## Story

As the Marcus-SPOC production runtime,
I want a manifest-driven four-node workbook band between operator handoff and the deterministic workbook renderer,
so that later workbook writers and demand-driven research have stable production seams proven offline before live behavior lands.

## Dependency Position

Story 38.0 is done. This is the next required slice:

`38.0 -> 38.3b -> {36.*, 37.1, 37.2a, 37.3, 37.4} -> 38.3a -> 38.1 -> 37.2b -> 39.1 -> 38.2 -> 39.2 -> 40.1`

Closing 38.3b unlocks only the writer set shown above.

## T1 Regime Decision

The Epic-38 graph-shape party ratified this topology. It is Tier-2 governed structural work but, under the later determinism-witness policy, a **v4.2-lineage terminal-sidecar refinement**, not v4.3. Keep manifest versions uniform; add no learning event, gate, or HUD step; regenerate only the v4.2 `-gen` witness; preserve frozen mapping-axis v4.2 and production-canonical v5 byte-for-byte.

`07W.1` and `07W.3` carry exactly `app/marcus/orchestrator/workbook_writer_model_config.yaml`, parsed as `SpecialistModelConfig` with `specialist_id: workbook_writer`, `default_model: gpt-5`, `per_node_overrides: {}`, and `temperature_default: 0.2`. `gpt-5` must validate against the current registry. The nodes intentionally retain `specialist_id: null`: this config is future live-writer metadata, never a dispatch identity in 38.3b. This stub story must not invoke it live. `07W.2` and `07W.4` stay model-free.

## Acceptance Criteria

1. **Exact topology:** add `07W.1`–`07W.4` so the chain is exactly `15 -> 07W.1 -> 07W.2 -> 07W.3 -> 07W.4 -> 07W -> __end__`. All four are gate-free, HUD-hidden, `sub_phase_of: "07W"`, v4.2-lineage orchestration nodes with no learning events. `.1/.3` share the writer model config; `.2/.4` use null. Terminal `07W` remains registered, model-free, deterministic, and semantically unchanged.

2. **Composition owns the entire band:** the workbook component owns all five IDs and bumps its fragment version. With workbook selected, all five and the exact chain survive. With workbook deselected, all five disappear and `15 -> __end__` is bridged with no dangling or deck-owned band node.

3. **Deterministic/idempotent stub seam:** add one orchestrator-owned `workbook_wiring` seam keyed by the four node IDs. The hook is unconditional whenever either walk reaches a band node—independent of OpenAI credentials, live flags, or `allow_offline_cost_report`; only later injected implementations may choose model dispatch. Offline defaults execute deterministic stubs exactly once in order. Idempotency means checking exact `(specialist_id,node_id)` contribution presence **before** invoking a factory; same-process repeat, persisted resume, and partial-band resume call only missing nodes. The helper receives/returns `ProductionEnvelope` and uses only `get_contribution`/`add_contribution`, never a second run.json writer. Structural precondition: the envelope argument must be an actual `ProductionEnvelope`; any other value raises tagged `SpecialistDispatchError` `workbook.band.invalid-context`. Unknown node IDs raise `workbook.band.unknown-node`. Both failures error-pause without advancing.

4. **Truthful placeholder identities:** all stubs use `model_used: deterministic-workbook-band-stub`. `07W.1` writes `workbook_brief_stub@07W.1` with exactly `{stub_status: not_yet_wired, brief_payload: {}, known_losses: [semantic_writers_not_yet_wired]}`. `07W.3` writes `workbook_review_stub@07W.3` with exactly `{stub_status: not_yet_wired, review_payload: {}, known_losses: [semantic_writers_not_yet_wired]}`. `07W.2` writes `ask_a_enrichment@07W.2` with `{research_entries: [], stub_status: not_yet_wired, known_losses: [ask_a_not_yet_wired]}`; `07W.4` writes `ask_b_hot_topics@07W.4` with the analogous `ask_b_not_yet_wired`. Research-intake and triangulation keys are absent. These are present-but-empty contributions, never fabricated scholarship, generic fallback, or live claims. Pin coordinates against Story-38.0 public constants without a reverse orchestrator import into `lesson_plan`.

5. **Future writer injection without stealing writer contracts:** `.1` is the future Scene/Promise/Deep-Dive-skeleton position; `.3` is the future enrichment/check/reflection position. 38.3b owns only a neutral node-keyed callable/factory protocol accepting node id + envelope context and returning the pinned placeholder output. It must not define or import `SceneComposer`, `PromiseTransformer`, `DeepDiveWriter`, `CheckWriter`, or `ReflectionWriter`; Epics 36/37 later register those callables without a topology edit. Prove generic injection with spies and make no live call.

6. **Behavioral two-walk parity:** wire one shared band helper into both runner walks. Tests prove a start walk paused before the band does not claim execution and a continuation reaching it executes the four hooks in exact order with matching shapes and idempotency. Static source counts alone are insufficient.

7. **Lockstep closure (party-amended at code review):** enroll exact unique rows `app/marcus/orchestrator/workbook_wiring.py` and `app/marcus/lesson_plan/research_packet.py` in `block_mode_trigger_paths`; make no unrelated trigger churn. Update the `07W` template and regenerate only `docs/workflow/production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md`. The T1 record must prove: terminal-only/HUD-hidden band; no operator-visible workflow, gates, or events; concrete before/after SHA equality for mapping-axis v4.2 and production v5; only the `-gen` witness changes. Lockstep, frozen-SHA, and no-hand-edit guards pass. Standard and cluster structural walks must be READY. Motion is `AMBIENT-FAIL / NO-NEW-REGRESSION` only if the same command at baseline `83df9e9c` and candidate reproduces the identical sole frozen-v4.2 marker-order signature with no added failure. Record command, exit, signature/path/marker coordinates, and carry the defect as separately owned debt requiring its own regime decision. Any missing baseline proof or changed/additional motion failure blocks closure. This is a one-signature exception, not precedent.

8. **Evidence:** pin manifest IDs/order/attributes/model-config split, terminal model-free invariant, exact-once deterministic walk, resume idempotency, injected factory, selected/deselected composition and digest replay, frozen Ask-A/B strings, generic `04.55` regression, terminal no-model-client, zero new events/gates/HUD steps, focused tests, Ruff, and diff check. No paid/live run is required and no real packet/prose claim is allowed.

## Tasks / Subtasks

- [x] Record T1 regime evidence and freeze scope (AC: 7-8)
- [x] Add manifest band and truthful writer model config (AC: 1, 7)
- [x] Expand workbook composition ownership/version (AC: 2)
- [x] Implement deterministic `workbook_wiring` seam (AC: 3-5)
- [x] Wire shared hook into both runner walks (AC: 3, 6)
- [x] Update template and regenerate only v4.2 `-gen` witness (AC: 7)
- [x] Add topology, wiring, two-walk, composition, and contract tests (AC: 1-8)
- [x] Run lockstep and focused validation battery (AC: 7-8)

### Review Findings

- [x] [Review][Decision] Resolve AC7 motion-walk conflict — party amendment proven baseline-identical and separately filed as debt.
- [x] [Review][Patch] Convert unexpected factory exceptions and non-dict/non-serializable outputs into tagged `SpecialistDispatchError` so both walks error-pause recoverably [app/marcus/orchestrator/workbook_wiring.py:112]
- [x] [Review][Patch] Add true serialized/reloaded partial-band resume evidence proving only missing nodes invoke factories [tests/integration/marcus/test_workbook_band_wiring.py:81]
- [x] [Review][Patch] Exercise invalid-context and unknown-node failures through runner error-pause branches without advancing [tests/integration/marcus/test_workbook_band_wiring.py:99]
- [x] [Review][Patch] Prove band execution with credentials absent and both offline-cost flag states [tests/integration/marcus/test_workbook_band_wiring.py:152]
- [x] [Review][Patch] Narrow the lockstep checker's legacy-manifest fallback so malformed graph manifests cannot be mislabeled and obscured [scripts/utilities/check_pipeline_manifest_lockstep.py:203]
- [x] [Review][Patch] Record concrete before/after SHA evidence for frozen mapping-axis v4.2 and production-canonical v5 [38-3b T1 evidence]
- [x] [Review][Audra][Blocker] Restore schema-only and manifest-only drift detection: Check 8 must reject conflicting explicit node schema refs instead of silently filtering them out while retaining the narrow legacy-manifest fallback [scripts/utilities/check_pipeline_manifest_lockstep.py]

## Dev Notes

### Expected files

- `state/config/pipeline-manifest.yaml`
- `app/marcus/orchestrator/workbook_wiring.py` (new)
- `app/marcus/orchestrator/workbook_writer_model_config.yaml` (new; exact path)
- `app/marcus/orchestrator/production_runner.py`
- `app/marcus/lesson_plan/composition.py`
- `scripts/generators/v42/templates/sections/07W-companion-workbook-producer.md.j2`
- generated v4.2 `-gen` witness
- focused integration/composition/lockstep tests
- T1 evidence in this story

Do not edit `research_packet.py` behavior; only enroll its path as load-bearing.

### Precedents and constraints

- Mirror `package_builders`/`research_wiring` node-keyed hooks.
- Use exact `ProductionEnvelope.get_contribution`/`add_contribution`; never manually duplicate contributions.
- Keep band nodes `specialist_id: null` so they remain orchestration; add no dispatch entries.
- Expand workbook fragment ownership from only `07W` to the full band or deselection leaks `.1`–`.4` into the deck base.
- Update the 07W generator template because its current prose falsely says `15 -> 07W -> end`.

| Node | 38.3b role | Contribution identity |
|---|---|---|
| `07W.1` | pre-work/deep-dive placeholder + DI seam | stable pinned workbook-brief stub identity |
| `07W.2` | Ask-A honest-empty placeholder | `ask_a_enrichment@07W.2` |
| `07W.3` | enrichment/check/reflection placeholder + DI seam | stable pinned workbook-review stub identity |
| `07W.4` | Ask-B honest-empty placeholder | `ask_b_hot_topics@07W.4` |

The manifest list order and `insertion_after` values are pinned: `.1` after `15`, `.2` after `.1`, `.3` after `.2`, `.4` after `.3`, and terminal `07W` after `.4`. Compiled edges and list order must agree because runner iteration uses manifest order.

The generic factory protocol is temporary topology infrastructure, not a writer API. Its default mapping is:

| Node | Manifest specialist | Model config | Wiring identity | Future owner |
|---|---|---|---|---|
| `07W.1` | null | shared workbook-writer config | `workbook_brief_stub` | Epics 36 + 37.2a |
| `07W.2` | null | null | `ask_a_enrichment` | Story 38.1 |
| `07W.3` | null | shared workbook-writer config | `workbook_review_stub` | Epic 37 |
| `07W.4` | null | null | `ask_b_hot_topics` | Story 38.2 |

### Scope fences

No real Ask-A/Ask-B dispatch (38.1/38.2), semantic writers (36/37), consume-side readers (38.3a), citation coverage (37.2b), glossary/trends work (39), cover (40), terminal `_act.py`/render change, generic `04.55` change, packet/envelope schema change, event/gate/HUD/operator-surface change, pack-family bump, or proofing accommodation.

### Validation

- Render v4.2 `-gen`, then run `scripts/utilities/check_pipeline_manifest_lockstep.py`.
- Run focused band tests, `tests/composition`, selection/resume, pipeline smoke, frozen/generated-pack, and `04.55` regressions.
- Run standard, motion, and cluster structural walks.
- Ruff changed Python/tests and run `git diff --check`.
- Create/run `tests/integration/marcus/test_workbook_band_wiring.py` for exact identities, unconditional offline execution (credentials absent and offline-cost mode), injection, same-process/persisted/partial resume idempotency, tagged errors, and behavioral continuation parity.
- Extend `tests/specialists/workbook_producer/test_workbook_producer_brick.py` and `tests/unit/composition/test_composer_topology.py` for every selection adjacency, selected/deselected two-part digest replay, manifest list order, and terminal pin.
- Explicit start/continuation setup: start pauses before the post-G1 terminal band with zero calls; continuation reaches and executes all four. Unit-test helper order separately—no paid/full production traversal.

Any unexpected schema/generator change, new event/gate/operator surface, frozen-pack mutation, or need for writer semantics is a kill-switch requiring renewed party consensus.

### References

- `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` — A1/A4/A5 and ratified graph shape
- `_bmad-output/planning-artifacts/workbook-presentation-support-redesign-2026-07-12.md` — §§8, 11, 13
- `docs/dev-guide/pipeline-manifest-regime.md`
- `state/config/pipeline-manifest.yaml`
- `app/marcus/orchestrator/production_runner.py`
- `app/marcus/lesson_plan/composition.py`
- `_bmad-output/implementation-artifacts/38-0-two-packet-intake-contract.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex (Amelia developer agent)

### Debug Log References

- 2026-07-12 T1 regime: party-ratified v4.2-lineage terminal-sidecar refinement. Scope is terminal-only, HUD-hidden, gate/event-free, and operator-surface-neutral. Only the generated v4.2 `-gen` witness may change; frozen mapping-axis v4.2 and production-canonical v5 SHA witnesses must remain byte-identical.
- RED: the focused wiring test initially failed because `workbook_wiring` did not exist. GREEN: deterministic seam tests passed before topology integration.
- Behavioral parity: a real start walk paused at G1 with zero workbook-band calls; the resumed walk traversed later unrelated gates offline and called all four hooks exactly once in manifest order.
- Validation: final focused battery 94 passed; lockstep exit 0; Ruff clean; `git diff --check` clean. Expanded packet regression battery: 150 passed / 4 failed solely at the pre-existing live preflight dependency (`openai`/HUD health), before tested code.
- Structural walks: standard READY, cluster READY. Motion retains the pre-existing marker-order failure in the untouched frozen mapping-axis v4.2 document; AC7 prohibits changing it. Frozen mapping-axis v4.2 and production-canonical v5 are byte-unchanged; only v4.2 `-gen` changed.
- AC7 baseline comparison (party amendment): from clean detached worktree at `83df9e9c`, and from the candidate, ran the same environment/command `.venv/Scripts/python.exe -m scripts.utilities.structural_walk --workflow motion --dry-run --output <isolated-report>`. Both exited `1`, reported `NEEDS REMEDIATION`, `Critical findings: 1`, and the identical critical signature: `Creative directive resolution step | Fail | docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md contains required markers out of order`. The full selected failure/block signature was byte-equal; candidate added no failure. Frozen marker coordinates: heading line 504, `creative-directive.yaml` line 519, first `narration_profile_controls` line 114. Separately filed debt: `motion-structural-walk-frozen-v42-marker-order-reconciliation` in deferred inventory.
- Concrete frozen SHA-256 equality at baseline `83df9e9c` versus candidate: mapping-axis v4.2 `dcb8b85ed78433a9ac2fde15653902fc2f05c8d05ebcb235d3ca0d57bb0a7228` = same; production-canonical v5 `dde6df2599faba4a1d05bd04b994a47b3a3520a73fad2a4c7182439b8def9f96` = same.
- Review continuation RED/GREEN: three factory-boundary tests first failed with raw `RuntimeError`/validation/serialization exceptions; implementation now converts them to `workbook.band.factory-failed` or `workbook.band.invalid-output`. Serialized partial resume and runner-level invalid-context/unknown-node error-pause/no-advance cases pass. Credentials-absent walks pass with persisted `allow_offline_cost_report` both false and true.
- Review-continuation final validation: 103 passed; lockstep exit 0; Ruff clean; `git diff --check` clean.
- Audra closure blocker RED/GREEN: exact tests `test_red_path_fixtures_fail_correctly_schema_only` and `test_red_path_fixtures_fail_correctly_manifest_only` reproduced PASS/0 incorrectly, then passed 2/2 after Check 8 began rejecting explicit node `schema_ref` values that conflict with the manifest-level schema. The live checker remains exit 0. Full checker utility file is 5/5 green; the broader structural/integration checker collection retains unrelated stale expectations (orchestration-only roster growth and the intentionally muted PR-trigger workflow), neither caused by this patch.

### Completion Notes List

- Ultimate context engine analysis completed — comprehensive developer guide created.
- Added the exact terminal five-node workbook band, pinned model-config split, and full-band composition ownership.
- Added neutral injectable deterministic stubs with exact-coordinate idempotency, honest-empty research outputs, and tagged invalid-input errors.
- Wired one unconditional helper into start and continuation walks without credential, live-flag, or offline-cost gating.
- Regenerated only the v4.2 generated witness and preserved frozen pack families.
- Resolved all code-review patches and the AC7 party amendment; malformed graph manifests can no longer enter the legacy lockstep fallback.

### File List

- `_bmad-output/implementation-artifacts/38-3b-graph-topology-band-orchestrator.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/deferred-inventory.md`
- `app/marcus/lesson_plan/composition.py`
- `app/marcus/orchestrator/production_runner.py`
- `app/marcus/orchestrator/workbook_wiring.py`
- `app/marcus/orchestrator/workbook_writer_model_config.yaml`
- `docs/workflow/production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md`
- `scripts/generators/v42/templates/sections/07W-companion-workbook-producer.md.j2`
- `scripts/utilities/check_pipeline_manifest_lockstep.py`
- `state/config/pipeline-manifest.yaml`
- `tests/integration/marcus/test_workbook_band_wiring.py`
- `tests/test_check_pipeline_manifest_lockstep.py`
- `tests/specialists/motion_planner/test_motion_planner_producer.py`
- `tests/specialists/workbook_producer/test_workbook_producer_brick.py`
- `tests/unit/composition/test_composer_topology.py`

## Change Log

- 2026-07-12: Implemented Story 38.3b topology, deterministic seam, two-walk wiring, composition ownership, generated-pack lockstep, and focused evidence. Status set to review.
- 2026-07-12: Resolved seven review findings, including the party-amended baseline motion proof, hardened factory/error-pause boundaries, persisted resume evidence, narrowed legacy fallback, and concrete frozen SHA evidence.
- 2026-07-12: Resolved Audra closure blocker by restoring fail-closed schema/manifest drift detection without widening the legacy fallback; story remains in review.
