---
title: 'Close the phantom-delta silent-audio gap (dp-v1.2 rider, Amelia R1)'
type: 'bugfix'
created: '2026-06-12'
status: 'done'
baseline_commit: 'c510b82'
context:
  - '{project-root}/_bmad-output/planning-artifacts/deferred-inventory.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A segment-manifest delta whose `id` matches no Pass-2 narration segment joins as a row with `narration_text: ""` (`narration_join.py:53`). Enrique's TTS loop silently skips it (`enrique/_act.py:256` `if not text: continue` — no mp3, no error), while Quinn-R's G5 coverage counts the row's `slide_id` as covered (`quinn_r/_act.py:143` counts by slide_id regardless of text). Result: the finished lesson plays that slide in silence and every automated check reports the run clean.

**Approach:** Party-ratified fix shape (do not re-litigate): REFUSE in enrique pre-spend (symmetric with the existing dropped-segments guard) and DROP-pre-coverage in G5 grounding so `CoverageGapError` honestly names the silent slide. Detection policy ("which join rows are phantom") lives in the shared `narration_join` module — the single policy home. Pin both behaviors with red/green tests in the dp-v1.2 twins file.

## Boundaries & Constraints

**Always:** Engine is FROZEN for Trial A — minimal surgical diff. Detection helper is pure (no I/O, no raising) per the module's contract; starvation semantics stay with callers. New enrique error is a typed `EnriqueActError` with a stable tag (`elevenlabs.join.empty-narration-text`) so the runner error-pauses recoverably. Existing tests must stay green unmodified (they encode ratified contracts).

**Ask First:** Any change to the storyboard-B publisher's behavior. Any change to the generic (non-join) `segments`/locked-manifest TTS path beyond the join seam. Any new error class (vs reusing `EnriqueActError`/existing G5 flow).

**Never:** Do not fix the b-manifest join lossiness (first-perception_source policy / VO-slide sync) — that is the `b-manifest-join-lossiness` rider, deferred to storyboard-correctness work. Do not touch fold semantics, gate engine, or pipeline manifest. Do not make the join itself raise.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Happy path | Every delta id has a matching non-empty narration segment | Unchanged: TTS per joined row; G5 covered | N/A |
| Phantom delta at enrique (node 12) | Delta `seg-2` has no narration id match → joined row text `""` | REFUSE before any TTS call | `EnriqueActError`, tag `elevenlabs.join.empty-narration-text`, names `seg-2`; zero `text_to_speech` calls |
| Phantom delta at G5 (node 13) | Same join via `run_g5_grounding` | Row dropped pre-coverage → slide uncovered | `run_g5_checks` raises `CoverageGapError` naming the slide id |
| Whitespace-only narration text | Narration segment text `"  "` | Treated as phantom (same as empty) | Same as above |
| Empty-after-drop at G5 | ALL rows phantom | Grounding refuses (zero segments) | Existing `StoryboardBInputError` `quinn_r.g5.input-missing` path |

</frozen-after-approval>

## Code Map

- `app/specialists/narration_join.py` -- single policy home; add pure helper `phantom_segment_ids(rows)` (rows with empty/whitespace `narration_text`); join behavior itself unchanged
- `app/specialists/enrique/_act.py:184-217` -- `_segments` join branch; extend the pre-spend guard (after the `dropped` check) to refuse on phantom rows
- `app/specialists/quinn_r/quality_control_dispatch.py:95-113` -- `run_g5_grounding`; filter phantom rows out of `segments` before coverage; zero-rows-after-drop falls into the existing `input-missing` raise (move/extend the empties check)
- `tests/specialists/test_audio_segment_grounding.py` -- dp-v1.2 twins file; add PIN tests (precedent: `test_enrique_join_drop_refuses_pre_spend`)
- `tests/specialists/test_narration_join_shared.py` -- import-identity pin; add helper-policy coverage + pin both consumers route detection through the shared helper
- NOT on `block_mode_trigger_paths` (verified) — no manifest-regime tier applies

## Tasks & Acceptance

**Execution:**
- [x] `app/specialists/narration_join.py` -- add `phantom_segment_ids(rows: list[dict]) -> list[str]` (sorted ids where `narration_text` strips empty) + export -- detection policy single-homed
- [x] `app/specialists/enrique/_act.py` -- in `_segments` join branch, refuse when `phantom_segment_ids(raw)` non-empty (tag `elevenlabs.join.empty-narration-text`, message names ids) -- empty text never reaches the TTS loop's silent `continue`
- [x] `app/specialists/quinn_r/quality_control_dispatch.py` -- in `run_g5_grounding`, drop phantom rows before building `narration_segments`; if nothing remains, existing zero-segments raise fires -- silent slide becomes an honest `CoverageGapError` downstream
- [x] `tests/specialists/test_audio_segment_grounding.py` -- add `test_enrique_phantom_delta_refuses_pre_spend` (zero TTS calls, tag pinned) + `test_g5_phantom_delta_drops_to_coverage_gap` (CoverageGapError names slide) + whitespace-only variant -- PIN red/green per dp-v1.2 precedent
- [x] `tests/specialists/test_narration_join_shared.py` -- pin both consumers reference `phantom_segment_ids` (import-identity / source pin, same style as the join pin) -- a private re-implementation cannot reappear

**Acceptance Criteria:**
- Given a delta id with no narration match, when enrique's join path runs, then `EnriqueActError` (tag `elevenlabs.join.empty-narration-text`) raises with zero `text_to_speech` calls
- Given the same payload at G5, when `run_g5_checks(run_g5_grounding(payload))` runs, then `CoverageGapError` raises naming the phantom slide id
- Given fully-matched narration/deltas, when both paths run, then behavior is byte-identical to current (existing tests green unmodified)
- Given the import-identity pin suite, then both consumers route phantom detection through `app.specialists.narration_join`

## Spec Change Log

## Verification

**Commands:**
- `.\.venv\Scripts\python.exe -m pytest tests/specialists/test_audio_segment_grounding.py tests/specialists/test_narration_join_shared.py tests/specialists/enrique/ tests/specialists/quinn_r/ -q` -- expected: all pass incl. new pins
- `.\.venv\Scripts\python.exe -m pytest tests/audit/ -q` -- expected: 33 passed (taxonomy ratchet unaffected)
- `.\.venv\Scripts\python.exe -m pytest tests/integration/marcus/ -q` -- expected: 133+ passed, no new failures vs ambient roster
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` -- expected: exit 0
- `.\.venv\Scripts\lint-imports.exe` -- expected: 13 kept, 0 broken
- `.\.venv\Scripts\ruff.exe check app/specialists/narration_join.py app/specialists/enrique/_act.py app/specialists/quinn_r/quality_control_dispatch.py tests/specialists/test_audio_segment_grounding.py tests/specialists/test_narration_join_shared.py` -- expected: clean

## Suggested Review Order

**Detection policy — the single home**

- Pure helper defining "phantom"; no I/O, no raising — callers own refuse/drop semantics
  [`narration_join.py:65`](../../app/specialists/narration_join.py#L65)

**Refuse pre-spend (enrique, node 12)**

- Guard placed after the existing dropped-segments twin; fires before any paid TTS call
  [`_act.py:214`](../../app/specialists/enrique/_act.py#L214)

- Stable recoverable tag — runner error-pauses instead of crashing
  [`_act.py:220`](../../app/specialists/enrique/_act.py#L220)

**Drop pre-coverage (G5, node 13)**

- Phantom rows excluded before coverage counting; all-phantom falls into the existing starvation raise, naming the ids
  [`quality_control_dispatch.py:75`](../../app/specialists/quinn_r/quality_control_dispatch.py#L75)

- Witness trail: dropped ids recorded even when a twin segment covers the same slide
  [`quality_control_dispatch.py:126`](../../app/specialists/quinn_r/quality_control_dispatch.py#L126)

**Pins (tests)**

- Enrique twin: phantom refuses with zero TTS calls, names seg-2
  [`test_audio_segment_grounding.py:92`](../../tests/specialists/test_audio_segment_grounding.py#L92)

- G5 twin: phantom drops, CoverageGapError names the silent slide
  [`test_audio_segment_grounding.py:169`](../../tests/specialists/test_audio_segment_grounding.py#L169)

- All-phantom → honest starvation raise
  [`test_audio_segment_grounding.py:198`](../../tests/specialists/test_audio_segment_grounding.py#L198)

- Whitespace-only narration is phantom
  [`test_audio_segment_grounding.py:113`](../../tests/specialists/test_audio_segment_grounding.py#L113)

- Single-home pin: both consumers route detection through the shared module (identity + module-qualified source)
  [`test_narration_join_shared.py:61`](../../tests/specialists/test_narration_join_shared.py#L61)
