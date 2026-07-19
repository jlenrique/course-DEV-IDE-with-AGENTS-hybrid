# Authoring a new quality-scorecard dimension (Q2/Q3) — the GL-13 leak-registration contract

The project quality scorecard (`docs/quality/project-quality-scorecard.md`) grows one
`##` dimension section at a time. Epic Q1 built the shared engine (schema v2 reader,
`{level, signal, evidence_ref}` criterion model, the honesty-pin ratchet, the per-run
`fence_state`, and the deterministic final-report **projector**
`app/quality/report.py::render_scorecard_final_report`). Q2/Q3 dimensions reuse it.

This note records the ONE contract a new dimension must honor so its leaks reach the
operator's final report. Everything else (rubric, criteria, signal readers, the
dimension's own honesty pin) follows the Q1 DID exemplar.

## The contract: register your leaks into the shared cross-dimensional list (GL-13)

The final-report projector renders **ONE cross-dimensional "Ranked project leaks"
table** via `app.quality.report.ranked_project_leaks(block)`. It aggregates the
`leaks:` list from **every** dimension's machine block into a single list ranked by
lane priority (`paid-walk` → `learner-trust` → `governance`), then by declared rank.

**Therefore: every new dimension that has open leaks MUST add a `leaks:` list to its
machine block.** A dimension that declares `open_leaks > 0` but ships no `leaks:` list
stays silently DID-only — its leaks never appear on the shared ranked list.

### What to add (mirror the DID exemplar)

In your dimension's machine-block entry (the fenced `yaml` at the bottom of the
scorecard doc), alongside `open_leaks:`, add:

```yaml
    open_leaks: <N>
    leaks:
      - rank: 1            # ranked display position within your dimension (1..N)
        criterion: C3      # the §rubric criterion label the leak sits under
        slug: <deferred-inventory-slug>   # the registry/inventory slug for the leak
        lane: paid-walk    # one of: paid-walk | learner-trust | governance
      # ... one entry per open leak; len(leaks) == open_leaks
```

Rules:

- **`len(leaks) == open_leaks`** — the leak-count honesty pin
  (`tests/quality/test_scorecard_honesty_pins.py::test_leak_count_reconciles_on_real_repo`)
  reconciles the structured list length against `open_leaks` (additive: it only checks
  when the list is present).
- **`lane` ∈ `paid-walk` / `learner-trust` / `governance`** — this drives cross-dimensional
  ranking (outcome-weighting: paid-walk first). An unknown lane sorts last.
- **`slug`** mirrors the leak's slug in the deferred inventory / a dimension leak
  registry, so the count decouples from the deferred entry's archival lifecycle (see
  the DID `## DID Scorecard Leak Registry` precedent in
  `_bmad-output/planning-artifacts/deferred-inventory.md`).

### The structural guard (a sibling can't silently stay off the list)

`app.quality.report.leak_coverage_gaps(block)` returns a gap for any dimension with
`open_leaks > 0` but no (or an empty) `leaks:` list. The Q1.4b coverage test
(`tests/quality/test_scorecard_final_report.py::test_leak_coverage_gap_reds_for_dimension_without_leaks`)
asserts this goes RED for such a dimension. **Add your dimension to a real-repo
coverage assertion** (or rely on `test_leak_coverage_gaps_clean_on_real_repo`, which
must stay green) so an omitted `leaks:` list is caught at test time, not in a live run.

## Where the projector reads your dimension

`render_scorecard_final_report` renders four things per dimension, all deterministic:

- **Band** (label + Band + band_note) — NOT a false-precise `/100` headline;
- **Per-criterion trace (0–4)** — the compact reasoning trace under the Band;
- **Ranked project leaks** — the shared cross-dimensional list above;
- **Trend** — the arrow COMPUTED from `docs/quality/scorecard-history.jsonl` via
  `app.quality.history.trend_from_history` (never painted).

Keep your dimension's machine block valid and its history ledger appended (the mirror
honesty pin enforces the doc↔ledger mirror), and the projector picks it up with no
projector changes.
