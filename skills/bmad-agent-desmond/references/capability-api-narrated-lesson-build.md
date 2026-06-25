# Capability — API-based narrated-lesson build (APP bundle → Descript)

**Outcome:** Programmatically turn an APP assembly bundle (slide PNGs + per-segment narration
MP3s) into a **fully assembled, playable narrated-slide video** in Descript — no manual import,
no pre-rendering. First proven end-to-end on **2026-06-24** (see verified facts below).

This is the **automated** counterpart to `references/assembly-handoff.md` (which produces
manual operator steps). Prefer this path when the owner wants the project built for them.

## Tools (reusable — already in the repo)

- **Client:** `scripts/api_clients/descript_client.py` → `DescriptClient`
  (`status`, `list_projects`, `get_project`, `import_media`, `upload_to_signed_url`,
  `get_job`, `wait_for_job`, `agent_edit`, `publish`). Extends `BaseAPIClient`.
- **Builder:** `scripts/operator/build_descript_narrated_lesson.py`
  (`--dry-run`, `--skip-agent`, `--slides-dir`, `--audio-dir`, `--project-name`,
  `--publish`, `--project-id <id>` [publish-only, skip build], `--resolution`).
- **API reference:** `references/descript-api-reference.md` (endpoints, lifecycle, constraint).
- **OpenAPI spec (cached):** `references/cache/descript-openapi.json` (authoritative schemas).

## Auth

- Requires `DESCRIPT_API_KEY` in the environment — a **Drive-scoped Bearer token**.
- Observed token format: `dx_bearer_<uuid>:dx_secret_<uuid>`; the **entire string** (including
  the `:secret` half) is the Bearer value: `Authorization: Bearer dx_bearer_...:dx_secret_...`.
- **Never** commit or write the token to memory/`.env` in the repo. Owner pastes it in-session;
  remind them to **rotate** afterward if it was exposed in chat.
- Quick check: `GET /status` → `{drive_id, api_version}`.

## Where the package lives (APP bundle layout)

The `runs/compositor/DESCRIPT-ASSEMBLY-GUIDE.md` (regenerated each compositor run) is the index.
For the proven run it pointed at:

- **Slides:** `runs/compositor/assembly-bundle/visuals/slide-01.png … slide-NN.png`
- **Narration:** `state/config/runs/<run_id>/enrique-narration/assembly-bundle/audio/seg-01.mp3 …`
- **Captions:** same `enrique-narration/.../captions/seg-NN.vtt` (Underlord regenerates captions
  from transcription, so uploading the VTTs is optional).

Identify the **most recent completed trial**: look for the newest `DESCRIPT-ASSEMBLY-GUIDE.md`
plus a `run_summary.yaml` showing a terminal gate reached (e.g. `terminal_gate: G4A`,
`silent_bypass_events: 0`).

## Proven recipe (the path that works)

1. **Import (create project + request upload URLs).** `POST /jobs/import/project_media` with
   `project_name` + `add_media` map. For local files use **direct upload** entries:
   `{ "content_type": "<mime>", "file_size": <bytes> }`. Response returns `project_id`,
   `project_url`, and a signed `upload_url` per media key (valid ~3h). Do **not** send
   `add_compositions` — let Underlord assemble.
2. **Upload bytes.** `PUT` each file to its `upload_url` with
   `Content-Type: application/octet-stream`.
3. **Poll the import job.** `GET /jobs/{job_id}` until `job_state == "stopped"`; expect
   `result.status == "success"`.
4. **Assemble with Underlord.** `POST /jobs/agent` with `project_id` + an explicit prompt:
   play narration 1→N in order; hold each matching slide full-screen for its segment's full
   duration (slide-0k with narration-0k, 1:1); scale to 1920×1080; add captions; **invent
   nothing**. Poll that job to `stopped`/`success`.
5. **Verify.** `GET /projects/{project_id}` → expect one `media_type: video` composition whose
   **duration ≈ the sum of the narration clip durations** (the timing proof — see below).
6. **Publish (optional).** `POST /jobs/publish` (`media_type: Video`, `resolution: 1080p`) →
   `share_url` + time-limited `download_url`.

## Gotchas learned (these bit us — don't relearn them)

- **Import composition builder is sequential, single-track.** `add_compositions[].clips[]`
  accepts only `{ "media": "<ref>" }` — **no per-clip duration, no track/layer**. It cannot
  time a still to its audio or layer audio under a still. → **Use the Underlord agent** for any
  synced slideshow. (Pre-rendering stills→MP4 with ffmpeg is a fallback only; not needed, and
  ffmpeg is **not installed** on this machine anyway.)
- **Images import fine.** PNG (`type: image`), MP3 (`audio`), MP4 (`video`) all import as media.
  Earlier worry that PNGs weren't supported was wrong.
- **Timing proof.** A correct build has **composition duration == sum(narration durations)**.
  On 2026-06-24: 6 clips summed to 233.2s and the composition was 233.2s. If they diverge,
  Underlord didn't hold slides for full segments — re-prompt.
- **Windows console encoding.** Underlord `agent_response` text contains Unicode (e.g. `→`,
  U+2192). The default cp1252 console raises `UnicodeEncodeError` on `print`. Fix: set
  `PYTHONUTF8=1` or `sys.stdout.reconfigure(encoding="utf-8")` (the builder now does this).
- **Async always.** Imports and agent edits return a `job_id`; poll or pass `callback_url`.
  Jobs can run minutes (import ~45s for 6 clips; agent assembly ~3 min for 6 slides).
- **Error codes:** `402` = out of media-minutes / AI credits; `429` = rate limit (honor
  `Retry-After`); `401/403` = bad/forbidden token.
- **System Python is 3.10** here, not 3.11 — avoid `datetime.UTC` (use `timezone.utc`).

## Verified facts (2026-06-24)

- **Drive:** `c661f101-b1e1-4552-9ccb-a950d91507c8`.
- **Today's build:** project `15681d6b-cd16-4e0a-bef5-2c5614d3b977`
  ("APP Narrated Lesson - 6cb8eafd (2026-06-24)") — 6 slides + 6 narration, one ~233.2s video
  composition, import + agent both `success`. From trial run `6cb8eafd-…`.
- **Prior reference build:** project `a4dadd5f-c853-4fab-a599-89fc6c2f5eb6`
  ("Inflection Point: Designing a Health System", 2026-04-21) — built via Underlord
  ("Added with Underlord" folder), ~403s video composition; confirms the agent path is the
  established recipe.
- **Clustered A/B build (proves count-aware + the publish leg):** project
  `e2017771-00a1-4f9b-8bf7-39d9adb4a146` ("APP Narrated Lesson - c2c6dcbf clustered A/B")
  — **13** slides + **13** narration (a clustered, genuine per-sub-slide A/B trial),
  one ~488.9s video composition, import + agent both `success`. The Underlord prompt is now
  count-aware (`build_assembly_prompt(n)`), not hardcoded to 6.

### §Publish (witnessed 2026-06-24)
`--publish` (after a build) or `--publish --project-id <id>` (publish an existing project)
calls `DescriptClient.publish()` → polls the publish job → returns `share_url` + a
time-limited `download_url`. Witnessed live on project `e2017771`: `status=success`,
share `https://share.descript.com/view/TePGsXmfdQc`, download a signed `…/original.mp4`
(**46.8 MB**, `Content-Type: video/mp4`, valid `ftyp` container). Publish renders ~minutes;
errors 402 (credits) / 429 (rate limit). Default OFF; post-composition; idempotent intent
(no auto-republish).

## Automation Advisory (this capability, current Descript surface)

**REST API (`descriptapi.com/v1`):**
- Ingest (slides + audio) — **Full** — direct upload (`/jobs/import/project_media` + PUT).
- Assembly (slideshow timing, captions) — **Full** — via `/jobs/agent` (Underlord).
- Export/publish (MP4 + share link) — **Full** — `/jobs/publish`.

**MCP (`api.descript.com/v2/mcp`):** overlaps the agent path for conversational assembly; REST
agent is preferred for scripted/repeatable runs.

**App (manual):** only for fine timeline polish or anything Underlord misplaces on review.
