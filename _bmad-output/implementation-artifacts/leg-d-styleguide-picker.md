# Leg-D — HTML style-picker at CD-entry (pre-run operator surface, Fork A)

**Arc:** Gamma Styleguide Library · **Branch:** `dev/gamma-styleguide-leg-c-live-2026-07-01` · **Class:** S · **Status:** in-progress (dev complete, review pending)
**GREEN-LIGHT:** `leg-d-styleguide-picker-greenlight-party-record-2026-07-02.md` — **6/6 FORK A**; ALL amendments there are BINDING and are the spec authority (J-1..J-4, M-1..M-3 + AC regime, A-1, D-1..D-3, S-1..S-3, scope fence, honesty banner). This story file is the pointer + status carrier; do not restate-and-drift.
**Gate mode:** DUAL-GATE — 🧪 Murat (structural: AC regime incl. the AC-8 live leg + cite-the-consumer discipline) + 🎨 Dan (CD contract: sidecar-only last_used, curated thumbnail discipline, probe visibility, write-gate integrity). Sally advisory on S-1..S-3.

## What ships (scope fence, one story)
`app/marcus/orchestrator/styleguide_picker.py` (stdlib-only, reads the SSOT yaml directly): card-grid HTML (thumbnail-primary; slot-bar A/B; receipt panel; probe chip + default-hidden), localhost `http.server` pick capture (CLI fallback), directive `gamma_settings[]` write (existing A/B semantics verbatim) + `styleguide_picker_provenance` block, append-only `state/config/gamma-styleguide-picks.jsonl` sidecar, initial thumbnail curation (copy real evidence PNGs → `state/config/gamma-styleguide-thumbnails/` + validator-gated `presentation.thumbnail_ref` fill for the 3 seed guides), probe-visibility marker for the 2 Leg-C probe guides. Tests per Murat's AC-1..AC-8. DEFERS per the record.

## ACs — see the green-light record §MURAT'S AC REGIME (AC-1..AC-8, M-1..M-3). RED-first.

## Dev Notes

**Dev complete 2026-07-02 (Claude Fable 5 dev agent). Commits:** `dc335d05` (SSOT curation), `97ea6f2b` (picker module + AC-1..AC-7 tests), AC-8 evidence commit follows.

### RED evidence (RED-first)
- Both test files (`tests/marcus/orchestrator/test_styleguide_picker.py` — AC-1/4/5/6, A-1 fail-loud, capture server, CLI fallback, J-1 boundary; `test_styleguide_picker_consumers.py` — AC-2/3/7, M-1 real-module imports) were authored and RUN before `app/marcus/orchestrator/styleguide_picker.py` existed: `E ModuleNotFoundError: No module named 'app.marcus.orchestrator.styleguide_picker'` (pytest exit 2) — the shared RED for every AC in the regime. Implementation then went 27/27 green with no test edits.
- AC-8's RED-equivalent is the arbiter discipline itself: first-run-stands, 11/11 checks recorded in `result.json` (no retry-to-green).

### Choices made (with cited authority)
- **D-3 probe marker = `presentation.visibility: probe`** (NOT `status: probe`). The validator ignores `status` entirely so `status: probe` would have passed, but the green-light record's own inline correction directs the additive visibility marker; `status: active` keeps its existing meaning untouched. Validator green after each SSOT edit.
- **D-2 thumbnail curation** (real evidence PNGs → `state/config/gamma-styleguide-thumbnails/`):
  - `classic-freeform-x-cards` ← `evidence/leg-a-styleguide-differential-20260701T164108Z/render-A-classic/A_p3-high-maze.png` (true Classic output per AC5-SUMMARY; the HIGH-detail maze card is the richest representative of the illustrated-vector register).
  - `hil-2026-apc-blueprint-classic` ← same dir `render-A-classic/B_p3-high-maze.png` — the only live render of the blueprint surface on disk (the Edge#8 fixture-B deck). Verified byte-identical surface to the guide (theme `e8tz1vxb9v1urqp` + lineArt + recraft-v3-svg + blueprint keywords + preserve; the guide's provenance says it "Promotes DEFAULT_VARIANT_PAIR B"). Real live Gamma output, J-2 satisfied.
  - `hil-2026-apc-studio-image-card` ← `render-B-studio/gary_A_studio_02_p3-med-physicianship.png` (true Studio 16:9 full-bleed that passed `_assert_studio_image_card`).
  - Probe guides keep `thumbnail_ref: null` → S-3 "no live render" placeholder (test-pinned).
- **Thumbnail `src` = absolute `file://` URI** (`Path.as_uri()`) rather than a literal relative path — the page is written to an arbitrary temp/evidence dir, so a relative src would dangle; AC-6 pins that every rendered ref resolves to a real on-disk PNG (magic-bytes checked) and a dangling ref raises `PickerError`.
- **J-3 patch semantics:** picked variant's existing `gamma_settings` entry is patched in place (its other per-variant keys survive — they still override the styleguide base downstream), absent entry appended as `{variant_id, styleguide}`, unpicked variants untouched (test-pinned incl. Gary base-layer resolution via the real `_normalized_gamma_settings`).
- **Sidecar** `state/config/gamma-styleguide-picks.jsonl`: digest-idempotent append-only (mirrors `gamma-learned-observations.jsonl`); malformed line → loud `PickerError` with line number; J-1/D-1 boundary pinned by a test that scans `app/specialists/**` for picker imports (zero) + the SSOT `last_used` stays-null test.
- **Capture:** `_PickServer` (ephemeral port) serves GET=page, POST `/pick`; unknown-guide POST → 400 and keeps serving; valid POST → receipt JSON, server exits; `on_pick` exception → 500 + re-raise to the caller (fail-loud). CLI-numbered fallback only when the browser opener fails (test-pinned, incl. single-select blank-B path).

### Evidence + verification
- **AC-8 evidence dir:** `_bmad-output/implementation-artifacts/evidence/leg-d-picker-ac8-20260702T014409Z/` — harness + rendered `picker.html` + real `directive.yaml` + `dispatch-payload-snapshot.json` + `pick-event-log.json` + `result.json` (11/11, `AC8_PASS: true`) + `AC8-SUMMARY.md`. M-3 two-artifact diff: guide identity AGREES ((A, classic-freeform-x-cards), (B, leg-c-part3-floor-probe)); the floor probe threaded `{"min_cluster_floor": 8}` through the REAL `_runner_payload_for_specialist` irene_pass1 branch.
- **Tests:** 27 new (both picker files) + Leg-C battery 193 = **220 passed** post-AC-8. `validate_gamma_style_guides.py` green after every SSOT edit and after the live leg. Ruff clean on all touched files.
- **Scope fence held:** zero edits to gary/manifest/production_runner/irene; SSOT edits limited to probe markers + 3 seed thumbnail_refs; no gh-pages.
