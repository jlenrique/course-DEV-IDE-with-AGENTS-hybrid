# Story 35.4 — GET-only HUD server + projection reader — Completion Notes

**Date:** 2026-07-11
**Branch:** dev/hud-revival-2026-07-11 (no commit — orchestrator commits post-review)
**ADs:** 6 (GET-only transport, ETag poll), 8 (identity binding / refuse-to-render), consumer side of 4 (lenient-only), 12 (explicit-path reader seam).
**Dev discipline:** formal bmad-dev-story; owns ONLY new trees. Did not touch production_runner.py, trial.py, app/notify/**, run_hud.py, or the contract module.

## Files (all new, all owned by 35.4)

- `app/hud/__init__.py` — package marker + layer-rule docstring.
- `app/hud/data.py` — explicit-path projection reader: `read_operator_surface(run_dir)`, `read_snapshot(run_dir)` (one open-read-close → raw bytes + mtime_ns + lenient-parsed value), `projection_etag(parsed, *, mtime_ns=None)`, `PROJECTION_FILENAME`, `projection_path`.
- `app/hud/server.py` — `create_hud_app(trial_id, run_dir, launch_nonce, mode="session")` FastAPI factory (exactly 3 GET routes) + `run_hud_server(...)` env-driven uvicorn entry + `python -m app.hud.server` guard.
- `tests/hud/_helpers.py` — projection fixture builder (uses the strict producer model to author byte-valid fixtures — producer's job, not a consumer strict-parse).
- `tests/hud/conftest.py` — `run_dir`, `bound_trial_id` fixtures.
- `tests/hud/test_server_routes.py` — route inventory, mutation rejection, healthz, ETag/304, refuse-to-render, lenient/raw passthrough, placeholder shell.
- `tests/hud/test_data.py` — data.py unit tests.
- `pyproject.toml` — added import-linter contract **HUD1** (app.hud → orchestrator / gates / scripts forbidden). No dependency additions (httpx/fastapi/uvicorn already present).

## Route inventory proof (AD-6)

```
APIRoute count: 3
  APIRoute       /              ['GET']
  APIRoute       /projection    ['GET']
  APIRoute       /healthz       ['GET']
```

Exactly three routes, all GET-only, zero WebSocket/Mount/mutation routes. The FastAPI app is built with `docs_url=None, redoc_url=None, openapi_url=None` so the auto-mounted `/docs` + `/openapi.json` GET routes do not muddy the zero-mutation-surface proof. `test_route_inventory_is_exactly_three_get_routes` asserts count==3 and `methods == {"GET"}` per route; `test_no_route_exposes_a_mutating_verb` / `test_no_websocket_or_mount_routes` are the negative guards; `test_mutating_requests_are_rejected` confirms POST/PUT/DELETE → 405 at runtime.

## Design decisions of record

1. **`/projection` serves the RAW file bytes always (zero-lie).** The route reads the file once (open-read-close), parses those same bytes via the contract's `read_operator_surface_lenient`, derives the ETag, then responds with the exact on-disk bytes — never a re-serialization. Consumers see precisely what the runtime wrote. The **409 identity guard is the only gate** on that passthrough.
2. **Identity guard fires only on a parsed projection.** An `Unrecognized` snapshot (unknown schema_version / unknown status / garbage) carries no `trial_id` to compare, so it passes the guard and is served raw with an `unrecognized:<mtime_ns>` ETag — so the HUD page renders UNRECOGNIZED literally (never coerced) and the poll loop keeps cycling. A parsed projection whose `identity.trial_id` ≠ the bound id → `409 {refuse_to_render: true, bound, found}` (canonical-UUID compared, so hyphenation/case never manufacture a false mismatch).
3. **ETag = `<schema_version>:<seq>`** (route-implemented If-None-Match → 304, `Cache-Control: no-cache`). `seq` bumps on every write (AD-10), so same-size rewrites inside mtime granularity still change the ETag — the mtime+size trap AD-6 forbids is avoided. Fallback `unrecognized:<mtime_ns>` for unparseable snapshots.
4. **Absent projection → 404** (`{detail: "projection not found"}`), the honest state before the runtime has written `registered`. `read_operator_surface` / `read_snapshot` return `None` on absent file per spec.
5. **`/` is the v1 placeholder shell** (< 150 lines, #0F172A dark background, real ETag poll loop against `/projection` with `If-None-Match`, no buttons). Story 35.5 replaces it with the full render.

## Verification results

| Gate | Command | Result |
|---|---|---|
| Unit/route tests | `.venv/Scripts/python.exe -m pytest tests/hud -q` | **22 passed** |
| Lint | `ruff check app/hud tests/hud` | **All checks passed** |
| Import fences | `lint-imports` | **17 kept, 0 broken** (HUD1 KEPT) |
| Lockstep | `check_pipeline_manifest_lockstep.py` | **exit 0** (trace `reports/dev-coherence/2026-07-11-2137/…PASS.yaml`) |

`app/hud/**` and `tests/hud/**` were already registered in `block_mode_trigger_paths` by 35.0 (inert until file creation, AD-14); the checker stays green with the files now present.

## Deviations

1. **Import fence — `scripts.utilities.hud_data_sources` not directly nameable.** import-linter rejects a subpackage of an external package (`scripts` is not a `root_package`; only `app` is). The HUD1 contract therefore forbids the whole external `scripts` top-level from `app.hud` — a **strictly stronger** guarantee (the HUD imports nothing from `scripts/`, which is where the retired April readers live). Story 35.8 owns the full fence set and can add the precise `anything ↛ hud_data_sources` global rule once `scripts` joins `root_packages`; documented inline in pyproject.toml.
2. **Strict-parse fence is not import-linter-expressible.** AD-4 forbids consumers strict-parsing, but `OperatorSurfaceProjection` is a symbol inside the same contract module `app.models.runtime.operator_surface` (which `app.hud` must import for the lenient reader), so a module-level forbidden contract cannot separate the two. Enforced instead in-code (`data.py` calls `read_operator_surface_lenient` exclusively; `server.py` uses the model only for an `isinstance` identity check on the lenient result, never to parse). Noted for 35.8's fence-set review.
3. **`projection_etag` signature** takes an explicit `mtime_ns` kwarg (the spec sketched `projection_etag(raw_or_proj)`). The projection object does not carry file mtime, so the server passes `snapshot.mtime_ns` for the Unrecognized/None fallback branch; content-derived branch (`<schema_version>:<seq>`) ignores it.

## Follow-ons for downstream stories

- 35.5 replaces the `/` placeholder shell with the retargeted render, fed by the same `/projection` byte snapshots.
- 35.8 formalizes the full import-fence set (app.notify arrows + precise hud_data_sources rule) — coordinate with HUD1 (35.4 added only its own app.hud arrows per the epic's parallel-lane rule).

## Review-fold addendum (2026-07-11 — code-review findings folded)

Second dev pass folding the four accepted code-review findings. `.venv/Scripts/python.exe -m pytest tests/hud -q -p no:cacheprovider` → **33 passed** (was 22); `ruff check app/hud tests/hud` → clean.

### MUST-1 — Identity-guard bypass on Unrecognized snapshots (AD-8 breach, probe-proven)

A valid-shaped v1 document with a foreign `identity.trial_id` plus one malformed sibling field (e.g. `as_of`) lenient-parses to `Unrecognized` and previously sailed past the guard → served 200 raw → the placeholder shell rendered the WRONG run's `envelope.status`. Fix in `app/hud/server.py`: new `_raw_identity_trial_id(raw)` does a best-effort `json.loads` (try/except `ValueError`) and reads `identity.trial_id` then top-level `trial_id` (string, non-blank); the `/projection` guard now canonical-UUID-compares that extraction for Unrecognized snapshots and returns the SAME typed 409 refuse-to-render payload on mismatch. Serve-raw survives ONLY when no identity is truly extractable (non-JSON bytes, non-dict, absent/blank ids). Regression tests: probe case → 409 (`test_unrecognized_snapshot_with_foreign_identity_is_409`), top-level trial_id mismatch → 409, garbage bytes → 200 unrecognized ETag, matching raw identity → 200 (guard passes honestly). Probe replayed live post-fix: **409**.

### S2 — RFC-9110-conformant ETag

ETag now emitted in the quoted form (`"v1:1"`, `"unrecognized:<mtime_ns>"`) via `_quote_etag`; `projection_etag` in `data.py` still returns the unquoted core (test_data pins unchanged) — quoting happens once at the HTTP boundary. New `_if_none_match_matches` implements the comparison: strips `W/`/`w/` prefixes (weak comparison is correct for If-None-Match), strips quotes both sides, splits comma-lists, honors `*`. Placeholder JS echoes the header verbatim (verified — it stores `resp.headers.get("ETag")` and sends it back untouched; the server-side parse absorbs the quotes). Tests pin the QUOTED form exactly plus weak / comma-list / star / non-matching-list cases.

### S3 — Env entry exits cleanly

`run_hud_server` env path no longer KeyError-tracebacks: `_required_env` raises `SystemExit` with a one-line actionable message naming the missing var (`HUD_TRIAL_ID` / `HUD_RUN_DIR` / `HUD_LAUNCH_NONCE`), and a non-integer `HUD_PORT` raises `SystemExit` naming the var and the bad value (`from None`, no traceback chain). Three tests via monkeypatched env + `pytest.raises(SystemExit)`; the port test fails at parse time, before `create_hud_app`/uvicorn.

### S4 — Placeholder honest states

The shell now branches on the `unrecognized:` ETag prefix (after stripping `W/` + quotes in JS) BEFORE any `resp.json()`: a non-JSON 200 renders **UNRECOGNIZED** with a raw-text preview — never a parse-throw into DISCONNECTED. `DISCONNECTED` is now set only in the fetch catch (transport failure). The etag is cached only after a successful render: the honest UNRECOGNIZED render caches (so 304s flow), the defensive parse-failure branch does NOT cache (next poll retries fresh). Shell is 99 lines (<150). Pinned by `test_placeholder_shell_keys_unrecognized_off_etag_prefix` + a `<150 splitlines` assertion on `/`.

### Naming deviation noted (review NIT-6)

`app/hud/data.py::read_operator_surface` keeps its name (review NIT-6 suggested a rename). Deviation is deliberate: the name matches the spec's public-surface sketch and the contract-reader naming (`read_operator_surface_lenient`) it wraps; renaming would ripple into 35.5/35.8 references for zero behavioral value. Recorded here as the standing deviation of record.
