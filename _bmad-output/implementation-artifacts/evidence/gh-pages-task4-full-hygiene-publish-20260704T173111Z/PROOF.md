# Task 4 — real Phase-2 publish through the FULL hardened path (done-signal candidate)

**Arc:** gh-pages publish-hardening + durable-deploy. **Date:** 2026-07-04 (~17:31Z).
**Class S. Sole Claude dev lane.** Codex shadow-monitor OFF (concurrence unavailable this session).
**Operator-confirmed** the destructive retention prune before this run.

## What was proven — all three hygiene teeth fire in ONE real production publish
`publish_picker(run_tag="task4prod20260704T173111Z", verify=True)` — the Phase-2 interactive
picker surface, published end-to-end through the hardened + Actions-deployed path with FULL
hygiene (no monkeypatch; real `state/config/storyboard-publisher.yaml`).

1. **RETENTION fired (real, permanent).** The publish's retention prune deleted **15 >10-day
   storyboard packs (~62.8 MB)** — verified: 3 sampled packs
   (`242b859f…`, `8553ab38…-chooser`, `386912d6…-b`) all 404 in the tree post-publish. The
   deletes rode the SAME publish commit `0c6bf915` ("Publish assets/styleguide-picker/task4prod…")
   via the whole-repo/staged commit-gate. Current pack + 2 allowlisted gamma paths protected.
2. **SIZE-GUARD passed.** No `SizeGuardRefusal` — the push proceeded, which by construction means
   `project_published_size` measured the post-prune tree (~411 MB) under the 900 MB fail line
   (the guard runs fail-loud BEFORE commit/push; a trip would have blocked the push).
3. **VERIFY fired both ways.** The publisher's verify-after-push polled the new URL and **failed
   loud** (`PickerPublishError` `picker.publish.not-live`, HTTP 404 after 600 s) because that
   push's Actions deploy failed at GitHub's `syncing_files` CDN stage — the hardened refuse-a-dead-URL
   behavior, validated again by a real backend failure. After a deploy retry cleared the flake,
   `verify_build_after_push` against the live URL **PASSED (status 200)**. The URL serves real
   picker content (`Gamma Styleguide Picker` + full 8-style roster).

## External backend note (session-11 issue, persistent this session)
GitHub Pages' `syncing_files` CDN stage flaked on **two consecutive** deploys this session
(Task 3 cleanup `6dcc5dc`, Task 4 publish `0c6bf91`) — a stuck-rejecting streak matching session 11.
`upload-pages-artifact` always succeeded; only `deploy-pages` / `syncing_files` failed. An
empty-commit retrigger (`4950fac`, Git Data API) cleared it → 200. The publisher's verify correctly
never hands back a dead URL. The retention prune (474 → ~411 MB) did NOT prevent the flake, matching
session 11's finding that `syncing_files` fails even on healthy trees — it is an EXTERNAL, intermittent
GitHub backend state, not our code/content/size. **Filed follow-on:** a bounded deploy-retry inside
the publisher on `syncing_files` failure (before verify gives up) would reduce operator-visible
failures; the operator browser-side Source-toggle/republish reset (session 11) remains the hard reset.

## Cleanup
The task4 proof pack was removed from `main` in one commit (`3d3751b9`; 404 in tree). The **retention
prune of the 15 packs is the durable, intended production change and STANDS** (operator-confirmed,
10-day policy). Site served tree reduced ~62.8 MB.

## Outcome
Task 4 accomplished: a real production publish through the full hardened path with retention +
size-guard + verify all firing and the URL serving 200 real content. This is the goal done-signal
candidate — pending the fully-spawned BMAD party concurrence (recorded separately). Codex
shadow-monitor concurrence is UNAVAILABLE (OFF this session) — noted honestly, not asserted.
