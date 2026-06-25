# MEMORY — Desmond

## Descript version target

- Unknown — capture in First Breath (Settings → About).
- **API:** Public API v1, base `https://descriptapi.com/v1` (Early Access). Drive-scoped
  Bearer token in `DESCRIPT_API_KEY`. Owner's drive: `c661f101-b1e1-4552-9ccb-a950d91507c8`.

## API build path (preferred for narrated lessons) — see `references/capability-api-narrated-lesson-build.md`

- **Recipe:** `POST /jobs/import/project_media` (direct upload: content_type+file_size → PUT
  bytes) → poll `/jobs/{id}` to `stopped` → `POST /jobs/agent` (Underlord) to assemble →
  optional `POST /jobs/publish`. Do NOT pass `add_compositions` — the import composition builder
  is sequential single-track and can't time stills; Underlord does the timing.
- **Tools:** `scripts/api_clients/descript_client.py` + `scripts/operator/build_descript_narrated_lesson.py`.
- **Correctness check:** composition duration must ≈ sum of narration-clip durations.
- **Gotcha:** force UTF-8 on Windows (`PYTHONUTF8=1`) — Underlord responses contain Unicode.
  System Python is 3.10 (no `datetime.UTC`). `402`=out of credits, `429`=rate limit.
- **Never** store the API token here or in `.env`; remind owner to rotate after in-chat use.

## Proven builds

- 2026-06-24: project `15681d6b-…` ("APP Narrated Lesson - 6cb8eafd") — 6 slides + 6 narration,
  233.2s video, from trial run `6cb8eafd-…`. Import + Underlord both success.
- 2026-04-21: project `a4dadd5f-…` ("Inflection Point: Designing a Health System") — Underlord-
  built reference (~403s video).

## Package layout (APP bundle)

- Index: `runs/compositor/DESCRIPT-ASSEMBLY-GUIDE.md` (regenerated per compositor run).
- Slides: `runs/compositor/assembly-bundle/visuals/slide-*.png`.
- Narration: `state/config/runs/<run_id>/enrique-narration/assembly-bundle/audio/seg-*.mp3`.

## Glossary (APP → Descript)

- (Add team terms as they stabilize.)

## Doc cache

- Last refresh: 2026-06-24 — saved live OpenAPI spec to
  `references/cache/descript-openapi.json` (paths incl. `/jobs/import/project_media`,
  `/jobs/agent`, `/jobs/publish`, `/projects`, `/status`). Markdown snapshots also present.
  Note: `refresh_descript_reference.py` fixed for Python 3.10 (`timezone.utc`).
