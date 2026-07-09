# S5-3b AC-L — Two-lane LIVE witness PROOF

**Story:** S5-3b — G0-enrichment default flip + canonical G0E/G0R witness
**Role:** INDEPENDENT live-witness (two-lane, FROZEN judges, first-run-stands, NO retry-to-green)
**Branch:** `dev/workbook-2026-07-06` · **HEAD:** `6961eeac` + the **uncommitted** 3b flip in the working tree
**Corpus:** `course-content/courses/studio-smoke-min/` (real DIRECTORY, committed `a1158385`; lesson.md 1 H1 + 3 H2)
**Python:** `.venv/Scripts/python.exe`, `PYTHONIOENCODING=utf-8`

## VERDICT

| Lane | What it proves | JUDGE verdict |
|------|----------------|---------------|
| **(a)** canonical default-ENV walk (the FLIP proof, deterministic) | unset-env → first pause **G0E** → G0R → G1; receipt `deterministic-recorded`; $0 pre-pass | **PASS (8/8)** |
| **(b)** armed live-LLM walk (`--g0-dispatch-live`) | genuine live gpt-5 G0 pre-pass; receipt `live`; identical gate structure, only content SOURCE differs | **PASS (4/4)** |

**Total live spend: $0.0002844** (lane a $0.00001095 + lane b $0.00027345 — well under one cent).

## Freeze-time-vs-run-time validity protocol (first-run-stands)

- **Judges frozen at `2026-07-07T08:05:33Z`** — `judges-frozen.json` records the sha256 of `judge_a.py` + `judge_b.py`, written **before any lane ran**.
- **Every lane run occurred AFTER the freeze** (lane a final start `08:09:13Z`; lane b start `08:12:59Z`) — the criteria could not be tuned to the outcome.
- **Judge integrity re-checked at execution:** immediately before running each judge its sha256 was compared to the frozen manifest — **both MATCHED** (`judge_a` `f0cf3ebb…`, `judge_b` `4443bc18…`).
- **Each judge executed VERBATIM exactly ONCE** against the on-disk artifacts. No retry-to-green.

## Lane (a) — the FLIP proof (deterministic, $0 pre-pass)

- Driver: `lane_a_start.py` → `lane_a_resume_g0e.py` → `lane_a_resume_g0r.py`. Trial `7039838e-5477-4aba-9fcf-ab500f240588`.
- **F-1804 default-witness:** after `load_dotenv(override=True)` the driver asserted `os.environ.get("MARCUS_G0_ENRICHMENT_ACTIVE") is None` **by exact name** (and `MARCUS_G0_DISPATCH_LIVE` unset) — proving the **post-flip DEFAULT** (unset→ON), not a set value. `g0_enrichment_active()` returned `True`, `g0_dispatch_live()` returned `False`.
- **Pause sequence observed: `G0E → G0R → G1`** — the canonical flip sequence, live-witnessed via the **real runner resume path** (approve verdict at G0E confirm, then G0R ratify; `OperatorVerdict.verb="approve"`, the closed-enum verb the confirm/ratify gates consume).
- **Enrichment real:** 4 typed components + 1 provisional LO on the persisted `g0-enrichment.json`.
- **Receipt `enrichment_mode == "deterministic-recorded"`**, `model_id == "deterministic-g0-enrichment-offline"`.
- **$0 live-LLM pre-pass:** the cost report has **no `g0_enrichment` agent line** at all (only texas directive-composition $0.0000105 + a marcus placeholder $0.00000045). The deterministic pre-pass spent nothing on a live model.

**JUDGE-a checks (all PASS):** F1804 env-absent; F1804 dispatch-unset; 1 first-pause G0E; 2 G0E→G0R; 3 G0R→G1; 4 enrichment real; 5 receipt deterministic-recorded; 6 $0 pre-pass spend.

## Lane (b) — armed live-LLM (content-armed)

- Driver: `lane_b_start.py` → `lane_b_resume_g0e.py` → `lane_b_resume_g0r.py`. Trial `26d1dc94-61d4-4dac-8da9-224e6223a95d`.
- Armed the **real production switch** `MARCUS_G0_DISPATCH_LIVE=1` (the value the `--g0-dispatch-live` CLI flag resolves to) with the real OpenAI key. `g0_dispatch_live()`=True, `_has_live_openai()`=True. The `marcus` seam resolves to **`gpt-5`** (read-only introspection of `make_chat_model("marcus").entry.resolved`).
- **Genuine live call:** the G0E pre-pass dispatched a real gpt-5 component-extraction (start took **71s** vs lane a's 31s; the parsed response artifact is frozen at `g0-enrichment-cache/09312240…json`). Cost report shows a **`g0_enrichment` agent line, model `marcus`, $0.00013125** — absent in lane a.
- **Receipt `enrichment_mode == "live"`**, `model_id == "marcus"`. The G0E gate consumed the live content: 4 typed components + **5 provisional LOs** (richer than lane a's 1 — live semantic extraction vs deterministic scaffold).
- **Divergence guard PASS:** lane (b) pause sequence `G0E → G0R → G1` is **identical** to lane (a); the card-payload carrier keys are identical; the **only** delta is the enrichment content SOURCE (`marcus`/gpt-5 vs the deterministic offline marker).

**JUDGE-b checks (all PASS):** 1 live call dispatched; 2 receipt mode live; 3 gate consumed live content; 4 divergence guard.

## Observations / anomalies (reported honestly — none blocking)

1. **CLI status-masking (not a defect, documented):** `start_trial`'s returned dict masks `envelope.status` to `"registered-offline"` whenever `production_clone_launch_evidence` is `False` — which is the case at an **early gate like G0E**, before any specialist dispatch emits a LangSmith child-run trace. The **authoritative** walk state (`run.json` → `envelope.status`) is `paused-at-gate` with `paused_gate=G0E`. The lane-a start driver initially captured the masked CLI field; it was corrected **before any judge ran** to report the authoritative envelope status, and lane a was re-run fresh (deterministic, $0). First-run-stands for the JUDGES is intact (judges ran once, after freeze). A stray pre-fix lane-a trial `24b66c17…` remains on disk per cleanup-APPEND (F-701); the witnessed lane-a trial is `7039838e…`.
2. **`MARCUS_G0_DISPATCH_LIVE` arms Irene too (by design):** `ir_dispatch_live()` reuses the same env (feature-flag parity), so in lane (b) the G0E→G0R resume also ran a live gpt-5 Irene refinement ($0.00013125; the resume took 43s vs lane a's 17s). This strengthens the content-armed proof and does not affect the gate STRUCTURE — the divergence guard holds.
3. **Scope note:** the D3 "live-available affordance" narration (AC-5) is a narration-layer concern covered by the dev agent's offline tests; the task scoped the frozen JUDGE-a to the six enumerated pause/receipt/spend criteria, all PASS.

## No-mutation attestation

No production code edited; no commits/pushes/stashes; the working-tree flip was **run against, left intact**. The only `app/` diffs are the pre-existing uncommitted 3b flip (`g0_enrichment_wiring.py` + the `--g0-dispatch-live` arm in `marcus_spoc.py`) — untouched by this witness. All witness artifacts live under this evidence directory.

## Artifact index

- `judges-frozen.json` — freeze manifest (ts + sha256)
- `judge_a.py` / `judge_b.py` — FROZEN judges (executed verbatim once each)
- `judge_a-facts.json` / `judge_b-facts.json` — per-check verdicts
- `s5-3b-acl-witness-facts.json` — combined facts + spend
- `lane_a_*.py` / `lane_b_*.py` — drivers
- `lane_a-*.json` / `lane_b-*.json` — per-phase driver results
- `driver-log-lane-*.txt` / `walk-log-lane-*.txt` — logs
