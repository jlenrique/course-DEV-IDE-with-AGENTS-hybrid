# Trial-Run Documentation

This directory holds the trial-run methodology + per-trial instances + cross-trial register.

## Standing artifacts

- **`methodology.md`** — standing operations document; consult before launching any tracked trial
- **`cross-trial-learnings.md`** — patterns + run-shape learnings across trials; consulted pre-Trial-N read + appended at Trial-N postmortem close
- **`trial-N-templates/{launch,log,postmortem}.md`** — templates for the per-run trio; copy to `trial-N/` per instance

## Per-trial instances

- **`trial-3/`** — Trial-3 (forthcoming; first FRESH-corpus trial post-Slab-7c; skeleton authored at S3, fills at launch)
- _(Trial-4, Trial-5, ... appended as trials run)_

## Quick reference

When launching a tracked trial:
1. Read `cross-trial-learnings.md` top-to-bottom (5 min; pre-Trial-N read)
2. Copy `trial-N-templates/launch.md` → `trial-N/launch.md`; fill placeholders
3. Run preflight + final-launch token; confirm GREEN
4. Launch via `app.marcus.cli trial start ...`
5. Fill `trial-N/log.md` during the run (or compile-from-runtime-artifacts immediately after)
6. At trial close: fill `trial-N/postmortem.md` Shape A (15 min, mandatory); Shape B deferred 48h
7. Append Shape-A Q5 to `cross-trial-learnings.md` (post-Trial-N append, mandatory)

See `methodology.md` for full cadence + verdict framing + filing-disposition rules.
