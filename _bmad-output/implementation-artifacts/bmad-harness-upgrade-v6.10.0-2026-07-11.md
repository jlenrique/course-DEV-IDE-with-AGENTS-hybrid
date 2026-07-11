# BMAD Harness Upgrade — v6.10.0 (2026-07-11)

**Branch:** `chore/bmad-upgrade-v6.10.0-2026-07-11` (cut from consolidated master `067c687b`)
**Executed at operator direction** ("do this now on my behalf") per the upgrade-at-arc-boundary recommendation: consolidation first, dedicated branch, `--all-stable`, ceremony re-validation before the next real sprint gate.
**Research basis:** `_bmad-output/planning-artifacts/research/technical-latest-bmad-version-looping-feature-research-2026-07-10.md` + live GitHub release/CHANGELOG review 2026-07-11.

## Command

```
npx --yes bmad-method@latest install --directory . --action update --all-stable -y
```

## Version deltas

| Module | Before | After | Channel change |
|---|---|---|---|
| BMad Core | 6.6.1-next.5 | **6.10.0** | next → stable |
| BMad Method (bmm) | 6.6.1-next.5 | **6.10.0** | next → stable |
| BMad Builder (bmb) | v1.8.0 | **v2.1.0** (major) | stable |
| Test Architect (tea) | v1.17.0 | **v1.19.0** | stable |
| CIS | v0.2.0 | **v0.2.1** | stable |

## Install verification (all PASS)

- `_bmad/_config/manifest.yaml` shows 6.10.0, lastUpdated 2026-07-11T04:10Z.
- **323 custom files preserved** by installer; `_bmad/memory/` sanctums (322 git-tracked files) show **zero diff** — Marcus/Tracy/Texas/etc. sanctum trees untouched.
- `_bmad/custom/` overrides (config.toml, config.user.toml) intact.
- IDE stubs regenerated: 72 skills → `.claude/skills`; cursor/codex/github-copilot now target the universal **`.agents/skills`** dir; cline → `.cline/skills`.
- Governance-load-bearing skills confirmed present post-upgrade: `bmad-party-mode`, `bmad-sprint-run-charter`, `bmad-cis-agent-creative-problem-solver` (Dr. Quinn — impasse chain), `bmad-agent-pm` (John — tiebreaker), `bmad-tea`, full `bmad-testarch-*` suite, `bmad-code-review`, `bmad-quick-dev`, `bmad-dev-story`, `bmad-retrospective`.
- Skill replacements landed as expected: `bmad-investigate` removed (no replacement), `bmad-distillator` → `bmad-spec`, `bmad-create-ux-design` → `bmad-ux`. New: `bmad-forge-idea`, `bmad-dev-auto`, `bmad-prd`/`bmad-architecture` consolidated skills (legacy `bmad-create-prd`/`edit-prd`/`validate-prd`/`create-architecture` remain as deprecated shims until v7 — CLAUDE.md governance references keep working).
- `uv` 0.11.8 already on PATH (v7 readiness — v7 standardizes on `uv run`).

## Machine-local cleanup

- Removed stale `.cursor/skills/` and `.github/skills/` stub trees (65 old 6.6-era skills each, including since-removed skills). Superseded by installer-managed `.agents/skills/`. All stub dirs are gitignored; regenerable by re-running the installer on any machine.
- **Other machines:** after pulling, re-run the installer once per machine to regenerate local stubs (`npx bmad-method@latest install --directory . --action update --all-stable -y`).

## Git-visibility note

`_bmad/*` is gitignored except `_bmad/memory/`, and all IDE stub dirs are gitignored — so this upgrade intentionally produces **no tracked diff** beyond this record. The install is per-machine; this artifact + the manifest are the durable evidence. *(Superseded in part by the party amendments below: the amendments commit itself tracks `_bmad/custom/` and edits pyproject/.gitignore/dev-guide/deferred-inventory — the "no tracked diff" statement describes the installer run alone.)*

## Party-mode ceremony re-validation

v6.9/v6.10 changed party-mode (custom parties, persistent session memory, four run modes, anti-consensus club, point-to-point agent-team sync). Because sprint governance leans on party consensus (= approval) and the Quinn→John impasse chain, a live ceremony smoke was run post-upgrade as the validation gate for this upgrade itself — see §Ceremony smoke result below.

## Ceremony smoke result — 4/4 GO-WITH-AMENDMENTS (full-spawn subagent mode)

**Roster:** Winston (architect), John (PM), Amelia (dev), Murat (test architect) — governance core, each a real independently-thinking subagent. All four independently ran their own checks rather than trusting the presented verification (three independently discovered the same unstaged-record defect) — the ceremony demonstrably did NOT rubber-stamp.

| Voice | Vote | Key contribution |
|---|---|---|
| Winston | GO-WITH-AMENDMENTS | Branch tip == master; record artifact untracked → "merging nothing." Verification was presence-based, not behavior-based. Structural: repo has no tracked BMAD version pin — the record artifact is the only cross-machine signal. |
| John | GO-WITH-AMENDMENTS | Same catch. Job-to-be-done is durability/reproducibility, not the merge. pyproject defect passes the CLAUDE.md guardrail test (genuine repo problem). Demanded the standing "did the new machinery behave" note on the first real party gate. |
| Amelia | GO-WITH-AMENDMENTS | Independently found the branch at zero commits ahead with the record untracked (third voice on that catch). **Refuted the proposed one-line license fix by reproduction**: fatal error is setuptools flat-layout discovery (18 top-level dirs), license form is only a DeprecationWarning. Correct fix `[tool.uv] managed = false`; flagged `uv run` implicit-sync threat to the live-verified `.venv` (repro'd litellm download mid-build). Flagged `_bmad/custom` single-disk exposure. |
| Murat | GO-WITH-AMENDMENTS | Independent manifest + 72-skill-dir re-read. Witness matrix: install integrity/roster/removals/party-subagent-mode WITNESSED; code-review, dev-story/quick-dev, TEA GATE intent, bmb v2-vs-sanctums, memlog persistence UNWITNESSED → 5-receipt pre-gate witness set (filed in deferred inventory). "Signing the merge, not the harness." |

**Amendments executed at close (this commit):** record artifact committed; `pyproject.toml` → `license = "MIT"` + `[tool.uv] managed = false` with acceptance test (plain `uv run` at repo root: resolve_customization + resolve_party both pass, `.venv` site-packages digest unchanged; independently re-run live by the receipt-1 Acceptance Auditor on 2026-07-11 — both scripts launch cleanly, no build, no sync); `PYTHONUTF8=1` codified in `.claude/settings.json` env + dev-guide note; `.gitignore` negation `!_bmad/custom/` (tracks project overrides; inner `.gitignore` keeps `*.user.toml` out); deferred-inventory follow-ons filed (`bmad-6-10-pre-gate-witness-set`, `bmad-party-machinery-check`, `claude-md-v7-shim-reference-cleanup`, `bmad-cp1252-upstream-bug`).

**Ceremony behavior differences observed vs pre-upgrade party pattern (v6.9/v6.10 machinery):**
- New activation chain is script-resolved (`resolve_customization.py` → `resolve_party.py` via `uv run`) instead of prompt-only — this is what surfaced the two Windows defects, live.
- Party groups now exist as first-class rooms: `code-review-crew` and the new **`anti-consensus-club`** resolved as switchable groups.
- Per-party persistent memory (memlog) is available and enabled (`party_memory: true`); first memlog for the installed party written at this gate's close. Cross-session persistence is intentionally UNWITNESSED until next session start (receipt 5).
- Four run modes (session/auto/subagent/agent-team); this gate ran full-spawn `subagent`. `agent-team` mode remains unwitnessed.

**Verdict:** consensus GO with amendments executed inline; merge to master proceeds under party-consensus-=-approval governance. The harness earns full trust only after the 5-receipt witness set lands on the next real story.

## Pre-gate witness set — COMPLETE 2026-07-11 (all 5 receipts)

| # | Receipt | Result |
|---|---|---|
| 1 | `bmad-code-review` on existing diff (`7b65b879`) | **WITNESSED — machinery sharp.** Full 3-layer run (Blind Hunter + Edge Case Hunter + Acceptance Auditor). Real findings: setuptools>=77 floor needed for PEP 639 license string; `managed=false` silently killed `uv sync` in 3 muted CI workflows + a troubleshooting remedy; record-integrity gaps in this artifact. All triaged and fixed same-day (this commit). Acceptance Auditor: commit matches record, no drift. |
| 2 | `bmad-quick-dev`-class implement smoke | **WITNESSED** via the first supervised `bmad-dev-auto` iteration (spec → implement → dual adversarial review → done; merged at `6d265d2c`). |
| 3 | TEA v1.19 `GATE` intent | **WITNESSED — resolves and executes.** Gate verdict on Workbook W4 close: **PASS** (claim envelope fully covered; residual risks all ≤4). Machinery frictions filed: `python3` hardcoded (Windows takes fallback path), "trace Phase 2" not directly addressable, no read-only advisory-gate mode. |
| 4 | BMB v2.1 read-only analysis of one sanctum agent (Tracy) | **WITNESSED — analyzer runs clean on v1-era agent** (prepass classifies memory-agent correctly; scanners return findings, not crashes). ⚠️ **CRITICAL caveat:** v2's fix recommendations (add CREED/BOND/MEMORY/CAPABILITIES, rewrite bootloader) would BREAK test-pinned Class-C+ sidecar contracts (`test_tracy_sidecar_4_file_pattern`, `test_tracy_activation_contract`). Builders stay advisory-only on Class-C/C+ agents until `{agent.build_standards}` org injection encodes the sidecar classes. Also: builder could mis-resolve `skills/bmad_agent_tracy/` (underscore = production Python package). |
| 5 | memlog cross-context persistence | **WITNESSED from fresh context** — read path resolves cold, prior gate context recoverable, file git-tracked, live append 1→2 entries. Minor convention drift only (`--type` tag optional/omitted). |

**Standing rule from receipt 4:** do NOT point a BMB v2 builder (Create/Rebuild/Edit fix-pass) at any Class-C/C+ sidecar agent; Analyze is safe. Encode sidecar classes via builder `customize.toml` `{agent.build_standards}` before lifting this fence.

The harness is now behavior-witnessed on every surface the next sprint gate leans on: dev loop, review layers, gate rubric, builder analyzer, party machinery + memory.
