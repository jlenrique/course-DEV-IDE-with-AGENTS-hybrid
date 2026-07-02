# Leg-D AC-8 — LIVE local pick leg — PASS (11/11 checks)

**Date:** 2026-07-02 (UTC stamp 20260702T014409Z). **Branch:** `dev/gamma-styleguide-leg-c-live-2026-07-01`. **Fully LOCAL** — real ephemeral-port `http.server` + real rendered HTML + the REAL `production_runner` payload builders; zero external API calls, zero spend.

## What ran (headless harness `driver_ac8_local_pick.py`)

1. **Real roster** from the real SSOT (`load_picker_roster(include_probes=True)`) — 5 guides, the two Leg-C probes carried the `data-probe="1"` warning marker in the rendered page.
2. **Real rendered page** (`picker.html`, written by `capture_pick` with the live endpoint baked into the form action `http://127.0.0.1:65003/pick`). The client PARSED the rendered HTML (`html.parser`: form action + method + hidden field names `slot_A`/`slot_B` + card `data-guide` values) and POSTed the pick exactly as the page's Confirm would — no shortcut past the HTML.
3. **Real pick:** Style A = `classic-freeform-x-cards`, Style B = `leg-c-part3-floor-probe`. One valid POST → server exited (`server_exited_after_one_post: true`); page receipt == server receipt.
4. **Real directive** written (`directive.yaml`: `gamma_settings[]` verbatim semantics + `styleguide_picker_provenance` with ssot_sha256) and **real pick-event lines** appended to the production sidecar `state/config/gamma-styleguide-picks.jsonl` (run_id-tagged; real sidecar timestamp `2026-07-02T01:44:53.607002+00:00`).
5. **Real payload-builder boundary:** `_gamma_settings_from_directive` → both picked guides bound; `_runner_payload_for_specialist(specialist_id="irene_pass1", ...)` → `{"min_cluster_floor": 8}` (the floor probe's scripted floor threads through the REAL Leg-C consumer). Pinned in `dispatch-payload-snapshot.json`.

## M-3 arbiter — two-artifact diff: **AGREE**

| Artifact | Code path | Guide identity |
|---|---|---|
| `dispatch-payload-snapshot.json` | REAL `production_runner` directive read (post-hoc) | (A, classic-freeform-x-cards), (B, leg-c-part3-floor-probe) |
| `pick-event-log.json` | picker's sidecar emit at pick time (independent) | (A, classic-freeform-x-cards), (B, leg-c-part3-floor-probe) |

`two_artifact_guide_identity_agrees: true` — verdict **PASS** (`result.json`, first-run-stands).

## Files
- `driver_ac8_local_pick.py` — the harness.
- `picker.html` — the real rendered page the pick was driven through.
- `directive.yaml` — the picker-written run directive (provenance block intact).
- `dispatch-payload-snapshot.json` / `pick-event-log.json` — the two arbiter artifacts.
- `result.json` — 11/11 checks, `AC8_PASS: true`.

## Honest notes
- The paid Gamma walk is deferred by design (Murat: overkill for this surface); the live bar here is the John-specified one — real SSOT, real rendered+POSTed HTML, real pick event, real directive on disk, the real payload builder binding the picked guide, real sidecar timestamp.
- `include_probes=True` was used deliberately so the pick could bind the Leg-C floor probe and prove a NON-trivial `min_cluster_floor` thread (8), not just a None passthrough. The probe rendered with its warning marker (S-1) as the default-hidden rule requires.

## Addendum (2026-07-02, 3-lane remediation)
- **M-3 caveat (R9, Auditor#2):** the two arbiter artifacts share ONE pick event's `picks` dict as their common ancestor — the "independently generated" claim is **code-path-level** (runner directive read vs picker sidecar emit), **not event-level**. The diff catches divergence between the two write/read paths; it cannot catch an error upstream of the shared picks dict.
- **Superseded by re-run:** R1 (Blind#1 CORS) changed the primary flow to same-origin serve; this run's urllib POST bypassed the browser layer and could not have caught that defect. The post-remediation live leg is `leg-d-picker-ac8-20260702T020617Z/` (17/17 PASS). This dir stays as the pre-remediation record.
