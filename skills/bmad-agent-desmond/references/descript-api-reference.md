# Descript API — reusable reference (Desmond)

Durable, project-local reference for the Descript **Public API** (Early Access). Pairs with
the cached artifacts in `references/cache/` and the doc registry at
`references/descript-doc-registry.json`.

- **Live docs:** https://docs.descriptapi.com/ — human-readable
- **Product / token UI:** https://descript.com/api
- **Base URL:** `https://descriptapi.com/v1`
- **Auth:** `Authorization: Bearer <token>` — token is **Drive-scoped**. Stored as
  `DESCRIPT_API_KEY` in `.env` (never commit). Treat like a password.
- **CLI alternative:** `npm install -g @descript/platform-cli@latest` → `descript-api ...`
- **Remote MCP (assistants):** `https://api.descript.com/v2/mcp`

## Cached artifacts (in `references/cache/`)

- `descript-openapi.json` — full OpenAPI 3.0 spec (extracted from the docs Redoc state).
  Authoritative schema source for request/response shapes.
- `descript-api-docs.snapshot.txt` — rendered docs page snapshot.
- `descript-help-home.snapshot.txt` — help center snapshot.

Refresh snapshots: `python skills/bmad-agent-desmond/scripts/refresh_descript_reference.py`.

## Endpoint surface (v1)

| Verb | Path | Purpose |
|---|---|---|
| POST | `/jobs/import/project_media` | Create project + import media + create compositions |
| POST | `/jobs/agent` | Underlord natural-language create/edit (non-deterministic) |
| POST | `/jobs/publish` | Render + publish a composition → `share_url` + `download_url` |
| POST | `/export/transcript` | Export transcript (txt/markdown/html/rtf/docx) |
| GET | `/jobs` | List recent jobs (filter by `project_id`, `type`) |
| GET | `/jobs/{job_id}` | Poll job status (`job_state: queued|running|stopped`) |
| DELETE | `/jobs/{job_id}` | Cancel a running job |
| GET | `/projects` | List projects in the token's drive |
| GET | `/projects/{project_id}` | Project details (media_files + compositions) |
| GET | `/status` | Token + connectivity check → `{drive_id, api_version}` |
| GET | `/published_projects/{slug}` | Published-project metadata |
| POST | `/edit_in_descript/schema` | Partner "Edit in Descript" import URL (needs partner access) |

## Build lifecycle (direct file upload — for local assets)

1. **POST `/jobs/import/project_media`** with `project_name` + `add_media` items giving
   `content_type` + `file_size` (per file) + optional `add_compositions`. Response returns
   `project_id`, `project_url`, and a signed `upload_url` per media item (valid ~3h).
2. **PUT the bytes** to each `upload_url` with `Content-Type: application/octet-stream`.
3. **Poll `GET /jobs/{job_id}`** until `job_state == "stopped"`; check `result.status`.
4. Optional: **POST `/jobs/agent`** to polish, **POST `/jobs/publish`** to render/export.

Media URL imports (alternative to direct upload) require public/pre-signed URLs that support
HTTP Range requests (sign for 12–48h). Supported: audio WAV/FLAC/AAC/MP3; video h264/HEVC in
MOV/MP4.

## ⚠ Key constraint — composition builder is sequential, single-track

`add_compositions[].clips[]` accepts **only `{ "media": "<ref>" }`**. There is **NO**
per-clip `duration` and **NO** track/layer field. Clips are laid **end-to-end on one
timeline**. The import API therefore **cannot**, on its own:

- hold a still image for the exact length of a narration segment, or
- layer narration audio underneath a still.

`add_media` multitrack items (`{ "tracks": [{media, offset}] }`) are for **multicam-style
synchronized source media**, not slideshow timing.

### Implication for narrated-slide builds

The composition builder cannot time/layer stills, but **the assets themselves import fine** —
PNG **images, MP3 audio, and MP4 video are all supported** media types (proven below). So the
**proven recipe** is:

1. **Import** the raw assets (slide PNGs + per-segment narration MP3s) via direct upload —
   no compositions in the import call.
2. **`POST /jobs/agent`** (Underlord) with an explicit assembly prompt: play the narration
   clips in order and hold each matching slide full-screen for its segment's duration, add
   captions. Underlord performs the timeline assembly the import API cannot express.

This is exactly how the verified April 2026 project ("Inflection Point: Designing a Health
System", project `a4dadd5f-…`) was built — its media list contains `…motion_slide_NN.png`
(type `image`) + `…motion-card-NN.mp3` (type `audio`) all under an **"Added with Underlord"**
folder, assembled into one ~403s `video` composition. Pre-rendering stills to video with
`ffmpeg` is an *optional* fallback if deterministic timing is ever required; it is **not**
needed for the standard build.

## Verified live (2026-06-24)

`GET /status` → `200 {"drive_id":"c661f101-b1e1-4552-9ccb-a950d91507c8","api_version":"v1"}`.
`GET /projects` and `GET /projects/{id}` confirmed working (read-only).
