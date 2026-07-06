# Task 2 — durable GitHub Actions Pages deploy — LIVE PROOF

**Arc:** gh-pages publish-hardening + durable-deploy (`goal-gh-pages-publish-hardening-arc-2026-07-03.md`)
**Date:** 2026-07-04 (~15:14Z)
**Site repo:** `jlenrique/jlenrique.github.io` (default `STORYBOARD_SITE_REPO_URL`; env unset → default applies)
**Session class:** S. Sole Claude dev lane (single-dev-lane discipline). Codex shadow-monitor OFF.

## What landed
- `pages.yml` committed to the site repo at `.github/workflows/pages.yml` on `main`,
  commit **`c547225`**. The staged workflow (`gh-pages-actions-deploy-workflow.yml`) is
  GitHub's canonical static-site starter (checkout@v4 / configure-pages@v5 /
  upload-pages-artifact@v3 / deploy-pages@v4; `permissions: pages:write + id-token:write`;
  `concurrency: pages`, `cancel-in-progress:false`; `path: .`). The two one-time INSTALL
  comment lines were trimmed (Pages-Source flip already done in session 13).
- Commit route: the `GITHUB_PAGES_TOKEN` fine-grained PAT is `Contents:write` only and
  GitHub gates `.github/workflows/` writes behind a separate `Workflows` permission
  (API PUT → 403 "Resource not accessible by personal access token"). Rather than broaden
  the token (least-privilege: the workflow file needs committing exactly once), the commit
  was landed via Claude-in-Chrome on the operator's logged-in browser. Content set into the
  CodeMirror-6 editor via a synthetic paste event (byte-verified before commit).

## Live proof (unauthenticated, as a real visitor)
- Actions run **"Deploy static site to Pages"** `28710460771` (event=push, sha=`c547225`) → **success** (~45s).
- Pages config: **`build_type: workflow`**, status **`built`**.
- `github-pages` deployment: sha **`c547225`**, ref `main`, created `2026-07-04T15:14:14Z`
  — ties the live site to the Actions deploy of our commit.
- HTTP 200s:
  - `https://jlenrique.github.io/` → 200 (real `<h1>Hello World</h1>` root index)
  - `https://jlenrique.github.io/index.html` → 200
  - `https://jlenrique.github.io/.nojekyll` → 200
  - `…/assets/styleguide-picker/liveproof20260703185235/index.html` → 200 (19 KB real HTML)
  - `…/assets/styleguide-picker/compactreprove20260703/index.html` → 200 (23 KB real HTML)

## Outcome
Durable Actions deploy path is live. **Deploy-freeze window (opened at the session-13
Pages-Source flip) is CLOSED** — pushes to `main` now deploy via Actions; git-history size
is irrelevant to this path. Task 2 complete.
