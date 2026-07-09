---
title: 'gamma-single-slide-png-title-match'
type: 'bugfix'
created: '2026-07-08'
status: 'done'
baseline_commit: 'ec4a7407'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Gary's title-matched export materializer treats a legitimate single-card Gamma PNG (not a zip) as "no pages," so every briefed slot becomes `gamma.export.brief-unmatched` with empty unmatched pages. Live S8 Part-4 proof downloaded `gary_A.png` (~1MB) and failed this way; unit tests only covered a 1-page ZIP.

**Approach:** Teach `materialize_exported_slide_paths_by_title` to accept a lone PNG when exactly one slot is expected (cardinality bijection); keep the multi-page ZIP title-match path unchanged; fail loud when a non-zip image is paired with N>1 slots.

## Boundaries & Constraints

**Always:**
- Zip multi-page title-match path remains byte-behavior-identical for existing cases.
- N=1 lone PNG binds the sole page to the sole slot (same `SlideMatchResult` / matched path shape as the zip path).
- N>1 with non-zip image fails loud with unmatched_keys (no positional broadcast).
- Opaque download stems (e.g. `gary_A`) may bind by sole-slot cardinality only when N=1; do not later "tighten" into a title-required check without a new party round.
- RED-first tests for lone-PNG N=1 and lone-PNG N>1; existing zip tests stay green.
- Separate from S8 letter — do not reopen S8 claim envelope.

**Ask First:**
- Any change to `gary/_act.py` download filename policy.
- Reclassifying `brief-unmatched` from retryable to fail-fast (separate follow-on).
- Expanding scope into LLM residual matcher (`gary-export-llm-brief-to-page-matcher`).

**Never:**
- Positional broadcast of one PNG onto multiple slots.
- Production patches whose only justification is "make the Part-4 proof pass" without product merit (this fix has product merit: real Gamma single-card export shape).
- Touching `composition.py` / `component_selection.py` trigger paths.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Lone PNG + 1 slot | PNG file, `expected_slots=[(sid, title)]` | `matched[sid]` = materialized per-slide path; unmatched empty | N/A |
| Lone PNG + N>1 slots | PNG file, 2+ slots | All slots in `unmatched_keys`; no matched | Caller raises brief-unmatched (honest artifact mismatch) |
| Multi-page ZIP | Existing titled zip | Unchanged bijective title match | Existing ambiguous / unmatched behavior |
| Non-PNG / unsupported | Non-png or unsupported payload | Unmatched keys (fail loud) | Existing early path |

</frozen-after-approval>

## Code Map

- `skills/gamma-api-mastery/scripts/gamma_operations.py` -- `materialize_exported_slide_paths_by_title` (fix site); `match_pages_to_slots` (reuse for titled single page when stem parses)
- `app/specialists/gary/_act.py` -- caller only (no filename policy change); raises `gamma.export.brief-unmatched` from unmatched_keys
- `tests/specialists/gary/test_gary_gamma_dispatch.py` -- existing single-slide ZIP happy path
- `tests/specialists/gary/test_gary_export_url_materialization.py` -- multi-page ZIP title match
- New or extended unit tests beside Gary export materialization coverage for lone-PNG arms

## Tasks & Acceptance

**Execution:**
- [x] `skills/gamma-api-mastery/scripts/gamma_operations.py` -- handle lone PNG N=1 bind; N>1 fail loud; document opaque-stem cardinality rule -- permanent product fix
- [x] `tests/specialists/gary/` -- RED-first lone-PNG N=1 match + lone-PNG N>1 unmatched; keep zip suites green -- party riders
- [x] `_bmad-output/planning-artifacts/deferred-inventory.md` -- mark `gamma-single-slide-deck-title-matcher-flake` closed/superseded by this fix; leave retry-taxonomy follow-on untouched -- inventory hygiene

**Acceptance Criteria:**
- Given a lone PNG export and one expected slot, when materialize runs, then the slot is matched to a written per-slide PNG path.
- Given a lone PNG export and two+ expected slots, when materialize runs, then all slots are unmatched and nothing is positionally bound.
- Given an existing multi-page titled ZIP fixture, when materialize runs, then behavior matches pre-fix tests.
- Given the fix lands, when inventory is updated, then the single-slide flake entry records CLOSED with this spec/commit citation.

## Design Notes

Party green-light 2026-07-08: Winston B (3 riders), Amelia B (MUST-FIX tests + fail-loud + no `_act.py` filename churn), John A (out of S8). Retry taxonomy stays deferred.

Golden shape for N=1 lone PNG: synthesize `pages=[{"page_index": 1, "title": title_from_export_stem(stem) or stem, "path": str(downloaded)}]` then either run `match_pages_to_slots` when title tokens can edge, OR when N=1 and no edge (opaque stem), commit `matched[sole_sid]=copied_target_path` directly — same final matched path contract as the zip commit loop.

## Verification

- `pytest tests/specialists/gary/test_gary_gamma_dispatch.py tests/specialists/gary/test_gary_export_url_materialization.py` (+ new lone-PNG tests) green
- ruff clean on touched files
- No S8 letter edits

## Suggested Review Order

**Lone-PNG materialize arm**

- Entry: N=1 opaque-stem cardinality bind vs titled-stem fail-loud
  [`gamma_operations.py:1721`](../../skills/gamma-api-mastery/scripts/gamma_operations.py#L1721)

- Opaque-stem gate (`stem_is_opaque`) prevents silent wrong-bind
  [`gamma_operations.py:1777`](../../skills/gamma-api-mastery/scripts/gamma_operations.py#L1777)

- N>1 orphan-page diagnostic (no positional broadcast)
  [`gamma_operations.py:1800`](../../skills/gamma-api-mastery/scripts/gamma_operations.py#L1800)

**Tests**

- Opaque `gary_A.png` N=1 bind (live S8 shape)
  [`test_gamma_title_matching.py:261`](../../tests/specialists/gary/test_gamma_title_matching.py#L261)

- Titled-stem mismatch must fail loud
  [`test_gamma_title_matching.py:331`](../../tests/specialists/gary/test_gamma_title_matching.py#L331)

- N>1 orphan page recorded
  [`test_gamma_title_matching.py:348`](../../tests/specialists/gary/test_gamma_title_matching.py#L348)

**Inventory**

- Flake CLOSED for lone-PNG path; ZIP cover residue noted
  [`deferred-inventory.md`](../planning-artifacts/deferred-inventory.md)
