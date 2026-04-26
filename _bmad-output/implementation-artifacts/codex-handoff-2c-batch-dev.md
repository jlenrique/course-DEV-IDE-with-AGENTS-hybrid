# Codex Handoff Prompt — Slab 2c Batch Development (2c.1 → 2c.2 → 2c.3 → 2c.4)

**For:** Codex dev agent
**Issued:** 2026-04-26
**Branch:** `dev/langchain-langgraph-foundation`
**Anchor commit:** `8654086` (Slab 2c batch authored ready-for-dev with party-mode amendments)
**Predecessor:** Slab 2b CLOSED at commits `83caed7` + `b635586` (dispatch family completion); Slab 2a CLOSED at `0a02fa5`

---

## Mission

Develop all 4 Slab 2c stories in strict sequence (2c.1 → 2c.2 → 2c.3 → 2c.4). Slab 2c is the **Wondercraft Pilot + Generator Validation** epic; M2 acceptance gate ("Plug-and-play specialist claim validated") closes at 2c.3 with party-mode verdict; 2c.4 is SLAB CLOSING.

---

## Hard sequencing (BINDING)

```
2c.1 done ──► 2c.2 open
              2c.2 done ──► 2c.3 open
                            2c.3 done ──► 2c.4 open ──► Slab 2c CLOSED
```

**Do NOT open 2c.N+1 until 2c.N is BMAD-CLOSED.** 2c.3 reads 2c.1 + 2c.2 evidence at T1; opening 2c.3 against incomplete predecessors will fail T1 §2 pre-flight.

---

## Per-story BMAD cycle (apply uniformly)

For each of 2c.1, 2c.2, 2c.3, 2c.4:

1. **Read the spec end-to-end** at `_bmad-output/implementation-artifacts/migration-2c-{N}-*.md`. The spec already incorporates all party-mode amendments (BLOCKERs RESOLVED + RIDERs integrated; see header of each spec).
2. **Run T1 Readiness Block** verifying every pre-flight item + artifact-existence sweep + epic-doc-vs-runtime cross-check. **Halt and surface to operator if any pre-flight fails** (especially 2c.3 § "Predecessor close evidence" + 2c.4 § "2c.3 M2 verdict anchor").
3. **Implement the AC sequence** in declared order. Adhere to all RESOLVED-BY-VERIFICATION pins (e.g., 2c.4 AC-A `--retire` MUST mirror 2a.5 string-surgery, NO new TOML library; 2c.2 AC-D MUST use `--run-live` opt-in mechanism, NOT `addopts -m "not live_api"`).
4. **Run regression suite** at T8: `.venv/Scripts/python.exe -m pytest -q --tb=short` AND `.venv/Scripts/python.exe -m pytest tests/integration/scaffold_conformance/ -q`. Baseline target: ≥562 passed / ≥7 skipped placeholder-key (Slab 2b close baseline).
5. **Run lint:** `.venv/Scripts/python.exe -m ruff check app/ tests/ skills/ scripts/` AND `.venv/Scripts/python.exe -m lint_imports --config pyproject.toml`. Both must be clean (3/3 import-linter contracts KEPT).
6. **G6 single-gate self-conducted code review** per CLAUDE.md (Blind Hunter / Edge Case Hunter / Acceptance Auditor). Apply MUST-FIX patches; DISMISS aggressive on cosmetic NITs per `docs/dev-guide/story-cycle-efficiency.md`.
7. **Run `bmad-code-review`** on the diff in scope per CLAUDE.md §3 BMAD sprint governance. Address findings to GREEN before close.
8. **D12 close protocol** per spec AC. **Sprint-status flip + closeout hygiene per CLAUDE.md** ("update sprint-status.yaml first, update next-session-start-here.md second"). For 2c.4 SLAB CLOSING: also update `docs/dev-guide/specialist-anti-patterns.md` header annotation + `slab-2c-retrospective.md` + governance JSON if any state change.
9. **Commit per story.** Suggested message format:
   ```
   feat(2c.N): <one-line summary> + <key amendments-honored note>
   ```
10. **Run sandbox-AC validator** post-close on the next story before opening it: `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-2c-{N+1}-*.md`. Should still PASS (specs were validated at authoring; this re-validates against current substrate).

---

## Story-specific landmines (READ BEFORE OPENING EACH)

### 2c.1 — Path B Wondercraft regen + diff vs Wanda

- **AC-A `--mcp wondercraft`** (NOT `wondercraft-api`) per `ALLOWED_MCP_TOOLS` whitelist at `skills/bmad_create_specialist/scripts/generate.py:18-20`. The story-status comment at sprint-status.yaml line 787 contains the obsolete `wondercraft-api` text — IGNORE; the spec body is canonical.
- **AC-B-OP** ($0.50 smoke-test) is **operator-gated** with DEFERRED-PENDING-OPERATOR-WINDOW allowed. Do NOT autonomously incur cost. AC-G PERSISTENT diff-evidence Markdown is the M2 anchor for 2c.3 — DO NOT delete or relocate.
- **AC-F retire-to-fixtures default**: `git mv app/specialists/wanda_validation/ tests/fixtures/generator_validation/wanda_baseline/2026-04-25/` + author `BASELINE_METADATA.md` companion + manual C3 row removal with explanatory comment + re-emit guard test.
- **`2c-1-generator-auto-emit-retire-removal-support`** deferred-inventory entry MUST be filed at AC-F per Murat M-R6 meta-drift; this is RESOLVED by 2c.4 AC-A.

### 2c.2 — Wanda L5+L6 + live API artifact (executes 2b.8 deferred AC-B-OP)

- **L5 files location:** `skills/bmad-agent-wondercraft/references/L5-podcast-production/` (NEW sub-dir under operator-curated skill substrate; Decision #2). Augmenting, not replacing.
- **WANDA_REFERENCES tuple extension** at `app/specialists/wanda/graph.py:28-40` is the ONLY in-scope edit to Wanda runtime code (additive 11→14 entries; Decision #1 + A-R3-2c.2).
- **Sanctum AC-A is SKELETON-ONLY (per A-R5-2c.2):** dev creates `_bmad/memory/wanda-sidecar/{INDEX,PERSONA,access-boundaries,chronology}.md + L6-operational/wondercraft-context.md` with `<!-- TODO: operator-populate via First Breath ceremony -->` markers + minimal valid frontmatter + required §-headers. **Operator populates content** in own session before AC-G party-mode review. Acceptance is structural, NOT content-quality.
- **AC-D `live_api` mechanism (RESOLVED-BY-VERIFICATION):** marker registered at `pyproject.toml:62-63` + `tests/conftest.py:88`; opt-in is `--run-live` flag at `tests/conftest.py:71` via `pytest_collection_modifyitems` Pass 1 at line 129-149. Test invocation: `pytest <path> --run-live -v -s`. **Do NOT add `addopts -m "not live_api"`** — that's not the project mechanism.
- **AC-D-OP-FALLBACK:** if `create_scripted_podcast` $5 ceiling exceeded, operator may run `create_podcast` at $1-2 ceiling. Sentinel `artifact_format: scripted` OR `artifact_format: simple-fallback`.
- **AC-E round-trip** is filesystem sha256 ↔ LIVE_ARTIFACT_METADATA.md sha256, NOT receipt-key extraction (receipt is loose `dict[str, Any] | None` per `app/models/dispatch/wanda/receipt.py`).
- **M-R31-2c.2:** AC-D NEGATIVE test subprocess MUST sanitize `PYTEST_ADDOPTS` env + parse structured pytest output (exit code + summary-line `deselected` count), NOT free-text body match.

### 2c.3 — Time-to-deploy + 5-agent party-mode + M2 verdict

- **HARD predecessor:** 2c.1 + 2c.2 must be `done` per sprint-status.yaml. If 2c.2 AC-D-OP deferred, **PARTIAL-VERDICT path activates** (AC-D-PARTIAL); M2 verdict transitions GREEN-LIGHT → CONDITIONAL-GREEN; auto-files `2c-3-m2-verdict-conditional-on-2c-2-live-artifact` deferred-inventory entry.
- **15-invariant audit matrix is DEFERRED to Slab 5a** (RESOLVED-BY-DEFERRAL per A-R1-2c.3 BLOCKER). 2c.3 AC-D produces `slab-2c-wondercraft-invariant-stub.md` 2-row stub for Slab 5a absorption. Do NOT attempt matrix backfill.
- **5-agent party-mode roster pinned (HARD):** Winston + Murat + Paige + Quinn-R + Amelia. Quinn-R may legitimately ABSTAIN ("outside lane"); 4-of-5 consensus path is valid per Decision #4. Spawn each as Agent-tool subagent in parallel; capture each verbatim response; write into `slab-2c-m2-acceptance-verdict.md` under `### <agent>` headers per A-R4-2c.3 explicit T-task sequence.
- **T_first_real_artifact semantic pin (M-R4-2c.3 BINDING):** wall-clock instant `LIVE_ARTIFACT_METADATA.md` is written-to-disk with all required schema fields populated, after artifact-assembly returns success exit code. Operator-validation (listening, judging quality) is NOT in the time-to-deploy budget.
- **Test directory:** `tests/migration/test_slab_2c_m2_*.py` (flat layout per existing `tests/migration/test_bmb_scaffold.py` precedent). NO `tests/specialists/slab_2c/` directory.
- **Verdict regex 4-enum:** `(GREEN-LIGHT|GREEN-WITH-RIDERS|CONDITIONAL-GREEN|YELLOW|RED)` for consensus-level; per-agent enum is 6 (adds `ABSTAIN`).

### 2c.4 — SLAB CLOSING

- **HARD predecessor:** 2c.1 + 2c.2 + 2c.3 all `done`; 2c.3 M2 verdict ∈ `{GREEN-LIGHT, CONDITIONAL-GREEN}` (NOT YELLOW, NOT RED).
- **AC-A `--retire` flag implementation pin (A-R1 RESOLVED-BY-VERIFICATION BINDING):** mirror 2a.5 generator's **string-level surgery** at `skills/bmad_create_specialist/scripts/generate.py:284-365` (`pyproject_path.read_text` + text manipulation; `_write_text(path, content)` for write). **NO new TOML library imports** (no `tomli`, `tomlkit`, `tomllib`). Resolves `2c-1-generator-auto-emit-retire-removal-support` deferred-inventory entry.
- **AC-A T1 sub-task per A-R3:** grep `tests/specialists/generator/` for assertions on `--name required` argparse error-string format; mutual-exclusion change may alter the format.
- **AC-A K-floor recount (M-R1 BLOCKER):** 4 K-floor units (NOT collapsed). Idempotent variants count as 2 (mutation path + no-op path are DIFFERENT semantic branches).
- **AC-B subprocess isolation (A-R2 RESOLVED-BY-VERIFICATION BINDING):** invoke generator **programmatically** via `Request(repo_root=tmp_path, ...)` (per `Request` dataclass at line 59 + `(request.repo_root or _repo_root()).resolve()` at line 423). Do NOT mutate live tree.
- **AC-B throwaway-name (M-R3 BINDING):** `f"tmp_validate_{uuid.uuid4().hex[:8]}"` — UUID-suffixed; pre-test sweep `assert not Path(...).exists()`.
- **AC-B teardown (M-R2 BINDING):** pytest fixture with `yield` + `addfinalizer` cleanup that runs **regardless of test outcome**; cleanup is itself idempotent.
- **AC-C harvest-gate authority (3-agent BLOCKER consensus):** **STRIP all "Default verdict:" lines from candidates A14/A14-alt/A15-alt.** Spec author preempting harvest-gate violates Mary's gate. Dev agent at 2c.4 dev-time runs `bmad-party-mode` round on candidates → records each as `ACCEPT-AS-A<N>` / `DEFER-WITH-REASON` / `ABSORB-INTO-A<existing>` in Completion Notes. Spec lists candidates as PROVENANCE only.
- **AC-C header annotation (P-R3):** `"Slab 2 (2a + 2b + 2c) harvest cycle complete; 13+ entries A1–A<final> under format-freeze v1; Slab 3+ harvest continues under the same freeze unless party-mode consensus + version bump."` Distinguishes harvest-cycle-complete from catalog-closed.
- **AC-D retrospective format pin (A-R5+P-R2):** mirror `slab-2b-retrospective.md` canonical structure. 4 §-headers: `## Pre-Audit Bundle` / `## Slab Outcomes` / `## Next-Slab Preparation` / `## Slab 5a / 5b Handoff`.
- **AC-D per-entry verdict assertion (M-R5+P-R1 BINDING):** §"Next-Slab Preparation" lists ≥3 consulted deferred-inventory entries each with explicit verdict `<entry-id>: <RESOLVED|DEFERRED-CONTINUES|REACTIVATED-AT-SLAB-X|NOT-APPLICABLE>` + one-sentence justification.
- **AC-E sprint-status enum clarification (Amelia):** status value stays `done`; conditional context is **trailing comment** referencing M2 verdict artifact. NO new `done-with-conditional-m2` enum.
- **AC-J:** `next-session-start-here.md` update with Slab 2c CLOSED handoff + Deferred inventory status line per CLAUDE.md §closeout hygiene + §2.

---

## Governance non-negotiables

- **Sandbox-AC discipline (CLAUDE.md):** dev-agent ACs MUST verify via shipped Python deps + `pytest.skip(...)` on missing service; NO operator-CLI assumptions on PATH (`docker`, `psql`, `gh`, `kubectl`, etc.). Run `validate_migration_story_sandbox_acs.py` before opening any story.
- **Gate-mode pinned at governance JSON:** all 4 stories are `single-gate` per `docs/dev-guide/migration-story-governance.json:52-55`. DO NOT relitigate.
- **Live API discipline:** `live_api`-marked tests are deselected by default via `--run-live` opt-in (`tests/conftest.py`). 2c.1 AC-B-OP ($0.50) and 2c.2 AC-D-OP ($5/$1-2) are operator-gated — do NOT autonomously incur cost.
- **Hybrid working tree is sole input surface:** upstream/master severed at commit `3ed7c56` on 2026-04-24; do NOT pull from upstream.
- **Closeout hygiene:** every story close updates `sprint-status.yaml` first, then `next-session-start-here.md`, then any other top-level plan/status that would otherwise drift.
- **Deferred inventory governance (CLAUDE.md):** every new follow-on goes to `_bmad-output/planning-artifacts/deferred-inventory.md` (NOT just spec body); 2c.4 AC-D enforces per-entry consultation verdicts.
- **No commits without explicit user ask EXCEPT** for the per-story BMAD-CLOSE commits implicit in this batch directive — proceed with those (one commit per story close).
- **No force-push, no `--no-verify`, no `--amend` published commits.**

---

## What "done" means for the batch

- All 4 stories show `done` in sprint-status.yaml.
- `migration-epic-2c-slab-2-wondercraft-pilot: done` (with trailing comment if M2 conditional per AC-E).
- M2 milestone: `GREEN-LIGHT 2026-04-XX` OR `CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM` (recorded in `slab-2c-m2-acceptance-verdict.md`).
- `slab-2c-retrospective.md` exists with 4 canonical §-headers + per-entry deferred-inventory verdicts.
- Anti-patterns catalog has harvest-cycle-complete header annotation + 13-N entries (N depends on harvest-gate verdicts).
- Generator at `skills/bmad_create_specialist/scripts/generate.py` has `--retire <name>` flag (string-surgery) + throwaway-round-trip regression test passes.
- `next-session-start-here.md` reflects Slab 2c CLOSED + post-2c.4 deferred-inventory counts.
- Regression suite: ≥562 passed / ≥7 skipped placeholder-key baseline preserved (likely +20-30 net from 2c additions).
- Import-linter 3/3 contracts KEPT throughout.
- One commit per story-close (4 commits total) + optional umbrella commit at slab-close for retrospective + anti-patterns header.

---

## Escalation triggers (HALT and surface to operator)

- T1 pre-flight fails on any story (predecessor not `done`, anchor file missing, etc.).
- Sandbox-AC validator FAILS on a story spec (substrate state has drifted since authoring).
- 2c.3 M2 party-mode returns `YELLOW` or `RED` verdict (cannot proceed to 2c.4).
- 2c.4 AC-A finds 2a.5 generator uses TOML library after all (verification was wrong) — surface for re-design.
- 2c.4 AC-B subprocess isolation fails (generator can't accept `tmp_path` repo root) — surface for re-design.
- 2c.4 AC-C harvest-gate party-mode round produces a NEW catalog format change request — pause for operator + party-mode consensus per format-freeze.
- Regression count drops below baseline at any T8 (≥562 passed / ≥7 skipped).
- Live API call exceeds cost ceiling (2c.1 $0.50; 2c.2 $5 with $1-2 fallback) — abort + file overrun-rca follow-on.

---

## Reference anchors

- Spec files: `_bmad-output/implementation-artifacts/migration-2c-{1,2,3,4}-*.md` (commit `8654086`)
- Sprint status: `_bmad-output/implementation-artifacts/sprint-status.yaml` (Slab 2c block at line 783+)
- Governance JSON: `docs/dev-guide/migration-story-governance.json:52-55` (all 2c.x = single-gate)
- TEMPLATE doc: `docs/dev-guide/specialist-migration-template.md` v2.4
- Anti-patterns catalog: `docs/dev-guide/specialist-anti-patterns.md` (A1-A13 currently)
- Sandbox-AC validator: `scripts/utilities/validate_migration_story_sandbox_acs.py`
- 2c.1 epic anchor: `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` §Epic 2c lines 784-889
- Wondercraft skill substrate: `skills/bmad-agent-wondercraft/`
- Wanda runtime (2b.8 + 2b.15): `app/specialists/wanda/` + `app/models/dispatch/wanda/`
- Wondercraft API client: `scripts/api_clients/wondercraft_client.py`
- 2a.5 generator (auto-emit C3 + future `--retire` location): `skills/bmad_create_specialist/scripts/generate.py:284-365`
- Live API marker mechanism: `pyproject.toml:62-63` + `tests/conftest.py:68-149`

Proceed.
