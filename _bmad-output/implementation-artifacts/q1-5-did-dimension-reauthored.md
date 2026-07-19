---
baseline_commit: 38679e8f
---

# Story Q1.5: DID dimension — reauthored honestly (Band + leaks + trend)

Status: ready-for-dev

<!-- Epic Q1 (Scorecard Engine + DID Reframe, FOUNDATION). DISPATCH #5 of the binding GL-1 order: Q1.1 (done) → Q1.4a (done) → Q1.2 (done) → Q1.3 (done) → **Q1.5** → Q1.4b. Source epic: _bmad-output/planning-artifacts/epics-project-quality-scorecard-2026-07-19.md. This is the ONLY Q1 story that re-judges DID content. -->

## Story

As **the flagship dimension**,
I want **the DID assessment rebuilt to the consensus — evidence-reproducible, enumerated, and honest about what is OWED**,
so that **it is a re-checkable measurement, not a well-argued vibe, and every honesty pin passes by AGREEING WITH REALITY today**.

## Scope fence (read FIRST)

Q1.5 is the CONTENT reauthoring of the DID dimension. It applies the ratified evidence corrections, wires the Q1.2 signals into enumerated checklists, tags the 5 leaks, and reshapes the DID REPORT to Band+leaks+trend. It does **NOT**:

- **Build the deterministic final-report PROJECTOR** — that is **Q1.4b** (the code that renders Band+ranked-leaks+trend+fence_state for the operator, reusing `hil_tabular_projector`). Q1.5 authors the DID section CONTENT and the report SHAPE in the doc; Q1.4b builds the projector code that emits it.
- **Change the signal readers (Q1.2) / the fence_state emitter (Q1.4a) / the pin FRAMEWORK (Q1.3)** — Q1.5 CONSUMES them. It removes Q1.3's leak-count `xfail(strict=True)` (promoting it to a hard pin once 5 tags exist) and adds a DID-section golden; it does not rewrite the pin machinery.
- **Touch Q2/Q3 dimensions** — DID only.
- **Add module-scope `app.*` to `app/quality`** (GL-3).

## THE ONE STORY WHERE A NUMBER MAY MOVE — but honesty, not preservation, governs

Q1.1–Q1.3 preserved the DID numbers by rule. Q1.5 applies Mary's evidence corrections faithfully: if an honest re-read moves a level, **move it and surface it** (this is the correct place). The expectation is that the levels are UNCHANGED (the corrections clarify EVIDENCE — reading-path was always counted as *uncalibrated*, so C5=partial stands — not the judgments), but do **not** force the number either way. If any level rises, Q1.3's evidence-gated upgrade guard applies (cite advanced evidence_ref + advance `as_verified`); downgrades are free. Whatever the outcome, append/update `scorecard-history.jsonl` so Q1.3's mirror pin stays green.

## Acceptance Criteria

**AC1 — DID re-scored with enumerated, re-checkable evidence per criterion.** In `docs/quality/project-quality-scorecard.md §1.6`, each criterion carries `{level, signal, evidence_ref}` plus:
- **C2 (bone-determinism):** an ENUMERATED per-node checklist = the `bone_inventory_signal()` roster (the `model_config_ref_null` nodes) WITH the honest proxy caveat Q1.2 established (nullness is not proof of determinism; node 08 Irene Pass-2 + Pass-1 gates are LLM-with-null-ref) — the checklist is the honest FACT; `strong` remains the §1.6 architecture judgment (Leak 3 Gary-export is why it is 3/4).
- **C3 (fence-enforcement):** an ENUMERATED binary preset-fenced list = the `fences_enabled_signal()` output ({fidelity:OFF, coverage:OFF, udac:OFF} on `--preset production`) → `weak` (matches reality today; the fence-claim pin agrees).
- **C1 (neck-placement):** cites a RE-CHECKABLE artifact — an enumerated neck→digest-binding set (each protected neck + its digest-binding mechanism: G0R/§04.55/G3 four-artifact lock, contribution digests, `app/runtime/compiled_graph_digest.py`), checkable against the manifest/code — NOT a bare architectural assertion.
- C4/C5 keep their `derivation` (C4 judgment-with-evidence per Q1.2; C5 judgment).

**AC2 — Report Band + ranked-leak-list + trend arrow (no false-precise `/100` headline).** §1.6's headline becomes **Band** (B−) + a **ranked** open-leak list + a **trend** arrow; the per-criterion 0–4 levels stay BELOW as the reasoning trace. Keep the machine block's `score`/`max`/`band`/per-criterion `score` (the /20→/100 sum is the reasoning trace tooling + the Q1.3 arithmetic pin read — do NOT delete them; that would break `did_score_ref`/the CLI/the arithmetic pin). The change is presentation emphasis (Band-primary, `/100` de-emphasized as an internal trace), not deletion. `trend` stays `baseline` (matches empty prior history) unless a real prior exists.

**AC3 — Mary's evidence corrections (binding).** In §1.6 C5 + the leak list:
- **Reading-path:** the number is `0.071` = the **built-classifier** measurement (`subject=built-classifier, substrate=fresh@2026-06-23`, primary-key 1/14, per `reading-path-fresh-naive-holdout-pre-trial`); the **`0.93` was catalog-approach (Claude-labels), NOT the built classifier**; the **fresh NAIVE holdout is OWED / UNMEASURED** (the 14 held-out were consumed → any score is resubstitution/upper-bound). **NEVER imply a fresh-naive number was measured.** Record the single pinned metric+dataset+commit for what WAS run. Apply Mary's binding **metric-citation rule**: every reading-path accuracy number carries `(subject, substrate@date)`.
- **Motion capability-tier** "likely stale" → an explicit **verification TODO**, NOT a claimed leak (do not count it in `open_leaks`).

**AC4 — Tag the 5 DID leaks (fires Q1.3's self-clearing pin).** Add EXACTLY 5 `did_leak:` marker lines (one per DID leak), each line-anchored (`did_leak: <slug>` or `- did_leak: <slug>` — matching `_DID_LEAK_LINE_RE`), placed in an OPEN (non-archived, non-code-fence) region associated with each entry in `_bmad-output/planning-artifacts/deferred-inventory.md`:
  1. `leg4-narration-fidelity-gate-precision-before-flag-on` (C3 fidelity fence OFF)
  2. `braid-workbook-semantic-claim-citation-audit` (C5 workbook WARN-not-gate)
  3. `gary-export-llm-brief-to-page-matcher` (C2 Gary export determinism-pretending)
  4. `reading-path-fresh-naive-holdout-pre-trial` (C5 reading-path uncalibrated)
  5. `workbook-capability-tier-honesty-lag` (C5 capability ledger lag)
- Then `open_leak_count_signal()` == 5 == `open_leaks`. **Remove Q1.3's `xfail(strict=True)`** on `test_leak_count_reconciles_on_real_repo` → it becomes a HARD GREEN pin (5==5). Verify exactly 5 tag LINES exist (entries appearing multiple times must yield ONE tag each; the reader counts lines, and some slugs appear 2–3× in prose).

**AC5 — Every honesty pin passes by AGREEING WITH REALITY + a DID-section golden.** After the reauthor: the fence-claim pin (C3 weak == fences OFF), leak-count (5==5), score-arithmetic (score↔level↔band↔sum), mirror (history mirrors the reauthored block — append/update `scorecard-history.jsonl`), and trend (baseline) pins are all GREEN by matching reality. Add a golden test of the rendered DID §1.6 section (or the machine-block DID projection) so an unreviewed prose drift is caught. DID numbers reflected in `did_score_ref()`/CLI stay valid.

## Tasks / Subtasks

- [x] **T1 — Readiness.** Re-read the scope fence, consensus rules #1–#5, GL-11/GL-13/GL-14, Mary's metric-citation rule, and the `reading-path-fresh-naive-holdout-pre-trial` deferred entry (the source of truth for the 0.071/0.93/OWED facts). No pipeline-lockstep trigger path (docs + deferred-inventory + tests) → regime does not trigger.
- [x] **T2 — Reauthor §1.6** (AC1/AC2/AC3): enumerated C2 roster (from `bone_inventory_signal`) + caveat; enumerated C3 preset-fenced list (from `fences_enabled_signal`); re-checkable C1 neck→digest-binding artifact; Band+ranked-leaks+trend header with the 0–4 trace below; Mary's C5 corrections + metric-citation; motion→verification-TODO.
- [x] **T3 — Machine block** (AC2): keep score/band/per-criterion (reasoning trace); refresh `evidence_ref`s to the enumerated artifacts; `as_of`/`as_verified` — bump `as_of` only if prose changed, advance `as_verified` only if evidence was actually re-checked (it was — the enumerated rosters ARE fresh evidence; but the LEVELS are unchanged, so no upgrade-guard trip). Keep numbers unless honesty forces a move (then surface + apply the guard).
- [x] **T4 — Tag 5 leaks + promote the pin** (AC4): 5 `did_leak:` lines; remove the xfail; hard leak-count pin green.
- [x] **T5 — History mirror + golden** (AC5): append/update `scorecard-history.jsonl` to mirror the reauthored block; DID-section golden; run the full Q1.3 pin suite → all green.
- [x] **T6 — Verify.** `pytest tests/quality/ -q`; ruff; import-linter 18/0; clean-leaf green; `did_score_ref()`/CLI still valid; confirm exactly 5 `did_leak:` lines; confirm no honesty pin is xfail/skipped that should now be hard.

## Dev Notes

### Verified evidence for AC3 (do not re-derive — cite this)
Per `_bmad-output/planning-artifacts/deferred-inventory.md` `reading-path-fresh-naive-holdout-pre-trial` + the honest-measurement report `p2-4b-honest-measurement-and-recalibration-2026-06-23.md`: `subject=built-classifier(S1/S2/S3), substrate=fresh@2026-06-23: primary-key 0.071 (1/14), full-tuple 0.0, macro 0.50, image_role 0.21, escalation 0.93`. The `0.93` elsewhere = catalog-approach (Claude labels), a DIFFERENT thing. The 14 held-out were CONSUMED (labeled) → non-naive dev set → resubstitution/upper-bound only. **Mary (binding):** a FRESH naive holdout (operator labels ≥12–15 NEW slides) is REQUIRED before any trial-ready claim; firm dissent against claiming trial-ready off the consumed-14. So C5's reading-path evidence = "uncalibrated; built-classifier 0.071 resubstitution@2026-06-23; fresh naive holdout OWED/unmeasured." This is also DID Leak 4 (cross-links to Q3.4 calibration — do not double-count).

### The 5 leaks ↔ criteria (for the ranked list + tagging)
1. [C3] fidelity fence OFF by default (strongest, paid-walk) → `leg4-narration-fidelity-gate-precision-before-flag-on`.
2. [C5] workbook semantic audit WARN-not-gate → `braid-workbook-semantic-claim-citation-audit`.
3. [C2] Gary export title-match determinism-pretending → `gary-export-llm-brief-to-page-matcher`.
4. [C5] reading-path uncalibrated (OWED holdout) → `reading-path-fresh-naive-holdout-pre-trial`.
5. [C5] capability ledger lag → `workbook-capability-tier-honesty-lag`.
Ranked-list order (per §1.6 prioritization): paid-walk first (1,3), then learner-trust (2,4), then governance (5). GL-13: leaks register into the shared project ranked-leak list (Q1.4b consumes; for now DID is the only contributor).

### `did_leak:` tagging mechanics (precise — the reader is line-anchored)
`_DID_LEAK_LINE_RE = ^[\s>]*(?:[-*+]\s+)?did_leak:` counts LINES in OPEN sections (excludes `## Closed Entries — Archived` at ~L1051 + fenced code). Add ONE tag line per leak (5 total). Some slugs appear 2–3× in prose (braid=2, gary-export=3) — that does NOT matter; the reader counts `did_leak:` lines, so add exactly 5. Place each tag on its own line at/adjacent to its entry, in an open section, not inside a ``` fence.

### Consumes (do not rebuild)
- `app/quality/signals.py`: `bone_inventory_signal` (C2 roster), `fences_enabled_signal` (C3 list), `open_leak_count_signal` (leak count), `level_from_signal`.
- `app/quality/history.py` + `scorecard-history.jsonl` (Q1.3): the mirror pin requires the newest entry to content-match the reauthored block.
- `tests/quality/test_scorecard_honesty_pins.py` (Q1.3): remove the leak-count xfail; all pins must be green-by-agreeing-with-reality after the reauthor.
- §1.5 rubric (bands/levels) — unchanged.

### Number-stability expectation
The levels are expected UNCHANGED (4·3·1·3·2 = 65/B-): Mary's corrections make the EVIDENCE honest, and the current levels already encode the honest judgment (C5=partial BECAUSE reading-path is uncalibrated + WARN-only + tier-lag; C3=weak BECAUSE fences OFF). If your honest re-read disagrees, STOP and report the specific criterion + the reason before moving it — do not silently paper over OR silently downgrade.

### Prior-story learnings
- Hold the Q1.4b boundary (no projector code).
- RED-first the promoted leak-count pin (prove it was xfail, now hard-green at 5==5; and that striking a tag → red).
- Golden must be a real doc↔golden check, updated deliberately (not auto-blessed).
- Clean leaf stays green.

### References
- [Source: epics-project-quality-scorecard-2026-07-19.md#Story Q1.5] + [#Green-light amendments GL-11/GL-13/GL-14] + consensus rules #3/#4/#5.
- [Source: deferred-inventory.md `reading-path-fresh-naive-holdout-pre-trial`] — the AC3 evidence SSOT + the 5 leak slugs.
- [Source: app/quality/signals.py · history.py · tests/quality/test_scorecard_honesty_pins.py] — consumed.
- [Source: docs/quality/project-quality-scorecard.md §1.5/§1.6 + machine block] — the reauthor target.
- [Prev stories: q1-1/q1-4a/q1-2/q1-3 all done] — the machinery Q1.5 completes with honest content.

## Dev Agent Record

### Agent Model Used

Opus 4.8 (1M context) — fresh BMAD dev agent, RED-first discipline. Status intentionally
left `ready-for-dev` and NOT committed per dispatch instruction (parent runs green-light /
`bmad-code-review` before advancing).

### Debug Log References

- Baseline (RED-first): `pytest tests/quality/ -q` → **131 passed, 1 xfailed** (the xfailed
  = `test_leak_count_reconciles_on_real_repo`, GL-14 self-clearing marker; `open_leak_count_signal()` returned 0, `open_leaks: 5` hand-carried).
- Signal rosters read live before authoring the enumerated lists: `bone_inventory_signal()` →
  52 nodes, 49 `model_config_ref:null`, `gates_all_model_config_ref_null=True`, 3 non-null-ref
  nodes = `07G` (vision perception neck), `07W.1`/`07W.3` (workbook writer seams);
  `fences_enabled_signal()` → `{fidelity:False, coverage:False, udac:False}` (0/3 → weak).
- After tagging: `open_leak_count_signal()` → **5**; 5 `did_leak:` lines confirmed via
  line-anchored grep (all in OPEN, non-fenced regions).
- Promoted-pin proofs: (a) WAS xfail (baseline above); (b) striking one real tag → count
  drops 5→4, `_reconcile(5,4)` False (RED) — proven on an in-memory copy, real file untouched.
- Golden non-vacuity: Part A RED under a seeded criterion-score drift; Part B RED under a
  seeded prose drift that redacts the metric-citation anchor (both on in-memory copies).
- Final: `pytest tests/quality/ -q` → **135 passed, 0 xfailed**; ruff clean; `lint-imports`
  → **18 kept, 0 broken**; CLI (`scripts/utilities/quality_scorecard.py`) renders 65/100 (B-),
  open_leaks 5, trend baseline; adjacent regression set (run-summary fence-state, status-surface,
  generate-next-session) → 44 passed.

### Completion Notes List

- **AC1 (enumerated, re-checkable per criterion) — met.** §1.6 per-criterion trace now carries
  `{level, signal, evidence_ref}` plus: **C2** an enumerated `model_config_ref` roster
  (49/52 null; the 3 non-null = `07G` perception neck + `07W.1`/`07W.3` writer seams) WITH the
  Q1.2 proxy caveat (nullness ≠ determinism; node 08 Irene Pass-2 + Pass-1 gates are LLM-with-null-ref;
  the roster only flags a breach, never awards strong — `strong` is the architecture judgment,
  Leak 3 is why 3/4); **C3** an enumerated preset-fenced list `{fidelity:OFF, coverage:OFF,
  udac:OFF}` on `--preset production` → weak; **C1** a re-checkable neck→digest-binding set
  (G0R/§04.55/G3 four-artifact lock, per-neck contribution digests, `app/runtime/compiled_graph_digest.py`),
  checkable against manifest/code — not a bare assertion.
- **AC2 (Band + ranked-leaks + trend headline; /100 de-emphasized not deleted) — met.** §1.6
  now leads with **Band B−**, a **ranked** 5-leak list (paid-walk → learner-trust → governance),
  and **trend ▬ baseline**; the per-criterion 0–4 levels sit BELOW as the reasoning trace. The
  machine block's `score/max/band`/per-criterion `score` are KEPT (the /20→/100 sum is the
  arithmetic-pin trace that `did_score_ref`/CLI/Q1.3 read) — de-emphasized in the report, not deleted.
- **AC3 (Mary's binding evidence corrections) — met.** Reading-path is metric-cited exactly:
  the only measured number is `subject=built-classifier(S1/S2/S3), substrate=fresh@2026-06-23:
  primary-key 0.071 (1/14)` (resubstitution on the consumed 14); the `0.93` is called out as
  catalog-approach (Claude-labels), NOT the built classifier; the **fresh-naive holdout is
  OWED/UNMEASURED** and the prose states "no fresh-naive number has been measured, and none may
  be implied." Every reading-path number carries `(subject, substrate@date)`. Motion capability-tier
  is an explicit **VERIFY (not a leak)** carve-out, NOT counted in `open_leaks`.
- **AC4 (tag 5 leaks + promote pin) — met.** Exactly 5 `did_leak:` lines added in OPEN, non-fenced
  regions (line-anchored to `^[\s>]*(?:[-*+]\s+)?did_leak:`): braid @ Braid-follow-ons, workbook-capability
  @ Static-validation-findings, leg4 @ Leg-4-CLOSE, gary + reading-path @ end of Named-But-Not-Filed
  (both live in that section's long table → placed at section end to avoid orphaning the table header;
  still in-section/associated). `open_leak_count_signal()` == 5 == `open_leaks`. Q1.3's
  `xfail(strict=True)` on `test_leak_count_reconciles_on_real_repo` REMOVED → hard green pin.
- **AC5 (pins pass by agreeing with reality + DID golden) — met.** All Q1.3 honesty pins green by
  matching reality: fence-claim (C3 weak == fences OFF), leak-count (5==5), score-arithmetic
  (13/20→65, B-), mirror (history mirrors the block — unchanged, already content-matches), trend
  (baseline). New `tests/quality/test_scorecard_did_section_golden.py` = a real doc↔golden check
  (Part A machine-block DID projection; Part B §1.6 prose honesty anchors + all 5 leak slugs),
  proven RED under seeded drift and updated deliberately (not auto-blessed).
- **Numbers UNCHANGED (honest re-read agreed).** 4·3·1·3·2 = 13/20 = 65/B−. Mary's corrections
  clarify EVIDENCE, not levels (C5=partial already encodes "reading-path uncalibrated + WARN-only +
  tier-lag"; C3=weak because fences OFF). No level moved → no upgrade-guard trip; downgrades N/A.
- **History mirror: no edit needed.** Same-day edit (2026-07-19) with all mirrored fields
  (score/band/levels/open_leaks/as_of/as_verified) unchanged → the existing `scorecard-history.jsonl`
  baseline entry already content-matches the reauthored block; the mirror pin is green.
- **Filing note:** `reading-path-fresh-naive-holdout-pre-trial` existed only as a `[[...]]` named
  follow-on inside the p2-4b mega-entry; its `did_leak:` tag was placed adjacent to that entry's
  section (governance §3 — a story naming a follow-on carries it in the inventory).
- **Scope fence honored:** no Q1.4b projector; no change to signal readers (Q1.2) / fence_state
  emitter (Q1.4a) / pin framework (Q1.3) beyond removing the leak xfail + adding the DID golden;
  no Q2/Q3 touch; no module-scope `app.*` added to `app/quality` (clean-leaf green). One Q1.2
  TRANSITIONAL test (`test_open_leak_count_real_is_zero_today`) was updated to reflect the new
  tagged reality (5, not 0) and renamed — the reader itself is unchanged.

### Review Follow-ups (coordinator 3-layer code-review batch, applied RED-first)

- **FIX-1 [HIGH] — stable did_leak registry.** Created a fixed `## DID Scorecard Leak Registry`
  governance section near the top of `deferred-inventory.md` holding ALL 5 `did_leak:` tags in
  one place, with a maintenance-rule comment ("closing a DID leak = remove its tag HERE **and**
  decrement `open_leaks` in the scorecard, in lockstep"). Removed the 5 scattered tags (3 nested
  under deferred entries, 2 in a standalone block) — replaced each with a pointer comment. This
  decouples the leak COUNT from the entries' close/archival lifecycle. **Proven:** moving the
  leg4 owner entry into the `## Closed Entries — Archived` section leaves `open_leak_count_signal()`
  == 5 (previously would have dropped to 4 and spuriously reddened both hard pins on routine
  hygiene). Also resolves the LOW findings (remote-tag locality, Leak-4 wikilink-not-entry — its
  registry line notes the underlying follow-on lives in the p2-4b entry, archive-prose trap).
- **FIX-2 [MED] — scoped the leak reconcile to DID.** `test_leak_count_reconciles_on_real_repo`
  now reconciles `block["dimensions"][_DID_KEY]["open_leaks"]` ONLY (not every dimension); comment
  notes per-dimension leak namespacing is a Q2/Q3 concern.
- **FIX-3 [MED] — fixed the stale xfail reference** in the pins-module docstring (present-tense
  "xfail(strict=True)" → "a hard reconciliation pin (Q1.5 removed the xfail…)").
- **FIX-4 [MED] — fixed stale honesty comments in `app/quality/signals.py`** ("0 tags today" →
  "5 tags today, all in the registry"; reader docstring updated). Comment-only, no logic change
  beyond FIX-7 (scope-fence exception granted for review-surfaced drift my own change created).
- **FIX-5 [MED] — disambiguated the two 0.93s** in the §1.6 metric-citation: added a "⚠️ Two
  DISTINCT quantities both round to 0.93" clarifier (built-classifier ESCALATION ≈0.929 — an
  over-escalation defect — vs catalog-approach PRIMARY-KEY accuracy 0.93; the built-classifier
  accuracy is the 0.071, NOT either 0.93). Kills the H4 inherited-green conflation trap.
- **FIX-6 [LOW/MED] — golden robustness.** (a) Part B anchors are now load-bearing TOKENS
  (`0.071`, `subject=built-classifier`, `substrate=fresh`, `catalog-approach`, `fresh-naive`,
  `OWED`, `UNMEASURED`, `VERIFY (not a leak)`, `Band: B`, `baseline`, `OFF by default`) instead
  of long exact-spaced phrases; (b) added `assert section, …` heading-found guard before both
  anchor loops.
- **FIX-7 [LOW/MED] — reader strips HTML comments.** `open_leak_count_signal` now strips
  `<!-- … -->` spans (new `_strip_html_comments`) before matching, so a commented-out tag does
  not count. **RED-first witness:** a multi-line `<!-- … did_leak: x … -->` counted 2 before the
  strip, 1 after (`test_open_leak_count_multiline_comment_disables_tag`); a single-line form was
  already skipped by the line-anchor (regression guard). Scope-fence exception granted (honest
  counting; the registry sits near comments).
- **Post-batch verification:** `pytest tests/quality/ -q` → **137 passed, 0 xfailed** (+2 FIX-7
  tests); ruff clean; `lint-imports` → **18 kept, 0 broken**; leak count 5; DID numbers still
  65/B− (unchanged); clean-leaf/mirror/golden/arithmetic pins all green.

### File List

- `docs/quality/project-quality-scorecard.md` — reauthored §1.6 (Band+ranked-leaks+trend headline;
  enumerated C1/C2/C3 evidence; Mary's reading-path metric-citation; motion VERIFY-not-leak);
  machine-block comments refreshed (leak-count now RECONCILED at 5). Numbers unchanged.
- `_bmad-output/planning-artifacts/deferred-inventory.md` — added the fixed `## DID Scorecard Leak
  Registry` governance section holding all 5 `did_leak:` tags (FIX-1) + maintenance rule; pointer
  comments left at the former scattered locations; motion VERIFY note.
- `app/quality/signals.py` — added `_strip_html_comments` + wired it into `open_leak_count_signal`
  (FIX-7); refreshed the now-stale "0 tags today" honesty comments to "5 tags / registry" (FIX-4).
  No level/derivation logic changed.
- `tests/quality/test_scorecard_honesty_pins.py` — removed the `xfail(strict=True)` on
  `test_leak_count_reconciles_on_real_repo`; docstring updated to the hard-pin contract.
- `tests/quality/test_signal_readers.py` — updated the transitional leak-count test to the tagged
  reality (0 → 5), renamed.
- `tests/quality/test_scorecard_did_section_golden.py` — NEW: DID §1.6 doc↔golden check
  (machine-block projection + prose honesty anchors + 5 leak slugs).
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Q1.5 row cycled in-progress→ready-for-dev
  (left ready-for-dev per dispatch instruction; not advanced to review, not committed).
