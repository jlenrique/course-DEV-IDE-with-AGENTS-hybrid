# Migration Story 2c.1: Wondercraft Generator Validation — Path B (regenerate from scratch + diff against migrated Wanda)

**Status:** done
**Sprint key:** `migration-2c-1-wondercraft-generator-validation-path-b`
**Epic:** Slab 2c (migration Epic 2c — Wondercraft Pilot + Generator Validation) — **OPENING story; Slab 2c kickoff per slab-2b-retrospective handoff + operator ratification 2026-04-25**.
**Pts:** 2 | **Gate:** single (per governance JSON `2c-1.expected_gate_mode = "single-gate"`, rationale: null — generator-validation pilot, no schema-shape, no lane-boundary, no invariant-preservation). **K-target:** ~1.3× (target 8 / floor 6; documentation-heavy + diff-comparison-evidence + minimal new test surface; matches epic 2c.1 K=~1.3× framing).

**Lean party-mode amendments applied 2026-04-25 (Murat + Amelia):** 2 BLOCKERs + 6 RIDERs integrated:
- **A-BLOCKER-mcp-value (CRITICAL):** Generator `--mcp wondercraft` is INVALID — `ALLOWED_MCP_TOOLS` per `skills/bmad_create_specialist/scripts/generate.py:18-20` is `{"none","gamma","elevenlabs","canvas","kling","wondercraft"}`. **Spec corrected: `--mcp wondercraft` (no `-api` suffix).**
- **A-BLOCKER-c3-removal:** AC-F manual C3 row removal underspecified — pin comment text + add re-emit guard test.
- **A-BLOCKER-LITE-terminology:** "fully-conformant" reframed to "scaffold-conformant" (dispatch family is intentionally N/A for validation tree per AC-D drift-classification).
- **M-R1 K-target reconciliation:** AC-C diff-evidence test split into 3 tests (file-presence + score-computed + drift-categorization-triple); raises real K-floor to 6 honestly.
- **M-R2 diff-evidence two-tier metric:** AC-C requires BOTH (a) file-presence ≥60% AND (b) skeleton-line match ≥40% on files-in-both-trees (excludes `_act` body + dispatch wrapper specifics per expected-divergence).
- **M-R3 timer-block structured table:** AC-E Dev Agent Record T8 evidence block requires structured timer table + paused-at/resumed-at sub-table for any gap >30 min; separates T_dev_close from T_first_artifact when AC-B-OP defers.
- **M-R5 BASELINE_METADATA.md sentinel test:** AC-F retire-to-fixtures requires `BASELINE_METADATA.md` companion documenting (a) generator commit SHA, (b) Wondercraft skill commit SHA, (c) emit-date + sentinel test asserting fixture + metadata present.
- **M-R6 deferred-inventory follow-on:** AC-F files `2c-1-generator-auto-emit-retire-removal-support` follow-on per Decision #3 meta-drift (auto-emit machinery doesn't auto-remove on retirement).
- **A-R3 test count delta:** AC-B acknowledges auto-discovery sweep gains 15th iteration (frame­work files unchanged; test count +1 in collected output).
- **A-R4 diff command pin:** AC-C pins `git diff --no-index --no-color app/specialists/wanda/ app/specialists/wanda_validation/` (git is shipped + portable; not POSIX `diff -ru`).
- **A-R6 frozen-audit fixture isolation:** AC-F retire-to-fixtures stipulates "frozen audit baseline only — no code-loads from this fixture path"; post-`git mv`, the relocated tree's `from app.models.state...` imports become broken paths; that's expected since fixture is frozen-reference.
- **A-R10 time-to-deploy mechanism pin:** AC-E pins per-timestamp mechanisms (Python `time.perf_counter()` wrappers + `pytest --durations=0` + file mtime + operator-paste).
- **M-PASS-with-note (#4):** AC-B-OP $0.50 ceiling clarified as smoke-test-purpose ("API answers + audio-file lands + sha256 computes" — rich artistic-quality production is Story 2c.2 scope).

**Path-B framing per operator ratification 2026-04-25** (slab-2-roster-reconciliation §Wondercraft Decision): Wondercraft was absorbed at 2b.8 as Path A (hand-authored migrated Wanda at `app/specialists/wanda/`). 2c.1 revives Path B to validate the generator: regenerate Wondercraft from scratch via `bmad-create-specialist` into a sibling validation tree (`app/specialists/wanda_validation/`); diff the generator-emitted output against the shipped Wanda; measure time-to-deploy + structural-match evidence; close. **Together Path A (2b.8) + Path B (2c.1) satisfy M2 "Plug-and-play specialist claim validated"** with real API + real artifact + measurable <1-dev-day + diff-against-baseline evidence.

**Time-to-deploy target:** ≤1 dev-day from 2c.1 dev-story open (T0) to first real artifact (live Wondercraft API episode-preview). Per epic 2c.1 framing: generator step ≤30 sec; conformance-green ≤5 min; total elapsed ≤8 clock hours of active dev work.

---

## T1 Readiness Block

**Before writing any code**, the dev agent reads in order:

### Standing Pre-Flight items

1. **Governance lookup** — `docs/dev-guide/migration-story-governance.json` confirms `2c-1.expected_gate_mode = "single-gate"` (rationale: null). Do not relitigate.
2. **Operator ratification** — slab-2b-retrospective.md §"Slab 2c Kickoff Handoff" carries the Path B ratification stamp 2026-04-25; slab-2-roster-reconciliation.md §"Wondercraft Decision" annotated likewise.
3. **Canonical 9-node contract** — `tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS` frozenset. Auto-discovery framework from Story 2b.16 picks up the new specialist directory automatically.
4. **TEMPLATE doc** — [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md) v2.4 R1–R14. Most rules N/A for generator-validation (this story emits a specialist; doesn't migrate one). R5 auto-emit C3 row machinery from Story 2a.5 still applies — generator emits new C3 row for `wanda_validation` (count 18→19 in live repo).
5. **Generator entrypoint** — `skills/bmad_create_specialist/scripts/generate.py`. Auto-emit C3 + atomic rollback contract per Story 2a.5.
6. **Wondercraft skill substrate** — [`skills/bmad-agent-wondercraft/`](../../skills/bmad-agent-wondercraft/) (~19+ files; SKILL.md + 6 capability references + init-sanctum.py). Already proved usable at 2b.8 hand-authored migration.
7. **Comparison baseline** — `app/specialists/wanda/` (shipped at 2b.8 close per commit `b14d54c`). NOT touched by 2c.1; serves as the diff target.
8. **Scaffold-conformance framework** — auto-discovery sweep at `tests/integration/scaffold_conformance/test_framework_auto_discovery.py` (post-2b.16) picks up `app/specialists/wanda_validation/` automatically with ZERO framework changes per FR14 architectural enforcement. Validates the W-R7 architectural pin from 2b.9.
9. **Severance posture** — hybrid working tree is sole input surface.
10. **Predecessor close evidence** — Slab 2b CLOSED at 2b.17 (commit `83caed7` + `b635586` dispatch-family completion). Migration-suite regression baseline at Slab 2b close: 562 passed / 7 skipped placeholder-key. Lint-imports 3/3 KEPT.

### Slab 2c artifact-existence sweep (8-point)

- **A** `skills/bmad-agent-wondercraft/` exists with substrate (verified 2026-04-25 at 2b.8 close).
- **B** `app/specialists/wanda/` exists as the diff baseline (shipped at 2b.8 commit `b14d54c`).
- **C** Generator is hardened post-2a.5 + post-2b.x exercise (auto-emit fired 13 times across Slab 2b without regression).
- **D** Scaffold-conformance auto-discovery from 2b.16 picks up new specialists with ZERO framework changes.
- **E** Dispatch family pattern from 2b.15 — `wanda_validation` will need `app/models/dispatch/wanda_validation/{input,receipt,error}.py` if 2c.1 retains the specialist past close OR strict-typing is N/A if `wanda_validation` is discarded at close.
- **F** `pyproject.toml` C3 contains 18 rows post-Slab-2b close. Wanda-validation auto-emit makes 19 (or rolled back if 2c.1 close discards the validation tree per AC-2c.1-G).
- **G** Wondercraft API credentials available in operator's `.env` (operator-side — not dev-agent visible).
- **H** Auto-emit C3 row machinery fires idempotently — if `wanda_validation` row is present pre-run from a prior 2c.1 attempt, no duplicate row.

### Epic-doc-vs-framework cross-check (per R6)

#### (a) Framework drifts

**NONE at 2c.1.** Story is a generator-validation pilot, not a per-specialist migration. No drifts to harvest.

#### (b) TEMPLATE scope decisions

**Decision #1 — Bounded scope (per R1):** scope is generator regeneration + diff-against-baseline + time-to-deploy measurement + ONE live Wondercraft API call (operator-gated). NOT in scope: rewriting the migrated Wanda; populating `wanda_validation` sanctum beyond generator stubs; producing multiple podcast artifacts; benchmarking against other specialists.

**Decision #2 — Validation tree retirement (operator preference; default at story-author time = retire to fixtures):** `app/specialists/wanda_validation/` is a transient validation artifact. At 2c.1 close, retire to `tests/fixtures/generator_validation/wanda_baseline/<timestamp>/` so future M2 audits + Slab-3 generator changes have a frozen baseline for regression-comparison. Operator may override at AC-G to discard entirely if disk-footprint concern overrides audit value.

**Decision #3 — Drift items file as deferred-inventory follow-ons (NOT 2c.1 in-scope fixes):** any divergence between generator-emitted Wondercraft tree and shipped `app/specialists/wanda/` becomes a deferred-inventory entry for future generator-polish work (Slab 2c.4 final close OR Slab-3 enhancement). 2c.1 documents the diff; does NOT remediate.

---

## Story

As an **operator + dev agent jointly validating the M2 plug-and-play innovation claim**,
I want **`bmad-create-specialist --name wanda_validation --mcp wondercraft --expertise-tier L5-podcast-production --from-skill skills/bmad-agent-wondercraft` to emit a fully-conformant specialist into a sibling validation tree + scaffold-conformance auto-discovery framework picks it up with ZERO framework changes + diff against shipped `app/specialists/wanda/` produces a structural-match evidence artifact + ONE live Wondercraft API episode-preview run produces a real podcast artifact at AC-B-OP**,
So that **M2 "Plug-and-play specialist claim validated" has its first defensible measurement combining real-API + real-artifact + diff-against-baseline + measurable <1-dev-day, completing the Path-A-at-2b.8 + Path-B-at-2c.1 evidence pair operator ratified at 2026-04-25**.

---

## Acceptance Criteria

All ACs are dev-agent-executable except AC-2c.1-B-OP (operator-gated live Wondercraft API call). Sandbox-AC compliant.

### AC-2c.1-A — Generator emits `wanda_validation` (scaffold-conformant) from Wondercraft skill within 30 seconds

- **Given** [`skills/bmad-agent-wondercraft/`](../../skills/bmad-agent-wondercraft/) contains the Wondercraft skill substrate (SKILL.md + 6 capability references + init-sanctum.py); generator at `skills/bmad_create_specialist/` is hardened post-2a.5 + post-Slab-2b; `--mcp wondercraft` is in `ALLOWED_MCP_TOOLS` whitelist (verified per `skills/bmad_create_specialist/scripts/generate.py:18-20`)
- **When** the dev agent runs at T0:
  ```
  .venv\Scripts\python.exe -m skills.bmad_create_specialist.scripts.generate \
    --name wanda_validation --mcp wondercraft \
    --expertise-tier L5-podcast-production \
    --from-skill skills/bmad-agent-wondercraft
  ```
- **Then** within **30 seconds (epic 2c.1 binding)** the generator emits the 9 items from `_planned_items` (counts include both `app/specialists/<name>/` tree + companion test/fixture files):
  1. **5 files in `app/specialists/wanda_validation/`:** `__init__.py`, `graph.py`, `state.py`, `model_config.yaml`, `expertise/README.md`
  2. **4 companion files outside the specialist tree:** `tests/specialists/wanda_validation/test_wanda_validation_state_shape.py`, `tests/fixtures/specialists/wanda_validation/golden_envelope.json`, `tests/fixtures/specialists/wanda_validation/golden_return.json`, `tests/integration/scaffold_conformance/test_scaffold_wanda_validation.py`
  3. `pyproject.toml` C3 `ignore_imports` row appended atomically per Story 2a.5: `"app.specialists.wanda_validation.graph -> app.gates.resume_api",  # generated by bmad-create-specialist for wanda_validation`
- **Terminology pin per Amelia A-BLOCKER-LITE:** `wanda_validation` is **scaffold-conformant**, NOT "fully-conformant" — the validation tree has NO `app/models/dispatch/wanda_validation/` family (the 2b.15 dispatch-roster is intentionally hardcoded at the migrated 14; validation trees are exempt by design). The missing dispatch family is **expected divergence per AC-D drift-classification "operator-customization" category**, NOT a generator gap.
- **Test pin:** `tests/specialists/wanda_validation/test_wanda_validation_generator_emit.py` — 2 tests:
  1. `test_wanda_validation_files_emitted` (file-existence + 5-app-tree + 4-companion shape)
  2. `test_wanda_validation_c3_row_auto_emitted` (uses `temp_repo_root` fixture per R5; asserts row count growth + comment marker exact form)
- **Time-to-deploy measurement (epic 2c.1 binding) per Amelia A-R10 mechanism pin:** wrap generator invocation in Python with `time.perf_counter()`:
  ```python
  import time, subprocess
  t0 = time.perf_counter()
  result = subprocess.run([...], check=True, capture_output=True, text=True)
  t_emit_elapsed = time.perf_counter() - t0
  print(f"T_emit_elapsed={t_emit_elapsed:.2f}s")
  ```
  Record in Dev Agent Record T8 evidence block per AC-E structured timer table.

### AC-2c.1-B — Auto-discovery framework picks up `wanda_validation` with ZERO framework changes (FR14 architectural enforcement)

- **Given** scaffold-conformance auto-discovery framework from Story 2b.16 sweeps `app/specialists/*/` with `Path("app/specialists").iterdir()` filter `is_dir() and not name.startswith(("_", "."))`
- **When** the framework runs against the live tree post-AC-A
- **Then** `pytest tests/integration/scaffold_conformance/ -q` runs the 14 conformance rules against `wanda_validation` parametrized alongside the existing 14 specialists (**collected test count +1 per Amelia A-R3** — auto-discovery sweep gains a 15th iteration; framework files UNCHANGED). All rules pass; `git diff --quiet tests/integration/scaffold_conformance/scaffold_contract.py` semantically (already covered by 2b.16's `test_framework_auto_discovery.py` positive-regression test fired against `wanda_validation` as a real instance).
- **Carve-out for hardcoded-roster tests:** `test_dispatch_contract_hardening.py::SPECIALIST_DISPATCH_FAMILIES` is hardcoded at 14 specialists (verified per 2b.15 close); `wanda_validation` does NOT bleed into that test's parametrize matrix. Validation tree exemption is structural, not by accident.
- **Time-to-conformance-green (epic 2c.1 binding) per A-R10:** `pytest tests/integration/scaffold_conformance/ -q --durations=0` reports per-test elapsed; aggregate ≤5 minutes from T0; record in Dev Agent Record T8 evidence per AC-E timer table.
- **Test pin:** the existing `tests/integration/scaffold_conformance/test_framework_auto_discovery.py` parametrized run is the test surface; no NEW test file.

### AC-2c.1-B-OP — Live Wondercraft API episode-preview (operator-gated; ≤$0.50 SMOKE-TEST cost ceiling)

- **Given** Wondercraft API credentials in operator's `.env` (`WONDERCRAFT_API_KEY`); `app/specialists/wanda_validation/` shipped per AC-A; `_act` populated to invoke `gamma-style-api-mastery` substrate-equivalent for Wondercraft (post-AC-A `_act` is generator-stub; operator wires real dispatch OR re-uses `app/specialists/wanda/wondercraft_dispatch.py` from 2b.8)
- **When** the operator runs ONE live Wondercraft API call producing a real episode-preview artifact (~$0.50 SMOKE-TEST cost ceiling per operator ratification 2026-04-25 + Murat clarification)
- **Then** the operator pastes into Completion Notes: (a) audio-file path + sha256; (b) chapter markers + voice_id used; (c) Wondercraft API request/response timestamps; (d) total cost ≤$0.50; (e) one-line operator-readable summary of episode content. No dev-agent automation of the live API; this AC is operator-machine evidence paste.
- **Smoke-test purpose pin per Murat:** $0.50 ceiling is **smoke-test purpose** — "API answers + audio-file lands + sha256 computes." Rich artistic-quality production (multi-minute episodes; full L5+L6 expertise + real demo artifacts) is **Story 2c.2 scope**, NOT 2c.1. 2c.1's AC-B-OP is the wire-test; 2c.2's AC builds the real product.
- **Operator deferral allowed (DEFERRED-PENDING-OPERATOR-WINDOW):** if operator does not have time to execute live Wondercraft call in same session, AC-B-OP MAY defer to next operator-window without blocking story close — file as deferred-inventory entry `2c-1-ac-b-op-live-wondercraft-evidence` with reactivation gate "operator-window opens AND `WONDERCRAFT_API_KEY` valid in `.env`." **Per Murat M-R3 separation:** if AC-B-OP defers, T_dev_close (AC-A through AC-F dev close) and T_first_artifact (AC-B-OP completion) are tracked SEPARATELY in AC-E timer table.

### AC-2c.1-C — Diff `wanda_validation` against shipped `app/specialists/wanda/` produces TWO-TIER structural-match evidence

- **Given** `app/specialists/wanda/` shipped at Slab 2b 2b.8 close (commit `b14d54c`) as hand-authored migrated reference; `app/specialists/wanda_validation/` emitted at AC-A as generator-output
- **When** the dev agent runs **`git diff --no-index --no-color app/specialists/wanda/ app/specialists/wanda_validation/`** (per Amelia A-R4 portability pin — git is shipped + Windows-portable; NOT POSIX `diff -ru`) and writes the output to `_bmad-output/implementation-artifacts/2c-1-wondercraft-path-b-diff-evidence.md`
- **Then** the diff evidence document captures:
  1. **TIER 1: File-presence match (≥60% floor):** count of files appearing in BOTH trees / total files in either tree. Measures generator emits the right *shape*. Target: ≥60% (per epic FR13 generator-validation evidence).
  2. **TIER 2 per Murat M-R2: Skeleton-line match (≥40% floor) on files-in-both:** for each file appearing in both trees, count identical lines / total lines. EXCLUDES `_act` body + dispatch wrapper specifics + `_SPECIALIST_ID` constant differences (these are operator-customization expected-divergence per AC-D). Measures generator emits the right *content* for the parts it should auto-derive (imports, class scaffolding, node-id frozenset, return-shape stubs). Target: ≥40% on files-in-both subset.
  3. **Field-level drift inventory:** which `XxxReturn` fields, `_act` body shapes, dispatch wrapper patterns differ between generator-output and hand-authored.
  4. **Categorization (REQUIRED non-empty for each category OR explicit "none in this category" sentinel per Murat M-R1):** each drift item classified as (a) **generator-gap** (generator should emit this; file as 2c.4 polish follow-on), (b) **operator-customization** (legitimate hand-author choice generator can't auto-derive; documented as expected-divergence — at minimum: `_act` body, dispatch wrapper, `_SPECIALIST_ID`, missing `app/models/dispatch/<name>/` family per AC-A terminology pin), (c) **drift candidate** (TBD; party-mode at 2c.1 close decides classification).
- **Test pin per Murat M-R1 (split AC-C into 3 tests):** `tests/specialists/wanda_validation/test_wanda_validation_diff_evidence.py` — 3 tests:
  1. `test_diff_evidence_file_exists_with_required_sections` — file present + all 4 sections present (Tier 1 score, Tier 2 score, drift inventory, categorization).
  2. `test_diff_evidence_scores_meet_floors` — Tier 1 file-presence ≥60% parses + computed value passes; Tier 2 skeleton-line match ≥40% on files-in-both subset parses + passes.
  3. `test_diff_evidence_categorization_triple_present` — all 3 categorization sub-sections (`generator-gap` / `operator-customization` / `drift candidate`) present with non-empty bullets OR explicit "none in this category" sentinel string.

### AC-2c.1-D — Drift items filed as deferred-inventory follow-ons (NOT 2c.1 in-scope fixes)

- **Given** AC-C produces a categorized drift inventory
- **When** the dev agent reviews drift items at story close
- **Then** every "generator-gap" drift item files as a deferred-inventory entry under §Named-But-Not-Filed Follow-Ons with parent story `2c.1` and reactivation gate "Slab 2c.4 generator polish OR Slab-3 enhancement." Every "operator-customization" item is documented as expected-divergence in the diff-evidence Markdown (no follow-on filed). Every "drift candidate" requires party-mode disposition before 2c.1 close.

### AC-2c.1-E — Time-to-deploy measurement recorded in Dev Agent Record T8 STRUCTURED TIMER TABLE per Murat M-R3

Per epic 2c.1 binding "≤1 dev-day from story open to first real artifact" + Murat M-R3 structured-timer requirement:

**Required structured timer table in Dev Agent Record T8 evidence block:**

| Timestamp | Mechanism (per Amelia A-R10) | Target | Recorded value |
|---|---|---|---|
| T0 | `time.perf_counter()` at generator subprocess invocation | — | — |
| T_emit | T0 + `subprocess.run` elapsed (perf_counter delta) | T0 + ≤30 sec | — |
| T_conformance_green | `pytest tests/integration/scaffold_conformance/ -q --durations=0` aggregate elapsed | T0 + ≤5 min | — |
| T_diff_evidence | `os.path.getmtime("_bmad-output/implementation-artifacts/2c-1-wondercraft-path-b-diff-evidence.md")` | (no hard target) | — |
| T_dev_close | story BMAD-CLOSE-AC-A-through-AC-F timestamp (independent of B-OP) | T0 + ≤8 clock hrs active | — |
| T_first_artifact | AC-B-OP operator-paste timestamp (Wondercraft audio file mtime) | T0 + ≤8 clock hrs active OR DEFERRED | — |
| T_close | story BMAD-CLOSE-FULL timestamp | (after T_first_artifact) | — |

**Required paused-at/resumed-at sub-table per Murat M-R3:** for any gap >30 min between adjacent timestamps, log paused-at/resumed-at pairs. If no pauses, write "no pauses ≥30 min."

**Pass criterion per Murat M-R3 separation (binding):**
- **T_dev_close - T0 ≤ 8 clock hours of active dev work** (excludes paused intervals; can span calendar days). This is the dev-agent-only metric.
- **T_first_artifact - T0 ≤ 8 clock hours of active dev work** when AC-B-OP fires in same window. If AC-B-OP defers, T_first_artifact tracks SEPARATELY (operator-window) and is NOT a 2c.1 close-blocker per AC-B-OP DEFERRED-PENDING-OPERATOR-WINDOW.
- If either exceeded, root cause documented in Dev Agent Record + filed as `2c-1-time-to-deploy-overrun-rca` follow-on.

### AC-2c.1-F — Validation tree retirement at story close (default: retire to fixtures with BASELINE_METADATA.md; operator override available)

- **Given** Decision #2 above (default retire to `tests/fixtures/generator_validation/wanda_baseline/<YYYY-MM-DD>/`; operator override = discard)
- **When** the story closes
- **Then** at operator's election:
  - **Default (retire to fixtures) per Murat M-R5:** `git mv app/specialists/wanda_validation/ tests/fixtures/generator_validation/wanda_baseline/2026-04-25/`; **author companion `BASELINE_METADATA.md` in the same fixture directory documenting:** (a) generator commit SHA at emit time (output of `git rev-parse HEAD` at AC-A T0), (b) Wondercraft skill-substrate commit SHA (output of `git log -n 1 --format=%H -- skills/bmad-agent-wondercraft/` at AC-A T0), (c) emit-date 2026-04-25, (d) operator name, (e) one-line "frozen audit baseline for Slab-3+ generator regression-comparison" purpose statement; `pyproject.toml` C3 row for `wanda_validation` REMOVED with explanatory comment per A-BLOCKER pin: `# 2c.1 retire-to-fixtures: wanda_validation row removed at AC-F per Decision #2 (2026-04-25); fixture frozen at tests/fixtures/generator_validation/wanda_baseline/2026-04-25/ — see BASELINE_METADATA.md`; scaffold-conformance auto-discovery sweep no longer picks up the directory.
  - **Operator override (discard entirely):** `rm -rf app/specialists/wanda_validation/`; same C3 row removal + same comment minus fixture-pointer; NO BASELINE_METADATA.md authored.
  - **Frozen-audit isolation per Amelia A-R6:** post-`git mv`, the relocated tree's `from app.models.state.run_state import RunState` imports become broken paths (no longer under `app.specialists`). This is **expected** — the fixture is frozen-reference for diff-comparison only; NO test or import touches the relocated tree's Python files at runtime. Confirm `tests/fixtures/generator_validation/` has no `__init__.py` AND no `conftest.py` post-move (pytest defaults exclude `tests/fixtures/` from collection anyway; verify per project precedent at `tests/fixtures/specialists/`).
- **Test pins per Amelia A-BLOCKER + Murat M-R5/M-R6:**
  1. **Default-path:** post-retirement, `pytest tests/integration/scaffold_conformance/ -q` passes against the 14 specialists (no `wanda_validation` parametrize case); `pyproject.toml` C3 row count = 18 (original Slab 2b close state).
  2. **`tests/specialists/generator/test_generator_baseline_fixture_present.py` — sentinel test per M-R5:** asserts `tests/fixtures/generator_validation/wanda_baseline/2026-04-25/` exists + contains 5-file specialist subtree + `BASELINE_METADATA.md` companion present + metadata file parses + has all 5 required keys. (If operator-override discard chosen, this test is skipped with reason naming the discard decision; sentinel doesn't fire.)
  3. **`tests/specialists/generator/test_generator_c3_row_post_retire_absent.py` — re-emit guard test per A-BLOCKER:** asserts `pyproject.toml` C3 list does NOT contain `app.specialists.wanda_validation.graph -> app.gates.resume_api` row post-retirement; asserts the explanatory comment on a nearby line names "2c.1 retire-to-fixtures." Defends against accidental re-emit on next `--force` run with `--name wanda_validation`.

**Meta-drift follow-on per Murat M-R6:** AC-F manual-edit workflow normalizes a manual procedure that will repeat on future generator-validation exercises. File `2c-1-generator-auto-emit-retire-removal-support` as a deferred-inventory entry with reactivation gate "Slab 2c.4 generator polish OR first repeat-exercise of generator-validation reveals manual-edit friction." Honors Decision #3 ("drift items file as deferred-inventory follow-ons") for the meta-drift in the generator's own machinery.

### AC-2c.1-G — Diff-evidence Markdown is the load-bearing M2 artifact

- **Given** AC-C produces `_bmad-output/implementation-artifacts/2c-1-wondercraft-path-b-diff-evidence.md`
- **When** Story 2c.3 (Time-to-Deploy Measurement + Party-Mode Validation) opens later in Slab 2c
- **Then** the diff-evidence Markdown is the M2 acceptance evidence anchor for "FR13 demonstrated on a fresh specialist" + "Plug-and-play specialist claim validated." 2c.3 references this artifact in its acceptance criteria; do NOT delete or relocate without 2c.3 author's coordination.

### AC-2c.1-H — TEMPLATE compliance (per R1–R14 v2.4)

R1–R14 v2.4 honored where applicable. **Most rules N/A** (story emits a specialist for validation; doesn't migrate one). Applicable: R5 (auto-emit C3 row + idempotency at AC-A); R6 (no drifts to harvest at this story).

### AC-2c.1-I — D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** Slab-1 + Slab-2a + Slab-2b substrate intact; auto-emit C3 row machinery fired for `wanda_validation` then rolled back at retirement; FR14 architectural enforcement validated by auto-discovery picking up the new specialist with ZERO framework changes.
2. **Anti-pattern harvest:** N/A (no new drifts at this story).
3. **Migration-guide update:** §12.5 framing sentence may add a note about "five categories validated across Slab 2b + generator-regeneration validation at 2c.1"; alternatively defer to 2c.4 slab-close.
4. **TEMPLATE compliance:** R1–R14 v2.4 honored where applicable. Numeric anchors recorded: T_emit ≤30 sec / T_conformance_green ≤5 min / T_diff_evidence / T_first_artifact / T_first_artifact - T0 ≤8 clock hours.

### AC-2c.1-J — Sprint-status state-flips at filing AND at close

At filing: `migration-2c-1-wondercraft-generator-validation-path-b: ready-for-dev` added under NEW Slab 2c block; `migration-epic-2c-slab-2-wondercraft-pilot: in-progress` opens. At close: `migration-2c-1-...: done`; epic stays `in-progress` (closes at 2c.4 SLAB-CLOSING). `last_updated` field updated.

---

## File Structure Requirements

### NEW files (transient — most retired or relocated at AC-F)

```
app/specialists/wanda_validation/
├── __init__.py                                 # generator-emitted (transient)
├── graph.py                                    # generator-emitted (transient)
├── state.py                                    # generator-emitted (transient)
├── model_config.yaml                           # generator-emitted (transient)
└── expertise/
    ├── __init__.py
    └── README.md                               # generator-emitted (transient)

tests/specialists/wanda_validation/
├── __init__.py
├── test_wanda_validation_generator_emit.py     # 2 tests (AC-A); retire if validation tree discarded
└── test_wanda_validation_diff_evidence.py      # 1 test (AC-C)

_bmad-output/implementation-artifacts/
└── 2c-1-wondercraft-path-b-diff-evidence.md    # NEW per AC-C; M2 evidence anchor for 2c.3 (PERSISTENT — does NOT retire at AC-F)
```

### POSSIBLY MIGRATED files at AC-F retire-to-fixtures

```
tests/fixtures/generator_validation/wanda_baseline/2026-04-25/
└── (entire app/specialists/wanda_validation/ tree moved here per default Decision #2)
```

### MODIFIED files

- `pyproject.toml` — auto-emit during AC-A adds C3 row for `wanda_validation`; AC-F removes the row at story close (manual edit with explanatory comment; auto-emit machinery does NOT auto-remove). Net change: ZERO at story close (18 rows in / 18 rows out).
- `_bmad-output/planning-artifacts/deferred-inventory.md` — drift items per AC-D + `2c-1-ac-b-op-live-wondercraft-evidence` follow-on if AC-B-OP deferred.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-J.

### NOT modified

- `app/specialists/wanda/` — DO NOT TOUCH; serves as the AC-C diff baseline.
- `skills/bmad-agent-wondercraft/` — READ-ONLY substrate (operator-curated).
- `app/models/dispatch/wanda/` — DO NOT TOUCH; the migrated Wanda's strict-typed dispatch family from 2b.15.

---

## Testing Requirements

**K-target ~1.3× (target 8 / floor 6).** Test count: 2 (AC-A generator emit + C3 row) + 1 (AC-C diff evidence) + 0 (AC-B framework picks up via 2b.16 auto-discovery — NO new test file) + 0 (AC-B-OP operator-paste) + retirement test absorbed in standard regression run = **3 collectible** at the new test file level + measurement-evidence in Dev Agent Record (NOT pytest-collected). K-floor 6 met by counting the 3 collectibles + 3 pre-existing scaffold-conformance auto-discovery cases that fire against `wanda_validation` (parametrize-collapse: 1 K-floor unit per the auto-discovery sweep covering 14+1 specialists).

**Regression target at T8:** ≥562 passed / ≥7 skipped placeholder-key (Slab 2b close baseline preserved); +3 net at story-author and -3 net at story-close (validation tests retire with the validation tree) so net zero. Import-linter 3/3 KEPT throughout (atomic auto-emit + manual removal at AC-F). Ruff clean. Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_

### T1 Readiness

- 2026-04-26: Loaded BMAD config, `CLAUDE.md`, project context, full 2c.1 spec, sprint status, governance JSON, TEMPLATE v2.4, scaffold conformance contract, auto-discovery framework, generator entrypoint, Wondercraft substrate, and Wanda baseline.
- Governance confirmed: `docs/dev-guide/migration-story-governance.json` has `2c-1.expected_gate_mode = "single-gate"` with null rationale; gate mode not relitigated.
- Operator ratification confirmed: `_bmad-output/planning-artifacts/slab-2-roster-reconciliation.md` `Wondercraft Decision` records Path A completed at 2b.8 and Path B ratified for 2c.1; `_bmad-output/implementation-artifacts/slab-2b-retrospective.md` has Slab 2c kickoff handoff.
- Artifact sweep passed: `skills/bmad-agent-wondercraft/` exists, `app/specialists/wanda/` exists, generator whitelist includes `wondercraft`, scaffold auto-discovery is active, no pre-existing `app/specialists/wanda_validation/`, no pre-existing `tests/specialists/wanda_validation/`, and no pre-existing 2026-04-25 frozen baseline fixture.
- Sandbox-AC validator passed: `.venv\Scripts\python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-2c-1-wondercraft-generator-validation-path-b.md`.
- T1 disposition: PASS; no halt condition.

### T2–T7 Implementation Notes

- AC-A: Generated `wanda_validation` with `.venv\Scripts\python.exe -m skills.bmad_create_specialist.scripts.generate --name wanda_validation --mcp wondercraft --expertise-tier L5-podcast-production --from-skill skills/bmad-agent-wondercraft`; measured `T_emit_elapsed=0.14s`.
- AC-B: Scaffold conformance auto-discovery picked up `wanda_validation` while it was live; transient validation run passed `67 passed` across `tests/specialists/wanda_validation/` plus `tests/integration/scaffold_conformance/`.
- AC-C: Authored persistent M2 diff anchor `_bmad-output/implementation-artifacts/2c-1-wondercraft-path-b-diff-evidence.md`; Tier 1 file-presence score `83.33%`, Tier 2 skeleton-line score `44.67%`.
- AC-D: Filed four deferred-inventory entries: `2c-1-ac-b-op-live-wondercraft-evidence`, `2c-1-generator-wanda-audio-return-field-polish`, `2c-1-generator-skill-reference-loader-polish`, and `2c-1-generator-auto-emit-retire-removal-support`.
- AC-F: Retired generated live tree to `tests/fixtures/generator_validation/wanda_baseline/2026-04-25/`; added `BASELINE_METADATA.md`; removed transient `wanda_validation` C3 row with explanatory pyproject comment; removed transient validation tests/fixtures that would import the retired live-tree package.

### T8 Regression Evidence + Time-to-Deploy Measurements

| Timestamp | Mechanism (per Amelia A-R10) | Target | Recorded value |
|---|---|---|---|
| T0 | `time.perf_counter()` at generator subprocess invocation | — | 2026-04-26 story implementation window |
| T_emit | T0 + `subprocess.run` elapsed (perf_counter delta) | T0 + ≤30 sec | 0.14s |
| T_conformance_green | `pytest tests/integration/scaffold_conformance/ -q --durations=0` aggregate elapsed | T0 + ≤5 min | 59 passed in 1.36s while validation tree was live; post-retirement 58 passed in 1.51s |
| T_diff_evidence | `os.path.getmtime("_bmad-output/implementation-artifacts/2c-1-wondercraft-path-b-diff-evidence.md")` | (no hard target) | 2026-04-26T00:56:53.1162378-04:00 |
| T_dev_close | story BMAD-CLOSE-AC-A-through-AC-F timestamp (independent of B-OP) | T0 + ≤8 clock hrs active | 2026-04-26T01:19:05-04:00; operator accepted proceeding with documented pre-existing repo-wide baseline blockers |
| T_first_artifact | AC-B-OP operator-paste timestamp (Wondercraft audio file mtime) | T0 + ≤8 clock hrs active OR DEFERRED | DEFERRED-PENDING-OPERATOR-WINDOW; deferred-inventory entry filed |
| T_close | story BMAD-CLOSE timestamp | AC-B-OP may defer per spec | 2026-04-26T01:19:05-04:00; closed with AC-B-OP deferred |

Paused-at/resumed-at: no pauses ≥30 min recorded before the T8 blocker.

T8 command evidence:
- PASS: `.venv\Scripts\python.exe -m pytest tests/integration/scaffold_conformance/ -q` → 58 passed post-retirement.
- PASS: focused post-retirement guard suite → 60 passed.
- PASS: `.venv\Scripts\lint-imports.exe --config pyproject.toml` → 3/3 contracts KEPT.
- PASS: focused ruff on new 2c.1 test files.
- OPERATOR-ACCEPTED BASELINE DRIFT: `.venv\Scripts\python.exe -m pytest -q --tb=short` still fails during collection on pre-existing pipeline-manifest schema errors and missing `marcus.dispatch.contract` imports in Texas legacy tests; operator directive "proceed to remaining 2c.x story development" authorizes continuing strict 2c sequence with the blocker documented.
- OPERATOR-ACCEPTED BASELINE DRIFT: `.venv\Scripts\python.exe -m ruff check app/ tests/ skills/ scripts/` reports a large pre-existing repository-wide lint backlog outside the 2c.1 diff; focused ruff on story-owned tests is clean.
- TOOLING DRIFT: `.venv\Scripts\python.exe -m lint_imports --config pyproject.toml` fails because `import-linter` exposes `lint-imports.exe`, not a `lint_imports` Python module; the executable form passes.

### Operator Gate — AC-B-OP Live Wondercraft Evidence

DEFERRED-PENDING-OPERATOR-WINDOW. Dev agent did not run a live Wondercraft API call or incur cost. Deferred-inventory entry `2c-1-ac-b-op-live-wondercraft-evidence` filed.

### G6 Layered Code-Review (Blind Hunter / Edge Case Hunter / Acceptance Auditor)

- Blind Hunter: no 2c.1 diff-introduced runtime import from the retired fixture; `app/specialists/wanda_validation` absent post-retirement.
- Edge Case Hunter: pyproject C3 row removal verified by guard test and import-linter executable; frozen fixture has no root-level `tests/fixtures/generator_validation/conftest.py`.
- Acceptance Auditor: AC-A through AC-F implementation evidence exists, AC-B-OP correctly deferred, and operator accepted the documented pre-existing repo-wide baseline drift for purposes of continuing the Slab 2c batch.
- `bmad-code-review` scoped result: no MUST-FIX findings in the 2c.1 diff after reviewing the retired fixture boundary, C3 row removal guard, diff-evidence anchor, and deferred-inventory entries. Residual risks are the explicitly documented repo-wide T8 baseline failures and deferred live Wondercraft smoke.

### D12 Close Stub

1. **Invariant preservation:** Slab-1 + Slab-2a + Slab-2b substrate remains intact; `wanda_validation` C3 auto-emit fired then was removed at retirement; FR14 auto-discovery was exercised while the validation tree was live.
2. **Anti-pattern harvest:** N/A for 2c.1; observed generator gaps were filed as deferred-inventory follow-ons rather than harvested as migration anti-patterns.
3. **Migration-guide update:** Deferred to 2c.4 slab-close so the guide can describe the full Slab 2c M2 verdict instead of a mid-slab partial note.
4. **TEMPLATE compliance:** R1-R14 v2.4 honored where applicable; numeric anchors recorded for T_emit, T_conformance_green, T_diff_evidence, T_dev_close, and AC-B-OP deferral.

### Completion Notes

- BMAD-CLOSED 2026-04-26. Path B Wondercraft regeneration evidence exists at `_bmad-output/implementation-artifacts/2c-1-wondercraft-path-b-diff-evidence.md` and is preserved as the 2c.3 M2 anchor.
- `wanda_validation` was generated with `--mcp wondercraft`, validated by scaffold conformance while live, compared against shipped Wanda, then retired to `tests/fixtures/generator_validation/wanda_baseline/2026-04-25/` with `BASELINE_METADATA.md`.
- AC-B-OP live Wondercraft smoke was not run by the dev agent and is deferred pending an operator window; canonical deferred-inventory count is now 29 named follow-ons.
- Repository-wide full pytest and full ruff remain blocked by pre-existing baseline drift outside the 2c.1 diff; operator directive accepted continuing with these failures documented.

### File List

- `_bmad-output/implementation-artifacts/2c-1-wondercraft-path-b-diff-evidence.md`
- `_bmad-output/implementation-artifacts/migration-2c-1-wondercraft-generator-validation-path-b.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/deferred-inventory.md`
- `pyproject.toml`
- `tests/fixtures/generator_validation/wanda_baseline/2026-04-25/BASELINE_METADATA.md`
- `tests/fixtures/generator_validation/wanda_baseline/2026-04-25/__init__.py`
- `tests/fixtures/generator_validation/wanda_baseline/2026-04-25/expertise/README.md`
- `tests/fixtures/generator_validation/wanda_baseline/2026-04-25/graph.py`
- `tests/fixtures/generator_validation/wanda_baseline/2026-04-25/model_config.yaml`
- `tests/fixtures/generator_validation/wanda_baseline/2026-04-25/state.py`
- `tests/specialists/generator/test_generator_baseline_fixture_present.py`
- `tests/specialists/generator/test_generator_c3_row_post_retire_absent.py`
