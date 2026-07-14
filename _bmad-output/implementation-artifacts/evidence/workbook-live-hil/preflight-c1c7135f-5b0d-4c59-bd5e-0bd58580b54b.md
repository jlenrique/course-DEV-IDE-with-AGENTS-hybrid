# Story 38.3a Amendment 5 — governed live-validation preflight

- authorization: unanimous BMAD party `GO-WITH-AMENDMENTS` (Winston, John, Amelia, Murat); root concurs
- authorization scope: exactly one fresh Marcus-SPOC production-runtime start
- trial_id: `c1c7135f-5b0d-4c59-bd5e-0bd58580b54b`
- recorded_at: `2026-07-13`
- git_head: `6ae42a5208bb4a9fcb5bee8668705d6c8b9dd1d7`
- tracked_diff_git_object: `f00f0b2c18aaee9020c835f1e03ab567844aa4b3`
- reviewed_scope_file_count: `43`
- reviewed_scope_tree_sha256: `51aa1abc4009fd9a3e7513f99043a88dbc4ecce33f1c4399674969210ca1fb79`
- runner_sha256: `a49c9b0e4fca25e820ec64189452d9e3e8205e53b4361c3f56b7e69efa22e71b`
- policy_file_sha256: `806f11388937d62e72396b469b04af61751a05dc1c54f3335c561b24edeef9b4`
- canonical_policy_digest: `4205b4dcb2a34846bac0da9f889365eefd22969613aac4e1a4c65e055b9a74a5`
- course_source_file_count: `12`
- course_source_tree_sha256: `b77c41a5536756bdb2ecb67772919b0f282adb6baf4e5e799d24e90707d5bb47`
- pre-spend close gate: `175 passed, 5 skipped` (runner + Pass-1 Amendment 5 + slide authority + Deep Dive)

## Explicit launch posture

- preset: `production`
- operator/delegate: `codex_hil_runner`
- input and course source root: `course-content/courses/tejal-apc-c1-m1-p2-trends`
- component selection: `deck=true`, `motion=false`, `workbook=true`
- HUD: `off`
- encounter mode: `recorded`
- writer execution mode: `live`
- LLM execution mode: `realtime`
- image-perception batch processing: `off` (realtime transport)
- G0 enrichment: `live production path`; no prior-run cache copied
- Irene Pass-1: `live production path`; no prior-run state or receipt copied
- research: `enabled on demand by the workbook authority/demand chain`; the current production front door has no independent research boolean
- Deep Dive: one selectable call maximum, `300s` timeout, `max_retries=0`
- gate policy: canonical Epics 36–40 delegated policy; real card-bound verdicts only

## Stop rules

This authorization permits `start` only. It forbids attach, recover, re-entry, a second start, retry-to-green, copied state, and mid-run code/config/source edits. Any refusal, timeout, batch wait, provider error, authority failure, or other non-`completed` terminal freezes this attempt as honest non-success evidence and requires a new party decision. Workbook artifacts count only if the normal production workflow reaches them.

## Frozen historical witness before launch

- run: `a28aa15a-fc80-46ae-b05a-09ac864829bb`
- file count: `67`
- full manifest sha256: `a7986fe61ae7f94856572fbf7789750e59cae02fb73315603288a60db311166b`
- `error-pause.json`: `4d9bc6f4c1c4ef5f662f6607326402dc741f1e845dd5ec1034f49283cc4fa6bc`
- `run.json`: `3935b017d343bfd5c8bcdd1b7998d07ef82238ab74fa5031b6a1df60b90bc50f`
- delegated journal: `d40966f13073d815e183a5d94d46d33de192363fe89672cff4c8e23f4e29b091`
- delegated summary: `63101565b9767044650098e939d4d71ca62cd3951b1e1668257fa99904075e2d`

The complete per-file frozen manifest is stored beside this record as `preflight-c1c7135f-5b0d-4c59-bd5e-0bd58580b54b-frozen.sha256`.
