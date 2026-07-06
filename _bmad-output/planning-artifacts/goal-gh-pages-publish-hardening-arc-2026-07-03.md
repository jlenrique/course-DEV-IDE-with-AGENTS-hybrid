# GOAL — gh-pages publish hardening + durable-deploy arc (2026-07-03)

**Product framing (binding):** every change must earn its place by improving the Marcus-SPOC production runtime — never to make an off-the-books proofing run pass (CLAUDE.md §CRITICAL DESIGN GUARDRAIL). Branch `dev/gamma-styleguide-phase2-2026-07-02`; do NOT consolidate to master.

## How we work (non-negotiable across every task)
- **BMAD spine, Marcus-first.** Drive each task through `bmad-quick-dev` with a **fully-spawned party-mode team** (Winston/architect for the shared-helper + deploy-path design; Amelia/dev; Murat/test; Marcus orchestrating). Party green-lights before dev opens; `bmad-code-review` before any task is called done; proceed by team consensus per sprint-governance.
- **Live testing is indispensable, incremental, never deferred.** Every component is exercised against the REAL gh-pages remote / real GitHub Pages backend AS it is authored or edited — a live round-trip (publish → verify HTTP 200 serving real content → decode/echo where applicable) is part of that component's own validation, not a final-only confirmation. No mocks for the deploy path.
- **The Codex shadow-monitor is a standing input.** Re-read the shadow-monitor notes (`_bmad-output/implementation-artifacts/marcus-studio-override-shadow-monitor-2026-07-03.md`) on its ~10-minute cadence AND at every gate; treat its independent findings as first-class review input to fold in before any task is closed.

## Tasks (ordered; ~6h total)

**Task 1 — gh-pages self-maintenance routine (FIRST UP).**
Spec: `_bmad-output/planning-artifacts/gh-pages-site-maintenance-routine-spec-2026-07-03.md`. Build retention-prune-on-publish (>10-day, allowlist), a pre-push size guard, and verify-build-after-publish; **consolidate the duplicated `_git_publish_dir` across the picker/chooser/storyboard/gamma publishers into one shared helper.** Live-prove against the real gh-pages remote.

**Task 2 — durable GitHub Actions deploy path.**
Adopt the staged workflow (`_bmad-output/implementation-artifacts/gh-pages-actions-deploy-workflow.yml`) as the durable deploy path so git-history size stops mattering. Live-prove one real Actions deploy serving 200.

**Task 3 — close picker task #4 against the live public URL.**
Re-run the hardened publisher (it self-verifies 200 or fails loud) and drive the Playwright interactive round-trip against the now-live public picker URL — no local server — proving zero mis-mapping, SOP-204 live, idempotent commit.

**Task 4 — prove the hardened path on the real arc.**
Publish the next Phase-2 styleguide item end-to-end through the now-hardened + pruned + Actions-deployed path, confirming retention + size-guard + verify all fire in a real production publish.

## Done-signal
The goal is complete when a **fully-spawned bmad party-mode team, spawned for this purpose, concurs that the final task (Task 4) is accomplished and validated** — with the live evidence and the shadow-monitor's concurrence on record. Push to `origin/<branch>` at every safety checkpoint and at WRAPUP (branch push only; no master merge).
