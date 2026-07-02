# gamma_docs fixtures — provenance

**Leg-E** (`leg-e-gamma-docs-live-doc-audit.md`, AC#7 / Murat M-8): every fixture in
this directory is a **recorded real page** — the verbatim response body of one HTTP
GET against a `developers.gamma.app` `.md` endpoint, captured 2026-07-02 with the
polite audit UA (`bmad-gamma-docs-audit/0.1`) during fixture capture (NOT the live
proof; the T7 live proof runs separately and first-run-stands). Machine-readable
copies of these stamps live in `_provenance.json` (same directory).

Unstamped fixtures do not merge: any new fixture added here MUST carry a row in
this table AND an entry in `_provenance.json`.

`content_sha256` is computed over the NORMALIZED text (CRLF→LF, unicode NFC),
matching the adapter's digest recipe (Murat M-6: digest normalized selector-scoped
text, never raw HTML). `raw_sha256` is over the raw response bytes. For these
captures the two coincide because the pages were served LF/NFC-clean.

## Files

| File | source_url | fetched_at (UTC) | content_sha256 | selector |
|---|---|---|---|---|
| `image_model_accepted_values.md` | https://developers.gamma.app/reference/image-model-accepted-values.md | 2026-07-02T03:19:14Z | `sha256:b30de00d2d3dc0a607273e79106ab64906dc4a0d55cc142d05992ad3f6a047b7` | whole-page raw markdown (`.md` suffix endpoint) |
| `generate_api_parameters_explained.md` | https://developers.gamma.app/guides/generate-api-parameters-explained.md | 2026-07-02T03:19:15Z | `sha256:3b6721983e1bafc6308cbb3268af0c5aebd95315a679539633bbb8aa8bc4bb3a` | whole-page raw markdown (`.md` suffix endpoint) |
| `async_patterns_and_polling.md` | https://developers.gamma.app/guides/async-patterns-and-polling.md | 2026-07-02T03:19:16Z | `sha256:dde0723a426ab60bf7d456b10ba2dcff675a8ab65b420f392d3604996230971c` | whole-page raw markdown (`.md` suffix endpoint) |
| `list_themes.md` | https://developers.gamma.app/workspace/list-themes.md | 2026-07-02T03:19:18Z | `sha256:ffe45653d496ca4ab10337bcc6301b028d3ab52e5c8618d09747646503f6a5fa` | whole-page raw markdown (`.md` suffix endpoint) |

## Synthetic fixtures (FABRICATED — never refresh from live)

| File | provenance |
|---|---|
| `synthetic_drift_image_model_accepted_values.md` | **FABRICATED** (D-4, enum-refresh party record 2026-07-02). NOT a recorded real page — deliberately planted deltas vs `IMAGE_MODEL_VALUES` in BOTH directions (`fake-model-alpha` documented-but-not-enum -> coverage-gap; real `recraft-v4-pro` omitted -> doc-drift). Exempt from the recorded-page table + `_provenance.json` BY DESIGN; the `synthetic_drift_` filename prefix marks it out of any fixtures-from-live refresh scope. If the enum changes, regenerate to (enum − {recraft-v4-pro}) + {fake-model-alpha}. |

## Terminal-state reachability (AC#7)

All three terminal states are reachable from these fixtures in the hermetic
battery (`tests/test_audit_gamma_docs_driver.py`):

- **confirmed** — e.g. `enum-parity-text-mode` against
  `generate_api_parameters_explained.md` (docs list exactly
  `generate`/`condense`/`preserve`).
- **drift-detected** — `enum-parity-image-model` against
  `synthetic_drift_image_model_accepted_values.md` (FABRICATED planted deltas
  both directions vs `IMAGE_MODEL_VALUES`; since the 2026-07-02 enum-refresh
  reconciliation the RECORDED page confirms — D-4 keeps the RED path synthetic,
  decoupled from live-world state); plus the labeled `probe` item's
  known-absent anchor (`kind: doc-restructure`).
- **indeterminate** — tests serve a fixture URL with a transport failure /
  non-200 status via `responses` (the fixture body is real; the failure is the
  simulated condition, per Winston W-5 transport-failure classification).

## Discipline

Tests use per-test `responses.RequestsMock()` registered at the REAL doc URLs
(anti-pattern #8 guard — no module-level leaks, no stateful mocks), mirroring
`tests/test_retrieval_scite_provider.py`.
