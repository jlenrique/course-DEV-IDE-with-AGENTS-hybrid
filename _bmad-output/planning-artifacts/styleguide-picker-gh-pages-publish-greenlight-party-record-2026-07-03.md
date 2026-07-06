# Green-Light Party Record — `styleguide-picker-gh-pages-publish`

**Date:** 2026-07-03 (session 11, operator-present start; operator stepped away during green-light ratification — proceeded on party consensus per the autonomous-consensus standing order).
**Branch:** `dev/gamma-styleguide-phase2-2026-07-02` (arc mid-flight; NOT consolidated to master).
**Team (tailored):** 🏗️ Winston (architect), 🎨 Sally (UX — operator-designated load-bearing), 🧪 Murat (test/reliability — operator-designated load-bearing), 🎬 Marcus (production orchestrator, adjunct). Dr. Quinn / John (PM) not needed — no impasse.
**Verdict:** **GO-WITH-AMENDMENTS, 4/4 unanimous.** Amendments complementary (no contradiction).

## Objective
Make the Leg-D Gamma style Picker a RELIABLE INTERACTIVE surface on the PUBLIC gh-pages site — exactly as Storyboard-A's per-slide chooser is today — so the operator AND clients select, per run: (i) WHICH styleguide(s), and (ii) 1 OR 2 versions (single deck vs A/B). Solves session-09 GOTCHA a (localhost picker unreachable from clients' browsers). PRIMARY operator bar: thoroughly-tested interactive mechanics for reliable client-facing public-site UI; selection code round-trips into a valid directive with ZERO mis-mapping.

## Reuse-first pattern mirrored
`chooser_publisher.py::publish_chooser_for_gate` + `_git_publish_dir` (env `STORYBOARD_SITE_REPO_URL` default `jlenrique.github.io`, `GITHUB_PAGES_TOKEN`) → public `publish_url` + receipt. Return-path: `chooser_html_emitter.render_chooser_html` emits a static page whose buttons build a copyable SELECTION CODE (`SBA-{run_tag}-…` via `navigator.clipboard`); client pastes back; `marcus_spoc.narrate_gate(G2B)` surfaces the url. Picker reuses its existing `write_pick_to_directive` (fail-loud, crash-atomic, A-M1 lifecycle/probe invariant) + `append_pick_event` (append-only sidecar) marcus-side.

## Resolved design questions
- **Q1 Emitter location →** NEW `picker_html_emitter.py` mirroring `chooser_html_emitter.py`; **single-source** shared logic (roster load, card render, slot→deck-count rule, selection-code grammar) with the localhost picker so the two transports can't drift. (Winston)
- **Q2 Grammar →** transparent slug-based `SGP-{run_tag}-A:{slug}[ B:{slug}]`. **NO-GO on base64.** Grammar frozen in ONE place both encoder + decoder reference. (Murat + Winston)
- **Q3 Write locus →** marcus-side only; static page inert. `decode → write_pick_to_directive → append_pick_event`. (all)
- **Q4 Invocation seam →** dedicated PRE-FLIGHT beat before G1: publish → surface url → client picks → paste code → **echo-and-confirm** → commit directive → then open G1. Run start blocks fail-loud on an unresolved pick (or explicit default-guide path). (Marcus + Winston)

## Ratified amendment ledger (all blocking; all RED-first)
- **A1 (Sally, load-bearing) — explicit versions control.** Visible `role=radiogroup` "1 version / 2 versions" segmented control drives slot-B visibility; count stated in words. 1-version → code has only `A:`; 2-version → `A:`+`B:`. No directive-semantics change. **Operator-ratified by proceed-on-consensus (operator away).**
- **A2 (Sally + Murat) — copy/paste-back robustness.** Code ALWAYS visible in a selectable `<textarea>`/`<code>`; clipboard is convenience only (feature-detect + try/catch; "✓ Copied!" only on resolved promise; manual-copy fallback). Copy button inert-disabled (`aria-disabled`) until slot A filled, with why-text. Verbal paste-back close.
- **A3 (Murat, highest severity) — run_tag binding.** `picker_publisher` bakes live run_tag into the page; encoder emits only that tag. `decode_picker_selection_code(code, expected_run_tag)` — required arg, HARD-reject on mismatch. Stale code cannot decode into a foreign run.
- **A4 (Murat, primary bar) — ZERO mis-mapping.** Slots explicitly label-keyed (`A:`/`B:`), never positional. Transposition oracle: `slugA≠slugB` property test asserting `decode(encode(A=x,B=y)) == {A:x,B:y}` AND `!= {A:y,B:x}`.
- **A5 (Murat) — reject matrix + parity.** Full fail-loud decode validation (prefix, charset whitelist, ≤256 length cap pre-parse, per-slot regex, duplicate-slot, slug membership → reuse A-M1 deprecated/probe rejection, empty/whitespace, strict case). Sidecar dedup key `(run_tag, code_hash)` — identical re-paste idempotent; different code = deliberate change (last-write-wins). JS↔Python golden-fixture parity test as anti-drift tooth.
- **A6 (Sally) — public-surface honesty.** CANDIDATE/probe/preview chips visible + named in confirmation echo; non-16:9/provisional thumbnails labeled, never silently cropped. Responsive to 320px; a11y floors (keyboard-complete, `aria-live` on copy/validation, contrast ≥4.5:1, no color-only state).
- **A7 (Marcus) — provenance chain.** Paste-back rehydrates `styleguide_picker_provenance`: who (operator vs named client), when (pick ts ≠ run-open ts), from which url (+ roster content-hash), what resolved (ids + version count), and the code itself. Unattributable pick → fail loud.
- **A8 (Winston + Marcus) — anti-drift / SPOC guardrail.** Keep the localhost picker (surviving operator-local use per session-09) but single-source shared logic with the static path. Keep the selection code minimal — no feature grows to make a concierge demo look better.

## Live-proof floor (Murat) — deferred to operator-present checkpoint
Real `_git_publish_dir` to the real gh-pages branch → fetch public URL (HTTP 200, carries live run_tag) → real browser selects A + a different B → capture real code → paste into real `marcus_spoc` → assert directive names A-guide Style-A, B-guide Style-B (no transposition) + one sidecar event → PLUS one negative live proof: stale-run_tag code rejected loudly. **This session builds up to this line (RED-first + headless-browser + temp-bare-repo publish proof); the real public publish runs at a paid/public checkpoint with the operator present.**

## Test oracle (Murat) — RED-first spine
- Encoder extracted as a pure JS `buildSelectionCode(runTag, picks)` (headless-testable, not buried in a click handler).
- Python decoder property tests: `decode(encode(x))==x`; transposition asymmetry; full reject-matrix (each rule → its own RED test); run_tag-mismatch rejection.
- JS↔Python golden-fixture parity (load-bearing anti-drift).
- Headless-browser (Playwright, in-repo): load emitted HTML → click Copy → assert textarea/clipboard == golden code; assert fallback textarea present + populated.
- `_git_publish_dir`: temp BARE repo as origin; assert pack lands on gh-pages branch + receipt shape matches `chooser_publisher.py`. No real GitHub in unit tests.
