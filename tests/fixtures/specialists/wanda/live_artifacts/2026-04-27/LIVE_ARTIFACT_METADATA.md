# M2 Live Artifact Metadata - 2026-04-27

- **Title:** M2 Operator-Window Ceremony
- **Artifact path:** `tests/fixtures/specialists/wanda/live_artifacts/2026-04-27/25dcc0554b12b3e5f99aa2290bcdb594d9b205d2a489fcdd16f6d87cad16b792.mp3`
- **SHA256:** `25dcc0554b12b3e5f99aa2290bcdb594d9b205d2a489fcdd16f6d87cad16b792`
- **Bytes:** 1139817
- **Estimated duration (sec; from byte count at 128kbps):** 71.2
- **Cost USD:** (not reported by Wondercraft API; per pricing ~10 credits = ~$2.25 on Pro plan)
- **Voice ID:** 231bca1f-eb6f-496c-8781-92cdc58e9ff3
- **Script word count:** 100
- **Job ID:** cf2917aa-d260-4e4c-8c74-7eef6cf86021
- **Captured at:** 2026-04-27T06:37:57.276031+00:00
- **Wondercraft API endpoint used:** `/podcast/scripted` (POST) + `/podcast/{job_id}` (GET)
- **Operator-session note:** harvested via harvest_wondercraft_job.py after M2 ceremony's
  poll-loop missed the terminal state (Wondercraft uses `finished: true` boolean, not `status` enum;
  in-session A16 instance — Composition-vs-Component Audit Gap).
