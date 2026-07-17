# HIL tabular-projector replay fixtures (Epic 43, Story 43-0)

Frozen, version-controlled **render inputs** for `app/marcus/cli/hil_tabular_projector.py`
and every gate renderer Epic 43 adds. Captured per green-light **rider R2** (party
2026-07-17): *"capture real `directive.yaml` / `decision-card-*.json` / poll-surface
dicts from runs `5169a872` + `bc747b51` as frozen test inputs BEFORE any renderer."*

`state/config/runs/` is **gitignored**, so these copies exist to make the two real runs
durable, replay-testable inputs (Epic 43 §5: *pure-render, replay-testable, zero live
spend*). Everything here is a faithful copy of what a real run wrote to disk, with the
scrub in §3 applied.

## (a) Provenance

| Fixture | Source run | Source file | Gate / surface it feeds |
|---|---|---|---|
| `directive-5169a872.yaml` | `5169a872-6421-4e75-b07e-6a3bda42a4cc` | `directive.yaml` | **G0 directive composition** (the raw-YAML-dump surface 43-1 replaces) |
| `operator-surface-5169a872.json` | `5169a872-…` | `operator-surface.json` | G0 operator surface — run **cancelled at G0** (`trial-cancelled-at-g0`) |
| `directive-bc747b51.yaml` | `bc747b51-7009-4742-9f65-8de6abc29ca4` | `directive.yaml` | **G0 directive composition** (2nd real directive, different gamma variants) |
| `g0-enrichment-bc747b51.json` | `bc747b51-…` | `g0-enrichment.json` | **G0 enrichment** — 64 typed_components, 14 provisional_los, reconcile, dissents |
| `decision-card-g0e-bc747b51.json` | `bc747b51-…` | `decision-card-G0E.json` | **G0E enrichment decision card** — operator_prompt, typed_components, provisional_los, coverage_plan |
| `decision-card-g0r-bc747b51.json` | `bc747b51-…` | `decision-card-G0R.json` | **G0R refinement decision card** — operator_prompt, refined_los, lo_delta, reconcile |
| `decision-card-g1-bc747b51.json` | `bc747b51-…` | `decision-card-G1.json` | **G1 trial-open decision card** — drafted_proposal, evidence, verb |
| `operator-surface-bc747b51.json` | `bc747b51-…` | `operator-surface.json` | G1 operator surface — **paused/recover** state (`next_action.command = trial recover …`) |

Run `bc747b51` is the fuller run: it reached **G1** (paused there, then error-paused).
Run `5169a872` was **declined at G0** — it never got past the directive confirm, so its
only durable HIL artifacts are the directive + a cancelled-at-G0 operator surface.

## (b) Coverage — what is REAL here vs. what each downstream story must still capture

Between the two runs, the **only** gates that ever produced real on-disk operator content
are **G0 (directive), G0 enrichment, G0E, G0R, and G1**. No real run in this corpus
reached any later gate, so those renderer stories must capture their own fixtures when
they build (their poll-surface dicts do not exist on disk yet).

| Gate content type | Story | Real fixture here? |
|---|---|---|
| G0 directive / `sources[]` inventory | 43-1 | ✅ `directive-5169a872.yaml`, `directive-bc747b51.yaml` |
| G0 enrichment (metrics / ungrounded / provisional LOs) | 42-1 (done) | ✅ `g0-enrichment-bc747b51.json` |
| G0E enrichment decision card | 43-2/43-1 | ✅ `decision-card-g0e-bc747b51.json` |
| G0R refinement decision card | 43-2 | ✅ `decision-card-g0r-bc747b51.json` |
| G1 trial-open decision card | 43-2 | ✅ `decision-card-g1-bc747b51.json` |
| Operator-surface projection (G0 cancel + G1 recover) | 43-2 | ✅ both `operator-surface-*.json` |
| G1.5 estimator / run-constants (section_04_5 / 04_55) | 43-5 | ❌ must capture on its own |
| G1A plan-unit ratification (section_04a) | 43-5 | ❌ must capture on its own |
| G2B per-slide mode (section_05_5) | 43-3 | ❌ must capture on its own |
| G2M A/B variant (section_07b) | 43-3 | ❌ must capture on its own |
| G4A voice-candidate selection (section_11) | 43-4 | ❌ must capture on its own |
| literal-visual build targets (section_06b) | 43-6 | ❌ must capture on its own |
| storyboard build targets (section_07c) | 43-6 | ❌ must capture on its own |
| G3B storyboard / live-URL (section_08b) | 43-6 | ❌ must capture on its own |
| G2.5 motion-plan (section_07d) | 43-7 | ❌ must capture on its own |
| G2F motion-clip (section_07f) | 43-7 | ❌ must capture on its own |
| G4B input-package (section_11b) | 43-8 | ❌ must capture on its own |
| G5 final handoff (section_15) | 43-8 | ❌ must capture on its own |
| research packets | 43-9 | ❌ must capture on its own |
| workbook content | 43-9 | ❌ must capture on its own |

**Rider-R2 discipline note:** because no real run reached the later gates, a downstream
story cannot lean on this corpus to close its named surface — it must add its own real
fixture (or a documented hand-built one) alongside. This corpus is exactly the "G0E-only
replay corpus" §3 pin 3 warns must never be able to re-close the whole requirement.

## (b.1) SYNTHETIC fixtures (no real run reached the gate)

Some gates were **never reached by any real run** in this corpus (see the ❌ rows in
the table above), so per the rider-R2 discipline note a downstream story that cannot
lean on a real capture must add its own **documented hand-built** fixture. These are
clearly labelled SYNTHETIC and are built to match the exact `display_*` return shape
of the named `poll_surface` — they are **generated by running the real
`display_*(...)` function against a constructed decision card**, so the shape is
guaranteed faithful (only the identity UUIDs / timestamp / node ids are synthetic).

| Fixture | Shape source (`poll_surface`) | Gate / surface it feeds | Real run? |
|---|---|---|---|
| `poll-per-slide-mode-synthetic.json` | `app/gates/section_05_5/poll_surface.py::display_per_slide_mode` | **G2B per-slide mode** selection (Story 43-3) | ❌ SYNTHETIC — no real run reached G2B |
| `poll-variant-ab-synthetic.json` | `app/gates/section_07b/poll_surface.py::display_per_slide_variant` | **G2M A/B variant** selection (Story 43-3) | ❌ SYNTHETIC — no real run reached G2M |

Both carry the full `display_*` top-level keys (`surface_id`, `slide_id`,
`decision_card_digest`, `decision_card`, and the `per_slide_mode_payload` /
`per_slide_variant_payload` sub-map). The `surface_id` (`section_05_5_g2b_per_slide_mode`
/ `section_07b_g2m_per_slide_variant`) doubles as the **routing key** through
`hil_tabular_projector.GATE_TO_CONTENT_TYPE` → the bespoke `per_slide_mode` /
`variant_ab` renderer (Story 43-3 AC-0 bridge). No credential is present (the source
is a constructed model, not a live run), so no scrub applies.

## (c) Scrub policy applied

Per rider R2 and the `app/hud/public.py` positive-allowlist reference, the goal is a
**faithful render input with no live credential**:

1. **Credentials / nonces — MANDATORY redaction.** Each decision card carried a top-level
   `server_nonce` (the resume-authorization secret). Its value is replaced with the stable
   placeholder `REDACTED-NONCE`. The **key is kept** (its presence is schema-relevant); only
   the value is redacted. No `launch_nonce` / `token` / `api_key` / `secret` value appears
   anywhere in these two runs.
2. **Resume-authorization digest — redacted.** The top-level `digest` on each decision card
   is the checkpoint digest that pairs with `server_nonce` to authorize a resume — the
   "resume paste string with pre-filled digest" that `public.py` forbids on any shareable
   surface. Replaced with `REDACTED-DIGEST`. It is **not** a projector render input, so no
   render fidelity is lost.
3. **Everything the projector renders is preserved verbatim:** directive header
   (`run_id` / `corpus_dir` / `gamma_settings`) and full `sources[]`
   (`ref_id` / `role` / `locator` / `description` / `expected_min_words` / `excluded_reason`);
   decision-card `card.*` (`operator_prompt`, `drafted_proposal`, `pick_context`,
   `refined_los`, `lo_delta`, `evidence`, `verb`, `gate_id`); enrichment
   `typed_components` / `provisional_los` / `reconcile` / `dissents`.
4. **Non-credential content hashes and local paths are kept** (`envelope_digest`,
   `ssot_sha256` / `roster_sha256`, `decision_card_digest`, `corpus_fingerprint`,
   `publish_url`, `checkpoint_path`, `locator` paths, `operator_id`/`picked_by = Juanl`).
   These are render/provenance inputs already present throughout the repo, not live secrets.
   This deliberately differs from `public.py`, whose stricter denylist governs a **public
   tunnel wire**; these fixtures are **private, version-controlled test inputs**, so
   faithfulness to render structure wins over public-wire minimization — provided no
   credential survives (it does not; see the guard test).

Verbatim-copied (no scrub needed — no secret present): both `directive-*.yaml`, both
`operator-surface-*.json`, `g0-enrichment-bc747b51.json`.

Guard: `tests/unit/marcus/cli/test_hil_projector_fixtures.py` asserts every fixture parses,
carries its expected top-level keys, and that **no raw `server_nonce` / resume-auth digest
literal survives** in any file.
