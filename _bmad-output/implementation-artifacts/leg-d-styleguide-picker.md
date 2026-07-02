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
- **AC-8 evidence dir:** `_bmad-output/implementation-artifacts/evidence/leg-d-picker-ac8-20260702T014409Z/` — harness + rendered `picker.html` + real `directive.yaml` + `dispatch-payload-snapshot.json` + `pick-event-log.json` + `result.json` (11/11, `AC8_PASS: true`) + `AC8-SUMMARY.md`. M-3 two-artifact diff: guide identity AGREES ((A, classic-freeform-x-cards), (B, leg-c-part3-floor-probe)); the floor probe threaded `{"min_cluster_floor": 8}` through the REAL `_runner_payload_for_specialist` irene_pass1 branch. **Superseded by the post-remediation re-run below (R1 changed the primary flow).**
- **Tests:** 27 new (both picker files) + Leg-C battery 193 = **220 passed** post-AC-8. `validate_gamma_style_guides.py` green after every SSOT edit and after the live leg. Ruff clean on all touched files.
- **Scope fence held:** zero edits to gary/manifest/production_runner/irene; SSOT edits limited to probe markers + 3 seed thumbnail_refs; no gh-pages.

### 3-lane remediation R1-R14 (2026-07-02, Claude Fable 5 remediation dev agent; RED-first)

**Findings remediated** (3-lane review: Blind Hunter / Edge Case Hunter / Acceptance Auditor) — one commit, all 14 items:

- **R1 [MUST-FIX, Blind#1 CORS]:** the primary flow opened the page via `file://` while its JS `fetch()`ed `http://127.0.0.1:<port>/pick` — null-origin CORS blocks reading the response, so the operator never saw the receipt panel (the server-side write still landed; the original AC-8 harness POSTed via urllib and bypassed the browser layer, masking this). FIX: the pick server now serves the page itself — the browser opens `http://127.0.0.1:<port>/`, `do_GET` serves the rendered page bytes AND the curated thumbnails under `/thumbnails/<guide>.png` (a `file://` img on an http page is browser-blocked too), and the form action is the RELATIVE `/pick` — same-origin end-to-end. The disk HTML copy is still written for evidence/debug (its relative thumbnail srcs resolve only when served; documented).
- **R2 [MUST-FIX, Auditor#1 J-2/D-2 honesty]:** **honest disclaimer** — the blueprint guide's thumbnail is a REAL Gamma render byte-matching the guide's prompt surface (theme e8tz1vxb9v1urqp + lineArt + recraft-v3-svg + blueprint keywords + preserve) BUT it is portrait/fluid **2400x2860** while the guide promises **16:9**: it is representative of palette/line-art, NOT of layout. The picker now renders a data-driven provenance chip on any such card ("render predates this guide's 16:9 frame — representative of palette/line-art, not layout"): SSOT `page_settings.card_options.dimensions == 16x9` + PNG aspect < 1.4, aspect read from the PNG IHDR chunk via a stdlib-only header parse (`_png_dimensions`). Follow-on filed (below + deferred-inventory): `gamma-styleguide-per-guide-thumbnail-renders`.
- **R3 [Blind#2]:** "waiting for your pick at <url> (timeout Ns; Ctrl-C to abort)" notice printed before `handle_request` blocks.
- **R4 [Blind#3]:** POST body reads capped at 64KB (`MAX_POST_BODY_BYTES`); oversized → 413 + server keeps serving.
- **R5 [Edge#1]:** duplicate `variant_id` rows in an existing directive's `gamma_settings` → `PickerError` at load (fail-loud, never first-match-patch; normalization-aware, so `A`/`a` dupes trip it).
- **R6 [Edge#2]:** `gamma_settings` present-but-non-list → `PickerError` (never silently discarded/overwritten); non-mapping list entries fail loud too (same silent-drop class).
- **R7 [Edge#3] symmetry:** post-`retire-default-variant-pair`, single-variant is legitimate — the CLI fallback now allows skipping Style A and picking only B (at least one slot required, mirroring the web 400); BOTH paths pinned by tests; module + `capture_pick` + `_cli_fallback` docstrings state that a single-variant directive dispatches exactly one deck.
- **R8 [Edge#5]:** advisory file locking (`msvcrt.locking` Windows / `fcntl.flock` POSIX; `<store>.lock` adjacent) around the sidecar digest-read+append AND the directive read-modify-write. HONEST guarantee documented: cooperating writers on the SAME host serialize; not a cross-host/non-cooperating guarantee.
- **R9 [Auditor#2]:** M-3 caveat appended to BOTH AC-8 summaries: the two arbiter artifacts share one pick event's `picks` dict — independence is code-path-level (runner directive read vs picker sidecar emit), not event-level.
- **R10 [NIT, Edge#4]:** thumbnail refs checked at render for `.png` extension + PNG magic/IHDR (reuses `_png_dimensions`).
- **R11 [NIT, Edge#6]:** empty-roster error now coaches `--include-probes` / `include_probes=True`.
- **R12 [NIT, Blind#4]:** `write_pick_to_directive` docstring states the yaml round-trip re-serialization (comments/anchors not preserved).
- **R14 [NIT, Auditor#3]:** direct CLI-fallback probe-exclusion test (D-3 default-hidden honored in the numbered roster).

**RED evidence (behavioral fixes, tests authored + run before the code change):**
- R1: `FAILED test_server_serves_page_same_origin_with_relative_pick_action` — `AssertionError: browser must be pointed at the server root` (opener received the `file://` URI) / `server must exit after one accepted POST`.
- R2: `AssertionError: the blueprint guide (16x9 promise, 2400x2860 portrait render) must qualify` (roster carried no `card_dimensions`; no chip rendered).
- R5: `Failed: DID NOT RAISE <class '...PickerError'>` (`test_duplicate_variant_id_in_existing_directive_fails_loud` — first-match-patch proceeded silently).
- R6: `Failed: DID NOT RAISE <class '...PickerError'>` ×2 (`test_gamma_settings_non_list_fails_loud`, `test_gamma_settings_non_mapping_entry_fails_loud` — non-list silently discarded).
- R7: `StopIteration` at the Style B prompt (`test_cli_fallback_a_blank_b_only_single_select` — blank Style A was rejected as "required") + `AssertionError` (`test_cli_fallback_requires_at_least_one_pick`).
- Also RED pre-fix: R8 (lock files absent), R10 (`DID NOT RAISE`), R11 (`Regex pattern did not match`). R14's pin passed pre-fix (roster loader already excluded probes) — recorded as a pin, not a fix.

**AC-8 RE-RUN (mandatory — primary flow changed):** `_bmad-output/implementation-artifacts/evidence/leg-d-picker-ac8-20260702T020617Z/` — the harness GET the page FROM the server (200; served bytes == disk copy), parsed the SERVED form (relative `/pick`), GET a same-origin thumbnail (image/png), POSTed exactly as the page's Confirm would; **17/17 checks, `AC8_PASS: true`, first-run-stands**; `AC8-SUMMARY.md` carries the R9 caveat.

**Post-remediation verification:** both picker test files **41 passed** (27 prior + 14 remediation); `tests/utilities/test_validate_gamma_style_guides.py` green; `validate_gamma_style_guides.py` script green (SSOT untouched by this remediation); ruff clean on touched files.

### Follow-ons (filed in deferred-inventory §Named-But-Not-Filed Follow-Ons)
- `gamma-styleguide-per-guide-thumbnail-renders` (Phase-2): systematic genuine per-guide renders replace the curated approximations — retires the R2 provenance-chip disclaimer case (each guide's thumbnail becomes a true render of that guide's full surface incl. its frame).
