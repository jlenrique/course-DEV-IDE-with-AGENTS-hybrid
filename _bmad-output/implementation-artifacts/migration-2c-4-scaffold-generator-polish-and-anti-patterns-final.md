# Migration Story 2c.4: Scaffold-Generator Polish + Specialist-Anti-Patterns Catalog Final 2b+2c Harvest (SLAB CLOSING)

**Status:** ready-for-dev
**Sprint key:** `migration-2c-4-scaffold-generator-polish-and-anti-patterns-final`
**Epic:** Slab 2c (migration Epic 2c — Wondercraft Pilot + Generator Validation) — **fourth story; SLAB CLOSING**.
**Pts:** 2 | **Gate:** single (per governance JSON `2c-4.expected_gate_mode = "single-gate"`, rationale: null — SLAB CLOSING + generator polish + anti-patterns harvest; no schema-shape, no lane-boundary, no invariant-preservation; the slab-retrospective + D12 protocol artifact). **K-target:** ~1.3× (target 8 / floor 6; throwaway-regen regression test + final-anti-patterns assertions + D12 close protocol).

**SLAB-CLOSING framing:** Story 2c.4 closes Slab 2c. It DELIVERS:
1. **Generator polish from 2c.1 feedback** (including resolution of `2c-1-generator-auto-emit-retire-removal-support` deferred-inventory follow-on filed at 2c.1 AC-F)
2. **Throwaway second-specialist regression test** — proves the generator produces a second NEW specialist that passes scaffold-conformance; throwaway is deleted at test close
3. **Final anti-patterns catalog harvest from 2b + 2c** — confirms ≥5 entries (≥7 preferred per epic 2c.4 binding); validates "harvested-not-invented" per Mary harvest-gate
4. **Slab 2c retrospective** at `_bmad-output/implementation-artifacts/slab-2c-retrospective.md` (NEW), mirroring the Slab 2a + Slab 2b retrospective conventions
5. **Conditional-resolution responsibility inherited from 2c.3 A-R6 hard-gate** — verifies 2c.3 M2 verdict is GREEN-LIGHT (or carries `CLOSED-WITH-CONDITIONAL-M2` close-state per A-R6-2c.3 if 2c.2 AC-D-OP deferred)
6. **D12 close protocol (single-gate; FOUR-line per A-R7)** + sprint-status closes `migration-epic-2c-slab-2-wondercraft-pilot: done` (or `done-with-conditional-m2`)
7. **15-invariant audit matrix Wondercraft entries deferred to Slab 5a** per 2c.3 A-R1 BLOCKER B1 RESOLVED-BY-DEFERRAL — 2c.4 confirms `slab-2c-wondercraft-invariant-stub.md` is in place for Slab 5a absorption

**Predecessor dependencies (HARD):**
- Stories 2c.1, 2c.2, 2c.3 must be `done` per sprint-status.yaml.
- 2c.3 M2 verdict must be one of `{GREEN-LIGHT, CONDITIONAL-GREEN}` (NOT YELLOW, NOT RED).
- If 2c.3 closed `CONDITIONAL-GREEN`, 2c.4 inherits the hard-gate per A-R6-2c.3: Slab 2c closes as `CLOSED-WITH-CONDITIONAL-M2` instead of `CLOSED-GREEN`.

**Authoring queue position:** 2c.4 spec is authored AFTER 2c.3 spec but BEFORE any 2c.x story has reached `done`. Drafted-for-queue per operator directive 2026-04-25 ("create stories 2c.1 - 2c.4 until each ready-for-dev; then batch-dev"). Spec stays at `ready-for-dev` BUT will not enter dev until 2c.1 + 2c.2 + 2c.3 close.

**Lean party-mode amendments applied 2026-04-26 (Murat + Amelia + Paige):** 5 BLOCKERs RESOLVED + 8 RIDERs integrated:
- **A-R1-2c.4 BLOCKER (TOML library) RESOLVED-BY-VERIFICATION:** 2a.5 generator at `skills/bmad_create_specialist/scripts/generate.py:284-365` uses **string-level surgery** (`pyproject_path.read_text(encoding="utf-8")` + text manipulation; no `tomli` / `tomlkit` / `tomllib` imports). `--retire` MUST mirror this approach — NO new TOML library introduction.
- **A-R2-2c.4 BLOCKER (subprocess isolation) RESOLVED-BY-VERIFICATION:** Generator already supports `Request(repo_root=tmp_path, ...)` programmatic invocation per `Request` dataclass at line 59 + `(request.repo_root or _repo_root()).resolve()` at line 423. `--repo-root` CLI flag NOT exposed in argparse (`_build_parser` lines 481-490). AC-B throwaway test invokes generator **programmatically** via `Request(repo_root=tmp_path)` against a tmp-repo-root fixture; NO live tree mutation.
- **M-R1-2c.4 BLOCKER (AC-A K-floor recount):** Idempotent variants test DIFFERENT semantic branches (mutation path vs no-op path); count as 2 K-floor units, NOT collapsed to 1. Recount AC-A: 4 K-floor units (not 3). New honest total: 8 firm K-floor (not 7).
- **M-R2-2c.4 + M-R3-2c.4 BLOCKERs (AC-B teardown + UUID-name):** Throwaway-name MUST be `f"tmp_validate_{uuid.uuid4().hex[:8]}"`; pytest fixture with `yield` + `addfinalizer` cleanup that runs **regardless of test outcome**; cleanup is itself idempotent.
- **M-R4-2c.4 + A-R4-2c.4 + P-R4-2c.4 BLOCKER (3-agent consensus on harvest-gate preemption):** Story-author preempting harvest-gate verdicts on A14/A14-alt/A15-alt **violates Mary's harvest-gate** (requires documented burn OR party-mode consensus). **STRIP all "Default verdict:" lines from AC-C.** Reframe candidates as "evaluation pending at 2c.4 dev-time" with provenance only; verdicts recorded in 2c.4 close notes after actual harvest-gate evaluation. Spec MAY pre-fill provenance; MUST NOT pre-fill verdicts.
- **M-R5-2c.4 + P-R1-2c.4 (deferred-inventory per-entry verdict assertion):** AC-D test strengthened — assert §"Next-Slab Preparation" lists each consulted deferred-inventory entry with explicit per-entry verdict in format `<entry-id>: <RESOLVED|DEFERRED-CONTINUES|REACTIVATED-AT-SLAB-X|NOT-APPLICABLE>` + one-sentence justification. CLAUDE.md §1 binding text cited verbatim in AC.
- **M-R6-2c.4 (AC-E hard-gate own test):** Add `tests/migration/test_slab_2c_close_state_matches_m2_verdict.py` — 1 test asserting sprint-status close-state matches 2c.3 M2 verdict-state per A-R6-2c.3 hard-gate. Raises K-floor +1 to 9 firm.
- **A-R5-2c.4 + P-R2-2c.4 (canonical retrospective format):** AC-D pinned to **mirror `slab-2b-retrospective.md` structure** (canonical; more recent precedent). Inline §-header list in AC. If 2a diverges, document variance in Dev Notes.
- **A-R3-2c.4 (argparse mutual exclusion + existing-test sweep):** AC-A T1 sub-task — grep `tests/specialists/generator/` for assertions on `--name required` argparse error string and update if present; mutual-exclusion change may alter argparse error message format.
- **P-R3-2c.4 (FINAL CLOSE phrasing):** Reframe AC-C header text as `"Slab 2 (2a + 2b + 2c) harvest cycle complete; 13 entries A1–A13 under format-freeze v1; Slab 3+ harvest continues under the same freeze unless party-mode consensus + version bump."` Distinguishes harvest-cycle-complete (event) from catalog-closed (would require format-version bump). Verify against 2a-close + 2b-close for prior "harvest CLOSED" annotation pattern.
- **P-R5-2c.4 + Amelia-clarification (next-session-start-here.md AC):** Add explicit AC-J — assert (a) file updated, (b) standing "Deferred inventory status" line reflects post-2c.4 counts. CLAUDE.md §2 + §closeout hygiene cited.
- **P-R6-2c.4 (parent inheritance clarification):** AC-E adds clarifying sentence: "Slab 2 parent close-state tracks max-severity sub-slab state at close-time; M2 conditional attribution remains with Slab 2c specifically; Slab 2a + 2b retain CLOSED-GREEN."
- **P-R7-2c.4 (D12 4-line diff against 2b.17):** AC-H T1 sub-task — diff proposed D12 4-line stub against 2b.17 SLAB-CLOSING D12 close. Align if drifted; document if novel.
- **Amelia-clarification (sprint-status enum):** AC-E pin: status value = `done`, conditional context = trailing comment + reference to M2 verdict artifact (NOT new `done-with-conditional-m2` enum). Existing convention preserved.

---

## T1 Readiness Block

**Before writing any code or polish or harvest**, the dev agent reads in order:

### Standing Pre-Flight items

1. **Governance lookup** — `docs/dev-guide/migration-story-governance.json` confirms `2c-4.expected_gate_mode = "single-gate"` (rationale: null). Do not relitigate.
2. **Predecessor close evidence** — Stories 2c.1, 2c.2, 2c.3 expected `done` per sprint-status.yaml. Verify via `grep "2c-1.*done\|2c-2.*done\|2c-3.*done" sprint-status.yaml` before proceeding. If any is `in-progress` or `ready-for-dev`, abort 2c.4 and surface to operator.
3. **2c.3 M2 verdict anchor** — `_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md` §"M2 Required Evidence Summary" → consensus-verdict line. Verify it parses + is one of `{GREEN-LIGHT, CONDITIONAL-GREEN}`.
4. **2c.1 generator-polish anchor** — `_bmad-output/planning-artifacts/deferred-inventory.md` §`2c-1-generator-auto-emit-retire-removal-support` (filed at 2c.1 AC-F per Murat M-R6 meta-drift). Verify entry present + contains the meta-drift description. 2c.4 RESOLVES this entry via generator polish at AC-A.
5. **Anti-patterns catalog current state** — `docs/dev-guide/specialist-anti-patterns.md` currently A1-A13 (verified 2026-04-26: 13 entries already present; well above epic 2c.4 ≥5 minimum). 2c.4 harvests any NEW entries from 2b + 2c migration logs + closes the catalog as canonical for FR64.
6. **TEMPLATE doc** — [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md) v2.4 R1–R14. Most rules N/A (no migration in scope; this is generator polish + harvest + close). Applicable: R1 bounded scope; R6 framework drift (final close — none expected; if any surface, file as A14+); R8 K-floor recalibration; **R-CLOSE (D12) protocol** for SLAB-CLOSING.
7. **Generator entrypoint** — `skills/bmad_create_specialist/scripts/generate.py`. Atomic auto-emit C3 + idempotency + rollback contract per Story 2a.5; AC-F manual-removal workflow at 2c.1 surfaced the `--retire` flag gap (per `2c-1-generator-auto-emit-retire-removal-support` follow-on).
8. **Severance posture** — hybrid working tree is sole input surface.
9. **Slab 5b readiness pin** — generator polish at 2c.4 must leave the generator "production-ready for the optional second new specialist in Slab 5b" per epic 2c.4 binding (FR64). Slab 5b will exercise the generator on a non-Wondercraft target (e.g., Canvas LMS or Qualtrics per epic 5b.1). 2c.4 polish PRESERVES that compatibility.
10. **Slab 2c.3 hard-gate inheritance per A-R6-2c.3** — if 2c.3 closed `CONDITIONAL-GREEN`, 2c.4 close-state is `CLOSED-WITH-CONDITIONAL-M2` per the hard-gate; D12 protocol records this state.

### Slab 2c.4 artifact-existence sweep (8-point)

- **A** Sprint-status: `migration-2c-1-...: done` AND `migration-2c-2-...: done` AND `migration-2c-3-...: done`.
- **B** `slab-2c-m2-acceptance-verdict.md` consensus-verdict line parses to `GREEN-LIGHT` OR `CONDITIONAL-GREEN`.
- **C** `slab-2c-wondercraft-invariant-stub.md` exists per 2c.3 AC-D close.
- **D** Anti-patterns catalog at `docs/dev-guide/specialist-anti-patterns.md` ≥5 entries (verified at authoring 2026-04-26: 13 entries).
- **E** `2c-1-generator-auto-emit-retire-removal-support` deferred-inventory entry exists per 2c.1 close.
- **F** Wanda + wanda_validation specialists in expected states (Wanda shipped at 2b.8 + L5/L6 populated at 2c.2; wanda_validation retired-to-fixtures at 2c.1 AC-F default OR discarded per operator override).
- **G** No `slab-2c-retrospective.md` exists yet (2c.4 creates it as the SLAB-CLOSING artifact); precedents at `slab-2a-retrospective.md` + `slab-2b-retrospective.md`.
- **H** Generator at `skills/bmad_create_specialist/scripts/generate.py` is hardened post-2a.5 + post-2b.x exercise (auto-emit fired 13× across Slab 2b + 1× at 2c.1; 0 regressions).

### Epic-doc-vs-evidence cross-check (per R6)

#### (a) Framework drifts

**At SLAB CLOSE, harvest any NEW drifts surfaced across 2c.1-2c.3:**
- 2c.1 surfaced ONE meta-drift (manual C3 row removal at retirement; auto-emit machinery does NOT auto-remove). RESOLVED at 2c.4 AC-A via generator `--retire` flag implementation.
- 2c.2 surfaced ONE epic-doc divergence (`.mcp.json` wiring vs. direct-package-import). NOT a generator drift; documented as operator-curation choice in 2c.2 close notes.
- 2c.3 NO drifts (measurement story).

#### (b) TEMPLATE scope decisions

**Decision #1 — Bounded scope (per R1):** scope is (a) generator polish (`--retire` flag implementation per `2c-1-generator-auto-emit-retire-removal-support` follow-on; clearer error messages from 2c.1 feedback; minor template improvements); (b) throwaway-second-specialist regression test that exercises the polished generator end-to-end; (c) anti-patterns catalog FINAL CLOSE harvest from 2b+2c; (d) `slab-2c-retrospective.md` SLAB-CLOSING artifact; (e) D12 close protocol; (f) sprint-status close-flips. NOT in scope: changing the 9-node scaffold contract; modifying TEMPLATE doc R1-R14; touching shipped specialists (Wanda, etc.); adding new MCP tools to ALLOWED_MCP_TOOLS whitelist; designing Slab 5b (out-of-slab).

**Decision #2 — Generator polish minimum-viable scope:** ONE polish item from `2c-1-generator-auto-emit-retire-removal-support` follow-on:
- **`--retire <name>` flag** at `skills/bmad_create_specialist/scripts/generate.py` that performs the inverse of `--name <name>` emit: removes the C3 row for `<name>` from `pyproject.toml` atomically (single transactional edit); idempotent (no-op if row already absent); produces console output naming the removed row.
- Other polish items (clearer error messages, template improvements) are **opportunistic** during dev; if surfaced, applied; if not, not blocking.

**Decision #3 — Throwaway second-specialist target choice:** the throwaway is generated with `--name <throwaway_name> --mcp none --expertise-tier <pick-one> --from-skill <pick-one or skip>`. Operator-discretion at dev time on the throwaway's specifics (name + mcp + tier + skill); throwaway is **deleted** at test close. Pin: throwaway name MUST be a fresh path (e.g., `tmp_validate`) NOT collide with any shipped specialist (`wanda`, `wanda_validation`, `gary`, etc. — full 14 + wanda_validation if not yet retired). Pre-test sweep: `assert not Path(f"app/specialists/{throwaway_name}").exists()`.

**Decision #4 — Slab 2c retrospective format:** mirrors `slab-2b-retrospective.md` format (3-part: Pre-Audit Bundle / Slab Outcomes / Next-Slab Preparation per `bmad-retrospective` skill convention). Captures: per-story outcomes (2c.1/2c.2/2c.3); cumulative anti-pattern harvest; M2 verdict + addendum-pending notes (if conditional); deferred-inventory consultation per CLAUDE.md §"Deferred inventory governance" §1; 5a/5b handoff notes.

---

## Story

As a **dev agent closing Slab 2c**,
I want **(a) generator polished with `--retire <name>` flag implementing the auto-emit-row removal symmetric to `--name <name>` emit (resolving `2c-1-generator-auto-emit-retire-removal-support` follow-on); (b) a throwaway second-specialist regression test that generates + conformance-validates a fresh specialist via the polished generator + deletes it; (c) anti-patterns catalog FINAL CLOSE with confirmed 2b+2c harvest (≥5 entries, currently A1-A13 = 13 entries; harvest-not-invented per Mary harvest-gate); (d) Slab 2c retrospective at `slab-2c-retrospective.md` mirroring 2a/2b precedent format + capturing deferred-inventory consultation per CLAUDE.md governance; (e) D12 close protocol with `migration-epic-2c-slab-2-wondercraft-pilot: done` (or `done-with-conditional-m2` per A-R6-2c.3 hard-gate inheritance)**,
So that **FR64 is met (generator production-ready for Slab 5b second-specialist exercise), the anti-patterns catalog is canonical, M2 milestone closes per the 2c.3 verdict, Slab 2c is structurally complete, and Slab 5a/5b kickoff has its evidence anchor**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Sandbox-AC compliant.

### AC-2c.4-A — Generator `--retire <name>` flag implementation (resolves `2c-1-generator-auto-emit-retire-removal-support`)

- **Given** `skills/bmad_create_specialist/scripts/generate.py` currently supports `--name <name>` emit (per Story 2a.5) but NOT `--retire <name>` removal (gap surfaced at 2c.1 AC-F manual workflow); deferred-inventory entry `2c-1-generator-auto-emit-retire-removal-support` documents the meta-drift
- **When** the dev agent extends `generate.py` with `--retire <name>` flag:
  ```
  .venv/Scripts/python.exe -m skills.bmad_create_specialist.scripts.generate --retire <name>
  ```
- **Implementation pin per A-R1-2c.4 RESOLVED-BY-VERIFICATION (BINDING):** `--retire` MUST mirror 2a.5 generator's **string-level surgery** approach at `skills/bmad_create_specialist/scripts/generate.py:284-365` (`pyproject_path.read_text(encoding="utf-8")` + text manipulation; `_write_text(path, content)` for write). NO new TOML library imports (no `tomli`, `tomlkit`, `tomllib`). Single-transaction read-then-write inversion of 2a.5's emit logic.
- **T1 sub-task per A-R3-2c.4:** grep `tests/specialists/generator/` for any assertions on `--name required` argparse error-string format (the mutual-exclusion change at point 3 below alters argparse's error string from "the following arguments are required: --name" to "one of the arguments --name --retire is required"). Update affected tests OR keep `--name` as `required=True` outside the exclusive group AND add a separate runtime check in `main()` for the mutual-exclusion (less elegant but preserves existing test contract).
- **Then**:
  1. The flag removes the C3 row for `<name>` from `pyproject.toml` `[tool.importlinter]` `ignore_imports` list via 2a.5-mirroring string surgery. Single-transaction read-then-write; idempotent (no-op if row already absent — produces console message `"row for {name} not present, no-op"` per regex `^row for \\S+ not present, no-op$`).
  2. The flag does NOT touch `app/specialists/<name>/` tree or test files (those are operator-discretion to remove or retire-to-fixtures per 2c.1 AC-F precedent).
  3. The flag is mutually exclusive with `--name`: `--name foo --retire bar` raises `ArgumentError` (or runtime `SystemExit` with stderr message naming the conflict); per A-R3-2c.4, implementation may use argparse `add_mutually_exclusive_group` OR a runtime check post-parse — pick whichever preserves existing test contract.
  4. Generator preserves all other 2a.5 contracts (atomic 9-file emission, idempotency, rollback-coupled).
- **Test pin per Murat M-R1-2c.4 K-floor recount (BLOCKER):** `tests/specialists/generator/test_generator_retire_flag.py` — 4 tests = **4 K-floor units (NOT collapsible)** because each tests an orthogonal semantic property:
  1. `test_retire_removes_c3_row_for_known_name` — **mutation path:** given a fixture `pyproject.toml` with row for `tmp_x`, `--retire tmp_x` removes it; assert row count -1 + row-line absent.
  2. `test_retire_idempotent_when_row_absent` — **no-op path (different semantic branch):** given a fixture `pyproject.toml` WITHOUT row for `tmp_x`, `--retire tmp_x` no-ops; assert row count unchanged + console message regex `^row for \\S+ not present, no-op$` match.
  3. `test_retire_does_not_touch_specialist_tree` — **separation-of-concerns property:** given a fixture `app/specialists/tmp_x/` exists, `--retire tmp_x` leaves it untouched; assert directory count unchanged.
  4. `test_retire_mutually_exclusive_with_name` — **argument-validation property:** `--name foo --retire bar` raises argparse error OR runtime SystemExit; assert exit code != 0 + stderr regex match.
- **Deferred-inventory cleanup:** at AC close, mark `2c-1-generator-auto-emit-retire-removal-support` as `RESOLVED-AT-2c.4` in `_bmad-output/planning-artifacts/deferred-inventory.md`.

### AC-2c.4-B — Throwaway second-specialist regression test (FR64 generator production-readiness; SUBPROCESS-ISOLATED per A-R2)

- **Given** the generator at `skills/bmad_create_specialist/scripts/generate.py` already supports `Request(repo_root=tmp_path)` programmatic invocation per dataclass at line 59 + `(request.repo_root or _repo_root()).resolve()` at line 423 (verified 2026-04-26 per A-R2 RESOLVED-BY-VERIFICATION); `--repo-root` CLI flag NOT exposed in argparse (test uses programmatic invocation, NOT CLI subprocess against live repo)
- **And** throwaway-name MUST be UUID-suffixed per Murat M-R3-2c.4: `f"tmp_validate_{uuid.uuid4().hex[:8]}"`. Pre-test sweep `assert not Path(f"{tmp_path}/app/specialists/{name}").exists()` becomes meaningful (no static-name collision risk).
- **And** Decision #3 reframed: throwaway-name MUST be UUID-suffixed; ALL operations against `tmp_path`-rooted fake repo (NOT live tree).
- **When** the dev agent invokes the generator **programmatically against `tmp_path`** (NOT CLI against live repo):
  ```python
  from skills.bmad_create_specialist.scripts.generate import Request, generate
  request = Request(
      name=throwaway_name,        # UUID-suffixed per M-R3
      mcp="none",
      expertise_tier="L4-generic",
      from_skill=None,
      repo_root=tmp_path,         # KEY: subprocess-isolated against tmp_path (per A-R2)
  )
  result = generate(request)
  ```
- **Pre-condition**: `tmp_path` populated by fixture with minimal repo skeleton: `pyproject.toml` (with importlinter `[tool.importlinter]` C3 stanza matching real repo's shape; can be a 50-line subset), `app/specialists/__init__.py`, `tests/specialists/__init__.py`, plus `skills/bmad_create_specialist/templates/` symlinked or copied so the generator can read template files.
- **Teardown discipline per Murat M-R2-2c.4 (BLOCKER):** pytest fixture with `yield` + `addfinalizer` cleanup that runs **regardless of test outcome** (use `tmp_path`'s automatic cleanup as the outermost layer; explicit `_force_cleanup(tmp_path / "app" / "specialists" / name)` as inner layer; cleanup is idempotent).
  ```python
  @pytest.fixture
  def throwaway_specialist(tmp_path, request):
      name = f"tmp_validate_{uuid.uuid4().hex[:8]}"
      assert not (tmp_path / "app" / "specialists" / name).exists()
      yield name, tmp_path
      # Runs even on test failure
      _force_cleanup(tmp_path, name)  # idempotent: rm tree + retire row + rm tests if present
  ```
- **Then**:
  1. Within 30 seconds, generator emits the standard 9-item bundle (5 in-tree + 4 companion files) per Story 2a.5 contract; auto-emit C3 row landed in `tmp_path/pyproject.toml`.
  2. Scaffold-conformance auto-discovery (per 2b.16) picks up `tmp_path/app/specialists/<throwaway_name>/` and the new specialist passes all 14 conformance rules. **Conformance test invocation against tmp_path requires the conformance harness to accept a parametrized `repo_root`** — verify at T1 OR have AC-B test re-implement the conformance check directly against the emitted files (lighter-weight; less test coupling).
  3. The dev agent then invokes `--retire <throwaway_name>` (AC-A) programmatically (`Request(name=None, retire=throwaway_name, repo_root=tmp_path)` or equivalent) to remove the auto-emit C3 row.
  4. The dev agent then deletes `tmp_path/app/specialists/<throwaway_name>/` + companion test files (in tmp_path, NOT live).
  5. Post-cleanup state: `tmp_path/pyproject.toml` C3 row count returns to baseline (- the throwaway row); `tmp_path/app/specialists/` no longer contains the throwaway tree.
  6. Live tree (`app/specialists/`, `pyproject.toml`, `tests/specialists/`) NOT touched by the test (verified via `git status` post-test produces empty output).
- **Test pin:** `tests/migration/test_slab_2c_generator_throwaway_round_trip.py` — 2 tests:
  1. `test_generator_produces_conformant_throwaway_then_retires_cleanly` — full round-trip via `Request(repo_root=tmp_path)` programmatic invocation: generate + conformance-pass + retire + delete + assert no leakage to live tree.
  2. `test_generator_round_trip_idempotent_under_repeated_invocation` — run the round-trip TWICE in same `tmp_path` session with DIFFERENT UUID-suffixed throwaway-names; assert baseline restored after each; assert no live-tree leakage either time.

### AC-2c.4-C — Anti-patterns catalog harvest-cycle complete (≥5 entries; currently A1-A13 = 13; verdicts NOT preempted at story-author per 3-agent BLOCKER)

- **Given** `docs/dev-guide/specialist-anti-patterns.md` currently has 13 entries (A1-A13; verified 2026-04-26)
- **And** harvest-gate per Mary round-3 caveat (per catalog format-freeze): each candidate requires (a) documented burn (story-closure note citing actual defect/cycle-cost/rework evidence) OR (b) party-mode consensus that the pattern is real even without a burn. **Speculative entries rejected; story-author verdict-preemption violates the gate (per Murat M-R4 + Amelia A-R4 + Paige P-R4 BLOCKER consensus).**
- **When** 2c.4 close runs
- **Then**:
  1. **Harvest review at 2c.4 dev-time (NOT story-author-time):** dev agent reads 2c.1, 2c.2, 2c.3 close notes + Dev Notes + G6 findings for any candidate A14+ entries; assembles evidence-bundle in close notes per harvest-gate.
  2. **Candidates surfaced at story-author time (PROVENANCE ONLY; NO VERDICTS — verdicts assigned at 2c.4 dev-time):**
     - **Candidate-X1 (provenance: 2c.2 §Epic-doc-vs-runtime cross-check (a)):** "Epic literal text driving spec-vs-runtime divergence." Burn-evidence pointer: 2c.2 spec authoring spent ~30 min reconciling `.mcp.json`-vs-direct-package-import. Possible absorption: existing A3 ("architecture-vs-epics drift").
     - **Candidate-X2 (provenance: 2c.3 BLOCKER B1):** "Speculative-substrate AC referring to non-existent file." Burn-evidence pointer: 2c.3 spec AC-D drafted against `15-invariant-audit-matrix.md` that didn't exist. Possible counter-pattern: T1 sweep verifies ALL referenced artifact paths exist at story-author time.
     - **Candidate-X3 (provenance: 2c.2 spec authoring):** "Receipt-key strict-typing claim against loose-typed runtime." Burn-evidence pointer: 2c.2 AC-E original claim against `parsed.path/duration_sec/voice_id/sha256` was wrong (loose `dict[str, Any] | None` per 2b.15). Possible bundling with Candidate-X2 as generalized "AC drafted against unverified substrate state."
  3. **Dev agent at 2c.4 dev-time** runs `bmad-party-mode` round on candidates → records each as `ACCEPT-AS-A<N>` (added to A14+) or `DEFER-WITH-REASON` or `ABSORB-INTO-A<existing>` in Completion Notes per harvest-gate. **Spec author makes NO pre-commitment.**
  4. Catalog count post-2c.4: A1-A13 (existing 13) + 0-N new per actual harvest-gate evaluation. Comfortably ≥5 epic minimum + ≥7 preferred minimum regardless of net-add.
  5. **FINAL HEADER ANNOTATION per Paige P-R3-2c.4 (canonical-closure phrasing distinguishing harvest-cycle-complete from catalog-closed):** catalog header gains the line: `"Slab 2 (2a + 2b + 2c) harvest cycle complete; 13+ entries A1-A<final> under format-freeze v1; Slab 3+ harvest continues under the same freeze unless party-mode consensus + version bump."` Format-freeze v1 preserved. **Verify against 2a-close + 2b-close in Dev Notes** — if no prior "harvest cycle complete" annotation exists, this is a NEW header pattern; document the addition without claiming it's a continuation of a precedent.
- **Test pin:** `tests/migration/test_slab_2c_anti_patterns_catalog_final.py` — 1 test asserting:
  1. `docs/dev-guide/specialist-anti-patterns.md` exists.
  2. Entry count (regex `^### A\d+\.`) ≥ 5 (epic minimum) AND ≥ 13 (post-2b.17 baseline; ensures no regression-deletion).
  3. Header contains the harvest-cycle-complete annotation string `"Slab 2 (2a + 2b + 2c) harvest cycle complete"`.
  4. Format-freeze v1 line `"Format version: 1"` present (no version bump without party-mode consensus per format-freeze).

### AC-2c.4-D — Slab 2c retrospective at `slab-2c-retrospective.md` (NEW SLAB-CLOSING artifact; mirrors `slab-2b-retrospective.md` canonical structure per A-R5 + P-R2)

- **Given** Slab 2a + Slab 2b retrospectives exist at `_bmad-output/implementation-artifacts/slab-2a-retrospective.md` + `slab-2b-retrospective.md` per `bmad-retrospective` skill format
- **And** per A-R5-2c.4 + P-R2-2c.4: **`slab-2b-retrospective.md` is the canonical structural template** (more recent precedent, presumably incorporated 2a's lessons). Inline §-header list below. If 2a diverges from 2b on any §-header, dev agent documents the variance in Dev Notes and follows 2b.
- **When** the dev agent authors `_bmad-output/implementation-artifacts/slab-2c-retrospective.md` mirroring `slab-2b-retrospective.md` 3-part structure
- **Then** the retrospective contains:
  - **§"Pre-Audit Bundle"** — sprint key + slab-key + dates + storypoint roll-up (2c.1 = 2pts; 2c.2 = 3pts; 2c.3 = 1pt; 2c.4 = 2pts; **total 8pts** vs ~4 stories) + commit anchors per story close
  - **§"Slab Outcomes"** — per-story outcome (BMAD-CLOSED + verdict; M2 state); cumulative anti-pattern harvest verdict (per AC-C, recorded post-actual-harvest-gate at 2c.4 dev-time); generator polish verdict (per AC-A); throwaway round-trip verdict (per AC-B); M2 verdict roll-up from 2c.3
  - **§"Next-Slab Preparation"** — **deferred-inventory consultation per CLAUDE.md §"Deferred inventory governance" §1 (BINDING).** Per CLAUDE.md §1 verbatim: *"Record which entries were consulted + the reactivation verdict per entry in the retrospective artifact."* Read `_bmad-output/planning-artifacts/deferred-inventory.md` against Slab 2c new substrate / evidence / learnings; flag now-ready-to-reactivate entries; **record per-entry verdict in format `<entry-id>: <RESOLVED|DEFERRED-CONTINUES|REACTIVATED-AT-SLAB-X|NOT-APPLICABLE>` + one-sentence justification per Murat M-R5-2c.4 + Paige P-R1-2c.4 BLOCKER consensus.** Notable consultations expected (≥3 per test assertion): `2c-2-mcp-architecture-divergence-from-epic-literal` (DEFERRED-CONTINUES); `2c-2-receipt-strict-typed-artifact-metadata` (DEFERRED-CONTINUES); `2c-3-m2-verdict-conditional-on-2c-2-live-artifact` (RESOLVED if 2c.2 AC-D-OP completed OR DEFERRED-CONTINUES); `2c-1-generator-auto-emit-retire-removal-support` (RESOLVED-AT-2c.4 per AC-A).
  - **§"Slab 5a / 5b Handoff"** — `slab-2c-wondercraft-invariant-stub.md` is the M5 invariant-audit-matrix-creation seed for Slab 5a; generator at `skills/bmad_create_specialist/` is FR64-ready for Slab 5b second-specialist exercise; named-but-not-filed follow-ons go to deferred-inventory per CLAUDE.md §3.
- **Test pin per Murat M-R5-2c.4 + Paige P-R1-2c.4 (strengthened from structural-presence to per-entry-verdict assertion):** `tests/migration/test_slab_2c_retrospective_present.py` — 1 test asserting:
  1. `_bmad-output/implementation-artifacts/slab-2c-retrospective.md` exists.
  2. Four required §-headers present (regex `^## Pre-Audit Bundle`, `^## Slab Outcomes`, `^## Next-Slab Preparation`, `^## Slab 5a / 5b Handoff`) — mirrors slab-2b precedent.
  3. §"Next-Slab Preparation" contains `"deferred-inventory.md"` reference (CLAUDE.md §1 structural).
  4. **PER-ENTRY VERDICT ASSERTION (M-R5 + P-R1):** §"Next-Slab Preparation" lists ≥3 consulted entries each with explicit verdict in format `<entry-id>:\s*(RESOLVED|DEFERRED-CONTINUES|REACTIVATED-AT-SLAB-X|NOT-APPLICABLE)`. Specifically: regex match for `2c-1-generator-auto-emit-retire-removal-support:\s*RESOLVED` (since AC-A resolves it).

### AC-2c.4-E — Conditional-resolution responsibility inheritance from 2c.3 A-R6 hard-gate (with own-test per Murat M-R6 + sprint-status enum clarification per Amelia)

- **Given** 2c.3 closed with M2 verdict either `GREEN-LIGHT` (full close) OR `CONDITIONAL-GREEN` (operator-window pending per 2c.2 AC-D-OP DEFERRED)
- **When** 2c.4 D12 close protocol executes
- **Then** (sprint-status enum clarification per Amelia: status value stays `done`; conditional context recorded as **trailing comment** referencing the M2 verdict artifact, NOT a new `done-with-conditional-m2` enum):
  - **If 2c.3 verdict = GREEN-LIGHT:** Slab 2c closes as `CLOSED-GREEN`; M2 milestone marked `GREEN-LIGHT 2026-04-XX`; sprint-status: `migration-epic-2c-slab-2-wondercraft-pilot: done  # M2 GREEN-LIGHT 2026-04-XX per slab-2c-m2-acceptance-verdict.md`.
  - **If 2c.3 verdict = CONDITIONAL-GREEN per A-R6 hard-gate:** Slab 2c closes as `CLOSED-WITH-CONDITIONAL-M2`; M2 milestone remains `CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM`; sprint-status: `migration-epic-2c-slab-2-wondercraft-pilot: done  # M2 CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM per slab-2c-m2-acceptance-verdict.md; operator-window addendum pending per 2c-3-m2-verdict-conditional-on-2c-2-live-artifact deferred-inventory entry`.
- **Parent inheritance clarification per Paige P-R6-2c.4:** "Slab 2 (parent) close-state tracks max-severity sub-slab state at close-time; M2 conditional attribution remains with Slab 2c specifically; Slab 2a + 2b retain CLOSED-GREEN. Parent label `done  # CONDITIONAL-M2 from 2c only` honestly reflects the state without implying 2a/2b carry the conditional."
- **Test pin per Murat M-R6-2c.4 (BLOCKER — hard-gate own test, not piggybacking):** `tests/migration/test_slab_2c_close_state_matches_m2_verdict.py` — 1 test asserting:
  ```python
  def test_slab_2c_close_state_matches_2c3_m2_verdict():
      verdict = parse_consensus_verdict("_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md")
      sprint_state, sprint_comment = parse_sprint_status_with_comment("migration-epic-2c-slab-2-wondercraft-pilot")
      assert sprint_state == "done"
      if verdict == "GREEN-LIGHT":
          assert "GREEN-LIGHT" in sprint_comment
          assert "CONDITIONAL" not in sprint_comment
      elif verdict == "CONDITIONAL-GREEN":
          assert "CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM" in sprint_comment
          assert "2c-3-m2-verdict-conditional-on-2c-2-live-artifact" in sprint_comment
      else:
          pytest.fail(f"verdict {verdict} not in {{GREEN-LIGHT, CONDITIONAL-GREEN}}")
  ```
  Defends the hard-gate enforcement against silent-drift across the cross-artifact assertion-spreading approach (sprint-status governance + AC-D retrospective text + 2c.3 AC-A/AC-C verdict-text). +1 K-floor unit firm.

### AC-2c.4-F — Anti-pattern catalog harvest at SLAB CLOSE (per R6)

- **Given** 2c.4 close runs the final 2b+2c harvest per AC-C
- **When** any A14+ candidate surfaces during 2c.4 dev (e.g., from generator polish friction OR throwaway-round-trip surprises)
- **Then** the candidate is added per harvest-gate; if absorbed by existing A1-A13, document the absorption in 2c.4 close notes; format-freeze v1 preserved.

### AC-2c.4-G — TEMPLATE compliance (per R1–R14 v2.4)

R1–R14 v2.4 honored where applicable. Most rules N/A (no migration; this is generator polish + harvest + close). Applicable: R1 bounded scope (Decision #1); R6 framework-drift harvest (per AC-C + AC-F); R8 K-floor recalibration (~1.3× = target 8 / floor 6 honored).

### AC-2c.4-H — D12 close protocol (single-gate; SLAB-CLOSING; FOUR-line per A-R7; verified against 2b.17 SLAB-CLOSING per Paige P-R7)

**T1 sub-task per Paige P-R7-2c.4:** diff proposed D12 4-line stub against 2b.17 SLAB-CLOSING D12 close at `_bmad-output/implementation-artifacts/migration-2b-17-anti-patterns-catalog-consolidation-slab-close.md`. If lines align, note "4-line format per 2b.17 precedent" in 2c.4 close stub. If drifted, either align or document drift with rationale in Dev Notes.

1. **Invariant preservation:** Slab-1 + Slab-2a + Slab-2b + Slab-2c.1-2c.3 substrate intact; generator polish at AC-A is additive (`--retire` flag; no contract changes); throwaway-round-trip at AC-B leaves no artifacts in live tree (subprocess-isolated against tmp_path per A-R2); FR14 architectural enforcement validated by 2b.16 auto-discovery handling the throwaway specialist correctly.
2. **Anti-pattern harvest:** per AC-C harvest-cycle-complete annotation + actual harvest-gate verdicts at 2c.4 dev-time (NOT preempted at story-author per 3-agent BLOCKER consensus). 13-N entries (N depends on harvest verdicts).
3. **Migration-guide update:** §12 framing sentence may add a Slab-2c-close note ("Slab 2c closed 2026-04-XX with Wondercraft Pilot complete + generator FR64-ready; harvest cycle complete at A1-A<final> canonical under format-freeze v1"). `slab-2c-retrospective.md` is the SLAB-CLOSING artifact.
4. **TEMPLATE compliance:** R1, R6, R8 honored. Numeric anchors recorded: throwaway round-trip duration; anti-patterns count post-harvest; M2 verdict-state per AC-E.

### AC-2c.4-I — Sprint-status state-flips at filing AND at close

At filing: `migration-2c-4-scaffold-generator-polish-and-anti-patterns-final: ready-for-dev`. At close: `migration-2c-4-...: done`; `migration-epic-2c-slab-2-wondercraft-pilot: done` (with trailing-comment per AC-E enum-clarification); Slab 2 parent state updated per AC-E parent-inheritance clarification. `last_updated` field updated.

### AC-2c.4-J — `next-session-start-here.md` update (per Paige P-R5 + Amelia clarification + CLAUDE.md §2 + §closeout hygiene)

- **Given** CLAUDE.md §closeout hygiene mandates: "update `sprint-status.yaml` first, update `next-session-start-here.md` second"; CLAUDE.md §"Deferred inventory governance" §2 mandates standing "Deferred inventory status" line reflects current counts (backlog epics / deferred stories / follow-ons)
- **When** 2c.4 close runs after AC-I sprint-status flip
- **Then**:
  1. `next-session-start-here.md` is updated to reflect Slab 2c CLOSED handoff:
     - Active-slab line transitions Slab 2c → Slab 2d (or whatever epic kicks off next, per current planning).
     - "Deferred inventory status" line reflects post-2c.4 counts (backlog epics / deferred stories / follow-ons; numerics derived from `_bmad-output/planning-artifacts/deferred-inventory.md` post-AC-D consultation cleanup).
     - M2 milestone status reflects 2c.3 verdict (GREEN-LIGHT or CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM per AC-E).
     - Hot-start guidance for next session names the post-Slab-2c next priority.
- **Test pin:** `tests/migration/test_slab_2c_next_session_start_here_updated.py` — 1 test asserting:
  1. `next-session-start-here.md` exists.
  2. File contains `"Slab 2c"` reference with `"CLOSED"` or `"closed"` keyword.
  3. "Deferred inventory status" line present (regex `^Deferred inventory status:` OR similar; verify exact line shape against current `next-session-start-here.md` precedent at T1).

---

## File Structure Requirements

### NEW files (PERSISTENT)

```
_bmad-output/implementation-artifacts/
└── slab-2c-retrospective.md                              # SLAB-CLOSING retrospective per AC-D (mirrors slab-2b-retrospective.md per A-R5+P-R2)

tests/specialists/generator/
└── test_generator_retire_flag.py                         # 4 tests (AC-A; 4 K-floor units per M-R1 BLOCKER recount; NOT collapsible)

tests/migration/
├── test_slab_2c_generator_throwaway_round_trip.py        # 2 tests (AC-B; subprocess-isolated tmp_path per A-R2 BLOCKER)
├── test_slab_2c_anti_patterns_catalog_final.py           # 1 test (AC-C; harvest-cycle-complete annotation, NOT verdict-preempted)
├── test_slab_2c_retrospective_present.py                 # 1 test (AC-D; per-entry verdict assertion per M-R5+P-R1 BLOCKER)
├── test_slab_2c_close_state_matches_m2_verdict.py        # 1 test (AC-E; hard-gate own test per M-R6 BLOCKER)
└── test_slab_2c_next_session_start_here_updated.py       # 1 test (AC-J; CLAUDE.md §closeout hygiene per P-R5)
```

### MODIFIED files

- `skills/bmad_create_specialist/scripts/generate.py` — `--retire` flag added per AC-A; **string-level surgery (mirrors 2a.5; NO new TOML library) per A-R1 RESOLVED-BY-VERIFICATION**. Mutually exclusive with `--name` (argparse exclusive group OR runtime check post-parse, whichever preserves existing test contract per A-R3).
- `docs/dev-guide/specialist-anti-patterns.md` — harvest-cycle-complete annotation in header per AC-C (NOT "FINAL CLOSE" — distinguishes harvest-cycle-event from format-version-bump per P-R3); 0-N new entries per actual harvest-gate verdicts at 2c.4 dev-time (NOT story-author preemption per 3-agent BLOCKER consensus).
- `_bmad-output/planning-artifacts/deferred-inventory.md` — `2c-1-generator-auto-emit-retire-removal-support` marked RESOLVED-AT-2c.4 per AC-A. New deferred-inventory entries (if any) per AC-D §"Next-Slab Preparation" with per-entry verdicts per M-R5+P-R1.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-I; status enum stays `done` with trailing comment per AC-E enum-clarification (NOT new `done-with-conditional-m2` enum).
- `next-session-start-here.md` — per AC-J (CLAUDE.md §closeout hygiene + §2 standing deferred-inventory line).

### NOT modified

- 9-node scaffold contract (`tests/integration/scaffold_conformance/scaffold_contract.py`) — DO NOT TOUCH.
- TEMPLATE doc (`docs/dev-guide/specialist-migration-template.md`) — DO NOT TOUCH (R1-R14 v2.4 stable).
- All shipped specialists (`app/specialists/{aria,cd,desmond,enrique,gary,irene,kim,kira,mira,quinn_r,tamara,texas,tracy,vera,vyx,wanda}/`) — DO NOT TOUCH.
- ALLOWED_MCP_TOOLS whitelist at `skills/bmad_create_specialist/scripts/generate.py:18-20` — DO NOT TOUCH (operator decision to extend).

---

## Testing Requirements

**K-target ~1.3× (target 8 / floor 6).** Test count and K-floor accounting per Murat M-R18 honest-count discipline + post-amendment recount per Murat M-R1 BLOCKER + M-R6 BLOCKER + Paige P-R5:

| AC | Tests collected | Honest K-floor units |
|---|---|---|
| A | 4 (NOT collapsible per M-R1 BLOCKER; mutation + no-op + separation + arg-validation are orthogonal) | **4** |
| B | 2 (round-trip + idempotent-under-repetition) | **2** (each is independent property) |
| C | 1 (count + harvest-cycle-complete annotation + format-freeze; multi-property single test) | **1** |
| D | 1 (presence + 4 §-headers + per-entry verdict assertion per M-R5+P-R1) | **1** (verdict-assertion is property-collapsible with structural assertions in same test file) |
| E | 1 (hard-gate own test per M-R6 BLOCKER) | **1** |
| J | 1 (next-session-start-here.md update per P-R5) | **1** |
| **Total** | **10 collected** | **10 firm K-floor units** |

**Honest K-floor: 10 (well above floor 6 minimum).** Recalibrate K-target up to ~1.5× (target 10 / floor 8) post-amendments to honestly reflect the expanded test surface, OR accept K-target ~1.3× as a SOFT framing acknowledging the stretch — operator decision at story-open. Recommendation: recalibrate to ~1.4-1.5× (the BLOCKER amendments materially expanded the K surface; pretending it's still ~1.3× would be the K-target inflation pattern that the riders themselves were preventing).

**Regression target at T8:** ≥562 passed / ≥7 skipped placeholder-key (Slab 2b close baseline preserved; Slab 2c additions over 2c.1-2c.3 add ~12-14 collected); +10 collected at file level for 2c.4. Throwaway round-trip leaves NO net artifacts in live tree (subprocess-isolated against `tmp_path` per A-R2 BLOCKER). Import-linter 3/3 KEPT throughout. Ruff clean. Sandbox-AC PASS (no live API calls; all polish + tests via shipped Python tooling).

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_

### T1 Readiness

_(Populated at T1)_

### T2–T7 Implementation Notes

_(Populated during implementation)_

### T8 Regression Evidence + Polish + Harvest Outcomes

_(Populated at T8 with throwaway round-trip duration + anti-pattern harvest verdict + retrospective notes + M2 verdict-state)_

### G6 Layered Code-Review (Blind Hunter / Edge Case Hunter / Acceptance Auditor)

_(Single-gate self-conducted per CLAUDE.md; populated at T8)_

### D12 Close Stub

_(Populated at story close per AC-2c.4-H)_

### Completion Notes

_(Populated at story close)_

### File List

_(Populated at story close)_
