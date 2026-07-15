---
title: 'Workbook LO-overlay bridge: authority-map join replaces fragile marker bridge'
type: 'bugfix'
created: '2026-07-15'
status: 'done'
review_loop_iteration: 0
baseline_commit: '46c2fafa57bae81b23bb1508bdcf09d76c0a3cda'
context:
  - '{project-root}/docs/dev-guide/how-to-add-a-specialist.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-38-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The first completed workbook run (trial `a940c5eb`) rendered its Learning Objectives section as 6/6 placeholders: `_unit_to_enrichment_lo_map` (`app/specialists/workbook_producer/_act.py:513`) joins plan units to G0 LOs only via `[evidence: src-NNN]` markers inside plan-unit `source_refs`, but on this run those `source_refs` carry raw slide-title/narration strings with zero markers (run-verified). Worse, the marker join is cross-namespace unsound: Texas's `src-NNN` enumeration (slides only) and G0's `src-NNN` enumeration (all corpus files — on this run G0 `src-001` = an assessments file while a Texas marker `src-001` means slide 1), so even when markers exist the bridge can attach the WRONG LO.

**Approach:** Join through the run's own digest-bound artifacts instead: slide-authority map (`workbook-slide-authority-map.v1.json`, per-unit `source_path`) → G0 card `enumeration_provenance` (`locator` → G0 `source_id`) → `provisional_los[].source_refs[].source_id` → `objective_id`. Exact posix-normalized path equality only — no fuzzy matching. Keep the direct-key resolution (collateral bound straight to `lo-g0-NNN`) untouched. **Structural precedence (party W1 MUST-FIX):** when a valid authority map is present, the legacy marker bridge is disabled entirely — units the authority join cannot resolve take the visible placeholder (never a marker gap-fill, which can silently attach the WRONG LO cross-namespace). The marker bridge operates only when the authority map is absent/invalid (older runs/fixtures).

## Boundaries & Constraints

**Always:**
- Deterministic, exact joins only. Normalizer is defined (party A3): `value.replace("\\", "/")` on both sides before equality — byte-identical cross-platform (a naive `Path().as_posix()` is platform-divergent on backslashes).
- Preserve existing degrade semantics: unresolved objectives still mint the visible placeholder + `lo_overlay_loss` record (never silent, never fabricated statements).
- Respect the M3 boundary: `app/specialists/**` may import `app.marcus.lesson_plan.*` (already does) but never `app.marcus.orchestrator`.
- Read the authority map via the existing `read_slide_authority_map(run_dir)`; the bridge seam catches `SlideAuthorityInvalidError` ONLY (party W3 — the reader funnels its whole failure envelope incl. absent-file into that type; a bare `except Exception` would swallow producer bugs). Any such failure ⇒ "map absent" fallback; never crash the 07W leaf on a malformed sidecar.
- Deterministic tests use the real run-`a940c5eb` artifact shapes (plan units without markers; G0 provenance; authority rows) as fixture data.

**Ask First:**
- Any change to the rendered workbook LO section format beyond statements resolving (e.g. renaming ids shown to the learner).
- Any schema change to `WorkbookSlideAuthorityMapV1`, the G0 card, or the lesson plan (none is expected to be needed).

**Never:**
- No fuzzy/text-similarity matching, no LLM calls, no mocks.
- Do not touch `state/config/pipeline-manifest.yaml` or graph topology (no lockstep-trigger paths expected in this diff; if one becomes unavoidable, HALT).
- Do not reopen the closed 38.x live gate or mutate frozen negative-witness runs; `runs/a940c5eb…` is read-only evidence.
- Do not modify Irene Pass-1 plan-unit authoring or G0 enrichment to "add markers back" — the fix is consume-side.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Live-run shape (a940c5eb) | Authority rows u01–u06→slides 1–6; G0 provenance slides→src-006..011; LOs bind src-006..011; plan-unit source_refs have NO markers | `unit_to_lo` = {u01→lo-g0-005 … u06→lo-g0-010}; 6/6 LO statements resolve; `lo_overlay_loss is None` | N/A |
| Cross-namespace trap (party M2/W1) | Valid authority map; plan units ALSO carry marker `[evidence: src-001]` where G0 `src-001` is a NON-slide file (assessments/…); authority row disagrees | Authority join wins; assert the mapping VALUE (u01→lo-g0-005), NOT the marker's mis-attach target (lo-g0-001) | N/A |
| Authority map absent (old run / fixture) | No `workbook-slide-authority-map.v1.json`; plan units carry valid G0-namespace markers | Legacy marker bridge resolves as before (backward compat; existing Q1 pins stay green) | N/A |
| Both absent | No map, no markers | Empty map; placeholders + `lo_overlay_loss` recorded (current behavior) | Visible degrade, no crash |
| Malformed authority sidecar | Corrupt/symlinked/duplicate-key file | Treated as absent → marker fallback eligible | `SlideAuthorityInvalidError` caught at the bridge seam only |
| Map present, provenance absent (party M1+W1) | Valid authority map; G0 card lacks/empty `enumeration_provenance` (older card shape) | Authority join yields nothing; markers do NOT gap-fill (structural precedence); visible placeholders + `lo_overlay_loss`; no crash | Visible degrade |
| Locator/path mismatch (corpus drift / multi-root locator, party W2) | Valid map; authority `source_path` not equal to any G0 locator (e.g. traversal-root-relative locator) | Unit unresolved; NO marker fallback (map is present); visible degrade — pin so nobody later "fixes" with suffix/fuzzy matching | N/A |
| Backslashed/`./`-prefixed path (party M4/A3) | One side carries `slides\slide-1-…md` or `./slides/…` | Normalizer (`replace("\\","/")`; strip `./`) joins byte-identically cross-platform | N/A |
| Interstitial units (u03i1/u03i2) | Authority rows exist for interstitials sharing the parent slide | Mapped identically to parent's LO (harmless; only section-bound objectives render; `overlay_attached` dedup prevents duplicate exercises) | N/A |
| LO binds multiple srcs / src bound by multiple LOs | Duplicate potential | First-LO-wins per src (stable, matches existing `src_to_lo` discipline) | N/A |

</frozen-after-approval>

## Code Map

- `app/specialists/workbook_producer/_act.py` — the bridge (`_unit_to_enrichment_lo_map`, line 513) + its sole call site (line 722) and `_resolve_overlay_key`/LO-brief resolution (724–811); fix lands here.
- `app/marcus/lesson_plan/slide_authority.py` — `read_slide_authority_map(run_dir)` (line 337, fail-loud reader), `WorkbookSlideAuthorityMapV1.rows[].{unit_id,source_path}`.
- `app/marcus/lesson_plan/workbook_enrichment.py` — `load_enrichment_card` returns the raw `g0-enrichment.json` dict incl. `enumeration_provenance` (source_id ↔ locator) and `provisional_los`.
- `runs/a940c5eb-1043-42c1-a2a4-8a6301b6bcf4/{workbook-slide-authority-map.v1.json,g0-enrichment.json,irene-pass1.lesson-plan.json,exports/workbooks/u01@1.md}` — read-only evidence anchoring fixture shapes.
- `tests/specialists/workbook_producer/test_workbook_terminal_fixes_36_40.py` — existing terminal-band test home; new tests co-locate or add a sibling module.

## Tasks & Acceptance

**Execution:**
- [x] `app/specialists/workbook_producer/_act.py` — extend `_unit_to_enrichment_lo_map(lesson_plan, card, authority_map=None)` (or a composed helper called at line 722): build `src_to_lo` (unchanged); if `authority_map` is not None, resolve units ONLY via authority `unit_id→source_path` × G0 `locator→source_id` (normalizer: `value.replace("\\", "/")` + strip leading `./` on both sides, exact equality) — the marker loop runs ONLY when `authority_map` is None; load the map near line 722 via `read_slide_authority_map(run_dir)` guarded by `except SlideAuthorityInvalidError → None` (no bare except) — rationale: consume-side deterministic fix; structural precedence kills the cross-namespace mis-attach class.
- [x] `tests/specialists/workbook_producer/test_lo_overlay_bridge_authority_join.py` — unit-test EVERY I/O-matrix row with fixture shapes lifted verbatim from run `a940c5eb`; the cross-namespace trap asserts the mapping VALUE (u01→lo-g0-005, not lo-g0-001); include the multi-root/locator-mismatch pin (W2) and backslash normalization row (M4) — rationale: pin join semantics + regression floor.
- [x] `tests/specialists/workbook_producer/test_lo_overlay_bridge_authority_join.py` (same module) — offline replay probe against the REAL `runs/a940c5eb…` dir: loads via the production `read_slide_authority_map` + `load_enrichment_card` + `lesson_plan_from_run` (never hand-parsed JSON) and asserts the exact 6-key map; `pytest.skip("run a940c5eb artifacts unavailable")` when the run dir is absent (fresh clone/CI) — rationale: environment-guarded floor on the real artifacts (party M3).
- [x] `tests/specialists/workbook_producer/` (existing suites) — run and reconcile any test asserting the old empty-map behavior (Q1 pins at `test_workbook_terminal_fixes_36_40.py:210-244` use no-sidecar fixture dirs and should stay green unchanged) — rationale: no stale pins.

**Acceptance Criteria (deterministic done-bar — ACs 1–4):**
- Given the exact artifact shapes of run `a940c5eb` (no markers; authority map + G0 provenance present), when the workbook producer builds LO briefs, then all 6 bound objectives resolve real statements/Bloom from the enrichment overlay and `lo_overlay_loss` is None.
- Given a run with no authority sidecar and marker-carrying plan units, when the bridge runs, then behavior is byte-identical to the pre-fix marker bridge.
- Given a corrupt authority sidecar, when the bridge runs, then the producer neither crashes nor mints partial junk — it falls back exactly as if the map were absent.
- Given the full deterministic suite (`pytest tests/specialists/workbook_producer tests/integration/marcus -q` non-live), when run post-fix, then green with zero regressions; ruff clean on touched files.

**Acceptance Criterion 5 (operator-gated live leg — OUTSIDE the deterministic done-bar; party M5/J-B):**
- Given one fresh governed live run (`MARCUS_G0_DISPATCH_LIVE=1`, fresh trial id, first-run-stands, operator-authorized posture per `next-session-start-here.md`), when it completes, then the rendered workbook's Learning Objectives section shows real source-grounded statements — 0 placeholders AND no "Enrichment overlay loss" degrade callout (party J-A) — and the runner grants `success: true`. If the live run fails, the run STANDS as immutable evidence (no retry-to-green): file the defect and return to spec (party J-B).

## Design Notes

Run-verified join chain (trial `a940c5eb`): authority rows `u01→slides/slide-1-…md … u06→slides/slide-6-…md`; G0 provenance `slides/slide-1-…md→src-006 … slides/slide-6-…md→src-011`; LOs `src-006→lo-g0-005 … src-011→lo-g0-010`. Expected map: `{u01:lo-g0-005, u02:lo-g0-006, u03:lo-g0-007, u04:lo-g0-008, u05:lo-g0-009, u06:lo-g0-010}` — 6/6. The namespace-conflation hazard is why a present map disables markers entirely (structural precedence, party W1).

Staleness containment (party W4, no change required): the reader validates the map's self-digest but does NOT cross-check `plan_units_digest` against the loaded lesson plan — contained by construction (join keys off `unit_id`; unknown/stale units are inert; mint-once/reconcile discipline + append-only run dirs). Do NOT add an ad-hoc digest cross-check in tests without a spec update.

Party green-light 2026-07-15: Winston / John / Amelia / Murat — 4/4 APPROVE-WITH-AMENDMENTS; all amendments folded above (W1 structural precedence MUST-FIX, W2 multi-root pin, W3 exception seam, W4 note, J-A loss-callout done-bar, J-B live-failure path, M1 half-state row, M2 trap-in-matrix, M3 replay-probe skip-guard + production loaders, M4/A3 normalizer definition, M5 live leg operator-gated). Orchestrator concurred; per CLAUDE.md party-consensus-=-approval, Checkpoint-1 satisfied without a redundant human hold (operator may override asynchronously).

## Verification

**Commands:**
- `.venv/Scripts/python.exe -m pytest tests/specialists/workbook_producer -q` — expected: all pass incl. new bridge tests.
- `.venv/Scripts/python.exe -m pytest tests/integration/marcus -q` — expected: green (non-live).
- `.venv/Scripts/ruff.exe check app/specialists/workbook_producer/_act.py tests/specialists/workbook_producer/` — expected: clean.
- Offline replay probe against the real run dir (read-only): a small pytest that points the bridge at `runs/a940c5eb…` artifacts and asserts the 6/6 map — expected: exact expected mapping above.

**Manual checks (if no CLI):**
- After the governed live verification run: open `runs/<fresh-id>/exports/workbooks/u01@1.md` §Learning Objectives — every bullet carries a real statement (no "objective statement unresolved" text).

## Suggested Review Order

**The join redesign (design intent)**

- Two-bridge contract: authority join with structural precedence; legacy markers only when the map is absent.
  [`_act.py:529`](../../app/specialists/workbook_producer/_act.py#L529)

- Authority branch: provenance locator→src map with conflict poisoning; marker loop unreachable here.
  [`_act.py:583`](../../app/specialists/workbook_producer/_act.py#L583)

- Zero-join anomaly warning: shape drift is distinguishable from genuinely-unbound LOs.
  [`_act.py:619`](../../app/specialists/workbook_producer/_act.py#L619)

- Cross-platform normalizer: byte-identical `replace("\\","/")`, deliberately not `Path.as_posix()`.
  [`_act.py:518`](../../app/specialists/workbook_producer/_act.py#L518)

**The call-site seam**

- Guarded map load: `SlideAuthorityInvalidError` only; visible (logged) downgrade to the marker bridge.
  [`_act.py:814`](../../app/specialists/workbook_producer/_act.py#L814)

**Tests (matrix pins + real-run floor)**

- Matrix row 1: the a940c5eb shape resolves 6/6 via the authority join.
  [`test_lo_overlay_bridge_authority_join.py:341`](../../tests/specialists/workbook_producer/test_lo_overlay_bridge_authority_join.py#L341)

- The motivating hazard: a marker must not mis-attach across namespaces.
  [`test_lo_overlay_bridge_authority_join.py:387`](../../tests/specialists/workbook_producer/test_lo_overlay_bridge_authority_join.py#L387)

- Real-run replay probe via production loaders (skip-guarded local floor).
  [`test_lo_overlay_bridge_authority_join.py:662`](../../tests/specialists/workbook_producer/test_lo_overlay_bridge_authority_join.py#L662)

- T4 hardening pins: conflict poisoning, gate decoupling, non-list provenance, legacy characterization.
  [`test_lo_overlay_bridge_authority_join.py:722`](../../tests/specialists/workbook_producer/test_lo_overlay_bridge_authority_join.py#L722)
