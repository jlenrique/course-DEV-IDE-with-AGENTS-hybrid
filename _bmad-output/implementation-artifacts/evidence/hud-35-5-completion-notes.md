# Story 35.5 — Flight-deck render retarget — completion notes

**Status:** COMPLETE (all DoD witnesses green). No commit (orchestrator commits post-review).
**Branch:** dev/hud-revival-2026-07-11. **Agent:** fresh bmad-dev-story (retry after prior spend-limit death that wrote nothing — this run started clean).

## Files (all within declared ownership)

New — `app/hud/render/**`:
- `app/hud/render/__init__.py` — package exports (`render_page`, `render_zones`, `ZONE_IDS`).
- `app/hud/render/page.py` — pure projection→HTML render. `render_page(data)->str` (cold-load full page), `render_zones(data)->dict[str,str]` (zone-id→innerHTML). No I/O inside render.
- `app/hud/render/styles.py` — the stylesheet as one embedded CSS asset; DESIGN.md hex tokens VERBATIM.
- `app/hud/render/client.py` — the client poll renderer (`POLL_JS`), embedded JS asset.

Edited:
- `app/hud/server.py` — swapped the `/` placeholder shell for `render_page`; added `_flight_deck_data(...)` (identity-guarded cold-load envelope builder). Still GET-only, still exactly 3 routes, every 35.4 behavior preserved.
- `tests/hud/test_server_routes.py` — the one placeholder-shell test whose line-count pin (`< 150`) no longer holds was updated honestly to the real page (`> 150` + the five stable zone-container ids). The unrecognized-off-ETag test passes unchanged (JS idioms preserved).
- `pyproject.toml` — added `app/hud/render/styles.py` + `client.py` to `[tool.ruff.lint.per-file-ignores]` E501 (embedded CSS/JS asset files — the exact, already-established precedent used for `scripts/utilities/run_hud.py` and `generate-storyboard.py`). `page.py` (the render logic) stays within the 100-col limit.

New tests + fixtures:
- `tests/hud/_render_fixtures.py` — deterministic projection dicts (7 statuses) + panel-state + narrowed-component-selection envelopes; fixed `NOW`/`as_of` so age stamps and the stale veil are byte-stable.
- `tests/hud/test_render_goldens.py` — the v1 golden matrix.
- `tests/hud/test_render_units.py` — `render_zones` render-unit (stable ids, purity, changed-only isolation).

## DoD witnesses

- `pytest tests/hud -q` → **green** (33 pre-existing + 29 new = 62; full `tests/hud` + `tests/contracts/test_operator_surface_parity.py` = 153 passed).
- `ruff check app/hud tests/hud` → **All checks passed**.
- `lint-imports` → **HUD1 KEPT** (17 kept, 0 broken) — `app.hud` still imports the contract only; never orchestrator / gates / `scripts`.
- `check_pipeline_manifest_lockstep.py` → **exit=0** (PASS trace under `reports/dev-coherence/…`).

## Client-side-renderer DECISION of record

Server renders the full page for the COLD load (`render_page` on `GET /`); the browser then polls `GET /projection` (ETag `If-None-Match`, RFC-quoted form per 35.4) and re-renders the **dynamic** zones **client-side** from the projection JSON with a small vanilla-JS renderer mirroring `render_zones` (annunciator text+class, identity badge + freshness age, health tile values/ages, map current-step, briefing swap). No framework, no build step, no buttons, no `location.reload`.

Replacement is **zone-scoped innerHTML** (ladder: no granular DOM diffing). A zone is replaced only when its freshly-built HTML differs from what is installed (string-equality content compare), so `<details>` open-state, scroll, and a selection inside an *unchanged* zone all survive; a zone that currently holds a live selection is skipped. On a changed zone that carries `<details>`, open-state is captured by key and re-applied after replacement, with the **urgency auto-expand contract** (`data-auto-open="urgent"` → forced open) winning over remembered collapse — carried forward verbatim from `hud_per_step_summary.py`/`run_hud.py`. The pinned honesty idioms from 35.4 are preserved: UNRECOGNIZED is keyed off the `unrecognized:` ETag prefix BEFORE any `resp.json()`, and `DISCONNECTED` is set only in the fetch (transport) catch. Python `render_zones` is the byte-pinned source of truth under golden test; the live JS preservation check rides the 35.7 witness checklist (amendment 10).

## De-scope ladder cuts taken (party greenlight amendment 3+10, BINDING)

1. **Zone-scoped innerHTML replacement, NO granular DOM diffing** — implemented in `client.py::applyZone`.
2. **Specialist chips trimmed** — monogram/status/activity/current-node/last-artifact kept; **model-in-use + cost attribution dropped** (pinned by `test_specialist_chips_are_trimmed`: `gpt-5`/`cost_usd` absent from the deck).
3. **Health-tile drill-down history dropped** — tiles render value + age + confidence + threshold ring + stale veil; no per-reading history drill-down.
4. **State-trace = minimal append-only feed** — newest-last mono `<pre>`, `<details>` disclosure only; no filter UI.
5. **v1 golden matrix = 7 statuses + 4 panel states** (no-active-run, unrecognized, refuse-to-render, stale-veil). The `binding` / `feed-lost` / `config-unreadable` panel fixtures are the named fast-follow (amendment 10) — the RENDER PATHS exist and are wired (`binding`/`feed-lost` handled in `page.py` + `client.py`; config-unreadable renders the header ⚠ chip from `notifications_echo.parse_status`), only their dedicated goldens are deferred.

**Never-cut items — all present:** gate/error/batch briefings each render the **verbatim `next_action.command`** in a selectable `.cmd` block (pinned per pause class); deliverables summary on `completed` (FR16); identity-guard panel states — `refuse-to-render` + `binding` + `no-active-run` (FR17); `UNRECOGNIZED` with raw value quoted (FR18, pinned incl. a legacy-shaped-dir case rendered through the real server route).

## Contract-fidelity notes (contract boundaries, NOT ladder cuts)

The render surfaces exactly what the v1 `operator-surface` contract carries (zero-lie). The UX spine's richer "Projection Demands" are thinner in the shipped 35.1 contract, so:
- **Gate briefing** renders `paused_gate` + `next_action.command` (verbatim) + the paused node's `locked_artifact_summary` as the artifact-under-judgment. The spine's `gate_focus` / `operator_prompt` / drafted-proposal-with-confidence / discrete artifact list (G2B thumbnails, G4A voice rows) are **not v1 contract fields** → not rendered. The inline-artifacts-collapse-beyond-3 helper (`_artifacts_block`) is implemented and ready for when the contract carries a decision-card artifact list.
- **Error / failure briefing** renders `paused_error_tag` verbatim as the error identity + node/walk index + re-entry point + recover command (or "no automated recovery — see SPOC"). The spine's separate verbatim `error-pause.json` message and LangSmith trace link are not discrete v1 fields (the LangSmith URL rides a health tile's sub-line when present).
- **Deliverables summary** is built from `specialists[].last_artifact` paths + `completed_at` + the cost tile — the contract has no discrete deliverables section.
- **Annunciator `aria-live`** is a static `polite` on the stable zone container (keeps zone replacement clean); the spine's assertive-on-pause-class nuance is the one minor deviation. `aria-live` + `role` + reduced-motion media query are all present.

These are worth surfacing to the party as candidate 35.1-contract enrichments if the operator wants the fuller gate/error/deliverables fidelity the spine sketches; none are blockers for a truthful v1 flight deck.

## Kept-pin / Dev-Cycle-M5 note

No April `run_hud.py` render pins were re-pointed here (35.5 owns the NEW `app/hud/render/**` tree; the legacy `run_hud.py` retirement + its pin migration is 35.8's scope, strictly after this). Dev-Cycle / M5 panels are absent by construction — the legacy-shaped-dir golden asserts a legacy `dev_cycle` payload renders only as quoted raw UNRECOGNIZED text, never as chrome (`class="tab"` absent).
