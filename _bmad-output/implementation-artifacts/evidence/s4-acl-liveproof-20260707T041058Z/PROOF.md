# S4 AC-L live witness — FAIL-LOUD flip (Canonical Production Conversation arc)

**LEG 3 (happy path STILL dispatches — anti-outage): JUDGE-3 = PASS (15/15)**
**LEG 2 (parity divergence WARN→ERROR HALT): JUDGE-2 = PASS (16/16)**
**LEG 1 (named-variant-styleguide-less WARN-seed→HALT): JUDGE-1 = PASS (12/12)**

Independent live-witness for Story S4. Repo branch `dev/workbook-2026-07-06`, HEAD `13792617` + the
uncommitted S4 diff LIVE in the working tree (Flip A `_act.py:599`, Flip B `_act.py:1148-1181`).
Witness edited NO production code. Evidence dir:
`_bmad-output/implementation-artifacts/evidence/s4-acl-liveproof-20260707T041058Z/`.

## Validity protocol (integrity-critical)

- **Judges frozen BEFORE any leg ran.** `judge1.py` / `judge2.py` / `judge3.py` written and hashed at
  **2026-07-07T04:13:57.364Z** (`judges-frozen.json`, sha256 recorded). Earliest leg action was leg-3
  start at **04:14:50Z** — i.e. every leg ran AFTER the freeze. Post-run re-hash confirms all three
  judges **UNCHANGED** since freeze (no retry-to-green tampering):
  - judge1.py `7a58d868…`, judge2.py `84129248…`, judge3.py `411bee9b…`
- **Each judge executed verbatim exactly ONCE** after its leg paused. Stdout verbatim in
  `judgeN-output.txt`; structured facts in `judgeN-facts.json`. First-run-stands: every judge PASSED
  on its single execution.
- All spend REAL (OpenAI gpt-5 family + Gamma Generate API). `.venv/Scripts/python.exe` only;
  `PYTHONIOENCODING=utf-8`; `.env` via `load_dotenv(override=True)` after popping the shell
  `OPENAI_API_KEY` (sk-subst sentinel gotcha) — loaded key `sk-proj-…oc0A` (len 164);
  `MARCUS_G0_ENRICHMENT_ACTIVE` popped so the first pause is G1.
- Legs driven foreground with hard in-process watchdogs (`threading.Timer` + `faulthandler` +
  `os._exit`); the long happy-path resume ran detached with the same in-process watchdog + a single
  terminal-state notification (never parked on an indefinite external watcher).
- No commits/pushes/stashes by the witness. The ONLY repo file mutated was
  `state/config/gamma-style-guides.yaml` (leg-2), restored via `git checkout --` + resolver re-probe
  (see Leg 2). `state/config/gamma-styleguide-picks.jsonl` carries one appended product-emitted pick
  event from the leg-3 scripted start (same class as S2/S3 live runs) — deliberately NOT reverted.

## Leg 3 — happy path still dispatches (anti-outage proof) — trial `4fe6073f-c8e2-4836-bb94-759dc5b97bbf`

1. **Start** (`leg3_start.py`, foreground, 149s): S2 scripted path — pre-minted trial id, selection
   code `SGP-4fe6073fc8e24836bb94759dc5b97bbf-A:hil-2026-apc-crossroads-classic` (`build_selection_code`,
   run_tag = trial_id.hex), `start_trial(selection_code=…, auto_confirm_directive=True,
   max_specialist_calls=8)` on corpus `course-content/courses/tejal-apc-c1-m1-p2-trends`. Paused at
   **G1**; directive_digest `ff90c166…283e27`.
2. **Resume** (`leg3_resume.py`, G1 approve per weed-clearing posture, cap=40, 197s): crossed 4.75 CD
   (live gpt-5) → 05/05B irene-pass1 → 06 builder → **§07 gary (REAL Gamma deck)** → 7.5 vera → 07B
   quinn-r → paused cleanly at **G2B**. Matcher fix `59a9a48a` is committed; no anomaly this time.
3. **JUDGE-3 verbatim: PASS 15/15** — §07 dispatched a REAL deck (generation_id `npkNxi1NwrKbfPj3NU61I`,
   calls_made 1, 12 slide rows each with a `.png` export under `…/exports/gary/`); parity receipt
   `outcome=ok, reason=match, clock_eligible=true, cd_status=resolved` (UNCHANGED from S3 leg-1 — the
   flip did NOT break the happy path); run `paused-at-gate G2B`, `paused_error_tag=None` (walk
   proceeded past §07); NO `gamma.styleguide.*` error tag in the run, error-pause, or walk log; CD
   bound_guides exactly `[hil-2026-apc-crossroads-classic]`.

## Leg 2 — parity divergence WARN→ERROR (HALT) — trial `648c9b3e-220a-4033-8a26-7e704737e10a`

Same rewind-recover setup S3 used to prove the WARN — post-S4 it must HALT.

1. **Prepare** (`leg2_prepare.py`, foreground): COPY leg-3's happy-path run dir → fresh trial id;
   run.json surgical id rewrite; DROPPED `gary@07`, `vera@7.5`, `quinn_r@07B`; **CD@4.75 STAYED**
   (authored in leg-3 against ORIGINAL SSOT bytes) → pins CD-before ordering; status flipped
   paused-at-gate → paused-at-error. error-pause.json fabricated (node 07 / gary, last_gate_crossed
   G1). Offline checks all green. `directive.yaml` NEVER touched.
2. **SSOT mutation** (after validation, before any gary dispatch): `gamma-style-guides.yaml`, picked
   guide `prompt_configuration.text_content.amount: minimal → concise` (valid UI vocab; F-806 — a
   resolver-emitted field so ssot AND base-resolution digests both diverge; directive untouched so the
   three directive digests stay EQUAL → genuine same-bytes divergence, not drift). ssot sha256
   `6b94739f…6ac5 → 58a4fc05…9054`; picked-guide resolution digest `5f872000…9463 → 83981ed0…a651f`;
   exactly ONE guide's resolution changed.
3. **Recover** (`leg2_recover.py`, foreground, **1s**): gary re-entered §07 vs the MUTATED SSOT and
   **HALTED PRE-SPEND** — `status=paused-at-error`, `paused_error_tag=gamma.styleguide.parity-divergence`
   (S3 WARN-proceeded to G2B here; S4 halts). `list_themes` (metadata) ran; NO generate call.
4. **JUDGE-2 verbatim: PASS 16/16** — error-pause tag `gamma.styleguide.parity-divergence`, node `07`,
   specialist gary; message carries the divergence `reason` (`resolution-mismatch`) AND the digest
   summary (cd_resolution_digest `5f872000…9463` ≠ gary_resolution_digest `83981ed0…a651f`; the three
   directive digests all EQUAL `ff90c166…283e27`) AND "pre-spend"; run `paused-at-error`
   (paused_gate null); ZERO Gamma generative spend (0 gary contributions — halt is pre-contribution;
   no `generation_id` anywhere); CD contribution retained; Flip-B ERROR line captured in
   `walk-log-leg2.txt`.
5. **Restore**: `git checkout -- state/config/gamma-style-guides.yaml`; sha256 back to `6b94739f…6ac5`;
   `git status` clean for the file; resolver re-probe `amount == minimal` (JUDGE-2 assertion
   `x0-ssot-restored-amount-minimal` PASS).

## Leg 1 — named-variant-styleguide-less WARN-seed→HALT — trial `cfe83980-d71d-49cb-8dff-fa403e5d422b`

Same rewind-recover mechanics; instead of the SSOT, the RECOVERED directive is edited.

1. **Prepare** (`leg1_prepare.py`, foreground): COPY leg-3's run dir → fresh trial id; DROP
   gary@07+downstream, KEEP CD@4.75; fabricate error-pause at gary@07. Then a **targeted text edit** of
   the recovered `directive.yaml`: strip the `styleguide` key from the NAMED variant A in
   `gamma_settings` → `[{variant_id: A, styleguide: hil-…}]` becomes `[{variant_id: A}]` (a named
   styleguide-less variant — NOT empty gamma_settings, which would fall back to default-A and NOT fire
   the flip). The `styleguide_picker_provenance` block was left byte-identical (verified).
2. **Recover** (`leg1_recover.py`, foreground, **1s**): gary re-entered §07, read the styleguide-less
   named variant from the directive, and **HALTED PRE-SPEND** in `_normalized_gamma_settings` (Flip A,
   which fires before the parity receipt) — `status=paused-at-error`,
   `paused_error_tag=gamma.styleguide.unbound`.
3. **JUDGE-1 verbatim: PASS 12/12** — error-pause tag `gamma.styleguide.unbound`, node `07`,
   specialist gary; message NAMES the offending variant ("variant A is present with no bound
   styleguide; … governance error (S4 fail-loud flip…)"); run `paused-at-error` (paused_gate null);
   ZERO Gamma generative spend (0 gary contributions; no `generation_id`); Flip-A ERROR line captured
   in `walk-log-leg1.txt`.

## Timeline (UTC 2026-07-07)

| time | event |
|---|---|
| 04:13:57 | judge1/2/3.py FROZEN (sha256 recorded in `judges-frozen.json`) |
| 04:14:50–04:17:21 | leg-3 start → paused G1 (149s) |
| 04:17:32–04:20:50 | leg-3 resume; 1 REAL Gamma deck (12 PNG); paused G2B (197s) |
| ~04:21 | JUDGE-3 verbatim: **PASS 15/15** |
| 04:21:13 | leg-2 prepare (copy/rewind/fabricate/validate) + SSOT mutation (F-806) |
| 04:21:24–04:21:25 | leg-2 recover; **HALT** `gamma.styleguide.parity-divergence` (1s, $0 generative) |
| ~04:21 | SSOT restored via git checkout; resolver back to `minimal` |
| ~04:21 | JUDGE-2 verbatim: **PASS 16/16** |
| 04:21:52 | leg-1 prepare (copy/rewind/fabricate) + directive styleguide-strip on variant A |
| 04:22:00–04:22:01 | leg-1 recover; **HALT** `gamma.styleguide.unbound` (1s, $0 generative) |
| ~04:22 | JUDGE-1 verbatim: **PASS 12/12** |

## Spend

- **Gamma**: exactly **1 deck generation** total (leg-3, generation `npkNxi1NwrKbfPj3NU61I`, +12 PNG
  exports). Legs 1 & 2 = **$0 generative** — both halted PRE-SPEND before any generate /
  create-from-template call (only the non-generative `client.list_themes()` metadata read ran, per
  F-1104). Zero-spend witnessed structurally: no gary contribution persisted and no `generation_id`
  anywhere in either halted run.
- **OpenAI (LangSmith-measured)**: leg-3 trial `total_cost_usd ≈ $0.323`. Legs 1 & 2 inherit leg-3's
  copied measurement (no new LLM calls beyond re-reaching §07 which raised immediately).
- Wall-clock: ~8 min end-to-end (04:14:50–04:22:01Z).

## Honest notes / residuals

- `state/config/gamma-styleguide-picks.jsonl` (tracked) carries 1 appended pick event from the leg-3
  scripted start — product-emitted provenance (same class as S2/S3); NOT reverted by the witness.
- The three run dirs (`4fe6073f…` leg-3, `648c9b3e…` leg-2, `cfe83980…` leg-1) remain on disk as live
  evidence (runs are untracked). No cleanup receipts written (nothing overwritten; F-701 respected).
- The leg-1/leg-2 copies' `checkpoint.json`/decision-cards still carry leg-3's trial id internally
  (recover does not read them for the halt).
- Both halt legs completed in ~1s, corroborating pre-spend: had a paid Gamma dispatch occurred it would
  have taken tens of seconds (cf. leg-3's 197s resume including one deck).

## Verdict

All three frozen judges PASSED on their single verbatim execution. The S4 FAIL-LOUD flip is
LIVE-PROVEN against real APIs: (Flip A) a named styleguide-less variant halts at
`gamma.styleguide.unbound` pre-spend; (Flip B) a parity divergence halts at
`gamma.styleguide.parity-divergence` pre-spend (the exact setup S3 proved WARN-proceeded); and the
canonical happy path still dispatches a real Gamma deck to G2B with an unchanged `ok/match` receipt —
the flip manufactured NO outage.
