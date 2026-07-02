# Carried-Findings (c) — Live Witness Record (D-C1 / D-C2 / D-C3)

Date: 2026-07-02 (UTC). Branch: `dev/carried-findings-enum-refresh-2026-07-02`.
Spec: `carried-findings-remediation-greenlight-party-record-2026-07-02.md` D-C1/D-C2/D-C3.
Discipline: first-run-stands; no retry-to-green.

## RED-first witnesses (c1 gating + c2 portability)

- `c1-gate-contract-RED-at-HEAD.txt` — gate-semantics contract test
  (`tests/test_conftest_llm_live_gating.py`) run BEFORE the conftest flip:
  `test_default_profile_deselects_llm_live_even_with_real_key` FAILED (llm_live
  test was collected in the default profile with a real-looking key); the other
  3 checks passed. 1 failed, 3 passed.
- `c1-gate-contract-GREEN-post-flip.txt` — same test after the
  `tests/conftest.py` Pass-1 flip: 4 passed.
- `c2-portability-unit-RED-before-helper.txt` — portability unit tests authored
  before `vision_capture_support.py` existed: collection error (module absent).
- `c2-portability-unit-GREEN.txt` — after helper implementation: 5 passed.

## W1 — $0 default-profile deselection witness (real key PRESENT via .env)

Shell env `OPENAI_API_KEY` was NOT set; `tests/conftest.py` loads the REAL key
from `.env` (`sk-proj-…oc0A`, len 164) — i.e., the exact pre-fix spend hazard
condition.

- `W1-default-profile-collect-only.txt` —
  `pytest tests/specialists/vision/test_vision_live_roundtrip.py --collect-only -q -n0`
  → `no tests collected (1 deselected)`.
- `W1-default-profile-run.txt` — same file, default-profile RUN →
  `1 deselected`, zero tests executed, zero spend.

VERDICT: default profile can no longer spend against llm_live even with a real
key present. PASS.

## W2 — ONE real `--run-live` recapture (real gpt-5.5 spend, first-run-stands)

- Pre-run snapshot: `W2-git-status-pre-run.txt` + `recordings-pre-run/` (the 6
  committed recordings as-is).
- Command: `pytest tests/specialists/vision/test_vision_live_roundtrip.py --run-live -n0 -q`
  run ONCE. Output: `W2-run-live-output.txt` (1 failed in 113.42s).

### Portability judgment (the claim under test) — PASS

All 6 recordings were REWRITTEN by the live run (git-modified, fresh
`captured_at = 2026-07-02T05:38:46Z`; see `W2-git-status-post-run.txt`).
Judgment script output: `W2-portability-judgment.txt` — every
`response.source_png_path` AND `_provenance.source_png` is repo-relative posix
(`runs/compositor/assembly-bundle/visuals/slide-NN.png`); no drive letters, no
backslashes. `ALL PORTABLE: True`. Rewritten files archived at
`recordings-post-run/`.

### Perception-anchor FLAKE (reported honestly, NOT retried)

The pytest run itself FAILED on a slide-01 perception anchor: variant set
`('74%',)` absent from the perceived text — this run the model rendered the
employment figure as "over 70%" instead of "74%". This is live-perception
variance, out of batch scope per D-C3 ("anchor variance itself is out of batch
scope"); it does NOT invalidate the portability witness, which is judged on
the written recording files. All 6 recordings were written BEFORE the anchor
assertions execute (capture loop precedes slide-01 assertions). The `$4.5t`
and `3x` anchors were satisfied; element-count/bbox/confidence assertions were
not reached (pytest stops at first failed assert). NOT rerun to green.

### Disposition

Per D-C2 amendment 3 (committed recordings stay as-is; recaptured LLM content
is nondeterministic fixture churn): after archiving, the working tree
recordings were restored via `git restore tests/fixtures/vision/recordings/`.
