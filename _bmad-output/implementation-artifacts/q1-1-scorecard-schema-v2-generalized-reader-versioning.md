---
baseline_commit: b133b1ef75532be351486009aeff1f112ff3a1e8
---

# Story Q1.1: Scorecard schema v2 + generalized reader + versioning

Status: ready-for-dev

<!-- Epic Q1 (Scorecard Engine + DID Reframe, FOUNDATION). DISPATCH #1 of the binding GL-1 order: Q1.1 → Q1.4a → Q1.2 → Q1.3 → Q1.5 → Q1.4b. Source epic: _bmad-output/planning-artifacts/epics-project-quality-scorecard-2026-07-19.md. -->

## Story

As **the quality-reporting substrate**,
I want **a versioned, dimension-agnostic scorecard schema (v2) plus a fail-soft, dimension-generalized reader**,
so that **any future dimension slots in without editing the reader, and stale or incompatible rubrics can never be silently compared or scored**.

## Scope fence (read FIRST — this is the #1 review-cycle risk)

This is the **foundation** story. It is **STRUCTURAL ONLY**. It establishes the v2 shape + the generalized reader + versioning fields, and migrates the *existing* DID content into v2 **mechanically, without re-judging a single value**. It explicitly does **NOT**:

- **Re-score / reauthor DID** (that is **Q1.5** — enumerated checklists, re-checkable C1 artifact, Mary's 0.071 correction, Band+leaks+trend reporting, `did_leak:` tags). Q1.1 carries the current headline numbers **verbatim**.
- **Wire any real signal** (that is **Q1.2** — C2/C3/C4/leak-count signal readers). At Q1.1 **every** criterion's `signal` is `null` and its `level` is the hand-carried v1 value.
- **Add honesty-pin ratchet tests** (that is **Q1.3** — `tests/quality/test_scorecard_honesty_pins.py`, the GL-6 dimension-coverage meta-ratchet).
- **Touch `run_summary.yaml` / `_emit_run_summary_yaml` / the `fence_state` block / `silent_bypass_events`** (that is **Q1.4a**).
- **Build the final-report projector or the Band/leaks/trend report surface** (that is **Q1.4b + Q1.5**).
- **Change the `/100 → Band-only` reporting** — the headline `score: 65 / max: 100 / band: B-` stays as-is; the reframe is Q1.5's judgment call. Q1.1 only makes the schema *able to carry* the richer shape.

If you find yourself editing a signal, re-judging a level, or touching `production_runner.py`, **stop — that is a different story.**

## Acceptance Criteria

**AC1 — Machine block bumped to `quality-scorecard/v2` with versioning fields.** In `docs/quality/project-quality-scorecard.md`, the `QUALITY-SCORECARD-MACHINE-BLOCK` fenced YAML:
- `schema: quality-scorecard/v2` (was `v1`).
- Each **dimension** carries `rubric_version` (integer; the DID rubric in §1.5 = version `1`), `as_of` (prose last-edited date), and `as_verified` (evidence last-re-checked date). At migration both dates = `2026-07-19` (today's carried baseline — no new evidence was checked, so they are equal now; the split earns its keep in Q1.3/Q1.5).
- Each **criterion** carries `{level, signal, evidence_ref}` (plus the existing `score`/`max` retained as the 0–4 reasoning trace per binding consensus rule #4). `signal: null` for **all five** criteria at this story (Q1.2 fills them). `evidence_ref` is a stable pointer to the current basis (e.g. `"§1.6 C3 · Leak 1"`).
- The dimension-level `score/max/band/band_note/open_leaks/trend` values are **preserved byte-for-value** from v1 (no re-judging).

**AC2 — Reader generalized off the hard-coded `_DID_KEY`.** In `app/quality/scorecard.py`:
- New `dimension_ref(key: str, path: Path | None = None) -> dict[str, Any]` returns the fail-soft summary of **any** dimension by its machine-block key; missing/absent dimension → `{"status": "unavailable", "source": ...}`.
- `did_score_ref()` is retained as a thin convenience wrapper delegating to `dimension_ref(_DID_KEY)` — its **return-key contract is unchanged** (`dimension`, `score`, `max`, `band`, `as_of`, `source`) so the two live consumers below keep working. It **may** additionally surface `as_verified`.
- The reader stays **fail-soft** (missing file · bad YAML · non-mapping · marker-absent → the `unavailable` marker, **NEVER raises**) and **stdlib + `yaml` only** (no `app.*` imports at module scope — the clean-leaf invariant, GL-3).
- A named canonical dimension-key universe is established as a module constant (e.g. `_EXPECTED_CANONICAL_DIMENSION_KEYS = ("dynamic_intelligence_vs_determinism",)`) so Q1.3's GL-6 meta-ratchet has a rail to consume. (Constant only here; the meta-ratchet **test** is Q1.3.)

**AC3 — Prose↔YAML no-silent-drift check.** A hermetic component test asserts **one prose criterion row per YAML criterion and vice-versa** (the §1.6 assessment table's C1–C5 rows ↔ the five machine-block criterion keys), so prose and numbers cannot drift apart silently. Prose owns meaning/basis; the machine block owns the numbers.

**AC4 — Consumers kept green (backward-compat, non-negotiable).** The two live consumers of the reader must pass unchanged in behavior:
- `app/marcus/orchestrator/production_runner.py::_quality_scorecard_ref()` (`:1402`, deferred-local-import, stamped at `:1448`) — still returns a well-formed dict; **do not touch this function** (Q1.4a owns it).
- `scripts/utilities/quality_scorecard.py` — **UPDATE required**: its `_fmt_summary` and `--run-summary-line` read the criterion `{score, level}` shape; adapt them to the v2 criterion shape so `--summary`, `--json`, `--run-summary-line`, and `--check` all still work. Keep the CLI's public flags identical. (`--check` staleness ratchet stays as-is; it is demoted to a secondary nag only in Q1.3.)

**AC5 — Clean-leaf structural guard (GL-3).** A structural pytest asserts `app.quality` imports **zero `app.*` modules at module scope** (AST-scan or import-graph of the `app/quality/` package). This is the leaf's honesty-pin; it must stay green from here through Q1.2 (which computes fence facts at the `production_runner` seam and passes them in as plain data, precisely so this test never goes red). `app.quality` is in **zero import-linter contracts today**, so this pytest — not CI import-linter — is the guard.

**AC6 — Component tests (hermetic).** Per the epic testing doctrine: parametrized reader fail-soft (missing file · bad YAML · non-mapping · marker-absent → `unavailable`, never raises); schema round-trip (v2 block parses; `rubric_version`/`as_of`/`as_verified` present; criteria carry `level`/`signal`/`evidence_ref`); `dimension_ref` returns the DID summary for the real key and `unavailable` for an unknown key; `did_score_ref()` return keys unchanged. All hermetic (fixture docs in a tmp path — no live calls, no repo-doc coupling in the fail-soft cases).

## Tasks / Subtasks

- [x] **T1 — Readiness (before any code).** Re-read this scope fence, the binding consensus rules #1–#4 and GL-1/GL-3/GL-6/GL-14/NFR4 in the epic, and confirm the two live consumers (AC4). No pipeline-manifest / schema-registry / learning-event paths are touched, so the pipeline-lockstep regime does **not** trigger (confirm by inspection). (AC: all)
- [x] **T2 — v2 machine block migration** in `docs/quality/project-quality-scorecard.md`. (AC1)
  - [x] Bump `schema` → `quality-scorecard/v2`; update the block's HTML-comment header (it names v1 + both reader/CLI consumers).
  - [x] Add `rubric_version: 1`, `as_of: 2026-07-19`, `as_verified: 2026-07-19` at the DID dimension level.
  - [x] Migrate each of the 5 criteria to `{level, signal: null, evidence_ref, score, max}`, carrying the existing `score`/`max`/`level` verbatim; author `evidence_ref` pointers to §1.6 rows + Leak IDs.
  - [x] Leave `score/max/band/band_note/open_leaks/trend` values unchanged.
- [x] **T3 — Generalize the reader** in `app/quality/scorecard.py`. (AC2)
  - [x] Add `dimension_ref(key, path=None)`; refactor `did_score_ref` to delegate; keep its return keys stable.
  - [x] Add `_EXPECTED_CANONICAL_DIMENSION_KEYS` constant.
  - [x] Preserve fail-soft + stdlib+yaml-only; keep the `datetime.date → str` coercion for `as_of` (and any new `as_verified`).
- [x] **T4 — Update the CLI** `scripts/utilities/quality_scorecard.py` to the v2 criterion shape (`_fmt_summary`, `--run-summary-line`); keep all flags + `--check` behavior. (AC4)
- [x] **T5 — Tests** in new `tests/quality/` (create the dir; follow existing test-dir conventions). (AC3, AC5, AC6)
  - [x] `test_scorecard_reader.py`: fail-soft matrix, schema round-trip, `dimension_ref`/`did_score_ref` behavior — hermetic via tmp fixtures.
  - [x] Prose↔YAML drift check (AC3) — reads the committed doc.
  - [x] `app.quality` clean-leaf import-scan (AC5).
- [x] **T6 — Verify consumers green.** Run the CLI four ways; run the `production_runner` run-summary emit test(s) that exercise `_quality_scorecard_ref`; ruff + import-linter clean. (AC4)

## Dev Notes

### Current state of each file being touched

**`app/quality/scorecard.py` (UPDATE).** Fail-soft reader; ~89 lines. `read_scorecard_block()` regex-extracts the fenced YAML after the `QUALITY-SCORECARD-MACHINE-BLOCK` marker, `yaml.safe_load`s it, returns the dict or `None` on any failure. `did_score_ref()` reaches `block["dimensions"][_DID_KEY]`, returns `{dimension, score, max, band, as_of, source}` or `{"status":"unavailable", "source":...}`. **Preserve:** the fail-soft contract (never raises), stdlib+yaml-only, the `as_of` `date→str` coercion (yaml parses a bare ISO date to `datetime.date`; it is coerced so the ref is JSON-clean when embedded). **Change:** factor the DID-specific accessor into a general `dimension_ref(key)`; `_DID_KEY` stays as the wrapper's argument.

**`docs/quality/project-quality-scorecard.md` (UPDATE).** Prose is the authority; §1.6 holds the current assessment table (C1–C5 with score/level/basis) + the "Open leaks" list (5) + the machine block at the bottom (currently `schema: quality-scorecard/v1`). The five criterion keys are exactly: `neck_placement`, `bone_determinism`, `fence_enforcement_default_on`, `lock_and_contract_discipline`, `honesty_and_calibration`. **Preserve** every prose word and every current number — this is a structural migration, not a re-authoring.

**`scripts/utilities/quality_scorecard.py` (UPDATE).** CLI over the reader. `_fmt_summary` iterates `dim["criteria"]` printing `score/max (level)` per criterion — this survives the v2 shape as long as `score`/`max`/`level` remain present on each criterion (they do, per AC1), so the change may be **minimal**; still verify `--json` (dumps the whole block — now v2) and `--run-summary-line` (uses `did_score_ref`). Keep `--check` unchanged.

**`app/marcus/orchestrator/production_runner.py` (DO NOT EDIT — read-only reference).** `_quality_scorecard_ref()` (`:1402`) already uses the **GL-3-correct deferred local import** and is fully fail-soft (bare-except → `unavailable`). It is stamped into `_emit_run_summary_yaml`'s payload at `:1448`. Q1.4a reworks this seam (fence_state block, honest `silent_bypass_events`, breadcrumb pointer). Q1.1's only obligation here is: **don't break `did_score_ref()`'s return contract** so this keeps working.

### Binding design consensus + GL amendments that constrain this story

- **Consensus rule #2 (honor the fence):** a criterion with a signal must not be hand-scored. At Q1.1 no signals exist yet, so all levels are legitimately hand-carried; the v2 shape *makes room* for `signal` so Q1.2 can flip C2/C3/C4/leak-count to computed. Do not pre-empt Q1.2.
- **Consensus rule #3 (`as_of` vs `as_verified`):** split now (both = today at migration). The value of the split shows up when prose is edited without re-checking evidence — Q1.3/Q1.5 exploit it.
- **Consensus rule #4 (Band not `/100`):** the reframe is Q1.5. Q1.1 keeps the headline; the schema merely *can* carry Band + per-criterion levels as the reasoning trace.
- **GL-3 (CRITICAL, clean leaf):** no `app.*` at `app/quality` module scope; enforce with AC5's structural test. This is *the* seam Winston flagged — `app.quality` is in zero import-linter contracts, so without this pytest a regression would pass CI while violating NFR4.
- **GL-6 (foreshadowed):** establish `_EXPECTED_CANONICAL_DIMENSION_KEYS` here as the rail; the meta-ratchet test (`test_every_dimension_has_a_honesty_pin`) is Q1.3.
- **GL-14:** the leak-count pin (Q1.3) has nothing to reconcile until Q1.5 lands the 5 `did_leak:` tags — irrelevant to Q1.1, noted so you don't add leak plumbing here.
- **NFR4 (additive-within-schema):** v2 is an additive superset shape; the reader generalizes off the hard-coded key; `rubric_version` per dimension is the forward-compat lever.

### Testing standards

- Framework: `pytest`; run via `.venv/Scripts/python.exe -m pytest tests/quality/ -q`. New dir `tests/quality/`.
- Hermetic: fail-soft cases use tmp-path fixture docs (write a good/bad/absent-marker doc to `tmp_path`, pass via the reader's `path=` param). The prose↔YAML drift check (AC3) and the leaf-import scan (AC5) legitimately read the real repo files.
- No live calls (Q1.1 has no live surface). No `--run-live`. Verify via shipped deps.
- Reliability doctrine: the drift check and the leaf-import scan should each **go RED under a seeded violation** (add a stray YAML criterion with no prose row → drift test red; add a module-scope `import app.<x>` to the leaf → leaf test red). Demonstrate this in the test design (parametrize or comment the RED trigger).

### Project structure notes

- Package `app/quality/` exists (`__init__.py` re-exports `did_score_ref`, `read_scorecard_block`; consider adding `dimension_ref` to `__all__`). Keep it a clean leaf.
- No pipeline-manifest / schema-registry / learning-event / run_hud / progress_map / workflow_runner paths are touched → **pipeline-lockstep regime does not trigger** (`state/config/pipeline-manifest.yaml::block_mode_trigger_paths`). Confirm at T1.
- This is Class-S substrate but hermetic; no operator-gated CLIs in dev-agent ACs (verify-via-shipped-deps holds).

### References

- [Source: _bmad-output/planning-artifacts/epics-project-quality-scorecard-2026-07-19.md#Story Q1.1] — the 4 base ACs.
- [Source: epics-project-quality-scorecard-2026-07-19.md#Green-light amendments] — GL-1 (order), GL-3 (clean leaf), GL-6 (meta-ratchet rail), GL-14, and consensus rules #1–#4.
- [Source: app/quality/scorecard.py] — reader to generalize.
- [Source: docs/quality/project-quality-scorecard.md#1.6] + machine block — the v1→v2 migration target.
- [Source: scripts/utilities/quality_scorecard.py] — CLI consumer to update.
- [Source: app/marcus/orchestrator/production_runner.py:1402-1448] — the read-only live consumer + the run_summary seam Q1.4a owns.
- [Source: tests/marcus/cli/test_projector_coverage_ratchet_43_10.py] — the RED-first ratchet / `_EXPECTED_CANONICAL_KEYS` named-pin pattern Q1.3 reuses (reference only; no pin tests in Q1.1).

## Dev Agent Record

### Agent Model Used

claude-opus-4-8[1m] (fresh BMAD dev agent, `bmad-dev-story` workflow, RED-first TDD).

### Debug Log References

- RED (reader): `tests/quality/test_scorecard_reader.py` → `ImportError: cannot import name '_EXPECTED_CANONICAL_DIMENSION_KEYS'` (dimension_ref / constant absent) — before T3.
- RED (drift, AC3): against v1 doc → `AssertionError: criterion 'neck_placement' missing evidence_ref` (v1 criteria carry no `evidence_ref`).
- Seeded-RED (drift, AC3): added a 6th machine-block criterion `SEEDED_DRIFT_VIOLATION` with `evidence_ref: "§1.6 C6 …"` (no prose row) → bijection + key-name tests both FAILED (`Extra items in the left set: 'SEEDED_DRIFT_VIOLATION'`); reverted.
- Seeded-RED (leaf, AC5): added module-scope `import app.marcus` to `scorecard.py` → `AssertionError: … violations: {'scorecard.py': ['import app.marcus (line 15)']}`; reverted.
- GREEN: `tests/quality/` 13 passed hermetically; +1 direct-seam consumer test (`test_nonzero_silent_bypass_events_logs_debug_warning`) passed → 14 passed.

### Completion Notes List

Scope-fence honored: **structural migration only** — no score/level re-judged, no signal wired (`signal: null` for all 5 criteria), no honesty-pin ratchets, no touch to `run_summary.yaml`/`_emit_run_summary_yaml`/`silent_bypass_events`/`fence_state`, no change to `/100 → Band` reporting, and `production_runner.py` **not edited**. Headline numbers (score 65 / max 100 / band B- / 4·3·1·3·2 per-criterion) carried verbatim; prose §1.6 table untouched (diff confined to the machine block).

- **AC1** — machine block bumped to `quality-scorecard/v2`; HTML-comment header updated (names v2 + both consumers + structural-migration note). DID dimension carries `rubric_version: 1`, `as_of: 2026-07-19`, `as_verified: 2026-07-19` (equal at baseline). Each of the 5 criteria migrated to `{level, signal: null, evidence_ref, score, max}` with `evidence_ref` pointers to §1.6 rows + Leak IDs. Block-level `as_of` retained (backward-compat with the reader's v1 accessor).
- **AC2** — `dimension_ref(key, path=None)` added (dimension-agnostic; missing/absent → `{"status":"unavailable", "source":…}`, never raises). `did_score_ref()` retained as a thin wrapper delegating to `dimension_ref(_DID_KEY)`; return-key contract unchanged (`dimension/score/max/band/as_of/source`), additively surfaces `as_verified`. `_EXPECTED_CANONICAL_DIMENSION_KEYS = ("dynamic_intelligence_vs_determinism",)` constant added as Q1.3's GL-6 rail. Fail-soft + stdlib+yaml-only preserved; `date → str` coercion kept for `as_of` and new `as_verified`. `dimension_ref` prefers the dimension-level `as_of`, falling back to block-level.
- **AC3** — prose↔YAML bijection guard (`test_scorecard_prose_yaml_drift.py`): set-equality of §1.6 C-ordinals (C1–C5) vs the C-ordinal each YAML criterion's `evidence_ref` points at, plus a named-key anti-regression check. Proven RED under a seeded stray criterion (see Debug Log).
- **AC4** — CLI (`scripts/utilities/quality_scorecard.py`) updated to the v2 criterion shape: `_fmt_summary` now surfaces schema/rubric_version/as_of/as_verified + per-criterion `signal`/`evidence_ref`; public flags unchanged. All four modes verified live: `--summary`, `--run-summary-line`, `--json`, `--check` → exit 0. The `production_runner._quality_scorecard_ref()` seam returns a well-formed dict against the real v2 doc (contract keys intact + `as_verified`).
- **AC5** — clean-leaf guard (`test_scorecard_clean_leaf.py`): AST scan of `app/quality/*.py` for module-scope foreign `app.*` imports (intra-package `app.quality[.*]` and relative imports allowed). `__init__.py` converted to a relative import (`from .scorecard import …`) so the package references **zero** absolute `app.*` at module scope. Proven RED under a seeded `import app.marcus` (see Debug Log).
- **AC6** — hermetic component tests: parametrized fail-soft matrix (missing file · bad YAML · non-mapping · marker-absent → `unavailable`, never raises), v2 schema round-trip (versioning fields + criterion shape, `signal is None`), `dimension_ref` real-key vs unknown-key, `did_score_ref` return-keys-unchanged + delegation. Fail-soft cases use tmp-path fixtures (no repo-doc coupling); the drift + leaf guards legitimately read the real repo files.

**Judgment call (documented for review):** AC5 says "zero `app.*` at module scope," but the shipped `__init__.py` re-exports from its own submodule. The only coherent reading (keeping the shipped, in-scope `__init__.py` compliant) is to forbid **foreign** absolute `app.*` imports while allowing the package's own subtree — realized by switching `__init__.py` to a *relative* import, which references no `app.*` name at all, so the guard can literally forbid every absolute `app.*` at module scope and still pass. The seeded-RED uses a foreign `import app.marcus` to prove the guard bites.

**Verification results.** `tests/quality/` 13 passed (hermetic); +1 direct scorecard-seam consumer test passed. `ruff check` clean on all touched Python files. `lint-imports` (import-linter): 18 contracts kept, 0 broken. CLI four ways exit 0. **Pre-existing, unrelated:** `test_run_summary_yaml_emit.py::test_clean_trial_run_summary_populated` and `::test_paused_at_g1_…` fail at the Epic 41 live-env preflight gate (`PreflightGateFailed: hud-server-healthz=fail, openai=fail`) — reproduced identically at baseline with my changes stashed; they never reach the scorecard seam. The scorecard seam itself is covered by the passing direct-`_emit_run_summary_yaml` test and the live `_quality_scorecard_ref()` invocation.

**Status left `ready-for-dev`** per orchestrator instruction (the orchestrator flips status after `bmad-code-review`). Not committed.

#### Post-review remediation pass (2026-07-19; code-review returned no BLOCKER/HIGH)

Applied 4 triaged fixes within the already-touched files, RED-first where testable:

- **FIX-1 (leaf-guard completeness — load-bearing, GL-3 is the sole guard for `app.quality`).** `test_scorecard_clean_leaf.py` now discovers modules via recursive `rglob("*.py")` (excludes `__pycache__`) so it covers future subpackages (Q1.2 signal readers), and walks *runtime* module scope — descending into module-level `if`/`try`/`with`/`for`/`while` bodies but NOT `def`/`async def`/`class` bodies. Carve-outs: `if TYPE_CHECKING:` blocks exempt; relative imports (`level>0`) allowed. RED-first proofs (both reverted): (i) `app/quality/_scratch_subpkg/x.py` with module-scope `import app.marcus` → scan FAILED naming `_scratch_subpkg/x.py`; (ii) a module-scope `try: import app.marcus / except: pass` in `scorecard.py` → scan FAILED naming `scorecard.py:22` while the co-located `if TYPE_CHECKING: from app.marcus import …` did NOT trip.
- **FIX-2 (`_fmt_summary` crash path).** Guarded `dimensions` null/list and DID-scalar with `isinstance` fallbacks mirroring the reader. New `test_scorecard_cli.py` (loads the CLI by file path) parametrizes dimensions-null / dimensions-list / DID-scalar / empty-block. RED-first: with the guard reverted, the three degenerate cases raised `AttributeError` (`NoneType`/`list`/`str` `.get`); GREEN after restore.
- **FIX-3 (prose-scan boundary).** `_prose_criterion_ordinals` now stops at the first `####` subsection after `### 1.6` (as well as the next `### ` section), confining the scan to the assessment table. New `test_prose_scan_stops_at_first_subsection_boundary` with a synthetic §1.6 whose `#### Open leaks` table carries a `C6` cell. RED-first: leaked `[1,2,3,4,5,6]` before the fix; `{1,2,3,4,5}` after.
- **FIX-4 (docstring honesty).** `did_score_ref` docstring corrected: return **keys** are stable (not full value-stability vs v1); `as_of` intentionally prefers the dimension-level date (falling back to block-level). No code change — the dimension-level preference is correct.
- **DEFER filed** to `_bmad-output/maps/deferred-work.md` (`[Review][Defer][Q1.1-CR1]`): `--check` keys on block-level `as_of` not per-dimension `as_verified` → Q1.3. **DISMISS:** `_EXPECTED_CANONICAL_DIMENSION_KEYS` runtime-dead is intentional Q1.3 forward-scaffolding — no action.

Post-remediation verification: `tests/quality/` **18 passed**; direct scorecard-seam consumer test passed; CLI four ways exit 0; `ruff check` clean; `lint-imports` 18 kept / 0 broken.

### File List

- `app/quality/scorecard.py` (MODIFIED — `dimension_ref()`, `did_score_ref()` refactored to delegate, `_EXPECTED_CANONICAL_DIMENSION_KEYS`)
- `app/quality/__init__.py` (MODIFIED — relative import; export `dimension_ref`)
- `scripts/utilities/quality_scorecard.py` (MODIFIED — `_fmt_summary` v2 criterion shape)
- `docs/quality/project-quality-scorecard.md` (MODIFIED — machine block v1→v2; prose untouched)
- `tests/quality/test_scorecard_reader.py` (NEW — AC2/AC6 hermetic reader tests)
- `tests/quality/test_scorecard_prose_yaml_drift.py` (NEW — AC3 drift guard)
- `tests/quality/test_scorecard_clean_leaf.py` (NEW — AC5 clean-leaf guard; FIX-1 recursive + block-descending scan)
- `tests/quality/test_scorecard_cli.py` (NEW — FIX-2 `_fmt_summary` degenerate-block robustness)
- `_bmad-output/maps/deferred-work.md` (MODIFIED — DEFER `[Q1.1-CR1]` `--check`→Q1.3)
- `_bmad-output/implementation-artifacts/q1-1-scorecard-schema-v2-generalized-reader-versioning.md` (MODIFIED — frontmatter `baseline_commit`, Tasks checked, this Dev Agent Record + remediation pass)
