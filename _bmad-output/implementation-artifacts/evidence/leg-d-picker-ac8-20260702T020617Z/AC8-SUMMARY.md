# Leg-D AC-8 — LIVE local pick leg RE-RUN (post R1 same-origin remediation) — PASS (17/17 checks)

**Date:** 2026-07-02 (UTC stamp 20260702T020617Z). **Branch:** `dev/gamma-styleguide-leg-c-live-2026-07-01`. **Fully LOCAL** — real ephemeral-port `http.server` + the page AS THE SERVER SERVES IT + the REAL `production_runner` payload builders; zero external API calls, zero spend. **First-run-stands** (no retry-to-green).

## Why a re-run

The 3-lane review's R1 (Blind#1, MUST-FIX) changed the PRIMARY flow: the old path opened the page via `file://` while its JS `fetch()`ed `http://127.0.0.1:<port>/pick` — null-origin CORS blocks reading the response, so the operator never saw the receipt panel (the prior AC-8 harness POSTed via urllib and bypassed the browser layer entirely, masking this). The remediated flow is same-origin end-to-end: the pick server itself serves the page at `http://127.0.0.1:<port>/` (plus `/thumbnails/*`), and the form action is the RELATIVE `/pick`. The live leg was therefore re-proven through the NEW path.

## What ran (headless harness `driver_ac8_local_pick.py`)

1. **Real roster** from the real SSOT (`load_picker_roster(include_probes=True)`) — 5 guides, the two Leg-C probes carried the `data-probe="1"` warning marker in the served page.
2. **Same-origin serve (R1, new):** the opener received the SERVER root `http://127.0.0.1:50307/`; the harness **GET the page FROM the server** (HTTP 200; served bytes byte-identical to the disk evidence copy `picker.html`), parsed the SERVED HTML (`html.parser`: form action `/pick` RELATIVE + method POST + hidden fields `slot_A`/`slot_B` + card `data-guide` values), and GET a same-origin `/thumbnails/...` src (200, `image/png`, PNG magic) — exactly what a browser does, no shortcut past the served page.
3. **Real pick:** Style A = `classic-freeform-x-cards`, Style B = `leg-c-part3-floor-probe`, POSTed to the relative action resolved against the served origin (what DOM `form.action` does). One valid POST → server exited (`server_exited_after_one_post: true`); page receipt == server receipt; the R3 "waiting for your pick at <url>" notice printed before the server blocked.
4. **Real directive** written (`directive.yaml`: `gamma_settings[]` verbatim semantics + `styleguide_picker_provenance` with ssot_sha256, written under the R8 advisory lock) and **real pick-event lines** appended to the production sidecar `state/config/gamma-styleguide-picks.jsonl` (run_id-tagged; sidecar timestamp `2026-07-02T02:07:10.032379+00:00`).
5. **Real payload-builder boundary:** `_gamma_settings_from_directive` → both picked guides bound; `_runner_payload_for_specialist(specialist_id="irene_pass1", ...)` → `{"min_cluster_floor": 8}` (the floor probe's scripted floor threads through the REAL Leg-C consumer). Pinned in `dispatch-payload-snapshot.json`.

## M-3 arbiter — two-artifact diff: **AGREE**

| Artifact | Code path | Guide identity |
|---|---|---|
| `dispatch-payload-snapshot.json` | REAL `production_runner` directive read (post-hoc) | (A, classic-freeform-x-cards), (B, leg-c-part3-floor-probe) |
| `pick-event-log.json` | picker's sidecar emit at pick time (independent code path) | (A, classic-freeform-x-cards), (B, leg-c-part3-floor-probe) |

`two_artifact_guide_identity_agrees: true` — verdict **PASS** (`result.json`, 17/17, first-run-stands).

**⚠️ M-3 caveat (R9, Auditor#2 — honest):** the two artifacts share ONE pick event's `picks` dict as their common ancestor — the independence claim is **code-path-level** (the runner's directive read vs the picker's sidecar emit are separate implementations that could each corrupt/diverge independently), **not event-level** (they do not witness two separate pick events). The diff catches divergence between the two write/read paths; it cannot catch an error upstream of the shared `picks` dict itself.

## Files
- `driver_ac8_local_pick.py` — the harness (same-origin GET-then-POST, per the R1 flow).
- `picker.html` — the disk evidence copy of the served page (byte-identical to the served bytes; its relative `/thumbnails/*` srcs resolve only when served).
- `directive.yaml` — the picker-written run directive (provenance block intact).
- `dispatch-payload-snapshot.json` / `pick-event-log.json` — the two arbiter artifacts.
- `result.json` — 17/17 checks, `AC8_PASS: true`.

## Honest notes
- The paid Gamma walk remains deferred by design (Murat: overkill for this surface); the live bar is the John-specified one — real SSOT, the page served by the real server and driven exactly as a browser would, real pick event, real directive on disk, the real payload builder binding the picked guide, real sidecar timestamp.
- `include_probes=True` was used deliberately so the pick could bind the Leg-C floor probe and prove a NON-trivial `min_cluster_floor` thread (8), not just a None passthrough. The probe rendered with its warning marker (S-1) as the default-hidden rule requires.
- The prior evidence dir `leg-d-picker-ac8-20260702T014409Z/` remains on disk as the pre-remediation record; its harness POSTed via urllib against the then-`file://` page and therefore could not have caught the CORS defect.
