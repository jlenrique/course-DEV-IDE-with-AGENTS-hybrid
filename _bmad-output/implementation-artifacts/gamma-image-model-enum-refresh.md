# Story: gamma-image-model-enum-refresh

**Status:** done (2026-07-02 — dual-gate CLOSED: Murat structural CLOSE no-conditions + Dan CD scoped-blocking checklist 4/4 PASS; 3-lane review 0 MUST-FIX [1 LOW + 1 INFO remediated]; resolving commit `2b963bc3`)
**Branch:** `dev/carried-findings-enum-refresh-2026-07-02` (HEAD at dev start: `e69b309c88d7b45296c358ba8660c5910c9757d7`; resolving commit: `2b963bc3` (committed post-dual-gate))
**Binding spec:** [`_bmad-output/planning-artifacts/gamma-image-model-enum-refresh-greenlight-party-record-2026-07-02.md`](../planning-artifacts/gamma-image-model-enum-refresh-greenlight-party-record-2026-07-02.md) (GREEN-LIGHT 6/6, D-1..D-5)
**Evidence dir:** [`_bmad-output/implementation-artifacts/evidence/enum-refresh-live-proof-20260702T053716Z/`](evidence/enum-refresh-live-proof-20260702T053716Z/)

## Ceremony disclaimer (DAN-1, verbatim — blocking)

Manual reconciliation citing learned-store observations obs-gamma-enum-parity-image-model-2026-07-02-3b951096 + obs-gamma-enum-parity-image-model-coverage-gap-2026-07-02-1bc1d8d2 (doc URL + fetch 2026-07-02T04:31:39Z). The promotion-path ceremony (automation-proposes / CD-ratifies-via-envelope) remains UNBUILT; this change does not instantiate it and is not a template for skipping it.

## The change (D-1 strict doc-parity)

`app/specialists/gary/_act.py::IMAGE_MODEL_VALUES` reconciled to the documented accepted values at <https://developers.gamma.app/reference/image-model-accepted-values.md>:

- **REMOVED (3, no longer documented):** `imagen-4-fast`, `qwen-image`, `qwen-image-fast`
- **ADDED (11, documented but absent):** `flux-1-pro`, `flux-1-quick`, `flux-1-ultra`, `flux-kontext-max`, `gpt-image-1-mini-high`, `gpt-image-1-mini-low`, `gpt-image-1-mini-medium`, `gpt-image-2`, `gpt-image-2-hd`, `gpt-image-2-mini`, `imagen-3-pro`

Enum size 32 → 40. Lockstep surfaces moved in this ONE change-set (D-2): `state/config/schemas/creative-directive.schema.yaml` + `.json` (embedded enum), `skills/gamma-api-mastery/references/parameter-catalog.md`, `tests/test_audit_gamma_docs_driver.py` (+ new synthetic fixture). Removal called out legibly here per D-1.

## Acceptance criteria → party decisions

| AC | Party decision | Result |
|---|---|---|
| AC-1 enum == documented values, both directions exact | D-1 (6/6) | DONE — live proof `enum-parity-image-model` → **confirmed**, exit 0 |
| AC-2 three-way parity pin (yaml ↔ json ↔ enum, SET equality), witnessed RED mid-sequence | D-2 (6/6) + Murat non-vacuity rider | DONE — `tests/test_gamma_image_model_enum_parity.py::test_image_model_enum_three_way_lockstep`; RED witness captured (Dev Notes W-2) |
| AC-3 provenance comment (doc URL + last-reconciled + refresh procedure) at the frozenset + schema YAML only | D-3 (6/6) | DONE — 3-line comment at `_act.py::IMAGE_MODEL_VALUES`; 3-line comment at yaml `image_model:`; json untouched by comments |
| AC-4 synthetic-drift fixture, loudly named, fabricated-commented, planted deltas BOTH directions, exact-diff assertions; :413/:416 stale-string assertions retired; captured-real fixture test STRUCTURE-only | D-4 (6/6) | DONE — `tests/fixtures/retrieval/gamma_docs/synthetic_drift_image_model_accepted_values.md` (`fake-model-alpha` docs-not-enum → coverage-gap; real `recraft-v4-pro` omitted → doc-drift); driver battery re-pointed; structure-only test added |
| AC-5 live proof first-run-stands: driver re-run vs real developers.gamma.app, `enum-parity-image-model` → confirmed, exit 0; driver keeps ledger WRITE MONOPOLY (zero hand-authored mutations) | D-5 (6/6) | DONE — exit **0**, ledger byte-identical (written=0, noop=1), zero hand edits; see Live proof below |
| AC-6 machine-readable `provenance: documented-tier, unverified-in-production` on EVERY never-rendered entry, parseable/display-consumable | Gary condition 1 / Dan condition 2 | DONE — dedicated per-model Provenance column in the catalog's Unclassified table; teeth: `test_catalog_never_rendered_models_carry_machine_readable_provenance` |
| AC-7 explicit "Unclassified — never rendered, tier TBD" catalog row; NO invented tiers; Gamma's own credits/tiers cited verbatim with URL + fetch date | Amelia L-5 / John fence | DONE — tier taxonomy untouched; documented tier + credits cited from the live page fetched 2026-07-02T05:43:58Z |
| AC-8 removals demonstrated (not asserted): zero live stale bindings | DAN-1 evidence rider | DONE — see Removal evidence below |
| AC-9 scope fence: no promotion-path automation, no tier redesign, no keywords→style, no test renders, no styleguide edits, no refresh automation | John (binding) | HELD — diff surfaces are exactly the lockstep set + tests + this record + evidence |

## Dev Notes — RED-first sequence (Murat, executed exactly)

**T1 discovery (hard gate) findings:**

1. **json-from-yaml generation story:** NO generator exists. `creative-directive.schema.json` is hand-maintained in lockstep with the `.yaml` (grep of `scripts/` found only the validator reading the json; `git log --follow` shows both schemas edited in the same feature commits, e.g. `bd0003d3`, `314c3ede`). → **three-way pin** per D-2, not json==generate(yaml).
2. **Flipped-symbol sweep (all 14 strings, exact token-boundary regex `(?<![A-Za-z0-9.\-])value(?![A-Za-z0-9.\-])` — `qwen-image` never matched inside `qwen-image-fast`):** 73 hits across `app/`, `scripts/`, `tests/`, `skills/`, `state/`; every hit accounted for: the 3 enum copies (changed here), catalog (changed here), driver test :413/:416/:417 (repaired here), recorded-real fixtures (correct — they ARE the docs), the learned-store ledger rows 4–5 (driver-owned, untouched), and one **prose** `notes:` field in `gamma-doc-audit-manifest.yaml` (dated authoring-time record, NOT an enum copy — the manifest is a pointer table with a tested no-literals rule; left as-is, out of surface; flagged for the gates). **NO fourth enum copy** → no dual-gate escalation. No `len(` count pins on the enum exist anywhere.
3. **L-4 persisted-state sweep (`_bmad-output/`, `state/`, `runs/`, stale trio):** 38 hits, ALL archived/driver-owned — party records, leg-e evidence run-reports, the ledger's own drift rows, and the two schema files (changed here). **ZERO hits in `runs/`** (no persisted directive/bundle binds a stale value) and **ZERO hits in `state/config/gamma-style-guides.yaml`**. → removal is NOT a migration; no STOP tripwire fired. Evidence: `t1-flipped-symbol-sweep.json`.
4. **Parallel-agent fence:** `git status` confirmed the other agents' files (`tests/conftest.py`, `tests/marcus_capabilities/test_pr_rc.py`, `tests/specialists/vision/**`, `tests/contracts/**`, …) — zero overlap with this story's surfaces.
5. **Live doc TODAY vs ledger rows:** fetched 2026-07-02T05:43:58Z, HTTP 200, **byte-identical to the committed leg-e fixture** (raw sha256 `b30de00d…a047b7`); today's live sets == the ledger rows' 3-remove/11-add sets exactly. No delta to reconcile. Capture + provenance: `live-doc-capture-image-model-accepted-values.md` + `live-doc-capture-provenance.json`.

**RED witnesses (evidence dir):**

- **W-1 (step 1, doc-fixture-vs-enum RED at HEAD)** — `red-witness-step1-at-HEAD-full.txt`: `test_enum_matches_documented_accepted_values` FAILED with the EXACT sets — `'phantom-in-enum-absent-from-docs': ['imagen-4-fast', 'qwen-image', 'qwen-image-fast']`, `'documented-absent-from-enum': ['flux-1-pro', 'flux-1-quick', 'flux-1-ultra', 'flux-kontext-max', 'gpt-image-1-mini-high', 'gpt-image-1-mini-low', 'gpt-image-1-mini-medium', 'gpt-image-2', 'gpt-image-2-hd', 'gpt-image-2-mini', 'imagen-3-pro']`. Same run: parity pin **PASSED** = GREEN-but-stale-in-sync recorded (step 2).
- **W-2 (step 3, pin non-vacuity RED)** — `red-witness-step3-pin-nonvacuity.txt`: after refreshing the enum ONLY, `test_image_model_enum_three_way_lockstep` FAILED (`creative-directive.schema.yaml image_model.allowed_values diverged from IMAGE_MODEL_VALUES — the three surfaces move in ONE change-set (D-2)`) while the doc-parity test flipped GREEN. Pin witnessed RED mid-sequence per Murat's rider.
- **W-3 (step 4/5 GREEN)** — `green-witness-step5-all-surfaces.txt`: all 4 parity/catalog tests GREEN after schema + catalog refresh.
- **W-4 (synthetic-drift detection post-refresh)** — `test_classify_enum_drift_is_asymmetric_with_distinct_kinds` (exact planted diffs `doc-drift == ['recraft-v4-pro']`, `coverage-gap == ['fake-model-alpha']`) + end-to-end `test_exit_ten_on_drift` (EXIT_DRIFT=10 against the synthetic page) — the driver DETECTS drift post-refresh; the RED path is decoupled from live-world state (D-4; re-pin-to-confirmed was REJECTED and not done).

**Battery + lint:** consolidated scoped battery **301 passed, 1 skipped** (`final-scoped-battery.txt`; the skip is a pre-existing live-gated gary test): driver 66/66, new pins 4/4, creative-directive schema 10/10, styleguide validator battery, full `tests/specialists/gary`, gamma-docs provider battery, `test_run_gary_dispatch`, gary activation contract. `ruff check` on all touched Python files: **All checks passed** (new test file also `ruff format`-clean; `_act.py`/driver test were not format-clean at HEAD — pre-existing, not churned). Full-tree runs show unrelated churn from the parallel agents; batteries scoped per the fence.

## Live proof (D-5, first-run-stands)

`.venv/Scripts/python scripts/utilities/audit_gamma_docs.py --evidence-dir …/enum-refresh-live-proof-20260702T053716Z/audit-run` — real fetch, no key, run started 2026-07-02T05:54:36Z:

- **exit tier 0** (bar met, first run stands). `enum-parity-image-model` → **confirmed** ("enum-membership parity"). All 12 real items confirmed.
- Probe drifted as designed (doc-restructure, report-only); the two `findings_only` items drifted as expected at authoring time (report-only, tier-excluded per P6). **No NEW unrelated drift.**
- **Ledger discipline held:** before/after sha256 identical (`e8f8331f…`), lines 6 → 6, written=0, noop=1 (the burst-throttle standing-resolution row re-derived digest-idempotently). ZERO hand-authored ledger mutations; snapshots `ledger-before-live-run.jsonl` / `ledger-after-live-run.jsonl`. The driver's only side-write was its designed `doc-sources.yaml::last_refreshed` stamp (1-line diff).
- **Driver-gap FINDING (expected, per D-5/Dan option 2):** the re-run does NOT flip/annotate the two standing candidate rows — the ledger has no resolution-row kind for drift candidates resolved by a code change; the rows persist as `status: candidate` while the run report says confirmed. Reported honestly, NOT hand-crafted around. This is exactly the `gamma-ledger-resolution-row-kind` follow-on (below).

## Candidate rows → resolving change (cross-reference)

| Ledger row (stands as `candidate`; see driver-gap finding) | Resolved by |
|---|---|
| `obs-gamma-enum-parity-image-model-2026-07-02-3b951096` (doc-drift: the 3 removals) | this story's change-set on `dev/carried-findings-enum-refresh-2026-07-02` (commit SHA: `2b963bc3`) — post-change driver re-run artifact `audit-run/run-report.{json,md}`, exit 0 |
| `obs-gamma-enum-parity-image-model-coverage-gap-2026-07-02-1bc1d8d2` (coverage-gap: the 11 additions) | same change-set + same re-run artifact |

## Removal evidence (demonstrated, not asserted — DAN-1)

- `state/config/gamma-style-guides.yaml`: **zero** stale-string hits (exact-match sweep) AND `scripts/utilities/validate_gamma_style_guides.py` → "OK … copacetic (5 styleguide(s))", exit 0, post-removal (`validator-styleguides-post-removal.txt`) — the validator's image_model check now runs against the refreshed 40-value enum.
- `runs/` (all run dirs incl. bundles/directives): **zero** hits for `imagen-4-fast` / `qwen-image` / `qwen-image-fast` (exact-match).
- `_bmad-output/` hits are party records + archived leg-e evidence only; `state/` hits are the ledger's own drift rows (driver-owned) + the two schema files changed here. Full listing: `t1-flipped-symbol-sweep.json` (sweep B).

## Phase-2 first-bind live-witness rider (Gary, binding)

The 11 added models are **documented-tier, unverified-in-production** (docs-ahead-of-API is the bite risk). **Phase-2's FIRST styleguide that binds any newly-added `image_model` is DESIGNATED the live availability witness** for that model: a live rejection at that first bind is a FINDING that files to the learned store (the designed loop), not a rollback trigger for this reconciliation. The machine-readable catalog marking clears ONLY on a real production render; another doc read does not clear it. Test teeth: `test_catalog_never_rendered_models_carry_machine_readable_provenance` pins the marked set to exactly these 11 until a render-witnessed story updates both catalog and pin.

## Proposed deferred-inventory entry (for the orchestrator to file — NOT filed by the dev agent)

> **`gamma-ledger-resolution-row-kind`** (attach to the promotion-path story). The learned-observations ledger has no row kind that records "this candidate was resolved/acted-on by a code change": after the 2026-07-02 enum refresh, rows `obs-gamma-enum-parity-image-model-2026-07-02-3b951096` + `obs-gamma-enum-parity-image-model-coverage-gap-2026-07-02-1bc1d8d2` persist as `status: candidate` although the drift they record is reconciled (post-change driver re-run confirmed, exit 0 — evidence `enum-refresh-live-proof-20260702T053716Z/audit-run/`). Dan's honesty rider: persisting `candidate` after acting is a lie in the other direction, but hand-writing resolution rows would break the driver's write monopoly. Scope: add a driver-written resolution/acted-on row kind (append-only, citing the resolving commit + the resolved observation_ids), wired to the promotion-path ceremony (automation-proposes / CD-ratifies-via-envelope). Direction may flip if the ledger substrate evolves.

## Files touched

- `app/specialists/gary/_act.py` — enum refresh + D-3 provenance comment (nothing else)
- `state/config/schemas/creative-directive.schema.yaml` — enum refresh + D-3 provenance comment
- `state/config/schemas/creative-directive.schema.json` — enum refresh (no comment; JSON)
- `skills/gamma-api-mastery/references/parameter-catalog.md` — stale trio removed from Standard row + Photorealistic line; Unclassified row + per-model provenance table added
- `tests/test_gamma_image_model_enum_parity.py` — NEW: doc-parity test, three-way pin, catalog mention-pin, provenance-marking teeth
- `tests/test_audit_gamma_docs_driver.py` — drift battery re-pointed at the synthetic fixture (exact diffs); confirmed-on-real-page twin + structure-only real-fixture test added
- `tests/fixtures/retrieval/gamma_docs/synthetic_drift_image_model_accepted_values.md` — NEW: fabricated drift fixture (header-declared)
- `tests/fixtures/retrieval/gamma_docs/README.md` — synthetic-fixture provenance section + reachability note updated
- this story record + evidence dir

**Out-of-surface, driver-owned side effect:** `skills/gamma-api-mastery/references/doc-sources.yaml` `last_refreshed` stamp (written by the live audit run itself, by design).
