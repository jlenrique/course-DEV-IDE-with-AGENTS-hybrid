# Task 3 — stamp picker #4 against the live public URL (durable Actions path)

**Arc:** gh-pages publish-hardening + durable-deploy. **Date:** 2026-07-04 (~16:31Z).
**Class S. Sole Claude dev lane.** Codex shadow-monitor OFF.

## What was proven
The hardened picker publisher + interactive selection-code round-trip, on the NOW-DURABLE
GitHub Actions deploy path (Task 2), against the real public URL — no local server.

### 1. Hardened publisher ran + self-verified (fail-loud validated by a REAL backend failure)
`publish_picker(run_tag="task3stamp20260704T163100Z", verify=True)` (retention forced OFF for
this stamp — non-destructive; the sanctioned prune is Task 4's deliverable; size-guard + verify
REAL). The publisher pushed the pack, then its verify-after-push polled the new URL for 600s and
got **HTTP 404** — because that push's Actions deploy **FAILED at GitHub's `syncing_files` CDN
stage** ("Deployment failed, try again later"). The publisher **correctly FAILED LOUD, refusing
to hand back a dead URL** (`PickerPublishError`) — the hardened verify tooth validated by a real
external backend failure, not a synthetic one.

### 2. `syncing_files` flakiness is transient + external (session-11 issue resurfacing)
`upload-pages-artifact@v3` succeeded (448 MB uploaded); `deploy-pages@v4` failed only at the CDN
`syncing_files` stage. Three deploys succeeded minutes earlier (Task 2 `c547225`, Task 1b tooth-C
`37f45f7`, cleanup `b455506`), so it is NOT content/size — the same intermittent GitHub Pages
backend flake session 11 diagnosed. A **retry recovered**: an empty commit (`f33903a`, Git Data
API — no 474 MB clone) triggered a fresh deploy that succeeded, and the picker URL went **live
(200)**. (Token lacks `actions:write` → could not re-run the workflow via API; empty-commit
retrigger is the token-compatible path.)

### 3. Interactive round-trip on the LIVE public URL — real browser, zero mis-mapping
`https://jlenrique.github.io/assets/styleguide-picker/task3stamp20260704T163100Z/index.html`
served 200 with the full 8-style roster (real thumbnails; Studio candidate correctly shows the
`no live render` degrade placeholder, A-M2). Driven via real page interactions (Claude-in-Chrome):
- Selected **2 versions**, clicked **Crossroads Classic** → slot **A** (badge A, green outline),
  clicked **Blueprint palette** → slot **B** (badge B, blue outline).
- Page-emitted selection code:
  `SGP-task3stamp20260704T163100Z-A:hil-2026-apc-crossroads-classic B:hil-2026-apc-crossroads-blueprint`
- **SOP-204**: with 2 versions + only slot A filled, the code was empty and **copy was disabled**
  (blocked); enabled only once both distinct styles were picked.
- **Python-twin decode** (`decode_picker_selection_code`, `expected_run_tag` bound):
  → `{A: hil-2026-apc-crossroads-classic, B: hil-2026-apc-crossroads-blueprint}` = exactly what
  was clicked → **zero mis-mapping**. Idempotent decode. **Stale/foreign run_tag → hard-rejected.**

### 4. Cleanup
Stamp pack removed from `main` in one commit (`6dcc5dc9`, Git Data API subtree removal;
confirmed 404 in tree). No scratch content left on the client site.

## Follow-on (filed)
The durable Actions path still rides GitHub's intermittently-flaky `syncing_files` CDN stage on
the ~448 MB served tree. Mitigations: (a) the **retention prune** (Task 4) shrinks the served tree
→ fewer syncing_files failures; (b) candidate publisher enhancement — a bounded **deploy-retry**
on a `syncing_files` failure before the verify gives up (the verify correctly fails loud today, but
a retry would reduce operator-visible failures). Recommend filing to deferred-inventory.

## Outcome
Task 3 CLOSED: hardened publisher exercised (verify fail-loud validated by a real backend failure),
picker live on the durable Actions path via retry, interactive round-trip proven on the real public
URL (zero mis-mapping, SOP-204, stale-reject, idempotent), scratch cleaned up. Party concurrence
deferred to the Task 4 goal done-signal.
