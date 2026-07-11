# Codex Shadow Monitor - Agentic Research Foundations - 2026-07-10

**Role:** independent shadow monitor for the Grok/Cursor-led Agentic Research Foundations mini-epic.

This is an independent shadow-monitoring lane for the research-capability mini-epic. Each poll reads the current repository state and appends a time-stamped report with findings (`SOP-RNNN`). The monitor writes only this log. It does not modify production code, tests, runtime state, commits, branches, Grok/Cursor-owned artifacts, or BMAD-owned decision records.

**Primary SSOTs reviewed by this monitor lane:**
- `_bmad-output/planning-artifacts/epic-agentic-research-foundations-2026-07-10.md`
- `_bmad-output/planning-artifacts/agentic-research-foundations-party-greenlight-2026-07-10.md`
- `_bmad-output/implementation-artifacts/agentic-research-foundations-stories-2026-07-10.md`
- `_bmad-output/implementation-artifacts/research-r0-charter-taxonomy-live-matrix-2026-07-10.md`
- `_bmad-output/implementation-artifacts/research-r1-posture-runtime-2026-07-10.md`
- `_bmad-output/implementation-artifacts/research-r2-consensus-evidence-bolster-2026-07-10.md`
- `_bmad-output/implementation-artifacts/evidence/research-r*/`
- `_bmad-output/implementation-artifacts/evidence/consensus-mcp-oauth-smoke-20260710/`
- `_bmad-output/implementation-artifacts/evidence/jefferson-access-probe*/`

## Standing Watchpoints

1. **Marcus-SPOC product guardrail.** Research work must strengthen the Marcus-SPOC runtime research service. Do not shape production code for concierge/proofing convenience.
2. **Texas retrieval SSOT.** New provider work must flow through Texas `RetrievalAdapter` / dispatcher seams. No parallel product path through `scripts/api_clients/` or direct Tracy HTTP bypass.
3. **Single production seam.** R1 posture behavior must stay on the `research_wiring` / `IreneTracyBridge` path; no duplicate selector/dispatcher fantasy that leaves production on the old path.
4. **Flag discipline.** `MARCUS_RESEARCH_DETECTIVE_LIVE` remains default OFF until R3+R4 are hermetic and live green; flag-OFF behavior must remain bit-identical to the legacy Scite-canonical path.
5. **Live-test binding.** Hermetic tests are necessary but not sufficient for story close. Every R-story needs authentic live evidence on the real seam, except R0 docs/contracts and R5 if explicitly fenced for absent Jefferson credentials.
6. **Triangulation honesty.** Corroborate mode needs Scite+Consensus triangulation or fail-loud / explicit `single_provider` receipt. Dual dispatch is not the same claim as dual-provider convergence.
7. **Credibility surfacing.** R4 must make hierarchy tier, peer-review flag, and provider provenance visible on every research row; G2 remains resolvability, not semantic claim-support.
8. **No cite fabrication.** R6 intake must consume rows and fail on fabricated citation paths.
9. **Hard pause teeth.** R7 cannot close as advisory-only. Flag-ON must block Pass-2 until approve/reject/defer disposition is written; resume/recover resilience remains TRAIL unless explicitly pulled in.
10. **Jefferson honesty.** R5 may fence live only if credentials are absent or unusable; do not fake institutional-library proof.
11. **Code review and closure evidence.** `bmad-code-review`, MUST-FIX remediation, live evidence, BMAD concurrence, and commit/push evidence must be visible before final close claims.
12. **Dirty-worktree caution.** Monitor must distinguish committed durable claims from currently visible WIP.

---
### SOP-R000 - Baseline monitor opens during R3 WIP - 2026-07-10T19:35:31-04:00

**Scope reviewed:** current branch/status/log, research epic and party greenlight records, stories SSOT, R0/R1/R2 artifacts, latest R1/R2/R3/Consensus/Jefferson evidence directories, current diff/stat, and direct marker search across research wiring, Texas retrieval providers, Tracy bridge/dispatcher, and relevant tests. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this new monitor ledger is the only repo write by this poll.

**Current repo state:** workspace is on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). The visible local log still includes the Batch branch commits below it, but active work is now Research.

**Worktree state:** active Research WIP is substantial and uncommitted. Tracked modifications include `.cursor/mcp.json`, `.mcp.json`, `_bmad-output/implementation-artifacts/agentic-research-foundations-stories-2026-07-10.md`, `_bmad-output/implementation-artifacts/research-r1-posture-runtime-2026-07-10.md`, `_bmad-output/implementation-artifacts/sprint-status.yaml`, `app/marcus/orchestrator/research_wiring.py`, `skills/bmad-agent-texas/scripts/retrieval/consensus_provider.py`, `skills/bmad-agent-texas/scripts/retrieval/scite_provider.py`, `skills/bmad_agent_tracy/scripts/irene_bridge.py`, `skills/bmad_agent_tracy/scripts/posture_dispatcher.py`, `tests/contracts/test_tracy_postures.py`, and `tests/integration/marcus/test_braid_s3_research_wiring.py`. Untracked research files include R1/R2/R3 evidence packs, Jefferson probe packs, `research-r2-consensus-evidence-bolster-2026-07-10.md`, `skills/bmad-agent-texas/scripts/retrieval/triangulator.py`, `tests/unit/marcus/orchestrator/test_research_r1_posture_runtime.py`, `tests/unit/marcus/orchestrator/test_research_r2_evidence_bolster.py`, and `tests/unit/retrieval/test_consensus_markdown_and_triangulator.py`.

**Selected claim envelope classification:** active mini-epic is **Agentic Research Foundations / Tracy Detective Service**. The visible envelope is R0-R7 foundations: posture-aware deterministic research intents, Scite+Consensus evidence-bolster and triangulation, credibility fields, Jefferson provider seam, Irene intake, and hard pause teeth. Current visible implementation appears centered on **R1 posture runtime**, **R2 Consensus/evidence-bolster**, and **R3 triangulator**. R4-R7 remain not visibly implemented as completed story slices.

**BMAD gate/story visibility:** party greenlight exists and is explicit: 4/4 GO-WITH-AMENDMENTS from John/Winston/Amelia/Murat plus Quinn synthesis for R7. The operator live-test binding is folded into the epic and story SSOT. Story SSOT says R0 done, R1 done, R2 done, R3 in-progress, and R4-R7 backlog. R0 is durable in HEAD as a docs/contracts commit. R1/R2/R3 are visible as workspace WIP plus evidence, but no committed close for those story slices is visible in the current branch tip.

**Test / validation visibility:** live evidence is visible and non-vacuous for early slices:
- R1: `_bmad-output/implementation-artifacts/evidence/research-r1-20260710T211425Z/PROOF.md` records Scite live posture dispatch with one corroborate and one gap_fill result.
- R2: `_bmad-output/implementation-artifacts/evidence/research-r2-20260710T215111Z/PROOF.md` records Scite+Consensus dual dispatch, `total_rows=21`, and PASS.
- Consensus OAuth smoke: `_bmad-output/implementation-artifacts/evidence/consensus-mcp-oauth-smoke-20260710/PROOF.md` is visible.
- R3: `_bmad-output/implementation-artifacts/evidence/research-r3-20260710T215231Z/PROOF.md` records PASS by `explicit_single_provider_receipt`, with `dual_provider_count=0`.

This monitor did not rerun tests. Hermetic tests are visible as new/modified files, but their latest run output is not independently verified in this poll.

**Implementation visibility:** marker scan confirms research wiring now includes `MARCUS_RESEARCH_DETECTIVE_LIVE`, `evidence_bolster`, provider readiness checks, Scite/Consensus comments, and `triangulation_receipt` wiring. Texas retrieval now has modified Consensus and Scite providers plus a new `triangulator.py` with title normalization/bridge hooks. Tracy bridge propagates `evidence_bolster`. Tests cover posture runtime, evidence bolster, Consensus markdown parsing, and triangulator behavior. These are strong implementation signals, but they remain partly untracked/uncommitted in this poll.

**Scoreability:** R0 is scoreable as a committed charter/taxonomy/live-matrix slice. R1 and R2 are **provisionally scoreable as visible WIP with live evidence**, but should not be treated as durable story closes until code review/commit/party close evidence lands. R3 is **partially scoreable** for explicit single-provider receipt behavior; it is not yet scoreable as true dual-provider convergence because the latest live proof reports `dual_provider_count=0`. R4-R7 are not scoreable as implemented.

**Findings / cautions:**
**F-R-0001 [P1] R1/R2/R3 claims are still mostly dirty-worktree claims.** The branch HEAD only states R0 done. The monitor sees substantial implementation and evidence for R1/R2/R3, but not a committed story-close state. Treat these as active WIP until close artifacts/code review/commit/push appear.
**F-R-0002 [P1] R3 live proof currently proves explicit single-provider receipt, not dual-provider convergence.** This is permitted by the party decision only when honest, but it must not be summarized later as Scite+Consensus triangulated convergence unless a new live proof shows dual-provider clusters.
**F-R-0003 [P2] Story SSOT says R3 in-progress while code/evidence suggest R3 follow-through is underway.** Keep status precise: R3 is not done until the story file, hermetic run, live proof, review, and close evidence agree.
**F-R-0004 [P2] Sprint status is modified but not a clear mini-epic status authority in this poll.** It is broad and historically stale; the research epic/story SSOT is cleaner for current status, but final close should reconcile sprint-status rows.
**F-R-0005 [P2] Jefferson probe evidence exists before R5 story close.** This may be useful discovery, but R5 scoreability still needs Texas provider registration/contract tests and a live-or-fenced R5 story record.

**Residual fencing:** R4 credibility field surfacing, R5 Jefferson provider seam and credential/live fence, R6 Irene intake with no fabricated cites, R7 hard pause teeth, semantic claim-source audit, Epic 17 related-resources/inline/hypothesis modes, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, novel HAI/PHS ingestion, and any claim that G2 has become semantic claim-support.

**Verdict:** Research mini-epic is active and moving fast. The strongest visible progress is R1/R2 live proof and R3 triangulator WIP. Completion is **not yet established** for the mini-epic: R4-R7 remain open, R3 is not fully done, and R1/R2/R3 need durable close evidence beyond dirty-worktree artifacts.

---
### SOP-R001 - R3 dual-provider proof and R4 credibility evidence appear; still dirty-worktree - 2026-07-10T19:49:15-04:00

**Scope reviewed:** research monitor ledger through SOP-R000, current `git status --short --branch --untracked-files=all`, local git log, updated stories SSOT, latest R3/R4 evidence packs, current diff/stat, and search for visible research code-review / close artifacts. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). No new commit is visible since SOP-R000; branch HEAD still only durably claims the R0 opening commit.

**Worktree state:** active Research WIP expanded materially since SOP-R000. Newly visible tracked modifications include `app/marcus/lesson_plan/workbook_producer.py`, `app/marcus/orchestrator/research_citation.py`, and `app/specialists/workbook_producer/_act.py` in addition to the R1/R2/R3 files already named in SOP-R000. Newly visible untracked Research files include `app/marcus/orchestrator/research_credibility.py`, `scripts/utilities/run_research_r3_live_evidence.py`, `scripts/utilities/run_research_r4_live_evidence.py`, `tests/unit/marcus/orchestrator/test_research_r4_credibility.py`, and fresh evidence directories for `research-r3-20260710T233547Z`, `research-r3-20260710T233619Z`, and `research-r4-20260710T233843Z`. The monitor ledger itself is also untracked because this lane was just opened.

**Selected claim envelope classification:** active work has advanced from R1/R2/R3 WIP into **R3 triangulator completion evidence** and **R4 credibility surfacing evidence**. The story SSOT now states **R0-R4 done; R5-R7 backlog**. The monitored envelope remains Agentic Research Foundations: deterministic Tracy postures, Scite+Consensus triangulation, credibility fields, Jefferson seam, Irene intake, and hard pause teeth.

**BMAD gate/story visibility:** party greenlight and epic guardrails are unchanged. The story SSOT now marks R3 and R4 done and lists delivered code/evidence for both. However, no visible `bmad-code-review` artifact, research close record, final party concurrence, or new commit/push evidence appears in this poll. This keeps R1-R4 as strong visible implementation evidence but not durable branch-close evidence.

**Test / validation visibility:** evidence improved materially:
- R3 latest proof `_bmad-output/implementation-artifacts/evidence/research-r3-20260710T233619Z/PROOF.md` records `pass=True reason=dual_provider`, `row_count=26`, `cluster_count=21`, `dual_provider_count=5`, `single_provider_count=16`, and `title_bridge_rows_added=5`. This resolves SOP-R000's live-proof caution for R3 dual-provider convergence at the evidence level.
- R4 proof `_bmad-output/implementation-artifacts/evidence/research-r4-20260710T233843Z/PROOF.md` records `pass=True entries=21 non_vacuous=21`, `has_dual_provider_entry=True`, and sample entries with hierarchy tier, peer flag, provenance, triangulation status, and score.
- R1/R2 evidence remains as before and still supports early posture and dual-dispatch claims.

This monitor did not rerun hermetic tests, and no independent test transcript beyond the evidence packs was reviewed.

**Implementation visibility:** R4 implementation is now visible in the worktree: a new `research_credibility.py`, additions to `research_citation.py`, workbook producer projection changes, and new R4 tests. R3 implementation remains visible through `triangulator.py`, Scite title support, Consensus identity parsing, and `research_wiring` triangulation receipt wiring. These changes appear aligned with the epic's Texas/research-entry/product path, but they are still uncommitted WIP.

**Scoreability:** R0 remains scoreable as committed. R1/R2 remain provisionally scoreable as visible WIP with live evidence. R3 is now provisionally scoreable for **dual-provider triangulation** based on the newer live proof. R4 is provisionally scoreable for **credibility surfacing** based on the live proof and visible code/test changes. R5-R7 are not scoreable as implemented. The mini-epic as a whole is not complete because Jefferson, Irene intake, hard pause teeth, promote close, code review, final party concurrence, and commit/push evidence remain absent.

**Findings / cautions:**
**F-R-0006 [P1] R1-R4 are still dirty-worktree closes, not durable branch closes.** The story SSOT now says R0-R4 done, and live evidence is strong for R1-R4, but HEAD remains `d1effcfa` and no review/commit/party close evidence is visible.
**F-R-0007 [P1] R4 adds workbook projection surfaces, raising blast radius.** The change now touches `workbook_producer.py`, `research_citation.py`, and specialist workbook output. Before close, review should verify additive rendering only, no workbook layout redesign, and no regression to legacy flag-OFF research rows.
**F-R-0008 [P2] R3 dual-provider proof appears resolved, but only in the latest evidence pack.** Future summaries should cite `research-r3-20260710T233619Z`, not the older `research-r3-20260710T215231Z` single-provider proof.
**F-R-0009 [P2] R5 Jefferson evidence remains probe-only.** Jefferson probe artifacts are still useful discovery, but no R5 provider registration / contract / live-or-fenced story close is visible.
**F-R-0010 [P2] No code-review artifact is visible despite story SSOT done flags.** Given the breadth of new retrieval, citation, workbook, and evidence logic, `bmad-code-review` should be treated as a required gate before durable close.

**Residual fencing:** R5 Jefferson provider seam and credential/live fence, R6 Irene intake with no fabricated cites, R7 hard pause teeth, promote close, semantic claim-source audit, Epic 17 related-resources/inline/hypothesis modes, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, novel HAI/PHS ingestion, and any claim that G2 has become semantic claim-support. R1-R4 also remain fenced from durable close until review/commit evidence lands.

**Verdict:** Progress is real and stronger than SOP-R000. R3 now has visible dual-provider live proof, and R4 has live credibility-surfacing proof. The session is **not complete** against the full research mini-epic: R5-R7 remain open, and even R1-R4 are not durable until review, commit, push, and BMAD close evidence appear.

---
### SOP-R002 - R4 evidence remains latest; durability gates still absent - 2026-07-10T20:04:15-04:00

**Scope reviewed:** research monitor ledger through SOP-R001, current `git status --short --branch --untracked-files=all`, local git log, updated stories SSOT, latest evidence directory timestamps, and searches for visible research code-review / close artifacts. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). No new commit is visible since SOP-R001; branch HEAD still only durably claims the R0 opening commit.

**Worktree state:** materially stable against SOP-R001. Tracked Research-related modifications remain visible in `.cursor/mcp.json`, `.mcp.json`, the research story/status artifacts, `app/marcus/orchestrator/research_wiring.py`, `app/marcus/orchestrator/research_citation.py`, `app/marcus/lesson_plan/workbook_producer.py`, `app/specialists/workbook_producer/_act.py`, Texas Scite/Consensus providers, Tracy bridge/dispatcher, and related tests. Untracked Research files still include this monitor ledger, R1/R2/R3/R4 evidence packs, Jefferson probe packs, `app/marcus/orchestrator/research_credibility.py`, `skills/bmad-agent-texas/scripts/retrieval/triangulator.py`, R1/R2/R3/R4 live evidence scripts, and R1/R2/R3/R4 tests. No new R5/R6/R7 implementation artifact surfaced in this poll.

**Selected claim envelope classification:** active work remains **Agentic Research Foundations / Tracy Detective Service**, with visible R1-R4 implementation/evidence and R5-R7 still backlog in the story SSOT. The story SSOT still states **R0-R4 done; R5-R7 backlog**. The active visible claim is therefore early-foundation slices, not full mini-epic completion.

**BMAD gate/story visibility:** party greenlight and epic live-test guardrails are unchanged. The stories SSOT remains advanced to R0-R4 done, but this poll still finds no visible `bmad-code-review` artifact, research close record, final party concurrence, or commit/push evidence. The lack of those gates is unchanged from SOP-R001.

**Test / validation visibility:** no newer evidence directory appears after `_bmad-output/implementation-artifacts/evidence/research-r4-20260710T233843Z/`. Latest visible evidence remains:
- R3 dual-provider proof: `_bmad-output/implementation-artifacts/evidence/research-r3-20260710T233619Z/PROOF.md`, `dual_provider_count=5`, `title_bridge_rows_added=5`.
- R4 credibility proof: `_bmad-output/implementation-artifacts/evidence/research-r4-20260710T233843Z/PROOF.md`, `entries=21`, `non_vacuous=21`, `has_dual_provider_entry=True`.
- R1/R2 and Consensus smoke evidence remain visible as earlier.

This monitor did not rerun hermetic tests and did not find a new independent test transcript.

**Implementation visibility:** unchanged from SOP-R001. R3 triangulation/title-bridge and R4 credibility/workbook projection code remain visible in dirty worktree state. The change scope still spans retrieval, orchestration, citation models, workbook output, MCP config, and tests, so review load remains significant before durable close.

**Scoreability:** R0 remains scoreable as committed. R1/R2/R3/R4 remain provisionally scoreable as visible WIP with live evidence, with R3 now supported by the newer dual-provider proof and R4 by credibility-surfacing proof. R5/R6/R7 remain not scoreable as implemented. The mini-epic as a whole remains not complete because R5-R7, promote close, review, commit/push, and party concurrence evidence remain absent.

**Findings / cautions:**
**F-R-0011 [P1] No durability transition since SOP-R001.** HEAD is still `d1effcfa`; R1-R4 remain dirty-worktree story closes rather than durable branch closes.
**F-R-0012 [P1] R5-R7 remain unimplemented against the full foundations DoD.** Jefferson provider, Irene intake, and hard-pause teeth are still backlog in the SSOT and have no scoreable implementation evidence in this poll.
**F-R-0013 [P2] R4 blast-radius review remains required.** Workbook projection and citation model changes are still visible and still need code review for additive-only rendering, legacy flag-OFF compatibility, and no workbook-layout redesign.
**F-R-0014 [P2] Evidence freshness is stable, not advancing.** The newest evidence remains R4 at 2026-07-10 19:38 local; no new live proof appeared after SOP-R001.
**F-R-0015 [P2] Jefferson remains probe-only.** Multiple Jefferson access probe directories remain visible, but no R5 provider story close or live/fenced provider record appears.

**Residual fencing:** R5 Jefferson provider seam and credential/live fence, R6 Irene intake with no fabricated cites, R7 hard pause teeth, promote close, semantic claim-source audit, Epic 17 related-resources/inline/hypothesis modes, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, novel HAI/PHS ingestion, and any claim that G2 has become semantic claim-support. R1-R4 also remain fenced from durable close until review/commit evidence lands.

**Verdict:** No material Research proof change since SOP-R001. R3 dual-provider and R4 credibility evidence remain the latest positive signals, but the session is still **not complete** against the full mini-epic and R1-R4 are still not durable without review/commit/push and BMAD close evidence.

---
### SOP-R003 - No material change; R1-R4 still not durable - 2026-07-10T20:19:18-04:00

**Scope reviewed:** research monitor ledger through SOP-R002, current `git status --short --branch --untracked-files=all`, local git log, latest evidence directory timestamps, searches for visible research code-review / close artifacts, and current diff/stat. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). No new commit is visible since SOP-R002.

**Worktree state:** materially unchanged from SOP-R002. The same broad dirty Research surface remains visible: MCP config, research story/status artifacts, `research_wiring.py`, `research_citation.py`, workbook producer surfaces, Texas Scite/Consensus provider changes, Tracy bridge/dispatcher, and related tests. Untracked Research WIP remains visible for the monitor ledger, R1-R4 evidence packs, Jefferson probe packs, `research_credibility.py`, `triangulator.py`, R1-R4 live scripts, and R1-R4 tests. No new R5/R6/R7 file or evidence directory surfaced in this poll.

**Selected claim envelope classification:** unchanged: **Agentic Research Foundations / Tracy Detective Service** with visible R1-R4 implementation/evidence and R5-R7 still not scoreable. The active visible claim is still early-foundation slices, not full mini-epic completion.

**BMAD gate/story visibility:** no visible transition since SOP-R002. Story SSOT remains at R0-R4 done / R5-R7 backlog, but no `bmad-code-review`, research close record, final party concurrence, or commit/push evidence is visible. The story done flags therefore remain weaker than the governance done-bar.

**Test / validation visibility:** no evidence directory newer than `_bmad-output/implementation-artifacts/evidence/research-r4-20260710T233843Z/` appears. Latest positives remain R3 dual-provider proof (`research-r3-20260710T233619Z`, `dual_provider_count=5`) and R4 credibility proof (`research-r4-20260710T233843Z`, `entries=21`, `non_vacuous=21`, `has_dual_provider_entry=True`). This monitor did not rerun hermetic tests and did not find a new independent test transcript.

**Implementation visibility:** unchanged from SOP-R002. The visible WIP continues to align with R1-R4, including posture dispatch, evidence-bolster, Consensus parsing, triangulation/title-bridge, credibility classification, citation enrichment, and additive workbook projection. No R5 Jefferson adapter implementation, R6 Irene intake implementation, or R7 hard-pause implementation is visible as a scoreable story slice.

**Scoreability:** R0 remains scoreable as committed. R1-R4 remain provisionally scoreable as dirty-worktree WIP with live evidence, but not durable. R5-R7 remain not scoreable as implemented. Full mini-epic completion remains not scoreable.

**Findings / cautions:**
**F-R-0016 [P1] No review/commit durability transition.** The same governance gap persists: R1-R4 have evidence, but HEAD remains R0-only and no review/close artifact is visible.
**F-R-0017 [P1] R5-R7 still block the mini-epic claim.** Jefferson provider, Irene intake, and hard pause teeth are required foundations stories and remain unimplemented/not evidenced.
**F-R-0018 [P2] Evidence freshness has not advanced.** Latest evidence remains R4 at 2026-07-10 19:38 local; no new live proof appeared in this 15-minute poll.
**F-R-0019 [P2] Dirty diff remains large and cross-cutting.** The diff still spans retrieval, orchestration, citation, workbook projection, config, and tests; review should be treated as load-bearing.
**F-R-0020 [P2] Jefferson is still discovery/probe-only.** Existing Jefferson probe directories do not satisfy R5 provider registration, contract, or live/fenced story close.

**Residual fencing:** R5 Jefferson provider seam and credential/live fence, R6 Irene intake with no fabricated cites, R7 hard pause teeth, promote close, code review, final party concurrence, commit/push, semantic claim-source audit, Epic 17 related-resources/inline/hypothesis modes, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, novel HAI/PHS ingestion, and any claim that G2 has become semantic claim-support.

**Verdict:** No material Research proof change since SOP-R002. R3 and R4 remain strong visible evidence, but R1-R4 are still dirty-worktree closes and the full Agentic Research Foundations mini-epic remains incomplete until R5-R7 and governance durability gates land.

---
### SOP-R004 - R5-R7 and promote artifacts appear; claim scoreable but not durable - 2026-07-10T20:34:18-04:00

**Scope reviewed:** research monitor ledger through SOP-R003, current `git status --short --branch --untracked-files=all`, local git log, updated stories SSOT, R5/R6/R7 evidence packs, promote/close letter, latest evidence directory timestamps, searches for visible research code-review / close artifacts, and current worktree surface. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). No new commit is visible since SOP-R003. Branch HEAD still durably records only the R0 opening commit, while the full R0-R7/promote claim exists in dirty worktree artifacts.

**Worktree state:** materially expanded since SOP-R003. New tracked modifications include `_bmad-output/implementation-artifacts/research-r0-charter-taxonomy-live-matrix-2026-07-10.md`, `_bmad-output/planning-artifacts/deferred-inventory.md`, `_bmad-output/planning-artifacts/epic-agentic-research-foundations-2026-07-10.md`, `app/marcus/orchestrator/production_runner.py`, Texas `__init__.py` / `provider_directory.py`, and retrieval adapter/provider contract tests. Newly visible untracked Research artifacts include `_bmad-output/implementation-artifacts/agentic-research-foundations-promote-2026-07-10.md`, R5/R6/R7 evidence packs, `app/marcus/orchestrator/research_detective_gate.py`, `app/specialists/_shared/research_intake.py`, `app/specialists/irene/retrieval_intake.py`, `skills/bmad-agent-texas/scripts/retrieval/jefferson_library_provider.py`, R5/R6/R7 live evidence scripts, and R5/R6/R7 tests. A new planning strawman `_bmad-output/planning-artifacts/epic-workbook-research-products-glossary-trends-2026-07-10.md` also appeared for the next mini-epic.

**Selected claim envelope classification:** active claim has advanced from early R1-R4 slices to **Agentic Research Foundations promote / close**. Stories SSOT now states **R0-R7 + promote done** and next work is `workbook-research-products-glossary-and-trends`. The promote letter claims foundations closed with R5 accepted under a documented Chrome-session fence, detective flag default OFF, and TRAIL items filed.

**BMAD gate/story visibility:** the original party greenlight remains visible, and the promote letter records orchestrator close. However, this poll still finds no visible `bmad-code-review` artifact, separate research close-party concurrence record, or commit/push evidence. The promote letter is a strong close artifact, but it does not by itself satisfy the monitor's durability watchpoint for review + committed branch state.

**Test / validation visibility:** evidence advanced materially:
- R5: `_bmad-output/implementation-artifacts/evidence/research-r5-20260711T002458Z/PROOF.md` is **FENCED**, reason `chrome_running_quit_required`; it explicitly says do not fake live and to quit Chrome/re-run or accept fence. Story SSOT says R5 hermetic green and prior session3 PDF probe remains the access-pattern witness.
- R6: `_bmad-output/implementation-artifacts/evidence/research-r6-20260711T002804Z/PROOF.md` records `pass=True consumed=21`, `fabricate_cite_path_red=True`, and intake phrases from Scite/Consensus rows.
- R7: `_bmad-output/implementation-artifacts/evidence/research-r7-20260711T003255Z/PROOF.md` records `pass=True`, with landing point, Pass-2 block, advisory-cannot-unlock, disposition-then-proceed, flag-off noop, and production-runner seam all PASS.
- Earlier R1-R4 evidence remains visible and unchanged.

This monitor did not rerun hermetic tests and did not find a new independent test transcript beyond the evidence packs.

**Implementation visibility:** R5/R6/R7 implementation is now visible in dirty worktree state: Jefferson provider and provider-directory changes, shared/Irene research intake modules, hard-pause gate, production runner gate seam, R5/R6/R7 scripts, and R5/R6/R7 unit tests. This is a credible implementation surface for the remaining foundations stories, subject to review.

**Scoreability:** At the evidence/artifact level, the **full foundations claim is now provisionally scoreable with an explicit R5 fence**: R1-R4 have live evidence, R5 has hermetic/provider seam plus documented live fence, R6 has intake/fabrication-red evidence, and R7 has hard-pause teeth evidence. It is **not durable branch-scoreable** because the work remains uncommitted and no code-review/party-close artifact is visible beyond the promote letter. If the scoring standard allows dirty-worktree evidence plus a named R5 fence, the claim can be evaluated; if it requires committed reviewed code, it is not yet complete.

**Findings / cautions:**
**F-R-0021 [P1] Full promote claim appeared, but still without commit/review durability.** The story SSOT and promote letter now claim R0-R7 + promote done, but HEAD is still `d1effcfa` and no review/commit/push evidence is visible.
**F-R-0022 [P1] R5 is fenced, not live-proven.** The fence is honest and explicitly documented as `chrome_running_quit_required`; do not summarize Jefferson as live institutional-library retrieval until the fence is upgraded or expressly accepted as the close condition.
**F-R-0023 [P1] R7 touches production-runner pause semantics.** `production_runner.py` and a new `research_detective_gate.py` are now in scope. Review should verify both walks, flag-OFF noop, pause/resume side effects, and no accidental default-ON behavior.
**F-R-0024 [P2] R6 intake proof is positive but thin.** The proof shows 21 rows consumed and fabricate-cite RED, but the story itself fences thicker narration weave / segment-manifest follow-on. Avoid overclaiming full Irene research-product integration.
**F-R-0025 [P2] Next mini-epic artifact appeared before durable close.** `epic-workbook-research-products-glossary-trends-2026-07-10.md` is visible as next work; it should not blur the foundations close until R0-R7 are reviewed and committed.

**Residual fencing:** R5 live upgrade after Chrome quit / SSO-cookie availability, code review, final party concurrence beyond orchestrator close, commit/push, semantic claim-source audit, Epic 17 related-resources/inline/hypothesis modes, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, OpenAlex/ERIC/LoC adapters, workbook research products glossary/trends, novel HAI/PHS ingestion, and any claim that G2 has become semantic claim-support.

**Verdict:** Material progress since SOP-R003. R5-R7 evidence and a promote letter are now visible, so the full Agentic Research Foundations claim is **provisionally scoreable with the named R5 live fence**. It is still **not durable** until code review, commit/push, and final close concurrence are visible.

---
### SOP-R005 - Successor workbook W0-W1 starts atop uncommitted foundations close - 2026-07-10T20:49:16-04:00

**Scope reviewed:** research monitor ledger through SOP-R004, current `git status --short --branch --untracked-files=all`, local git log, latest evidence directory timestamps, Workbook Research Products W0/W1 artifacts, workbook party greenlight, current diff/stat, and searches for visible research code-review / close artifacts. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). No new commit is visible since SOP-R004. Branch HEAD still does not durably contain the R1-R7/promote work or the new workbook W0-W1 work.

**Worktree state:** dirty worktree expanded again. The Agentic Research Foundations dirty surface remains, and new successor Workbook Research Products artifacts are visible: `_bmad-output/implementation-artifacts/workbook-research-products-stories-2026-07-10.md`, `_bmad-output/implementation-artifacts/workbook-w0-charter-consumer-matrix-2026-07-10.md`, `_bmad-output/planning-artifacts/workbook-research-products-party-greenlight-2026-07-10.md`, `app/marcus/lesson_plan/research_packet.py`, `scripts/utilities/run_workbook_w1_live_evidence.py`, `tests/unit/marcus/lesson_plan/test_research_packet_w1.py`, and W1 evidence directories. Current diff/stat is larger than SOP-R004: 24 tracked files, 2831 insertions / 127 deletions, plus many untracked artifacts.

**Selected claim envelope classification:** the foundations claim remains **Agentic Research Foundations promote / close**, provisionally scoreable with R5 fence. New activity is a successor mini-epic, **Workbook Research Products / glossary + trends**, with W0-W1 already marked done in its story SSOT. This successor work should not be conflated with additional foundations close evidence.

**BMAD gate/story visibility:** Agentic Research Foundations story SSOT and promote letter still claim R0-R7 + promote done. No visible `bmad-code-review` artifact, separate close-party concurrence record, commit, or push evidence appeared. Workbook Research Products has its own party greenlight and W0/W1 story records, but that does not repair the missing durability gates for foundations.

**Test / validation visibility:** latest evidence is now successor workbook evidence, not foundations evidence:
- Workbook W1 latest proof `_bmad-output/implementation-artifacts/evidence/workbook-w1-20260711T003830Z/PROOF.md` records `pass=True`, 21 entries from the R4 live pack, same packet digest across two consumers, Irene intake same rows, required shape pins, empty fail-closed, and M3-safe module.
- Foundations latest evidence remains R7 `_bmad-output/implementation-artifacts/evidence/research-r7-20260711T003255Z/`, R6 `_bmad-output/implementation-artifacts/evidence/research-r6-20260711T002804Z/`, and R5 fenced `_bmad-output/implementation-artifacts/evidence/research-r5-20260711T002458Z/`.

This monitor did not rerun hermetic tests and did not find a new independent test transcript beyond evidence packs.

**Implementation visibility:** foundations implementation remains visible as dirty worktree only. Successor W1 adds a research packet facade in `app/marcus/lesson_plan/research_packet.py`, with shared-reader tests and live evidence. This appears consistent with the foundations consumer-availability invariant, but it is now layered on top of an uncommitted foundations base.

**Scoreability:** Foundations remain **provisionally scoreable at evidence/artifact level with explicit R5 fence**, but still **not durable branch-scoreable** because review/commit/push/close concurrence are absent. The successor workbook W0-W1 work is separately provisionally scoreable as WIP, but it should not be used to mark foundations durable. If the desired standard is committed reviewed code, neither foundations nor the successor W1 slice has crossed that line yet.

**Findings / cautions:**
**F-R-0026 [P1] Successor work is now stacked on an uncommitted foundations close.** Workbook W0-W1 artifacts and evidence appeared before Agentic Research Foundations has review/commit durability.
**F-R-0027 [P1] Foundations still lack code-review/commit evidence.** No `bmad-code-review`, separate close-party concurrence, commit, or push is visible; HEAD remains `d1effcfa`.
**F-R-0028 [P2] Workbook W1 evidence depends on R4 live pack.** That is coherent, but it means W1 proof inherits the dirty-worktree foundations base and should be considered successor evidence, not a substitute for foundations close review.
**F-R-0029 [P2] R5 remains fenced.** The Jefferson institutional-library seam remains `chrome_running_quit_required`, not live-proven.
**F-R-0030 [P2] Scope risk is increasing.** With foundations plus workbook-research product work in the same uncommitted branch state, final review should separate claims by mini-epic and avoid a single broad "research done" overclaim.

**Residual fencing:** foundations code review, final party concurrence beyond orchestrator close, commit/push, R5 live upgrade after Chrome quit / SSO-cookie availability, semantic claim-source audit, Epic 17 related-resources/inline/hypothesis modes, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, OpenAlex/ERIC/LoC adapters, workbook W2-W4 glossary/trends/live Tejal arm, novel HAI/PHS ingestion, and any claim that G2 has become semantic claim-support.

**Verdict:** No durability transition for Agentic Research Foundations since SOP-R004. The foundations claim remains provisionally scoreable with R5 fenced, but still not durable. New Workbook Research Products W0-W1 work has started and produced evidence; it should be tracked as successor work layered on the unresolved foundations branch state.

---
### SOP-R006 - Workbook W2 evidence appears; foundations still uncommitted - 2026-07-10T21:04:17-04:00

**Scope reviewed:** research monitor ledger through SOP-R005, current `git status --short --branch --untracked-files=all`, local git log, latest evidence directory timestamps, Workbook Research Products W2 artifact/evidence, current workbook story SSOT, current diff/stat, and searches for visible research code-review artifacts. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). No new commit is visible since SOP-R005. Branch HEAD still does not durably contain the Agentic Research Foundations R1-R7/promote work or the successor Workbook W0-W2 work.

**Worktree state:** dirty worktree expanded again. Foundations artifacts and implementation remain uncommitted, successor Workbook W0-W1 remains uncommitted, and new Workbook W2 work is visible: `app/marcus/lesson_plan/glossary_projection.py`, `scripts/utilities/run_workbook_w2_live_evidence.py`, `tests/unit/marcus/lesson_plan/test_glossary_w2.py`, and evidence directories `workbook-w2-20260711T005815Z` / `workbook-w2-20260711T005835Z`. The current status still shows broad tracked modifications across MCP config, foundations stories/status/planning, orchestration, citation, workbook producer, Texas providers, Tracy bridge, provider tests, and integration tests, plus extensive untracked evidence and successor artifacts.

**Selected claim envelope classification:** the monitored foundations claim remains **Agentic Research Foundations promote / close**, provisionally scoreable with R5 fenced but not durable. New activity is now **Workbook Research Products W0-W2**, with W2 glossary encyclopedia component marked done. This is successor work, not additional durability evidence for foundations.

**BMAD gate/story visibility:** Agentic Research Foundations story SSOT and promote letter still claim R0-R7 + promote done. Workbook Research Products story SSOT now states **W0-W2 done; W3 next**. No visible `bmad-code-review` artifact, separate foundations close-party concurrence record, commit, or push evidence appeared in this poll. Workbook party greenlight and W0-W2 story records are visible, but they do not repair foundations durability.

**Test / validation visibility:** latest evidence is successor workbook W2:
- Workbook W2 proof `_bmad-output/implementation-artifacts/evidence/workbook-w2-20260711T005835Z/PROOF.md` records `pass=True`, `articles=3`, `non_vacuous=3`, sample term `Switching Stay Home Instruction`, provenance retained, MD/DOCX same composed model, G2 clean per story SSOT, and empty research not fabricated.
- Workbook W1 proof remains visible at `workbook-w1-20260711T003830Z`.
- Foundations latest evidence remains R7/R6/R5-fenced as recorded in SOP-R004.

This monitor did not rerun hermetic tests and did not find a new independent test transcript beyond evidence packs.

**Implementation visibility:** successor W2 adds a glossary projection path and workbook producer integration according to the W2 story. This work appears to use the W1 research packet and foundations R4 research entries, so it depends on the uncommitted foundations stack. No W3 trends/hot-topics implementation or W4 Tejal live arm evidence is visible yet.

**Scoreability:** Foundations remain **provisionally scoreable at evidence/artifact level with explicit R5 fence**, but still **not durable branch-scoreable**. Workbook W0-W2 are separately provisionally scoreable as dirty-worktree successor slices, with W2 live evidence now visible. Neither foundations nor workbook successor work has crossed the reviewed/committed durability line.

**Findings / cautions:**
**F-R-0031 [P1] More successor work is accumulating on the uncommitted foundations base.** Workbook W2 has evidence and implementation, while foundations still lack review/commit durability.
**F-R-0032 [P1] Foundations still lack code-review/commit evidence.** HEAD remains `d1effcfa`; no `bmad-code-review`, close-party concurrence, commit, or push is visible.
**F-R-0033 [P2] Workbook W2 evidence is positive but belongs to a different mini-epic.** It should be tracked as Workbook Research Products evidence, not as extra proof that foundations are durable.
**F-R-0034 [P2] W2 changes broaden workbook output surface.** Glossary projection and workbook producer integration need review for additive-only rendering, provenance retention, no fabricated articles, and markdown/DOCX parity.
**F-R-0035 [P2] W3/W4 remain open.** Trends/hot-topics and the live Tejal workbook arm are not visible as completed evidence in this poll.

**Residual fencing:** foundations code review, final party concurrence beyond orchestrator close, commit/push, R5 live upgrade after Chrome quit / SSO-cookie availability, semantic claim-source audit, Epic 17 related-resources/inline/hypothesis modes, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, OpenAlex/ERIC/LoC adapters, Workbook W3/W4 trends/live Tejal arm, novel HAI/PHS ingestion, and any claim that G2 has become semantic claim-support.

**Verdict:** No durability transition for Agentic Research Foundations since SOP-R005. Foundations remain provisionally scoreable with R5 fenced but not durable. Successor Workbook Research Products has advanced to W2 with live evidence, increasing the need to separate foundations close review from follow-on workbook-product scoring.

---
### SOP-R007 - No new research evidence; W3 still pending, durability still absent - 2026-07-10T21:20:24-04:00

**Scope reviewed:** research monitor ledger through SOP-R006, current `git status --short --branch --untracked-files=all`, local git log, latest evidence directory timestamps, Workbook Research Products story SSOT, and searches for visible research review/close artifacts. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). No new commit is visible since SOP-R006. Branch HEAD still does not durably contain the Agentic Research Foundations R1-R7/promote work or the successor Workbook W0-W2 work.

**Worktree state:** broad dirty state persists. Tracked modifications still span MCP config, foundations story/status/planning artifacts, Marcus orchestration/research citation/wiring, workbook producer surfaces, Texas retrieval providers, Tracy bridge/posture dispatcher, and research/provider tests. Untracked artifacts still include the Agentic Research Foundations monitor/promote files, R1-R7 evidence/scripts/tests, Jefferson provider/probes, Workbook W0-W2 artifacts/evidence/scripts/tests, generated workbook outputs, and unrelated run evidence from earlier sessions.

**Selected claim envelope classification:** the monitored foundations claim remains **Agentic Research Foundations promote / close**, provisionally scoreable with R5 fenced but not durable. Current visible follow-on work remains **Workbook Research Products W0-W2**; the story SSOT still states `W0-W2 done; W3 next`.

**BMAD gate/story visibility:** no new `bmad-code-review`, close-party concurrence, commit, or push evidence appeared. The foundations story SSOT/promote letter remain the visible close claim; Workbook Research Products retains its own party greenlight and W0-W2 story records. No W3 story completion or W4 live Tejal arm evidence is visible.

**Test / validation visibility:** latest evidence directory remains Workbook W2 at `_bmad-output/implementation-artifacts/evidence/workbook-w2-20260711T005835Z/`, with W2 proof already captured in SOP-R006. No evidence directory newer than W2 appeared in this poll. Foundations latest evidence remains R7/R6/R5-fenced as recorded in SOP-R004.

**Implementation visibility:** no new scoreable implementation slice is visible beyond foundations R1-R7 and successor Workbook W0-W2. W3 trends/hot-topics backmatter and W4 live Tejal workbook arm remain pending per story SSOT.

**Scoreability:** Agentic Research Foundations remains **provisionally scoreable at evidence/artifact level with explicit R5 fence**, but **not durable branch-scoreable** because review/commit/push/close concurrence are still absent. Workbook W0-W2 remain separately provisionally scoreable as dirty-worktree successor slices. W3/W4 are not scoreable.

**Findings / cautions:**
**F-R-0036 [P1] No durability transition.** HEAD remains `d1effcfa`; no review, close-party concurrence, commit, or push evidence appeared.
**F-R-0037 [P1] Successor work remains stacked on an uncommitted foundations base.** Workbook W0-W2 continue to depend on dirty foundations work that has not crossed review/commit gates.
**F-R-0038 [P2] No fresh validation evidence since W2.** Latest evidence remains Workbook W2 at 20:58 local; W3/W4 have not produced live proof.
**F-R-0039 [P2] Claim separation remains important.** Foundations close, R5 fence acceptance, Workbook W0-W2, and pending W3/W4 should be scored as distinct claims rather than collapsed into a broad "research capability done" statement.

**Residual fencing:** foundations code review, final party concurrence beyond orchestrator close, commit/push, R5 live upgrade after Chrome quit / SSO-cookie availability, semantic claim-source audit, Epic 17 related-resources/inline/hypothesis modes, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, OpenAlex/ERIC/LoC adapters, Workbook W3/W4 trends/live Tejal arm, novel HAI/PHS ingestion, and any claim that G2 has become semantic claim-support.

**Verdict:** No material research-mini-epic progress since SOP-R006. Foundations remain provisionally scoreable with R5 fenced but not durable; successor Workbook Research Products remains at W0-W2 done with W3 next.

---
### SOP-R008 - Second no-change poll after W2; review and W3 still absent - 2026-07-10T21:34:16-04:00

**Scope reviewed:** research monitor ledger through SOP-R007, current `git status --short --branch --untracked-files=all`, local git log, latest evidence directory timestamps, Workbook Research Products story SSOT, exact searches for W3/trends/hot-topics artifacts, and searches for visible research review/close artifacts. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). No new commit is visible since SOP-R007. Branch HEAD still durably contains only the R0 opening commit for this mini-epic.

**Worktree state:** broad dirty state persists with no visible narrowing or commit boundary. Tracked modifications remain across MCP config, foundations artifacts, Marcus research/orchestration code, workbook producer surfaces, Texas retrieval providers, Tracy bridge/posture dispatcher, and tests. Untracked files still include Agentic Research Foundations promote/monitor artifacts, R1-R7 evidence/scripts/tests, Jefferson probes/provider, Workbook W0-W2 artifacts/evidence/scripts/tests, generated workbook outputs, and unrelated run evidence from earlier sessions.

**Selected claim envelope classification:** monitored claim remains **Agentic Research Foundations promote / close**, provisionally scoreable with explicit R5 fence but not durable. Follow-on work remains **Workbook Research Products W0-W2**. The story SSOT still states `W0-W2 done; W3 next`.

**BMAD gate/story visibility:** no new `bmad-code-review`, close-party concurrence, commit, or push evidence appeared. Exact searches did not find research review/close artifacts. Workbook W3 remains specified but not marked done, and W4 remains future work.

**Test / validation visibility:** latest evidence directory remains `_bmad-output/implementation-artifacts/evidence/workbook-w2-20260711T005835Z/`; no newer evidence directory appeared. Exact W3/trends/hot-topics evidence searches returned no scoreable W3 artifacts. Foundations latest evidence remains R7/R6/R5-fenced, unchanged from SOP-R004.

**Implementation visibility:** no new scoreable implementation slice is visible beyond foundations R1-R7 and successor Workbook W0-W2. No W3 trends/hot-topics implementation script/test/evidence was found by exact-name search.

**Scoreability:** Agentic Research Foundations remains **provisionally scoreable at evidence/artifact level with explicit R5 fence**, but **not durable branch-scoreable** because review/commit/push/close concurrence remain absent. Workbook W0-W2 remain separately provisionally scoreable as dirty-worktree successor slices. W3/W4 are still not scoreable.

**Findings / cautions:**
**F-R-0040 [P1] Durability gap persists.** HEAD remains `d1effcfa`; no review, close-party concurrence, commit, or push evidence appeared.
**F-R-0041 [P1] No fresh scoreable slice since W2.** W3/trends/hot-topics searches found no evidence or implementation artifact that can be scored.
**F-R-0042 [P2] Dirty stack remains broad and layered.** Foundations and Workbook W0-W2 are still interleaved in a single uncommitted worktree, increasing review and claim-separation risk.
**F-R-0043 [P2] Latest validation is aging.** The latest evidence remains W2 at 20:58 local; this poll adds no new validation transcript.

**Residual fencing:** foundations code review, final party concurrence beyond orchestrator close, commit/push, R5 live upgrade after Chrome quit / SSO-cookie availability, semantic claim-source audit, Epic 17 related-resources/inline/hypothesis modes, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, OpenAlex/ERIC/LoC adapters, Workbook W3/W4 trends/live Tejal arm, novel HAI/PHS ingestion, and any claim that G2 has become semantic claim-support.

**Verdict:** No material research-mini-epic progress since SOP-R007. Foundations remain provisionally scoreable with R5 fenced but not durable; successor Workbook Research Products remains at W0-W2 done with W3 next and no fresh W3 evidence.

---
### SOP-R009 - Loose trends artifacts visible, but no W3 evidence or durability gate - 2026-07-10T21:49:15-04:00

**Scope reviewed:** research monitor ledger through SOP-R008, current `git status --short --branch --untracked-files=all`, local git log, latest evidence directory timestamps, Workbook Research Products story SSOT, exact searches for W3/trends/hot-topics artifacts, and searches for visible research review/close artifacts. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). No new commit is visible since SOP-R008. Branch HEAD still durably contains only the R0 opening commit for this mini-epic.

**Worktree state:** broad dirty state persists. The tracked dirty surface remains unchanged in kind: MCP config, foundations artifacts, Marcus research/orchestration code, workbook producer surfaces, Texas retrieval providers, Tracy bridge/posture dispatcher, and tests. Untracked files still include Agentic Research Foundations promote/monitor artifacts, R1-R7 evidence/scripts/tests, Jefferson probes/provider, Workbook W0-W2 artifacts/evidence/scripts/tests, generated workbook outputs, and earlier run evidence.

**Selected claim envelope classification:** monitored claim remains **Agentic Research Foundations promote / close**, provisionally scoreable with explicit R5 fence but not durable. Follow-on work remains **Workbook Research Products W0-W2**. The story SSOT still states `W0-W2 done; W3 next`.

**BMAD gate/story visibility:** no new `bmad-code-review`, close-party concurrence, commit, or push evidence appeared. Exact review/close searches returned no scoreable research review or close artifacts. Workbook W3 remains specified but not marked done, and W4 remains future work.

**Test / validation visibility:** latest evidence directory remains `_bmad-output/implementation-artifacts/evidence/workbook-w2-20260711T005835Z/`; no newer evidence directory appeared. No `workbook-w3*` evidence pack was found. Standalone generated trends files are visible at `_bmad-output/artifacts/workbooks-test/tejal-apc-c1-m1-p2-trends@1.md` / `.docx` with timestamps around 20:57 local, but they are not accompanied by W3 story completion, W3 evidence, a W3 test transcript, or a review gate. This monitor therefore does not count them as W3 scoreable evidence.

**Implementation visibility:** no new scoreable implementation slice is visible beyond foundations R1-R7 and successor Workbook W0-W2. No W3 trends/hot-topics implementation script/test/evidence was found that satisfies the W3 ACs.

**Scoreability:** Agentic Research Foundations remains **provisionally scoreable at evidence/artifact level with explicit R5 fence**, but **not durable branch-scoreable** because review/commit/push/close concurrence remain absent. Workbook W0-W2 remain separately provisionally scoreable as dirty-worktree successor slices. W3/W4 remain not scoreable.

**Findings / cautions:**
**F-R-0044 [P1] Durability gap persists.** HEAD remains `d1effcfa`; no review, close-party concurrence, commit, or push evidence appeared.
**F-R-0045 [P1] W3 is not scoreable despite loose trends outputs.** Generated trends workbook files exist, but there is no W3 evidence pack, story completion, RED/hermetic record, or live trends witness.
**F-R-0046 [P2] Latest formal validation remains W2.** The newest evidence pack remains Workbook W2 at 20:58 local; this poll adds no formal validation transcript.
**F-R-0047 [P2] Claim separation remains necessary.** Foundations, R5 fence acceptance, Workbook W0-W2, loose trends outputs, and pending W3/W4 should remain distinct in any close report.

**Residual fencing:** foundations code review, final party concurrence beyond orchestrator close, commit/push, R5 live upgrade after Chrome quit / SSO-cookie availability, semantic claim-source audit, Epic 17 related-resources/inline/hypothesis modes, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, OpenAlex/ERIC/LoC adapters, Workbook W3/W4 trends/live Tejal arm, novel HAI/PHS ingestion, and any claim that G2 has become semantic claim-support.

**Verdict:** No material scoreable progress since SOP-R008. Foundations remain provisionally scoreable with R5 fenced but not durable; successor Workbook Research Products remains formally at W0-W2 done with W3 next. Loose trends outputs are visible but are not W3-complete evidence.

---
### SOP-R010 - No change after loose trends output; W3 and durability remain open - 2026-07-10T22:04:16-04:00

**Scope reviewed:** research monitor ledger through SOP-R009, current `git status --short --branch --untracked-files=all`, local git log, latest evidence directory timestamps, Workbook Research Products story SSOT, W3/trends/hot-topics artifact search, and searches for visible research review/close artifacts. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). No new commit is visible since SOP-R009. Branch HEAD still durably contains only the R0 opening commit for this mini-epic.

**Worktree state:** broad dirty state persists with the same visible shape as SOP-R009. Tracked modifications remain across MCP config, foundations artifacts, Marcus research/orchestration code, workbook producer surfaces, Texas retrieval providers, Tracy bridge/posture dispatcher, and tests. Untracked files still include Agentic Research Foundations promote/monitor artifacts, R1-R7 evidence/scripts/tests, Jefferson probes/provider, Workbook W0-W2 artifacts/evidence/scripts/tests, generated workbook outputs, and earlier run evidence.

**Selected claim envelope classification:** monitored claim remains **Agentic Research Foundations promote / close**, provisionally scoreable with explicit R5 fence but not durable. Follow-on work remains **Workbook Research Products W0-W2**. The story SSOT still states `W0-W2 done; W3 next`.

**BMAD gate/story visibility:** no new `bmad-code-review`, close-party concurrence, commit, or push evidence appeared. Review/close artifact search returned no scoreable research review or close documents. Workbook W3 remains specified but not marked done; W4 remains future work.

**Test / validation visibility:** latest evidence directory remains `_bmad-output/implementation-artifacts/evidence/workbook-w2-20260711T005835Z/`; no newer evidence directory appeared. No `workbook-w3*` evidence pack was found. The standalone trends workbook files at `_bmad-output/artifacts/workbooks-test/tejal-apc-c1-m1-p2-trends@1.md` / `.docx` remain the only trend-named new outputs; they still lack W3 story completion, RED/hermetic record, live trends proof, and review gate. This monitor continues to treat them as loose output, not W3 evidence.

**Implementation visibility:** no new scoreable implementation slice is visible beyond foundations R1-R7 and successor Workbook W0-W2. No W3 trends/hot-topics implementation script/test/evidence satisfying W3 ACs was found.

**Scoreability:** Agentic Research Foundations remains **provisionally scoreable at evidence/artifact level with explicit R5 fence**, but **not durable branch-scoreable** because review/commit/push/close concurrence remain absent. Workbook W0-W2 remain separately provisionally scoreable as dirty-worktree successor slices. W3/W4 remain not scoreable.

**Findings / cautions:**
**F-R-0048 [P1] Durability gap persists.** HEAD remains `d1effcfa`; no review, close-party concurrence, commit, or push evidence appeared.
**F-R-0049 [P1] W3 remains open.** Trends outputs are visible, but no W3 evidence pack, story completion, hermetic/RED record, or live cited-trends witness exists.
**F-R-0050 [P2] Latest formal validation remains W2.** The newest evidence pack remains Workbook W2 at 20:58 local; this poll adds no new formal validation transcript.
**F-R-0051 [P2] Dirty stack still mixes claims.** Foundations, Workbook W0-W2, and loose trends outputs remain interleaved in one uncommitted worktree, so final scoring must separate them.

**Residual fencing:** foundations code review, final party concurrence beyond orchestrator close, commit/push, R5 live upgrade after Chrome quit / SSO-cookie availability, semantic claim-source audit, Epic 17 related-resources/inline/hypothesis modes, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, OpenAlex/ERIC/LoC adapters, Workbook W3/W4 trends/live Tejal arm, novel HAI/PHS ingestion, and any claim that G2 has become semantic claim-support.

**Verdict:** No material scoreable progress since SOP-R009. Foundations remain provisionally scoreable with R5 fenced but not durable; successor Workbook Research Products remains formally at W0-W2 done with W3 next. Loose trends outputs remain non-scoreable without a W3 evidence pack and story close.

---
### SOP-R011 - Workbook W3/W4 evidence and close appear; foundations still not durable - 2026-07-10T22:19:19-04:00

**Scope reviewed:** research monitor ledger through SOP-R010, current `git status --short --branch --untracked-files=all`, local git log, latest evidence directory timestamps, Workbook Research Products story SSOT, W3/W4 proof files, W4 consumer matrix, workbook close/promote letter, and review/close artifact visibility. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). No new commit is visible since SOP-R010. Branch HEAD still durably contains only the R0 opening commit for this mini-epic.

**Worktree state:** dirty worktree expanded materially since SOP-R010. In addition to the foundations R1-R7 and Workbook W0-W2 dirty surfaces, new untracked successor-work artifacts are visible: `app/marcus/lesson_plan/trends_projection.py`, `scripts/utilities/run_workbook_w3_live_evidence.py`, `scripts/utilities/run_workbook_w4_live_evidence.py`, `tests/unit/marcus/lesson_plan/test_trends_w3.py`, `tests/unit/marcus/lesson_plan/test_workbook_w4_empty_honesty.py`, evidence packs `workbook-w3-20260711T021204Z` and `workbook-w4-20260711T021418Z`, and `_bmad-output/implementation-artifacts/workbook-research-products-close-2026-07-10.md`.

**Selected claim envelope classification:** monitored parent claim remains **Agentic Research Foundations promote / close**, provisionally scoreable with explicit R5 fence but not durable. Follow-on work has advanced from **Workbook Research Products W0-W2** to **Workbook Research Products W0-W4 close**, with its own close letter. This is successor evidence and should remain distinct from foundations durability.

**BMAD gate/story visibility:** Workbook Research Products story SSOT now states **W0-W4 done / mini-epic CLOSED** and points to `workbook-research-products-close-2026-07-10.md`. The close letter claims W0-W4 delivered with hermetic + live evidence and detective default OFF. This poll still did not find a committed branch state or a separate code-review artifact for the combined foundations/workbook dirty stack. Foundations still have no new final party concurrence beyond the prior promote/orchestrator close.

**Test / validation visibility:** latest evidence is now successor workbook evidence:
- W3 proof `_bmad-output/implementation-artifacts/evidence/workbook-w3-20260711T021204Z/PROOF.md` records `pass=True`, `trends=5`, `hot topics=3`, one unusable injected model-prior item, and PASS for non-vacuous trends, bounded provenance, model-prior rejection, compose placement, and MD/DOCX same-model G2 clean.
- W4 proof `_bmad-output/implementation-artifacts/evidence/workbook-w4-20260711T021418Z/PROOF.md` records `pass=True`, trial `714013d0-7321-4f09-af14-c1e05b2bdbc7`, narrow Tejal research-to-glossary+trends claim, detective OFF, and PASS for Murat glossary/trends/consumer-matrix witnesses, MD/DOCX parity/G2, empty-honesty, and dual-consumer digest.
- W4 `consumer-matrix.json` records five PASS rows: glossary writer, trends projector, Irene intake, SPOC receipt, and future collateral, all sharing digest `17d56b0c0a8792194fed333a351fae6f71db67fa3ea56b77f3b28029ec9544eb`.

This monitor did not rerun hermetic tests and relies on the visible proof packs/story SSOT for test visibility.

**Implementation visibility:** W3 implementation is now visible via `trends_projection.py`, workbook producer / `_act.py` wiring already in the dirty tracked surface, W3/W4 scripts, and W3/W4 tests. This makes Workbook Research Products W0-W4 **provisionally scoreable at artifact/evidence level**. It remains uncommitted and not review-durable.

**Scoreability:** Agentic Research Foundations remains **provisionally scoreable at evidence/artifact level with explicit R5 fence**, but **not durable branch-scoreable** because review/commit/push/final close concurrence remain absent. Workbook Research Products W0-W4 is now **provisionally scoreable as a successor mini-epic close** with W3/W4 evidence and close letter visible, but it is also **not durable branch-scoreable** because the work remains uncommitted and no review artifact is visible.

**Findings / cautions:**
**F-R-0052 [P1] Workbook W0-W4 close appeared but is dirty-worktree only.** W3/W4 evidence and the workbook close letter are substantial, but HEAD remains `d1effcfa` with no commit/push.
**F-R-0053 [P1] Foundations durability gap persists.** The parent Agentic Research Foundations claim is still not durable despite successor workbook close evidence.
**F-R-0054 [P1] Review remains load-bearing.** The dirty stack now spans foundations R1-R7 plus Workbook W0-W4, including workbook production output changes and research detective seams; a code review should separate parent and successor claims.
**F-R-0055 [P2] W4 is narrow Tejal proof, not broad semantic audit.** The close letter correctly fences semantic claim-source audit to TRAIL; do not overclaim G2 as semantic source faithfulness.
**F-R-0056 [P2] R5 remains fenced.** The Jefferson live-upgrade fence still applies to the parent foundations claim.

**Residual fencing:** foundations code review, final party concurrence beyond orchestrator close, commit/push, R5 live upgrade after Chrome quit / SSO-cookie availability, semantic claim-source audit, Epic 17 related-resources/inline/hypothesis modes, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, OpenAlex/ERIC/LoC adapters, SME glossary writer replacing `GLOSSARY-WRITER-REQUIRED`, novel HAI/PHS ingestion, and any claim that G2 has become semantic claim-support.

**Verdict:** Material successor progress since SOP-R010. Workbook Research Products W3/W4 evidence and a close letter are now visible, making W0-W4 provisionally scoreable as a successor mini-epic close. The parent Agentic Research Foundations claim remains only provisionally scoreable with R5 fenced and still not durable; no commit, push, or review boundary is visible.

---
### SOP-R012 - Post-W4 close poll: no commit or review durability yet - 2026-07-10T22:34:19-04:00

**Scope reviewed:** research monitor ledger through SOP-R011, current `git status --short --branch --untracked-files=all`, local git log, latest evidence directory timestamps, Agentic Research Foundations story SSOT, Workbook Research Products story SSOT, and review/close visibility. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). No new commit is visible since SOP-R011. Branch HEAD still durably contains only the R0 opening commit for this mini-epic.

**Worktree state:** broad dirty state persists. The visible dirty surface still includes foundations R1-R7/promote work, Workbook W0-W4 successor work, W3/W4 evidence packs, workbook close letter, production code changes, tests, scripts, generated workbook outputs, and earlier unrelated run/evidence files. No narrowing, staging boundary, commit boundary, or push evidence is visible.

**Selected claim envelope classification:** parent monitored claim remains **Agentic Research Foundations promote / close**, provisionally scoreable with explicit R5 fence but not durable. Successor claim remains **Workbook Research Products W0-W4 close**, provisionally scoreable with W3/W4 live evidence and close letter, but not durable.

**BMAD gate/story visibility:** Agentic Research Foundations story SSOT still states **R0-R7 + promote done** and next equals workbook research products. Workbook Research Products story SSOT still states **W0-W4 done / mini-epic CLOSED** with close letter `workbook-research-products-close-2026-07-10.md`. This poll did not find a new code-review artifact, new party-close record beyond the workbook close letter, commit, or push.

**Test / validation visibility:** no evidence directory newer than `_bmad-output/implementation-artifacts/evidence/workbook-w4-20260711T021418Z/` appeared. Latest formal evidence remains W4 PASS, preceded by W3 PASS. Foundations latest evidence remains R7/R6/R5-fenced as recorded earlier. This monitor did not rerun hermetic tests.

**Implementation visibility:** no new implementation slice is visible beyond the already observed foundations R1-R7 and Workbook W0-W4 surfaces. W3/W4 remain visible through `trends_projection.py`, W3/W4 scripts/tests, workbook producer wiring, and W3/W4 proof packs.

**Scoreability:** Agentic Research Foundations remains **provisionally scoreable at evidence/artifact level with explicit R5 fence**, but **not durable branch-scoreable** because review/commit/push/final close concurrence remain absent. Workbook Research Products W0-W4 remains **provisionally scoreable as a successor mini-epic close**, but also **not durable branch-scoreable** because the work remains uncommitted and no review artifact is visible.

**Findings / cautions:**
**F-R-0057 [P1] No durability movement after W4 close.** HEAD remains `d1effcfa`; no commit, push, or review gate appeared after W4.
**F-R-0058 [P1] Dirty stack now contains two scoreable-but-undurable claims.** Parent foundations and successor workbook products are both evidence-backed, but both remain dirty-worktree only.
**F-R-0059 [P1] Review remains mandatory before broad close.** The combined surface includes research retrieval/provider seams, hard-pause behavior, workbook projection/rendering, and tests; review should explicitly separate parent and successor claims.
**F-R-0060 [P2] Latest formal proof remains W4.** No post-close regression or review transcript is visible in this poll.

**Residual fencing:** foundations code review, final party concurrence beyond orchestrator close, commit/push, R5 live upgrade after Chrome quit / SSO-cookie availability, semantic claim-source audit, Epic 17 related-resources/inline/hypothesis modes, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, OpenAlex/ERIC/LoC adapters, SME glossary writer replacing `GLOSSARY-WRITER-REQUIRED`, novel HAI/PHS ingestion, and any claim that G2 has become semantic claim-support.

**Verdict:** No material durability progress since SOP-R011. Workbook Research Products remains provisionally scoreable as W0-W4 closed with W3/W4 evidence; Agentic Research Foundations remains provisionally scoreable with R5 fenced. Neither claim is durable yet because no commit, push, or review boundary is visible.

---
### SOP-R013 - TRAIL trio closes with OpenAlex live proof; stack still uncommitted - 2026-07-10T22:49:19-04:00

**Scope reviewed:** research monitor ledger through SOP-R012, current `git status --short --branch --untracked-files=all`, local git log, latest evidence directory timestamps, OpenAlex live proof, TRAIL trio greenlight/close artifacts, TRAIL trio close letter, and review artifact visibility. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`, at `d1effcfa` (`feat(research): open Agentic Research Foundations mini-epic (R0 done)`). No new commit is visible since SOP-R012. Branch HEAD still durably contains only the R0 opening commit for this mini-epic.

**Worktree state:** dirty worktree expanded again. New visible TRAIL trio surfaces include `skills/bmad-agent-texas/scripts/retrieval/openalex_provider.py`, `scripts/utilities/run_openalex_live_evidence.py`, `tests/unit/retrieval/test_openalex_provider.py`, changes to `app/specialists/_shared/source_fidelity_audit.py` and its tests, OpenAlex live evidence `openalex-live-20260711T024437Z`, `_bmad-output/implementation-artifacts/trail-trio-close-2026-07-10.md`, and party greenlight/close artifacts under `_bmad-output/planning-artifacts/`. The stack still also contains foundations R1-R7/promote work and Workbook W0-W4 successor work. No staging, commit, push, or review boundary is visible.

**Selected claim envelope classification:** parent monitored claim remains **Agentic Research Foundations promote / close**, provisionally scoreable with explicit R5 fence but not durable. Successor claim remains **Workbook Research Products W0-W4 close**, provisionally scoreable but not durable. New activity is **TRAIL trio close**: OpenAlex adapter, glossary SME polish, and WARN-only semantic tripwire substrate.

**BMAD gate/story visibility:** TRAIL trio party greenlight records 4/4 GO-WITH-AMENDMENTS from John/Winston/Amelia/Murat. TRAIL trio party close records 4/4 CLOSE-WITH-AMENDMENTS, with a folded Amelia MUST that OpenAlex not map `is_oa` to peer-reviewed authority tier. The TRAIL trio close letter claims the trio is closed under fences. This poll still found no `bmad-code-review` / review artifact and no commit or push.

**Test / validation visibility:** latest evidence is now `_bmad-output/implementation-artifacts/evidence/openalex-live-20260711T024437Z/`. Its proof records `pass=True`, positive DOI `10.1038/s41586-020-2649-2` returning one row with OA link discovery, and negative DOI `10.9999/this-doi-does-not-exist-openalex-trail-2026` returning zero rows. The close letter reports OpenAlex hermetic 5/5; glossary SME polish hermetic pins; and semantic WARN tripwire hermetic warn/skip/overlap pins. This monitor did not rerun those tests and found no live proof for glossary/semantic beyond the stated hermetic scope.

**Implementation visibility:** OpenAlex implementation is visible via provider/script/test artifacts. Glossary polish and semantic tripwire are visible through modifications to `glossary_projection.py`, `source_fidelity_audit.py`, and related tests. TRAIL trio is **provisionally scoreable at artifact/evidence level** under its explicit fences: OpenAlex DOI metadata/OA links only, glossary research-informed stub/capability note only, semantic WARN-only heuristic only.

**Scoreability:** Agentic Research Foundations remains **provisionally scoreable at evidence/artifact level with explicit R5 fence**, but **not durable branch-scoreable**. Workbook Research Products W0-W4 remains **provisionally scoreable as a successor mini-epic close**, but **not durable branch-scoreable**. TRAIL trio is now **provisionally scoreable at artifact/evidence level** with OpenAlex live proof and party close, but also **not durable branch-scoreable** because the work remains uncommitted and no review artifact is visible.

**Findings / cautions:**
**F-R-0061 [P1] Third evidence-backed claim added without commit durability.** TRAIL trio now joins foundations and workbook close as scoreable-but-undurable work on the same dirty branch.
**F-R-0062 [P1] Review artifact still absent.** No code-review/review artifact was found for the expanded stack, which now includes OpenAlex provider, semantic tripwire, workbook projections, and hard-pause/research seams.
**F-R-0063 [P1] OpenAlex claim must stay narrow.** The live proof supports DOI metadata and OA link discovery only; it does not support PDF download, institutional SSO, arbiter scoring, or semantic validation.
**F-R-0064 [P2] Semantic tripwire is WARN-only.** The close letter correctly states `gates_production=False`; do not report it as full semantic claim-source audit or production gate.
**F-R-0065 [P2] Latest formal proof is OpenAlex only.** Glossary polish and semantic tripwire are represented as hermetic/pinned close evidence, not live evidence.

**Residual fencing:** commit/push, full code review, final branch-level close across the combined stack, R5 live upgrade after Chrome quit / SSO-cookie availability, full semantic claim-source audit calibration across multiple workbook runs, Epic 17 related-resources/inline/hypothesis modes, ERIC / LoC adapters, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, novel HAI/PHS ingestion, and any claim that G2 or the WARN tripwire has become semantic claim-support.

**Verdict:** Material artifact-level progress since SOP-R012. TRAIL trio has party close and OpenAlex live proof, so it is provisionally scoreable under tight claim fences. The branch remains not durable: no commit, push, or review boundary is visible, and the dirty stack now contains three scoreable-but-undurable claims.

---
### SOP-R014 - Research stack committed and pushed; review artifact still absent - 2026-07-10T23:04:18-04:00

**Scope reviewed:** research monitor ledger through SOP-R013, current `git status --short --branch --untracked-files=all`, local git log, commit stats for `3231dd43` and `3b88dd1e`, latest evidence directory timestamps, `SESSION-HANDOFF.md`, and review artifact searches. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`. HEAD has advanced and matches origin at `3b88dd1e` (`docs(session): pin research WRAPUP push SHA in SESSION-HANDOFF`), with prior close commit `3231dd43` (`feat(research): close foundations, workbook products, and TRAIL trio`). This is the first poll where commit/push durability is visible for the research stack.

**Worktree state:** the large research/workbook/TRAIL implementation stack is no longer dirty; it is contained in `3231dd43` plus wrap-up `3b88dd1e`. Remaining dirty/untracked items appear ambient/local and outside the research close surface: `.cursor/mcp.json`, `.mcp.json`, prior batch monitor ledger modification, workbooks-test outputs, prior product-gap monitor, regression scratch files, Irene literal proof leftovers, meeting transcript deconstruction files, and older `runs/*` artifacts. The current monitor append will make this ledger dirty again after this poll.

**Selected claim envelope classification:** parent monitored claim remains **Agentic Research Foundations promote / close** with explicit R5 fence; successor **Workbook Research Products W0-W4 close** is committed; and **TRAIL trio close** is committed. All three claims now have commit/push durability at branch level. They remain distinct claim envelopes and must not be collapsed into a single broad "semantic research solved" claim.

**BMAD gate/story visibility:** `SESSION-HANDOFF.md` records Research Foundations + Workbook Products + TRAIL trio CLOSED as Class S and says working-branch push was mandatory/done. It lists Step 0a/0b/0c skipped because Cora/`/harmonize` is unregistered, Step 1 ruff/focused suite green on TRAIL touchpaths, sprint-status update green, docs/current snapshot updated, and KG/ONBOARDING regeneration recommended later. TRAIL party close was visible in SOP-R013. This poll still found no separate `bmad-code-review` / code-review artifact for the combined stack.

**Test / validation visibility:** latest formal evidence remains `openalex-live-20260711T024437Z`, followed by Workbook W4/W3 and foundations R7/R6/R5-fenced. `SESSION-HANDOFF.md` summarizes validation as ruff cleaned on TRAIL touchpaths, focused suite green for OpenAlex + glossary W2 + source fidelity audit + sprint-status yaml, and `tests/test_sprint_status_yaml.py` green. This monitor did not rerun tests and did not find a separate test transcript beyond committed evidence packs and the handoff summary.

**Implementation visibility:** commit `3231dd43` is broad: 159 files changed, including foundations R1-R7, workbook research packet/glossary/trends production surfaces, W1-W4 evidence/scripts/tests, OpenAlex provider/evidence, semantic WARN tripwire, source-fidelity tests, docs, sprint/deferred inventory, and close artifacts. `3b88dd1e` pins the wrap-up SHA in `SESSION-HANDOFF.md`.

**Scoreability:** Agentic Research Foundations is now **branch-durable and provisionally scoreable with explicit R5 fence**. Workbook Research Products W0-W4 is now **branch-durable and scoreable as a successor mini-epic close**. TRAIL trio is now **branch-durable and scoreable under tight fences**: OpenAlex DOI metadata/OA link discovery, glossary capability-note polish, and semantic WARN-only tripwire substrate. The remaining review gap means this monitor does not mark the combined stack as independently review-durable.

**Findings / cautions:**
**F-R-0066 [P1] Commit/push durability landed.** The research/workbook/TRAIL stack is committed at `3231dd43` and pushed, with wrap-up at `3b88dd1e`.
**F-R-0067 [P1] Separate code-review artifact still absent.** I found party close/WRAPUP evidence but no dedicated code-review artifact for the 159-file close commit.
**F-R-0068 [P1] R5 remains an explicit fence.** Branch durability does not upgrade Jefferson institutional retrieval from fenced to live-proven.
**F-R-0069 [P2] Cora harmonize sweep was skipped.** Handoff records Step 0a/0b/0c skipped because Cora/`/harmonize` is unregistered, with a consecutive-skip tripwire.
**F-R-0070 [P2] Claim fences remain binding.** OpenAlex is metadata/OA links only; semantic tripwire is WARN-only; G2 is not semantic claim support; full semantic claim-source audit remains TRAIL.

**Residual fencing:** dedicated code-review artifact, R5 live upgrade after Chrome quit / SSO-cookie availability, full semantic claim-source audit calibration across multiple workbook runs, Epic 17 related-resources/inline/hypothesis modes, ERIC / LoC adapters, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, novel HAI/PHS ingestion, KG/ONBOARDING regeneration, and any claim that G2 or the WARN tripwire has become semantic claim-support.

**Verdict:** Material durability progress since SOP-R013. The research foundations, workbook products, and TRAIL trio stack is now committed and pushed on the research branch. It is branch-durable and scoreable under its named fences, but the absence of a dedicated code-review artifact remains the main governance caution.

---
### SOP-R015 - Stable pushed close; no review artifact or new evidence - 2026-07-10T23:19:21-04:00

**Scope reviewed:** research monitor ledger through SOP-R014, current `git status --short --branch --untracked-files=all`, local git log, latest evidence directory timestamps, review artifact searches, and current dirty-file list. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`. HEAD remains `3b88dd1e` (`docs(session): pin research WRAPUP push SHA in SESSION-HANDOFF`), with the main research close at `3231dd43` (`feat(research): close foundations, workbook products, and TRAIL trio`). No new commit is visible since SOP-R014.

**Worktree state:** the committed research/workbook/TRAIL stack remains branch-durable. Current tracked dirty files are limited to local MCP config, this research monitor ledger, and the older batch monitor ledger: `.cursor/mcp.json`, `.mcp.json`, `_bmad-output/implementation-artifacts/codex-shadow-monitor-agentic-research-foundations-2026-07-10.md`, and `_bmad-output/implementation-artifacts/codex-shadow-monitor-batch-mode-2026-07-10.md`. Untracked ambient artifacts remain visible, including workbooks-test outputs, prior product-gap monitor, regression scratch files, Irene literal proof leftovers, meeting transcript deconstruction files, and older `runs/*` artifacts. No newly dirty production/test research code is visible after the pushed close.

**Selected claim envelope classification:** parent **Agentic Research Foundations promote / close**, successor **Workbook Research Products W0-W4 close**, and **TRAIL trio close** remain branch-durable and scoreable under their named fences. The envelopes remain distinct: R5 is fenced, Workbook W4 is narrow Tejal proof, OpenAlex is metadata/OA-link discovery only, and semantic tripwire is WARN-only.

**BMAD gate/story visibility:** no new BMAD gate appeared after the WRAPUP handoff recorded in SOP-R014. Review artifact searches again found no dedicated `bmad-code-review` / code-review artifact for the combined 159-file close commit. Existing visible gates remain the story SSOTs, workbook close letter, TRAIL party greenlight/close, TRAIL close letter, and `SESSION-HANDOFF.md`.

**Test / validation visibility:** no evidence directory newer than `_bmad-output/implementation-artifacts/evidence/openalex-live-20260711T024437Z/` appeared. Latest formal evidence remains OpenAlex LIVE, followed by Workbook W4/W3 and foundations R7/R6/R5-fenced. This monitor did not rerun tests and found no new test transcript beyond committed evidence and handoff summaries.

**Implementation visibility:** no new implementation surface appeared since SOP-R014. The scoreable implementation remains the committed `3231dd43` stack plus the WRAPUP SHA pin at `3b88dd1e`.

**Scoreability:** Agentic Research Foundations remains **branch-durable and provisionally scoreable with explicit R5 fence**. Workbook Research Products W0-W4 remains **branch-durable and scoreable as a successor mini-epic close**. TRAIL trio remains **branch-durable and scoreable under tight fences**. The combined stack is still not independently review-durable because no dedicated review artifact is visible.

**Findings / cautions:**
**F-R-0071 [P1] Stable branch durability, but no review artifact.** HEAD remains pushed at `3b88dd1e`; no separate code-review artifact appeared.
**F-R-0072 [P2] No fresh validation after OpenAlex.** Latest evidence remains `openalex-live-20260711T024437Z`; no post-WRAPUP regression transcript is visible.
**F-R-0073 [P2] Remaining dirty files are ambient/monitor-local.** Research production/test implementation is not dirty in this poll; current tracked dirt is local config and monitor ledgers.
**F-R-0074 [P2] Claim fences remain binding.** R5 fenced, OpenAlex narrow, semantic WARN-only, and G2 not semantic support remain the key anti-overclaim constraints.

**Residual fencing:** dedicated code-review artifact, R5 live upgrade after Chrome quit / SSO-cookie availability, full semantic claim-source audit calibration across multiple workbook runs, Epic 17 related-resources/inline/hypothesis modes, ERIC / LoC adapters, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, novel HAI/PHS ingestion, KG/ONBOARDING regeneration, and any claim that G2 or the WARN tripwire has become semantic claim-support.

**Verdict:** No material change since SOP-R014. The research foundations, workbook products, and TRAIL trio stack remains committed, pushed, branch-durable, and scoreable under named fences. The only persistent governance caution is the absence of a dedicated code-review artifact.

---
### SOP-R016 - Docs and knowledge graph refresh pushed; review artifact still absent - 2026-07-10T23:34:27-04:00

**Scope reviewed:** research monitor ledger through SOP-R015, current `git status --short --branch --untracked-files=all`, local git log, commit stats for `5c08bcef`, latest evidence directory timestamps, and review artifact searches. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`. HEAD has advanced to `5c08bcef` (`docs(onboarding): refresh knowledge graph + ONBOARDING at 3b88dd1e (incremental) + fold research foundations into user/dev/admin guides`). The branch now contains the main close commit `3231dd43`, WRAPUP pin `3b88dd1e`, and the follow-on docs/onboarding commit `5c08bcef`, all visible on origin.

**Worktree state:** the committed research/workbook/TRAIL implementation stack remains branch-durable. The new `5c08bcef` commit updates `.understand-anything/fingerprints.json`, `.understand-anything/knowledge-graph.json`, `.understand-anything/meta.json`, `docs/ONBOARDING.md`, `docs/admin-guide.md`, `docs/dev-guide.md`, and `docs/user-guide.md`. Current remaining dirty/untracked state still appears ambient/monitor-local: local MCP config, this research monitor ledger, older batch monitor ledger, workbooks-test outputs, prior product-gap monitor, regression scratch files, Irene literal proof leftovers, meeting transcript deconstruction files, and older `runs/*` artifacts. No newly dirty production/test research code is visible.

**Selected claim envelope classification:** parent **Agentic Research Foundations promote / close**, successor **Workbook Research Products W0-W4 close**, and **TRAIL trio close** remain branch-durable and scoreable under their named fences. The new docs/onboarding commit improves operator-facing and developer/admin discoverability but does not change the claim envelope or evidence bar.

**BMAD gate/story visibility:** no new BMAD gate appeared after the WRAPUP handoff and prior party close artifacts. Review artifact searches again found no dedicated `bmad-code-review` / code-review artifact for the combined close commit. Existing visible gates remain the story SSOTs, workbook close letter, TRAIL party greenlight/close, TRAIL close letter, `SESSION-HANDOFF.md`, and now updated user/dev/admin/onboarding documentation.

**Test / validation visibility:** no evidence directory newer than `_bmad-output/implementation-artifacts/evidence/openalex-live-20260711T024437Z/` appeared. Latest formal evidence remains OpenAlex LIVE, followed by Workbook W4/W3 and foundations R7/R6/R5-fenced. This monitor did not rerun tests and found no new test transcript beyond committed evidence and handoff summaries.

**Implementation visibility:** no new implementation surface appeared since SOP-R015. Scoreable implementation remains the committed `3231dd43` stack; `3b88dd1e` records WRAPUP push; `5c08bcef` records docs/onboarding/knowledge-graph refresh.

**Scoreability:** Agentic Research Foundations remains **branch-durable and provisionally scoreable with explicit R5 fence**. Workbook Research Products W0-W4 remains **branch-durable and scoreable as a successor mini-epic close**. TRAIL trio remains **branch-durable and scoreable under tight fences**. Documentation coverage is now improved and pushed. The combined stack is still not independently review-durable because no dedicated review artifact is visible.

**Findings / cautions:**
**F-R-0075 [P1] Documentation follow-through landed.** User/dev/admin guides, ONBOARDING, and knowledge graph were refreshed and pushed in `5c08bcef`.
**F-R-0076 [P1] Separate code-review artifact still absent.** The branch has party close, WRAPUP, and docs follow-through, but no dedicated review artifact for the 159-file implementation close commit.
**F-R-0077 [P2] No fresh formal evidence after OpenAlex.** Latest evidence remains `openalex-live-20260711T024437Z`; the new commit is documentation/knowledge graph, not new runtime proof.
**F-R-0078 [P2] Claim fences remain binding in docs and scoring.** R5 fenced, OpenAlex narrow, semantic WARN-only, and G2 not semantic support remain the key anti-overclaim constraints.

**Residual fencing:** dedicated code-review artifact, R5 live upgrade after Chrome quit / SSO-cookie availability, full semantic claim-source audit calibration across multiple workbook runs, Epic 17 related-resources/inline/hypothesis modes, ERIC / LoC adapters, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, novel HAI/PHS ingestion, and any claim that G2 or the WARN tripwire has become semantic claim-support.

**Verdict:** Material documentation progress since SOP-R015. The research foundations, workbook products, and TRAIL trio stack remains committed, pushed, branch-durable, and scoreable under named fences, and the user/dev/admin/onboarding docs are now refreshed. The persistent governance caution remains the absence of a dedicated code-review artifact.

---
### SOP-R017 - Stable after docs refresh; no new evidence or review artifact - 2026-07-10T23:49:29-04:00

**Scope reviewed:** research monitor ledger through SOP-R016, current `git status --short --branch --untracked-files=all`, local git log, latest evidence directory timestamps, review artifact searches, and the newly visible untracked technical research planning file under `_bmad-output/planning-artifacts/research/`. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`. HEAD remains `5c08bcef` (`docs(onboarding): refresh knowledge graph + ONBOARDING at 3b88dd1e (incremental) + fold research foundations into user/dev/admin guides`). No new commit is visible since SOP-R016. The branch still contains the close commit `3231dd43`, WRAPUP pin `3b88dd1e`, and docs/onboarding refresh `5c08bcef`, all visible on origin.

**Worktree state:** the committed research/workbook/TRAIL implementation stack remains branch-durable and is not newly dirty. Current tracked dirt remains local/monitor-adjacent: `.cursor/mcp.json`, `.mcp.json`, this research monitor ledger, and the older batch-mode monitor ledger. Ambient untracked artifacts remain visible. A new untracked planning artifact is visible at `_bmad-output/planning-artifacts/research/technical-latest-bmad-version-looping-feature-research-2026-07-10.md`; its current content is the generic research workflow scaffold with placeholder metadata, so this poll treats it as unscored planning residue rather than BMAD gate, implementation evidence, or liveproof.

**Selected claim envelope classification:** parent **Agentic Research Foundations promote / close**, successor **Workbook Research Products W0-W4 close**, and **TRAIL trio close** remain branch-durable and scoreable under their named fences. No claim envelope expansion is visible in this poll. The new untracked technical research scaffold does not alter the selected claim classification.

**BMAD gate/story visibility:** no new BMAD gate appeared after SOP-R016. Existing visible gates remain the story SSOTs, workbook close letter, TRAIL party greenlight/close, TRAIL close letter, `SESSION-HANDOFF.md`, and updated user/dev/admin/onboarding documentation. Review artifact searches again found no dedicated `bmad-code-review` / code-review artifact for the combined implementation close.

**Test / validation visibility:** no evidence directory newer than `_bmad-output/implementation-artifacts/evidence/openalex-live-20260711T024437Z/` appeared. Latest formal evidence remains OpenAlex LIVE, followed by Workbook W4/W3 and foundations R7/R6/R5-fenced. This monitor did not rerun tests and found no new test transcript beyond committed evidence and handoff summaries.

**Implementation visibility:** no new implementation surface appeared since SOP-R016. Scoreable implementation remains the committed `3231dd43` stack; `3b88dd1e` records WRAPUP push; `5c08bcef` records docs/onboarding/knowledge-graph refresh.

**Scoreability:** Agentic Research Foundations remains **branch-durable and provisionally scoreable with explicit R5 fence**. Workbook Research Products W0-W4 remains **branch-durable and scoreable as a successor mini-epic close**. TRAIL trio remains **branch-durable and scoreable under tight fences**. Documentation coverage remains pushed. The combined stack is still not independently review-durable because no dedicated review artifact is visible.

**Findings / cautions:**
**F-R-0079 [P1] No material change after docs refresh.** HEAD remains pushed at `5c08bcef`; no new implementation commit or evidence appeared after SOP-R016.
**F-R-0080 [P1] Separate code-review artifact still absent.** Party close, WRAPUP, evidence packs, and docs updates are visible, but no dedicated review artifact is visible for the 159-file implementation close.
**F-R-0081 [P2] New untracked research planning scaffold is not scoreable.** The newly visible technical research file is placeholder/template-like and should not be counted as a gate, story, validation proof, or claim expansion unless later bound by BMAD artifacts and evidence.
**F-R-0082 [P2] Claim fences remain binding.** R5 fenced, OpenAlex narrow, semantic WARN-only, and G2 not semantic support remain the key anti-overclaim constraints.

**Residual fencing:** dedicated code-review artifact, R5 live upgrade after Chrome quit / SSO-cookie availability, full semantic claim-source audit calibration across multiple workbook runs, Epic 17 related-resources/inline/hypothesis modes, ERIC / LoC adapters, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, novel HAI/PHS ingestion, and any claim that G2 or the WARN tripwire has become semantic claim-support.

**Verdict:** No material change since SOP-R016. The research foundations, workbook products, and TRAIL trio stack remains committed, pushed, branch-durable, and scoreable under named fences, with refreshed docs/onboarding also pushed. The persistent governance caution remains the absence of a dedicated code-review artifact; the new untracked technical research scaffold is not scoreable evidence.

---
### SOP-R018 - Stable branch; no post-close evidence or review boundary - 2026-07-11T00:04:29-04:00

**Scope reviewed:** research monitor ledger through SOP-R017, current `git status --short --branch --untracked-files=all`, local git log, latest evidence directory timestamps, implementation-artifact inventory, and review artifact searches. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `dev/agentic-research-foundations-2026-07-10`, tracking `origin/dev/agentic-research-foundations-2026-07-10`. HEAD remains `5c08bcef` (`docs(onboarding): refresh knowledge graph + ONBOARDING at 3b88dd1e (incremental) + fold research foundations into user/dev/admin guides`). No new commit is visible since SOP-R017. The branch still contains the close commit `3231dd43`, WRAPUP pin `3b88dd1e`, and docs/onboarding refresh `5c08bcef`, all visible on origin.

**Worktree state:** the committed research/workbook/TRAIL implementation stack remains branch-durable and is not newly dirty. Current tracked dirt remains local/monitor-adjacent: `.cursor/mcp.json`, `.mcp.json`, this research monitor ledger, and the older batch-mode monitor ledger. Untracked ambient artifacts remain visible, including workbooks-test outputs, prior product-gap monitor, regression scratch files, Irene literal proof leftovers, meeting transcript deconstruction files, older `runs/*` artifacts, and the untracked placeholder-like technical research scaffold under `_bmad-output/planning-artifacts/research/`. No newly dirty production/test research implementation file is visible.

**Selected claim envelope classification:** parent **Agentic Research Foundations promote / close**, successor **Workbook Research Products W0-W4 close**, and **TRAIL trio close** remain branch-durable and scoreable under their named fences. No claim envelope expansion is visible in this poll. The current untracked planning scaffold remains outside the scoreable claim envelope.

**BMAD gate/story visibility:** no new BMAD gate appeared after SOP-R017. Current visible research implementation artifacts remain `agentic-research-foundations-stories-2026-07-10.md`, `agentic-research-foundations-promote-2026-07-10.md`, `research-r0-charter-taxonomy-live-matrix-2026-07-10.md`, `research-r1-posture-runtime-2026-07-10.md`, `research-r2-consensus-evidence-bolster-2026-07-10.md`, `workbook-research-products-stories-2026-07-10.md`, `workbook-w0-charter-consumer-matrix-2026-07-10.md`, `workbook-research-products-close-2026-07-10.md`, and `trail-trio-close-2026-07-10.md`. Review artifact searches again found no dedicated `bmad-code-review` / code-review artifact for the combined implementation close.

**Test / validation visibility:** no evidence directory newer than `_bmad-output/implementation-artifacts/evidence/openalex-live-20260711T024437Z/` appeared. Latest formal evidence remains OpenAlex LIVE, followed by Workbook W4/W3 and foundations R7/R6/R5-fenced. This monitor did not rerun tests and found no new test transcript beyond committed evidence and handoff summaries.

**Implementation visibility:** no new implementation surface appeared since SOP-R017. Scoreable implementation remains the committed `3231dd43` stack; `3b88dd1e` records WRAPUP push; `5c08bcef` records docs/onboarding/knowledge-graph refresh.

**Scoreability:** Agentic Research Foundations remains **branch-durable and provisionally scoreable with explicit R5 fence**. Workbook Research Products W0-W4 remains **branch-durable and scoreable as a successor mini-epic close**. TRAIL trio remains **branch-durable and scoreable under tight fences**. Documentation coverage remains pushed. The combined stack is still not independently review-durable because no dedicated review artifact is visible.

**Findings / cautions:**
**F-R-0083 [P1] Stable branch, no new scoreability movement.** HEAD remains pushed at `5c08bcef`; no new implementation commit, BMAD gate, or evidence directory appeared after SOP-R017.
**F-R-0084 [P1] Separate code-review artifact still absent.** Close letters, story artifacts, WRAPUP, evidence packs, and docs updates are visible, but no dedicated review artifact is visible for the combined implementation close.
**F-R-0085 [P2] Latest formal proof remains OpenAlex.** No validation newer than `openalex-live-20260711T024437Z` is visible; post-close status is stability, not fresh proof.
**F-R-0086 [P2] Ambient untracked files remain outside the research score.** The placeholder-like technical research scaffold and older run/evidence leftovers should not be counted as claim evidence unless later bound by a story/gate/evidence record.

**Residual fencing:** dedicated code-review artifact, R5 live upgrade after Chrome quit / SSO-cookie availability, full semantic claim-source audit calibration across multiple workbook runs, Epic 17 related-resources/inline/hypothesis modes, ERIC / LoC adapters, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, novel HAI/PHS ingestion, and any claim that G2 or the WARN tripwire has become semantic claim-support.

**Verdict:** No material change since SOP-R017. The research foundations, workbook products, and TRAIL trio stack remains committed, pushed, branch-durable, and scoreable under named fences, with refreshed docs/onboarding also pushed. The persistent governance caution remains the absence of a dedicated code-review artifact; no new post-close evidence or claim expansion is visible.

---
### SOP-R019 - Research merged to master; active checkout moved to BMAD upgrade chore - 2026-07-11T00:19:26-04:00

**Scope reviewed:** research monitor ledger through SOP-R018, current `git status --short --branch --untracked-files=all`, local git log, commit stats for `6d14c640` and `067c687b`, latest evidence directory names/timestamps, and review artifact searches. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace is no longer checked out on `dev/agentic-research-foundations-2026-07-10`. Current checkout is `chore/bmad-upgrade-v6.10.0-2026-07-11` at `067c687b` (`Merge branch 'dev/agentic-research-foundations-2026-07-10'`), which is also visible as `master`, `origin/master`, and `origin/HEAD`. The research dev branch and origin now point to `6d14c640` (`chore(session): bank arc-close strays before master consolidation`), above `5c08bcef`, `3b88dd1e`, and `3231dd43`. This is a material durability/consolidation change since SOP-R018: the research stack is now master-consolidated.

**Worktree state:** current tracked dirt is `pyproject.toml`, and a new untracked `_bmad-output/implementation-artifacts/bmad-harness-upgrade-v6.10.0-2026-07-11.md` is visible. Those appear to belong to the active BMAD harness upgrade chore, not the monitored research mini-epic. Prior ambient untracked workbooks-test outputs, regression scratch files, meeting transcript deconstruction files, and older `runs/*` artifacts remain visible. The prior monitor/local strays, including this ledger, batch monitor ledger, product-gap monitor ledger, Irene literal liveproof leftovers, MCP config changes, and the placeholder-like technical research scaffold, were banked into `6d14c640` before master consolidation.

**Selected claim envelope classification:** parent **Agentic Research Foundations promote / close**, successor **Workbook Research Products W0-W4 close**, and **TRAIL trio close** remain the selected research claim envelopes. The new active checkout/chore work is **BMAD harness upgrade**, outside the research mini-epic claim envelope. No research claim expansion is visible in this poll.

**BMAD gate/story visibility:** the master merge brings forward the previously visible story SSOTs, workbook close letter, TRAIL party greenlight/close, TRAIL close letter, `SESSION-HANDOFF.md`, and updated user/dev/admin/onboarding documentation. The `6d14c640` bank commit also captures prior monitor ledgers and arc-close strays. Review artifact searches again found no dedicated `bmad-code-review` / code-review artifact for the research/workbook/TRAIL implementation close; batch code-review artifacts exist but are not research review artifacts.

**Test / validation visibility:** no new research evidence directory name appeared. Evidence filesystem `LastWriteTime` values now show a common `2026-07-11 00:09:09` timestamp for committed evidence directories after consolidation/checkout, but the visible evidence set remains the same: foundations R1-R7, Workbook W1-W4, and `openalex-live-20260711T024437Z`. This monitor did not rerun tests and found no new research validation transcript beyond committed evidence and handoff summaries.

**Implementation visibility:** research implementation remains the committed stack rooted in `3231dd43`, with WRAPUP/docs in `3b88dd1e` and `5c08bcef`, stray-bank consolidation in `6d14c640`, and master merge in `067c687b`. No new research implementation surface appeared after the merge.

**Scoreability:** Agentic Research Foundations is now **master-durable and provisionally scoreable with explicit R5 fence**. Workbook Research Products W0-W4 is **master-durable and scoreable as a successor mini-epic close**. TRAIL trio is **master-durable and scoreable under tight fences**. The combined stack remains not independently review-durable because no dedicated research code-review artifact is visible. The active BMAD harness upgrade work is outside this score.

**Findings / cautions:**
**F-R-0087 [P1] Research stack consolidated to master.** `067c687b` merges `dev/agentic-research-foundations-2026-07-10`; research is now visible on `master` / `origin/master`, not just the dev branch.
**F-R-0088 [P1] Dedicated research review artifact still absent.** Merge durability improved, but no research-specific code-review artifact appeared for the broad implementation close.
**F-R-0089 [P2] Active checkout has moved to BMAD upgrade.** `pyproject.toml` and the untracked BMAD harness upgrade artifact should not be counted as research-mini-epic implementation or evidence.
**F-R-0090 [P2] Evidence timestamps refreshed, not evidence set expanded.** The evidence directory names still match the prior research/workbook/OpenAlex packs; no new post-close research proof is visible.

**Residual fencing:** dedicated research code-review artifact, R5 live upgrade after Chrome quit / SSO-cookie availability, full semantic claim-source audit calibration across multiple workbook runs, Epic 17 related-resources/inline/hypothesis modes, ERIC / LoC adapters, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, novel HAI/PHS ingestion, and any claim that G2 or the WARN tripwire has become semantic claim-support.

**Verdict:** Material durability progress since SOP-R018. The research foundations, workbook products, and TRAIL trio stack has been banked and merged to master, so the research claim is now master-durable and scoreable under named fences. No new research evidence or dedicated research review artifact appeared, and the active checkout has moved on to a separate BMAD harness upgrade chore.

---
### SOP-R020 - Master advanced through BMAD upgrade; research claim unchanged - 2026-07-11T00:34:27-04:00

**Scope reviewed:** research monitor ledger through SOP-R019, current `git status --short --branch --untracked-files=all`, local git log, commit stats for `7b65b879` and `0e24da30`, latest research/workbook/OpenAlex evidence directory names/timestamps, and review artifact searches. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace is now on `master`, tracking `origin/master`, at `e88cd030` (`Merge branch 'chore/bmad-upgrade-v6.10.0-2026-07-11'`). Since SOP-R019, the BMAD upgrade chore branch landed `7b65b879` (`chore(bmad): upgrade harness to v6.10.0 --all-stable + party-gate amendments`), the prior SOP-R019 monitor append was banked in `0e24da30`, and master merged that branch in `e88cd030`. The research line remains present underneath: `067c687b` master-consolidated the research branch, and `6d14c640` remains the tip of `dev/agentic-research-foundations-2026-07-10` / origin.

**Worktree state:** no tracked dirty production/test research files are visible before this SOP append. Current status shows only untracked ambient outputs: workbooks-test artifacts, regression scratch files, meeting transcript deconstruction files, and older `runs/*` artifacts. The previously dirty BMAD upgrade surfaces (`pyproject.toml` and `bmad-harness-upgrade-v6.10.0-2026-07-11.md`) are now committed/merged. This SOP append will make this monitor ledger dirty again after the poll.

**Selected claim envelope classification:** monitored research claim envelopes remain **Agentic Research Foundations promote / close**, **Workbook Research Products W0-W4 close**, and **TRAIL trio close**. The BMAD harness upgrade is a separate maintenance/chore envelope and does not expand or re-score the research mini-epic claim.

**BMAD gate/story visibility:** the previously visible research story SSOTs, workbook close letter, TRAIL party greenlight/close, TRAIL close letter, `SESSION-HANDOFF.md`, docs/onboarding updates, and master consolidation remain present. `7b65b879` adds a BMAD harness upgrade implementation artifact and related guide/config updates, but those are not research-specific gates. Review artifact searches again found no dedicated research `bmad-code-review` / code-review artifact for the research/workbook/TRAIL implementation close.

**Test / validation visibility:** no new research evidence directory name appeared. The visible research evidence set remains foundations R1-R7, Workbook W1-W4, and `openalex-live-20260711T024437Z`. Evidence directory `LastWriteTime` values remain commonly refreshed to `2026-07-11 00:09:09` after consolidation, but the evidence set itself did not expand. This monitor did not rerun tests.

**Implementation visibility:** no new research implementation surface appeared since SOP-R019. Scoreable research implementation remains rooted in `3231dd43`, with WRAPUP/docs in `3b88dd1e` and `5c08bcef`, stray-bank consolidation in `6d14c640`, research master merge in `067c687b`, and later non-research BMAD upgrade merge in `e88cd030`.

**Scoreability:** Agentic Research Foundations remains **master-durable and provisionally scoreable with explicit R5 fence**. Workbook Research Products W0-W4 remains **master-durable and scoreable as a successor mini-epic close**. TRAIL trio remains **master-durable and scoreable under tight fences**. The combined research stack remains not independently review-durable because no dedicated research code-review artifact is visible.

**Findings / cautions:**
**F-R-0091 [P1] Master advanced, research claim unchanged.** `e88cd030` merges BMAD upgrade work after research consolidation; it does not add new research evidence or broaden the research claim.
**F-R-0092 [P1] Dedicated research review artifact still absent.** No research-specific code-review artifact appeared despite master durability.
**F-R-0093 [P2] BMAD upgrade is separate from research scoreability.** `7b65b879` updates harness/config/docs and should not be counted as research-mini-epic implementation proof.
**F-R-0094 [P2] Worktree is cleaner for tracked files.** The previous BMAD upgrade tracked dirt is now committed/merged; remaining pre-append dirt is untracked ambient output, not research implementation.

**Residual fencing:** dedicated research code-review artifact, R5 live upgrade after Chrome quit / SSO-cookie availability, full semantic claim-source audit calibration across multiple workbook runs, Epic 17 related-resources/inline/hypothesis modes, ERIC / LoC adapters, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, novel HAI/PHS ingestion, and any claim that G2 or the WARN tripwire has become semantic claim-support.

**Verdict:** No research-claim movement since SOP-R019. The research foundations, workbook products, and TRAIL trio stack remains master-durable and scoreable under named fences. Master has also advanced through a separate BMAD harness upgrade merge, but no new research evidence or dedicated research review artifact appeared.

---
### SOP-R021 - Stable master after BMAD upgrade merge; no new research proof - 2026-07-11T00:49:27-04:00

**Scope reviewed:** research monitor ledger through SOP-R020, current `git status --short --branch --untracked-files=all`, local git log, latest research/workbook/OpenAlex evidence directory names/timestamps, implementation-artifact inventory, and review artifact searches. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace remains on `master`, tracking `origin/master`, at `e88cd030` (`Merge branch 'chore/bmad-upgrade-v6.10.0-2026-07-11'`). No new commit is visible since SOP-R020. The research line remains present underneath the master history: `067c687b` merged `dev/agentic-research-foundations-2026-07-10`, and `6d14c640` remains the tip of the research dev branch / origin.

**Worktree state:** before this SOP append, the only tracked dirty file was this research shadow-monitor ledger from the SOP-R020 append. Untracked ambient outputs remain visible: workbooks-test artifacts, regression scratch files, meeting transcript deconstruction files, and older `runs/*` artifacts. No tracked production/test research implementation dirt is visible.

**Selected claim envelope classification:** monitored research claim envelopes remain **Agentic Research Foundations promote / close**, **Workbook Research Products W0-W4 close**, and **TRAIL trio close**. The BMAD harness upgrade remains a separate maintenance/chore envelope and does not expand or re-score the research mini-epic claim.

**BMAD gate/story visibility:** previously visible research story SSOTs, workbook close letter, TRAIL party greenlight/close, TRAIL close letter, `SESSION-HANDOFF.md`, docs/onboarding updates, and master consolidation remain present. The newest non-research implementation artifact remains `bmad-harness-upgrade-v6.10.0-2026-07-11.md`, which is not a research gate. Review artifact searches again found no dedicated research `bmad-code-review` / code-review artifact for the research/workbook/TRAIL implementation close.

**Test / validation visibility:** no new research evidence directory name appeared. The visible research evidence set remains foundations R1-R7, Workbook W1-W4, and `openalex-live-20260711T024437Z`. Evidence directory `LastWriteTime` values remain commonly refreshed to `2026-07-11 00:09:09` after consolidation, but the evidence set itself did not expand. This monitor did not rerun tests.

**Implementation visibility:** no new research implementation surface appeared since SOP-R020. Scoreable research implementation remains rooted in `3231dd43`, with WRAPUP/docs in `3b88dd1e` and `5c08bcef`, stray-bank consolidation in `6d14c640`, research master merge in `067c687b`, and later non-research BMAD upgrade merge in `e88cd030`.

**Scoreability:** Agentic Research Foundations remains **master-durable and provisionally scoreable with explicit R5 fence**. Workbook Research Products W0-W4 remains **master-durable and scoreable as a successor mini-epic close**. TRAIL trio remains **master-durable and scoreable under tight fences**. The combined research stack remains not independently review-durable because no dedicated research code-review artifact is visible.

**Findings / cautions:**
**F-R-0095 [P1] Stable master, no new research movement.** HEAD remains `e88cd030`; no new research implementation commit, BMAD gate, or evidence directory appeared after SOP-R020.
**F-R-0096 [P1] Dedicated research review artifact still absent.** No research-specific code-review artifact appeared despite master durability.
**F-R-0097 [P2] Current tracked dirt is monitor-local.** The only tracked dirty file before this append was this ledger, from the previous monitor update.
**F-R-0098 [P2] Evidence set remains unchanged.** The visible proof set is still foundations R1-R7, Workbook W1-W4, and OpenAlex live; no new post-close research proof is visible.

**Residual fencing:** dedicated research code-review artifact, R5 live upgrade after Chrome quit / SSO-cookie availability, full semantic claim-source audit calibration across multiple workbook runs, Epic 17 related-resources/inline/hypothesis modes, ERIC / LoC adapters, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, novel HAI/PHS ingestion, and any claim that G2 or the WARN tripwire has become semantic claim-support.

**Verdict:** No research-claim movement since SOP-R020. The research foundations, workbook products, and TRAIL trio stack remains master-durable and scoreable under named fences. No new research evidence or dedicated research review artifact appeared; current tracked dirt is monitor-local.

---
### SOP-R022 - Active checkout moved to dev-auto residual; research score unchanged - 2026-07-11T01:04:26-04:00

**Scope reviewed:** research monitor ledger through SOP-R021, current `git status --short --branch --untracked-files=all`, local git log, commit stats for `aa336a8f` and `73eef7df`, latest research/workbook/OpenAlex evidence directory names/timestamps, the new residual spec artifact, and review artifact searches. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace is now on `chore/dev-auto-residuals-2026-07-11` at `73eef7df` (`chore(monitor): bank shadow-monitor ledger append`). This branch sits above `aa336a8f` (`chore(bmad): project override for bmad-dev-auto (guardrail facts + on_complete push ritual)`) and master `e88cd030` (`Merge branch 'chore/bmad-upgrade-v6.10.0-2026-07-11'`). The research line remains present underneath master via `067c687b` and `6d14c640`.

**Worktree state:** current tracked dirt is `app/marcus/cli/trial.py`, with a new untracked `_bmad-output/implementation-artifacts/spec-lesson-plan-json-cli-flag-docstring.md`. That spec declares a documentation-only residual for lesson-plan JSON CLI help/docstrings and explicitly says no behavior changes. This is outside the monitored research mini-epic claim. Ambient untracked workbooks-test artifacts, regression scratch files, meeting transcript deconstruction files, and older `runs/*` artifacts remain visible. No tracked production/test research implementation dirt is visible.

**Selected claim envelope classification:** monitored research claim envelopes remain **Agentic Research Foundations promote / close**, **Workbook Research Products W0-W4 close**, and **TRAIL trio close**. The active `dev-auto` residual and lesson-plan CLI docstring work are separate maintenance/residual envelopes and do not expand or re-score the research mini-epic claim.

**BMAD gate/story visibility:** previously visible research story SSOTs, workbook close letter, TRAIL party greenlight/close, TRAIL close letter, `SESSION-HANDOFF.md`, docs/onboarding updates, and master consolidation remain present. `aa336a8f` adds a BMAD dev-auto project override; `spec-lesson-plan-json-cli-flag-docstring.md` is a non-research residual spec. Review artifact searches again found no dedicated research `bmad-code-review` / code-review artifact for the research/workbook/TRAIL implementation close.

**Test / validation visibility:** no new research evidence directory name appeared. The visible research evidence set remains foundations R1-R7, Workbook W1-W4, and `openalex-live-20260711T024437Z`. Evidence directory `LastWriteTime` values remain commonly refreshed to `2026-07-11 00:09:09` after consolidation, but the evidence set itself did not expand. This monitor did not rerun tests.

**Implementation visibility:** no new research implementation surface appeared since SOP-R021. Scoreable research implementation remains rooted in `3231dd43`, with WRAPUP/docs in `3b88dd1e` and `5c08bcef`, stray-bank consolidation in `6d14c640`, research master merge in `067c687b`, BMAD upgrade merge in `e88cd030`, and later non-research dev-auto residual branch work in `aa336a8f` / `73eef7df`.

**Scoreability:** Agentic Research Foundations remains **master-durable and provisionally scoreable with explicit R5 fence**. Workbook Research Products W0-W4 remains **master-durable and scoreable as a successor mini-epic close**. TRAIL trio remains **master-durable and scoreable under tight fences**. The combined research stack remains not independently review-durable because no dedicated research code-review artifact is visible.

**Findings / cautions:**
**F-R-0099 [P1] Active branch moved again, but not for research.** The workspace is on `chore/dev-auto-residuals-2026-07-11`; the new dirty/spec surfaces concern lesson-plan CLI docstrings, not the research mini-epic.
**F-R-0100 [P1] Dedicated research review artifact still absent.** No research-specific code-review artifact appeared despite master durability.
**F-R-0101 [P2] Evidence set remains unchanged.** The visible proof set is still foundations R1-R7, Workbook W1-W4, and OpenAlex live; no new post-close research proof is visible.
**F-R-0102 [P2] Current tracked dirt is outside research score.** `app/marcus/cli/trial.py` and the lesson-plan JSON CLI residual spec should not be counted as research implementation or validation.

**Residual fencing:** dedicated research code-review artifact, R5 live upgrade after Chrome quit / SSO-cookie availability, full semantic claim-source audit calibration across multiple workbook runs, Epic 17 related-resources/inline/hypothesis modes, ERIC / LoC adapters, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, novel HAI/PHS ingestion, and any claim that G2 or the WARN tripwire has become semantic claim-support.

**Verdict:** No research-claim movement since SOP-R021. The research foundations, workbook products, and TRAIL trio stack remains master-durable and scoreable under named fences. Active work has moved to a separate dev-auto / lesson-plan CLI docstring residual; no new research evidence or dedicated research review artifact appeared.

---
### SOP-R023 - Dev-auto residual merged to master; research evidence unchanged - 2026-07-11T01:19:29-04:00

**Scope reviewed:** research monitor ledger through SOP-R022, current `git status --short --branch --untracked-files=all`, local git log, commit stats for `1c547ab3`, `31caec22`, and `5d0042f4`, latest research/workbook/OpenAlex evidence directory names/timestamps, and review artifact searches. No tests were run by this monitor poll. No production, test, runtime, Cursor, Grok, or BMAD-owned files were edited by this monitor; this SOP append is the only intentional write.

**Current repo state:** workspace is back on `master`, tracking `origin/master`, at `6d265d2c` (`Merge branch 'chore/dev-auto-residuals-2026-07-11'`). Since SOP-R022, the dev-auto residual branch landed `1c547ab3` (`docs(cli): clarify --lesson-plan-json / --lesson-plan-collateral-intent precedence + companion re-resolution boundary`), `31caec22` (`chore(spec): stamp final_revision on dev-auto spec`), and `5d0042f4` (`chore(monitor): bank shadow-monitor ledger append`), then merged to master. The research line remains present underneath master via `067c687b` and `6d14c640`.

**Worktree state:** before this SOP append, no tracked dirty files were visible. Untracked ambient outputs remain visible: workbooks-test artifacts, regression scratch files, meeting transcript deconstruction files, and older `runs/*` artifacts. The previously dirty `app/marcus/cli/trial.py` and lesson-plan JSON CLI residual spec are now committed/merged. No tracked production/test research implementation dirt is visible.

**Selected claim envelope classification:** monitored research claim envelopes remain **Agentic Research Foundations promote / close**, **Workbook Research Products W0-W4 close**, and **TRAIL trio close**. The merged dev-auto / lesson-plan CLI docstring residual is a separate maintenance envelope and does not expand or re-score the research mini-epic claim.

**BMAD gate/story visibility:** previously visible research story SSOTs, workbook close letter, TRAIL party greenlight/close, TRAIL close letter, `SESSION-HANDOFF.md`, docs/onboarding updates, and master consolidation remain present. The dev-auto residual spec is now committed but remains non-research. Review artifact searches again found no dedicated research `bmad-code-review` / code-review artifact for the research/workbook/TRAIL implementation close.

**Test / validation visibility:** no new research evidence directory name appeared. The visible research evidence set remains foundations R1-R7, Workbook W1-W4, and `openalex-live-20260711T024437Z`. Evidence directory `LastWriteTime` values remain commonly refreshed to `2026-07-11 00:09:09` after consolidation, but the evidence set itself did not expand. This monitor did not rerun tests.

**Implementation visibility:** no new research implementation surface appeared since SOP-R022. Scoreable research implementation remains rooted in `3231dd43`, with WRAPUP/docs in `3b88dd1e` and `5c08bcef`, stray-bank consolidation in `6d14c640`, research master merge in `067c687b`, BMAD upgrade merge in `e88cd030`, and later non-research dev-auto residual merge in `6d265d2c`.

**Scoreability:** Agentic Research Foundations remains **master-durable and provisionally scoreable with explicit R5 fence**. Workbook Research Products W0-W4 remains **master-durable and scoreable as a successor mini-epic close**. TRAIL trio remains **master-durable and scoreable under tight fences**. The combined research stack remains not independently review-durable because no dedicated research code-review artifact is visible.

**Findings / cautions:**
**F-R-0103 [P1] Non-research residual merged to master.** `6d265d2c` advances master through lesson-plan CLI docstring residual work; it does not add research evidence or broaden the research claim.
**F-R-0104 [P1] Dedicated research review artifact still absent.** No research-specific code-review artifact appeared despite master durability.
**F-R-0105 [P2] Evidence set remains unchanged.** The visible proof set is still foundations R1-R7, Workbook W1-W4, and OpenAlex live; no new post-close research proof is visible.
**F-R-0106 [P2] Worktree has no tracked research dirt.** Pre-append tracked status was clean; remaining visible dirt is untracked ambient output outside the research score.

**Residual fencing:** dedicated research code-review artifact, R5 live upgrade after Chrome quit / SSO-cookie availability, full semantic claim-source audit calibration across multiple workbook runs, Epic 17 related-resources/inline/hypothesis modes, ERIC / LoC adapters, PubMed v2, Tracy gate resume/recover, LLM Tracy refine, Consensus/Jefferson default-ON policy, novel HAI/PHS ingestion, and any claim that G2 or the WARN tripwire has become semantic claim-support.

**Verdict:** No research-claim movement since SOP-R022. The research foundations, workbook products, and TRAIL trio stack remains master-durable and scoreable under named fences. The dev-auto / lesson-plan CLI docstring residual has been merged to master, but no new research evidence or dedicated research review artifact appeared.
