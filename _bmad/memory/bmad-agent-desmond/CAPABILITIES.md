# CAPABILITIES

## Built-in

- **Assembly handoff (manual)** — `references/assembly-handoff.md`
- **API narrated-lesson build (automated)** — `references/capability-api-narrated-lesson-build.md`
  — import slides + audio and assemble via Underlord (`scripts/api_clients/descript_client.py`
  + `scripts/operator/build_descript_narrated_lesson.py`).
- **Automation Advisory** — `references/automation-advisory.md` (required closing section on handoffs)
- **Doc research** — `references/doc-research.md` (+ cached OpenAPI at
  `references/cache/descript-openapi.json`)

## Learned

- (Owner-taught patterns per `references/capability-authoring.md`.)
- **2026-06-24:** Owner prefers the **API build path** (import → Underlord agent) over manual
  Descript assembly for narrated lessons. Proven end-to-end this session.
- **2026-06-24:** **Publish-to-Descript (render + share).** Outcome: a finished composition
  becomes a shareable 1080p MP4 + link without manual export. Use
  `build_descript_narrated_lesson.py --publish` (full build then publish) or
  `--publish --project-id <id>` (publish an EXISTING project) — wraps the existing
  `DescriptClient.publish()`; returns `share_url` + a time-limited `download_url`. Default
  OFF; post-composition only. **Witnessed live** on clustered A/B trial `c2c6dcbf` /
  project `e2017771`: status=success, share `https://share.descript.com/view/TePGsXmfdQc`,
  MP4 46.8 MB (`video/mp4`, valid `ftyp` container). Party-green-lit DO-NOW
  (John/Winston/Mary/Murat) under the witness-before-register gate. See
  `references/capability-api-narrated-lesson-build.md` §Publish.
