# S3 AC-L live witness — Canonical Production Conversation arc

**LEG-1 (matching-pick PASS): JUDGE-1 = PASS (13/13)**
**LEG-2 (forced-divergence WARN): JUDGE-2 = PASS (10/10)**

Witness agent: independent live-witness (Fable 5). Repo branch `dev/workbook-2026-07-06`;
started @ `d049453b` + uncommitted S3 diff (725-green); mid-witness the coordinator's dev lane
landed `59a9a48a` (gamma-matcher apostrophe fix, party-ratified §10 — see Anomaly #1).
Evidence dir: `_bmad-output/implementation-artifacts/evidence/s3-acl-liveproof-20260707T011735Z/`

## Validity protocol

- `judge1.py` + `judge2.py` written and FROZEN at ~2026-07-07T01:18Z, BEFORE any leg ran; executed
  verbatim, once each, after their legs paused. Outputs verbatim at `judge1-output.txt` /
  `judge2-output.txt`; structured facts at `judge1-facts.json` / `judge2-facts.json`.
- All spend REAL (OpenAI gpt-5 family + Gamma Generate API). `.venv/Scripts/python.exe` only;
  `PYTHONIOENCODING=utf-8`; `.env` via `load_dotenv(override=True)` after popping the shell
  `OPENAI_API_KEY` (sk-subst sentinel gotcha); `MARCUS_G0_ENRICHMENT_ACTIVE` popped (first pause = G1).
- Foreground with hard timeouts where feasible; long walks ran backgrounded with hard in-process
  watchdogs + completion notification (never parked on an indefinite watcher).
- No commits/pushes/stashes by the witness. Only repo file touched: `state/config/gamma-style-guides.yaml`
  (leg-2 mutation), restored via `git checkout --` and verified clean (+ resolver re-probe: `amount`
  back to `minimal`).

## Leg 1 — matching-pick PASS (trial `a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9`)

1. **Start** (`leg1_start.py`, foreground, 142 s): S2 scripted path — pre-minted trial id, selection
   code `SGP-a18c2a86bbdb48a2ba63fb1a653bfaf9-A:hil-2026-apc-crossroads-classic`
   (`build_selection_code`, run_tag = trial_id.hex), `start_trial(selection_code=...,
   auto_confirm_directive=True, max_specialist_calls=8)`. Paused at **G1**; directive_digest
   `75271c67…ad2453`; pick event appended to the product sidecar
   `state/config/gamma-styleguide-picks.jsonl` (left in place — product-emitted provenance).
2. **Resume** (`leg1_resume.py`, G1 approve per weed-clearing posture, cap=40): crossed 04A → **4.75 CD
   (live gpt-5)** → 05/05B irene-pass1 → 06 package_builder → **§07 gary (REAL Gamma)** … and hit
   **Anomaly #1** (below) at §07.
3. **Post-fix recover** (`leg1_recover2.py`, ONE recover through fixed matcher `59a9a48a`, 94 s):
   §07 gary completed live (1 Gamma generation + PNG export, matcher matched all 12 briefed slides),
   7.5 vera + 07B quinn-r dispatched, paused cleanly at **G2B**.
4. **JUDGE-1 verbatim: PASS 13/13** — latest gary contribution carries `styleguide_parity` with
   outcome `ok`, reason `match`, `clock_eligible=true`, `cd_status="resolved"`;
   `trial_start_directive_digest == cd_directive_digest == gary_directive_digest ==`
   `75271c67b7b74fd8ade4d44c08aabe7791c2e2f87a395476cec4e0fe34ad2453` (all non-null; equals on-disk
   `trial-start.json.directive_digest`); CD block status `resolved`, bound_guides exactly
   `[hil-2026-apc-crossroads-classic]` @ ssot_digest `6b94739f…6ac5`; resolution digests identical
   (`5f872000…9463`). Extract: `leg1-parity-receipt.json`.

## ⚠ Anomaly #1 — pre-existing production matcher defect (NOT S3), found + fixed mid-witness

- Leg-1's first continuation error-paused at §07: tag `gamma.export.brief-unmatched`, slide-07.
- Exact pair: brief **`Technology's Promise Requires Clinical Innovators`** vs Gamma export slug
  **`Technologys-Promise-Requires-Clinical-Innovators`**. `normalize_title` turned the apostrophe
  into a token boundary (`{technology, s, …}`) while Gamma DELETED it (`{technologys, …}`) — no
  containment edge either direction ⇒ deterministic fail-loud on every regeneration.
- The runner's own in-walk variance retry (auto-retry 1/3..3/3) meant **4 Gamma generations per
  attempt**. Attempt 1 (resume): 4 generations. Attempt 2 (ONE documented `trial recover`, the
  product's designed verb for this pause family, launched pre-diagnosis): 4 more, failed
  identically (346 s) — recorded as attempt-2-of-documented-retry.
- **ORCHESTRATOR STAND-DOWN** honored at 01:40Z (no further retries); coordinator's dev lane landed
  the party-ratified fix `59a9a48a` (apostrophe-family deletion in `normalize_title`, RED-first,
  party record §10); **GO** received; ONE recover through the fixed matcher succeeded (94 s).
- Validity ruling (§10, recorded before the post-fix recover): the judged parity surface is computed
  at the RESOLVE site BEFORE Gamma dispatch and is deterministic given directive+SSOT+CD block (all
  unchanged); frozen judge-1 had never executed; error-pause → recover is the legitimate product
  path. **Not retry-to-green.**

## Leg 2 — forced-divergence WARN (trial `4d465677-188c-401c-ae37-1acb19658db0`)

Design (leg4-udac rewind-recover precedent; CD-before/gary-after ordering pinned structurally):

1. **Prepare** (`leg2_prepare.py`, foreground): COPY leg-1 run dir → fresh trial id (leg-1 dir
   untouched). run.json: surgical id rewrites only; DROPPED `gary@07`, `vera@7.5`, `quinn_r@07B`
   (every contribution at manifest index ≥ idx(07)=23); **CD@4.75 STAYED** (authored in leg 1
   against ORIGINAL SSOT bytes); status flipped paused-at-gate → paused-at-error
   (tag `s3.acl.leg2.rewind-reposition-to-gary`). error-pause.json fabricated from the copied G2B
   checkpoint (same run_state/runner family the runner persists), repositioned to node 07/gary,
   last_gate_crossed=G1. `directive.yaml` NEVER touched. Offline checks all green
   (`leg2-prepare-result.json`).
2. **Mutation** (after validation, before any gary dispatch): `state/config/gamma-style-guides.yaml`,
   picked guide's `prompt_configuration.text_content.amount: minimal → concise` (valid UI vocab;
   F-806 verified live: ssot sha256 `6b94739f…6ac5 → 58a4fc05…9054`; picked-guide base-resolution
   digest `5f872000…9463 → 83981ed0…a651f`; exactly ONE guide's resolution changed).
3. **Recover** (`leg2_recover.py`, foreground, 123 s): §07 gary re-dispatched LIVE against the
   mutated SSOT (1 Gamma generation; fixed matcher matched cleanly), 7.5 + 07B re-dispatched,
   paused cleanly at **G2B** — the WARN was a log line only; dispatch was never blocked.
4. **JUDGE-2 verbatim: PASS 10/10** — outcome `divergence`, reason `resolution-mismatch`; detail
   carries BOTH envelopes (`cd_block` + `gary_view`); three directive digests EQUAL and non-null
   (`75271c67…ad2453` — directive untouched ⇒ genuine same-bytes disagreement, not drift);
   `cd_resolution_digest 5f872000…9463 ≠ gary_resolution_digest 83981ed0…a651f` (gary's live digest
   EXACTLY equals the prepare-time predicted post-mutation digest); WARN line captured verbatim in
   `walk-log-leg2.txt` (`app.specialists.gary._act: styleguide parity DIVERGENCE
   (resolution-mismatch): …`); run did NOT halt (paused-at-gate G2B, paused_error_tag null).
   `clock_eligible=false` on the divergence receipt (F-702 behavior). Extract:
   `leg2-parity-receipt.json`.
5. **Restore**: `git checkout -- state/config/gamma-style-guides.yaml`; `git status` clean for the
   file; resolver re-probe `amount == minimal`.

## Timeline (UTC 2026-07-07)

| time | event |
|---|---|
| ~01:18 | evidence dir created; judge1.py + judge2.py FROZEN |
| 01:20:31–01:22:55 | leg-1 start → paused G1 (142 s) |
| 01:23:48–01:29:50 | leg-1 resume; 4 Gamma gens; error-pause `gamma.export.brief-unmatched` |
| 01:32:17–01:38:03 | attempt-2 documented recover (pre-fix); 4 Gamma gens; identical failure |
| 01:40 | STAND-DOWN recorded (orchestrator directive; deterministic defect diagnosed) |
| ~01:52 | GO: matcher fix `59a9a48a` committed by dev lane (party §10) |
| 01:53:13 (approx start) | post-fix single recover; 1 Gamma gen; paused-at-gate G2B (94 s) |
| ~02:19 | JUDGE-1 verbatim: **PASS 13/13** |
| 02:22:44–02:22:45 | leg-2 prepare (copy/rewind/fabricate/validate) + SSOT mutation |
| 02:22:58–02:25:01 | leg-2 recover; 1 Gamma gen vs mutated SSOT; paused-at-gate G2B (123 s) |
| ~02:25 | JUDGE-2 verbatim: **PASS 10/10** |
| ~02:26 | SSOT restored via git checkout; verified clean; resolver back to `minimal` |

## Spend

- **Gamma**: 10 deck generations total (leg-1: 9 — of which 8 were burned by the pre-fix
  deterministic matcher defect, 4 per attempt via the runner's internal auto-retry 1/3..3/3;
  post-fix: 1. leg-2: 1) + PNG exports (~10 MB each).
- **OpenAI (LangSmith-measured cost reports)**: leg-1 trial `total_cost_usd ≈ $0.296` (cd gpt-5,
  irene-pass1, vera, quinn-r, gary-nano segments; start-walk composition additional); leg-2 copy
  reports the inherited measurement (`cost-report.json` in both run dirs).
- Wall-clock: ~68 min end-to-end (01:18–02:26Z), including the ~13-min stand-down/fix interlude.

## Command log

1. `leg1_start.py` — foreground, 600 s cap — exit 0 (paused G1).
2. `leg1_resume.py` — background + watchdog — walk error-paused `gamma.export.brief-unmatched`.
3. `leg1_recover.py` — ONE documented pre-fix recover — identical failure (expected post-diagnosis).
4. STAND-DOWN … GO (`59a9a48a`).
5. `leg1_recover2.py` — ONE post-fix recover — paused-at-gate G2B.
6. `judge1.py a18c2a86-…` — **PASS 13/13** (`judge1-output.txt`).
7. `leg2_prepare.py` — foreground — prepare OK + F-806 mutation verified.
8. `leg2_recover.py` — foreground, 600 s cap — paused-at-gate G2B.
9. `judge2.py 4d465677-… walk-log-leg2.txt` — **PASS 10/10** (`judge2-output.txt`).
10. `git checkout -- state/config/gamma-style-guides.yaml` + clean verify + resolver re-probe.

## Honest notes / residuals

- `state/config/gamma-styleguide-picks.jsonl` (tracked) carries 1 new appended pick event from the
  leg-1 scripted start — product-emitted provenance (same class as the S2 live run); deliberately
  NOT reverted by the witness.
- Leg-2's rewound run dir `state/config/runs/4d465677-…` and leg-1's `…/a18c2a86-…` remain on disk
  as live evidence (runs are not tracked). No cleanup receipts were written (nothing overwritten;
  F-701 respected).
- The leg-2 copy's `checkpoint.json`/decision-cards still carry leg-1's trial id internally (recover
  does not read them; the walk re-wrote `checkpoint.json` at its own G2B pause).
- Anomaly #1 doubles as a genuine production finding fixed on the record (`59a9a48a`): export
  title-matching was brittle against Gamma's apostrophe-deleting slugs; witness cost of the defect
  was 8 Gamma generations.
