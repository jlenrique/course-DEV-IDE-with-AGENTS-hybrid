# Migration Story 2c.2: Wanda L5 + L6 Expertise Population + Live Wondercraft API Artifact (executes 2b.8 deferred AC-B-OP)

**Status:** ready-for-dev
**Sprint key:** `migration-2c-2-wanda-l5-l6-expertise-and-live-api`
**Epic:** Slab 2c (migration Epic 2c — Wondercraft Pilot + Generator Validation) — **second story; Path-A-residual completion**.
**Pts:** 3 | **Gate:** single (per governance JSON `2c-2.expected_gate_mode = "single-gate"`, rationale: null — expertise-population + deferred-live-API completion; no schema-shape, no lane-boundary, no invariant-preservation). **K-target:** ~1.3× (target 10 / floor 8; documentation-heavy + sanctum-population + ONE new live-API integration test + L5/L6 fingerprint regression).

**Lean party-mode amendments applied 2026-04-26 (Murat + Amelia):** 2 BLOCKERs RESOLVED-BY-VERIFICATION + 5 RIDERs integrated:
- **A-R1-2c.2 BLOCKER (live_api marker precedent) RESOLVED-BY-VERIFICATION:** Marker IS registered at `pyproject.toml:62-63` + `tests/conftest.py:88`; skip mechanism is `--run-live` opt-in via `pytest_collection_modifyitems` (NOT `addopts -m "not live_api"`). Spec AC-D rewritten to use the actual mechanism.
- **A-R2-2c.2 BLOCKER (dispatch return-shape keys) RESOLVED-WITH-NARROWING:** `WandaDispatchReceipt.wanda_audio: dict[str, Any] | None` per `app/models/dispatch/wanda/receipt.py` is loose-typed (NOT strict-typed for `path/duration_sec/voice_id/sha256`); dispatch wrapper at `app/specialists/wanda/wondercraft_dispatch.py:169-172` returns `{capability, receipt: <raw client output or mock dict>}` where receipt structure varies per capability. AC-E NARROWED: round-trip is **filesystem sha256 (LIVE_ARTIFACT_METADATA.md) ↔ filesystem sha256 (artifact bytes)**, NOT receipt-key extraction.
- **A-R3-2c.2:** L5 stays at `skills/bmad-agent-wondercraft/references/L5-podcast-production/`; explicit AC sub-criterion added at AC-B for `WANDA_REFERENCES` tuple extension at `graph.py:28-40`. Decision #1 reframed: "no behavioral changes to dispatch/scaffold; tuple extension for new reference content is in-scope minimal extension."
- **A-R4-2c.2:** AC-D-OP-FALLBACK added — if `create_scripted_podcast` exceeds $5 ceiling, operator may run `create_podcast` (shorter format) at $1-2 ceiling; live artifact marked "scripted preferred, simple acceptable."
- **A-R5-2c.2:** AC-A reframed — dev creates directory + placeholder skeleton files with `<!-- TODO: operator-populate via First Breath -->` markers + minimal valid frontmatter; operator populates persona content in own session before AC-G. AC-A acceptance is **structural** (files exist, git-tracked, valid frontmatter), NOT content-quality.
- **A-R6-2c.2:** AC-A clarifies "INDEX.md is operator-facing reference; runtime does not parse it" — prevents over-engineering as runtime manifest.
- **M-R18 (recall) — K-floor honesty:** AC-B `test_wanda_references_tuple_contains_l5_paths` 3-case parametrize collapses to 1 K-floor unit (membership-echo, not orthogonal property). Honest K-floor: 7. AC-B gains ONE behavior test `test_read_wanda_references_includes_l5_bodies_in_declared_order` to legitimately reach K-floor 8 (asserts `_read_wanda_references()` output contains each L5 file body in declared tuple order; verifies read path resolves the new sub-directory + ordering preserved).
- **M-R31-2c.2 (NEW):** AC-D NEGATIVE-test subprocess MUST sanitize `PYTEST_ADDOPTS` env var (`env={**{k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}, "PYTEST_ADDOPTS": ""}` with rationale comment) AND assert collection-count + deselection-count via structured pytest output parse, NOT free-text-string-match. Prevents subprocess-test flake from inherited dev environment.
- **M-R32-2c.2 (NEW) — RETIRED-MOOT:** addopts merge concern obviated by `--run-live` opt-in mechanism (no `-m` filter in `addopts` to merge with).
- **M-R33-2c.2 (NEW):** AC-D live-artifact duration assertions MUST be range-bounded (lower AND upper): `4*60 ≤ duration_sec ≤ 10*60`. Upper bound is runaway-generation canary paired with Decision #4 cost ceiling.
- **M-R34-2c.2 (NEW):** Skip-when-deferred AC-E test stays as SKIPPED-WITH-REASON in tree at story close if AC-D-OP defers; auto-files `2c-2-ac-e-round-trip-pending-live-artifact` deferred-inventory follow-on at story close. Round-trip validation does NOT migrate to a separate story.

**Path-A-residual framing:** Wanda was hand-authored at 2b.8 (commit `b14d54c`) with REST-API tool-dispatch wired against `scripts/api_clients/wondercraft_client.py` + 6-mode capability fan-out (EP/DP/AS/MB/CM/AH) + `wanda_audio` strict-typed receipt field (added at 2b.15). At 2b.8 close, three items deferred:

- **Sanctum cold-read (graceful-degrade per 2b.8 AC-D):** `_bmad/memory/wanda-sidecar/` directory absent; `_read_sanctum_digest` returns `""`. Sanctum population marked DEFERRED-OPERATOR-WINDOW.
- **L5/L6 expertise enrichment:** Wanda's `_read_wanda_references` already reads `skills/bmad-agent-wondercraft/references/` (11 files: 6 capability + 5 operational); however, the **3 podcast-production reference files** specifically named in epic 2c.2 (storytelling framework + audio-production patterns + narration-length-vs-engagement) are NOT present in the substrate. L6 operational context (voice-ID catalog + episode template + style-guide overrides) totally absent.
- **Live API artifact (per 2b.8 AC-B-OP):** "DEFERRED-PENDING-OPERATOR-WINDOW" — no live podcast artifact has been produced.

Story 2c.2 closes all three. The 2c.1 AC-B-OP smoke-test ($0.50 cap; "API answers + audio-file lands + sha256 computes") is **distinct** from 2c.2 live execution (production-quality artifact for M2 evidence). 2c.1 validates the GENERATOR-emitted specialist; 2c.2 validates the SHIPPED specialist end-to-end.

---

## T1 Readiness Block

**Before writing any code**, the dev agent reads in order:

### Standing Pre-Flight items

1. **Governance lookup** — `docs/dev-guide/migration-story-governance.json` confirms `2c-2.expected_gate_mode = "single-gate"` (rationale: null). Do not relitigate.
2. **2b.8 close evidence** — `_bmad-output/implementation-artifacts/migration-2b-8-wanda-wondercraft-scaffold-migration.md` AC-B-OP DEFERRED block + AC-D graceful-degrade decision. Story 2c.2 EXECUTES the deferred items; does NOT re-author Wanda's `graph.py`/`wondercraft_dispatch.py`.
3. **Wanda runtime** — `app/specialists/wanda/{graph.py, wondercraft_dispatch.py, state.py, model_config.yaml}` shipped. **DO NOT TOUCH `_act` orchestration**; only extend `_read_wanda_references` tuple + `WANDA_REFERENCES_DIR` constant if L5 reference files land in a new sub-directory (Decision #2 below).
4. **Wondercraft client substrate** — `scripts/api_clients/wondercraft_client.py` exposes `check_connectivity / list_episodes / create_podcast / create_scripted_podcast / create_conversation_podcast / get_job_status / wait_for_job`. Reads `WONDERCRAFT_API_KEY` from `.env` at instantiation.
5. **TEMPLATE doc** — [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md) v2.4 R1–R14. Most rules N/A (no migration in scope; this is post-migration enrichment). R7 resolution-trail uniformity preserved (no `_plan` semantics changed). R8 K-floor rules apply.
6. **Live API marker mechanism (verified 2026-04-26 per A-R1 BLOCKER resolution)** — `live_api` marker is ALREADY registered at `pyproject.toml:62-63` AND `tests/conftest.py:88` (and `live_api_e2e` companion). Skip mechanism: `--run-live` opt-in via `pytest_collection_modifyitems` at `tests/conftest.py:129-149` (Pass 1 deselects `live_api` items unless `--run-live` flag passed). NO `addopts -m "not live_api"` filter exists; do NOT add one. Default `pytest` invocation deselects live_api tests automatically; explicit `--run-live` opts them in.
7. **Sanctum BMB pattern** — `_bmad/memory/bmad-agent-marcus/{INDEX.md,PERSONA.md,chronology.md,access-boundaries.md}` is the canonical full-population reference. Wanda's sidecar directory follows the **sidecar** convention (`_bmad/memory/wanda-sidecar/`) per Wanda's existing `SANCTUM_DIR` constant at `app/specialists/wanda/graph.py:26`, NOT the `bmad-agent-wanda/` BMB layout (Wanda is a non-BMB specialist; sidecar pattern is correct per Slab-2b precedent — `kira-sidecar`, `vyx-sidecar`, etc.).
8. **Severance posture** — hybrid working tree is sole input surface.
9. **Predecessor close evidence** — Story 2c.1 expected `done` before 2c.2 opens (M2 evidence dependency: 2c.1 produces the diff-evidence Markdown; 2c.2 does NOT depend on it but assumes Wanda's runtime is unchanged from 2b.8 close + 2b.15 dispatch family completion).

### Slab 2c.2 artifact-existence sweep (7-point)

- **A** `app/specialists/wanda/{graph.py, wondercraft_dispatch.py, state.py, model_config.yaml}` exists per 2b.8 close.
- **B** `app/specialists/wanda/expertise/README.md` exists (placeholder per 2b.8); `app/specialists/wanda/expertise/` has NO `L5/` or `L6/` subdirectories yet.
- **C** `_bmad/memory/wanda-sidecar/` does NOT exist (graceful-degrade per 2b.8 AC-D).
- **D** `skills/bmad-agent-wondercraft/references/` exists with 11 files (verified at 2b.8); 3 podcast-production reference files (storytelling framework + audio-production patterns + narration-length-vs-engagement) NOT among them.
- **E** `scripts/api_clients/wondercraft_client.py` exists per 2b.8 substrate verification.
- **F** `.env` has `WONDERCRAFT_API_KEY` populated on operator's machine (operator-side; not dev-agent visible). Dev-agent verifies via `os.environ.get("WONDERCRAFT_API_KEY")` presence-check at test time and `pytest.skip(...)` if absent.
- **G** `pyproject.toml` `[tool.pytest.ini_options].markers` contains the `live_api` marker registration (verified 2026-04-26 at lines 62-63); `tests/conftest.py:68-149` registers `--run-live` opt-in flag + `pytest_collection_modifyitems` deselect-by-default Pass 1 logic.
- **H** `app/models/dispatch/wanda/receipt.py` `WandaDispatchReceipt.wanda_audio: dict[str, Any] | None` (loose-typed; verified 2026-04-26). Dispatch wrapper at `app/specialists/wanda/wondercraft_dispatch.py:169-172` returns `{capability: <code>, receipt: <raw client output or mock dict>}`; receipt key-shape varies per capability (EP/DP/AS pass through raw `wondercraft_client.create_*` returns; MB/CM/AH return mock dicts). NO guarantee that `parsed.path/duration_sec/voice_id/sha256` keys are present.

### Epic-doc-vs-runtime cross-check (per R6)

#### (a) Framework drifts

**ONE divergence from epic literal text 2c.2 ACs (operator-ratified at story-author time per Path-A absorption):**

- **Epic 2c.2 AC-2 says:** "the dev agent adds `.mcp.json` entry for wondercraft-api + authors `app/specialists/wondercraft/act.py` calling the MCP tool"
- **Runtime reality:** Wondercraft was implemented as **direct-package-import via `scripts/api_clients/wondercraft_client.py`** at 2b.8 (Decision #2-bis). `.mcp.json` has NO wondercraft entry. Wanda's `_act` already calls `wondercraft_client` via `wondercraft_dispatch.py`.
- **Resolution:** Spec adopts the **direct-package-import path**. NO `.mcp.json` entry added. NO `app/specialists/wondercraft/` tree created. AC-D below executes the live API call via the existing direct-package-import wiring. **Documented as `2c-2-mcp-architecture-divergence-from-epic-literal` follow-on** in deferred-inventory for future epic-doc reconciliation.

#### (b) TEMPLATE scope decisions

**Decision #1 — Bounded scope (per R1; reframed per A-R3-2c.2):** scope is sanctum population + L5 podcast-production references + L6 operational context + ONE live Wondercraft API podcast artifact (operator-gated) + the **minimal `WANDA_REFERENCES` tuple extension at `graph.py:28-40` to wire the new L5 file paths into the existing reference-loader**. **No behavioral changes to dispatch / scaffold orchestration / `_act` / `_plan` semantics**; tuple extension is in-scope minimal extension for new reference-content discovery. NOT in scope: redesigning Wanda's `_act`, multi-artifact production, voice-cloning research, episode-quality benchmarking, .mcp.json wiring (per (a) divergence above), generator regeneration of Wanda (Path B at 2c.1 is the regeneration story), `_read_wanda_references` refactor (additive tuple extension only).

**Decision #2 — L5 reference files location:** L5 files land at `skills/bmad-agent-wondercraft/references/L5-podcast-production/` (NEW sub-directory; existing 11 files stay at the parent). Wanda's `WANDA_REFERENCES` tuple extended with the 3 new files (full relative paths from `WANDA_REFERENCES_DIR`). Rationale: keeps reference-substrate co-located with the operator-curated skill (single source-of-truth) and matches the 2b.8 wiring (`WANDA_REFERENCES_DIR` already points at the skill).

**Decision #3 — L6 operational context location:** L6 file at `_bmad/memory/wanda-sidecar/L6-operational/wondercraft-context.md` (operational state belongs in sanctum, not skill substrate; sanctum is per-deployment-mutable, skill is operator-curated-stable). `_read_sanctum_digest` already reads anything under `SANCTUM_DIR` recursively, so no graph wiring change.

**Decision #4 — Live API single-artifact ceiling:** ONE live API podcast artifact at AC-D-OP. Cost ceiling: $5.00 (vs. 2c.1 AC-B-OP $0.50 smoke-test ceiling — 2c.2 produces production-quality content using `create_scripted_podcast` capability). Above this, defer to follow-on. Stored in `tests/fixtures/specialists/wanda/live_artifacts/<YYYY-MM-DD>/<sha256>.<ext>`.

---

## Story

As a **dev agent completing the Path-A residual items deferred at 2b.8 close**,
I want **`_bmad/memory/wanda-sidecar/` populated with PERSONA + access-boundaries + chronology + INDEX (BMAD sidecar pattern); 3 podcast-production reference files at `skills/bmad-agent-wondercraft/references/L5-podcast-production/` wired into Wanda's `WANDA_REFERENCES` tuple; L6 operational context at `_bmad/memory/wanda-sidecar/L6-operational/wondercraft-context.md`; ONE live Wondercraft API artifact (operator-gated, ~$5.00 cost ceiling) produced via `create_scripted_podcast` and stored in fixtures; Wanda's `wanda_audio` receipt artifact-metadata enrichment validated against the live artifact**,
So that **Wanda's expertise stack reflects genuine podcast-production knowledge beyond the generator stub, the 2b.8-deferred live-API evidence is on file, and M2 acceptance has its second defensible measurement (Path A end-to-end production-quality artifact paired with Path B 2c.1 generator-validation evidence)**.

---

## Acceptance Criteria

All ACs are dev-agent-executable except AC-2c.2-D-OP (operator-gated live Wondercraft API call). Sandbox-AC compliant.

### AC-2c.2-A — `_bmad/memory/wanda-sidecar/` skeleton creation (dev structural; operator content-population per A-R5)

- **Given** `_bmad/memory/wanda-sidecar/` does not exist (graceful-degrade per 2b.8 AC-D)
- **When** the dev agent creates the directory tree with **skeleton placeholder files** carrying minimal valid frontmatter + `<!-- TODO: operator-populate via First Breath ceremony -->` markers:
  ```
  _bmad/memory/wanda-sidecar/
  ├── INDEX.md                        # operator-facing reference index (NOT runtime-parsed per A-R6); references all sanctum files + L6 path
  ├── PERSONA.md                      # skeleton: title + 1-line role + TODO marker; operator populates persona/voice/capability-scope
  ├── access-boundaries.md            # skeleton: title + Wondercraft cost-ceiling note from Decision #4 + TODO marker for operator verbs
  ├── chronology.md                   # one entry: "2c.2 sanctum skeleton created 2026-04-26 by dev agent; operator-population pending"
  └── L6-operational/
      └── wondercraft-context.md      # skeleton: required-section headers (## Voice-ID catalog / ## Episode-template skeleton / ## Style-guide overrides) + TODO markers per section; operator populates content per Decision #3
  ```
- **Then** `_read_sanctum_digest()` returns a non-empty newline-separated list of `<rel-path>\t<sha256>` lines for the 5 sanctum files (sorted lexically); cache-prefix CRLF→LF normalization preserved per Wanda 2b.8 implementation at `app/specialists/wanda/graph.py:80-96`.
- **Authoring authority pin per A-R5:** dev creates **structural skeletons + TODO markers + valid frontmatter ONLY** — content quality (full persona narrative, voice-ID catalog values, access-boundary verb list) is **operator territory** populated via First Breath ceremony in operator's own session before AC-G party-mode review. AC-A acceptance is **structural** (files exist + are git-tracked + parse as valid Markdown + carry TODO markers + AC-A regex-pinned section headers present), NOT content-quality.
- **INDEX.md scope clarification per A-R6:** INDEX.md is **operator-facing reference only**; Wanda's runtime at `app/specialists/wanda/graph.py:80-96` globs `sanctum_dir.rglob("*")` and digests every file irrespective of INDEX.md content. Do NOT over-engineer INDEX.md as a runtime manifest with parse-validation; INDEX.md exists for human discoverability.
- **Test pin:** `tests/specialists/wanda/test_wanda_sanctum_populated.py` — 3 tests (parametrize-collapsible per Murat M-R18 → 1 K-floor unit):
  1. `test_sanctum_directory_exists` — `_bmad/memory/wanda-sidecar/` present + contains all 5 expected skeleton files.
  2. `test_sanctum_digest_nonempty_post_population` — `_read_sanctum_digest()` returns non-empty string + 5 lines + each line is `<path>\t<64-hex-sha256>`.
  3. `test_sanctum_digest_deterministic_under_crlf` — write a sanctum file with CRLF newlines, recompute digest, assert equals LF-equivalent (pins CRLF→LF normalization against future regression).

### AC-2c.2-B — L5 podcast-production reference files at `skills/bmad-agent-wondercraft/references/L5-podcast-production/` + Wanda wiring

- **Given** `skills/bmad-agent-wondercraft/references/` contains 11 operator-curated files at 2b.8 close
- **When** the dev agent authors 3 NEW reference files in `skills/bmad-agent-wondercraft/references/L5-podcast-production/`:
  - `storytelling-framework.md` — narrative arc patterns for educational podcast (hook → context → conflict → resolution → call-to-action); ≥40 lines substantive content
  - `audio-production-patterns.md` — voice-acting cadence + pause-discipline + music-bed-volume-curve patterns; ≥40 lines substantive content
  - `narration-length-vs-engagement.md` — minute-bracket guidance for retention (3-min "explainer" / 8-min "deep-dive" / 15-min "story-arc") with citation pointers; ≥40 lines substantive content
- **Then** Wanda's `WANDA_REFERENCES` tuple at `app/specialists/wanda/graph.py:28-40` is extended with the 3 new file paths (relative to `WANDA_REFERENCES_DIR`): `"L5-podcast-production/storytelling-framework.md"`, `"L5-podcast-production/audio-production-patterns.md"`, `"L5-podcast-production/narration-length-vs-engagement.md"`. **Existing 11 entries preserved unchanged** (additive only). Per A-R3-2c.2 + Decision #1 reframe, this tuple extension is the **only** in-scope edit to Wanda's runtime code at 2c.2.
- **Then** `_read_wanda_references()` returns a string containing all 14 reference headers + bodies in declared tuple order (verifies the read path resolves the new sub-directory correctly + ordering preserved).
- **Test pins:**
  1. `tests/specialists/wanda/test_wanda_l5_references_present.py` — 3 tests:
     - `test_l5_directory_and_three_files_exist` — `skills/bmad-agent-wondercraft/references/L5-podcast-production/` present + all 3 files exist + each ≥40 lines.
     - `test_wanda_references_tuple_contains_l5_paths` — `WANDA_REFERENCES` is a 14-tuple (11 original + 3 new); the 3 new entries match exactly the L5 file paths (membership-echo per Murat M-R18; 1 K-floor unit).
     - **`test_read_wanda_references_includes_l5_bodies_in_declared_order` (NEW per Murat M-R18 K-floor honest-add):** `_read_wanda_references()` output includes each L5 file body content + the L5 segment headers appear in the order declared in `WANDA_REFERENCES` tuple (orthogonal property: behavior of read path + ordering preservation, not tuple membership echo).
  2. **Existing test extension** at `tests/specialists/wanda/test_wanda_plan_node.py` (or equivalent) — assert `_read_wanda_references()` output length grew from 11-segment to 14-segment baseline; no regression on the original 11 segments.

### AC-2c.2-C — L6 operational context at `_bmad/memory/wanda-sidecar/L6-operational/wondercraft-context.md`

- **Given** `_bmad/memory/wanda-sidecar/L6-operational/` is created at AC-A
- **When** the dev agent authors `wondercraft-context.md` containing:
  - **Voice-ID catalog:** ≥3 production voices with role mapping (e.g., `voice_a_narrator: "Vivian"`, `voice_b_expert: "Marcus"`, `voice_c_student: "Lena"`); each entry annotated with usage-context + register + sample-rate cap.
  - **Episode-template skeleton:** standard 8-min explainer template (hook 0-30s / context 30s-2m / body 2-7m / CTA 7-8m) with timing-sensitive cues for `dispatch_episode` / `dispatch_dialogue`.
  - **Style-guide overrides:** music-bed-volume default −18LUFS; pause-after-question 1.2s; segue-tone preference per voice-pair.
  - File ≥60 lines.
- **Then** `_read_sanctum_digest()` includes `L6-operational/wondercraft-context.md` in the digest output (proven via AC-A `test_sanctum_digest_nonempty_post_population` parametrize sweep covering this file).
- **Test pin:** `tests/specialists/wanda/test_wanda_l6_operational_context.py` — 1 test: `test_l6_wondercraft_context_present_and_substantive` — file exists + ≥60 lines + parses for the three required sections (regex `^## Voice-ID catalog`, `^## Episode-template skeleton`, `^## Style-guide overrides`).

### AC-2c.2-D — Live Wondercraft API integration test (`@pytest.mark.live_api`; deselected by default per `--run-live` opt-in mechanism)

- **Given** the `live_api` marker is **already registered** at `pyproject.toml:62-63` + `tests/conftest.py:88` (verified 2026-04-26); `--run-live` flag registered at `tests/conftest.py:71`; deselect-by-default Pass 1 logic at `tests/conftest.py:129-149` removes `live_api` items from `selected` unless `--run-live` is passed
- **And** `WONDERCRAFT_API_KEY` may or may not be available in the dev-agent's `.env` (sandbox-AC discipline: dev-agent ACs verify via shipped Python dep + `pytest.skip(...)` when absent — composed with the `--run-live` opt-in)
- **When** the dev agent authors `tests/specialists/wanda/test_wanda_live_api_artifact.py`:
  ```python
  import hashlib
  import os
  import pytest
  from pathlib import Path
  from scripts.api_clients.wondercraft_client import WondercraftClient

  REPO_ROOT = Path(__file__).resolve().parents[3]
  ARTIFACT_DIR = REPO_ROOT / "tests" / "fixtures" / "specialists" / "wanda" / "live_artifacts" / "2026-04-26"

  @pytest.mark.live_api
  @pytest.mark.skipif(
      not os.environ.get("WONDERCRAFT_API_KEY"),
      reason="WONDERCRAFT_API_KEY absent — live API test deferred to operator window",
  )
  def test_wanda_live_artifact_via_create_scripted_podcast(tmp_path):
      client = WondercraftClient()
      assert client.check_connectivity() is True
      # invoke create_scripted_podcast with canonical 8-min explainer script;
      # wait_for_job; download MP3 to ARTIFACT_DIR / f"{sha256}.mp3";
      # assert: file exists; size > 0; sha256 computed locally matches name;
      # assert duration_sec range-bounded per M-R33: 4*60 <= duration_sec <= 10*60.
      ...
  ```
- **Mechanism reconciliation (per A-R1 RESOLVED-BY-VERIFICATION):** Default `pytest tests/specialists/wanda/ -q` invocation deselects this test automatically via `pytest_collection_modifyitems` Pass 1 (no `--run-live` flag → `live_api` items removed from `selected`). Explicit opt-in: `pytest tests/specialists/wanda/test_wanda_live_api_artifact.py --run-live -v -s`. **NO `addopts -m "not live_api"` modification** — that's not the project mechanism.
- **Then** the test, when invoked with `--run-live` AND `WONDERCRAFT_API_KEY` set, produces a real podcast MP3 + writes it to `tests/fixtures/specialists/wanda/live_artifacts/2026-04-26/<sha256>.mp3` + emits a `LIVE_ARTIFACT_METADATA.md` companion at the same directory recording: (a) trial-id, (b) API call duration, (c) cost in USD per Wondercraft response, (d) voice-ID used, (e) script SHA256, (f) operator who triggered.
- **Range-bounded duration assertion per Murat M-R33 (binding):** `4*60 <= duration_sec <= 10*60` (lower bound: artifact is substantive enough to validate quality; upper bound: runaway-generation canary paired with Decision #4 cost ceiling — duration drift correlates with cost drift on Wondercraft per-second pricing).
- **Test pins:**
  1. `tests/specialists/wanda/test_wanda_live_api_artifact.py` — 1 live test (deselected by default; opt-in via `--run-live`; counts as 1 K-floor unit).
  2. `tests/specialists/wanda/test_wanda_live_api_marker_skipped_in_default_run.py` — 1 NEGATIVE test asserting that **default `pytest` invocation** (no `--run-live`) deselects the live_api test, AND **`--run-live` invocation** selects it. Verified via:
     ```python
     import os
     import subprocess
     import sys

     def test_default_run_deselects_live_api(tmp_path):
         # Per Murat M-R31: sanitize PYTEST_ADDOPTS to prevent inherited-env flake;
         # explicit env-clear ensures developer's ad-hoc `PYTEST_ADDOPTS=--run-live` doesn't false-green this test.
         clean_env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
         clean_env["PYTEST_ADDOPTS"] = ""
         result = subprocess.run(
             [sys.executable, "-m", "pytest",
              "tests/specialists/wanda/test_wanda_live_api_artifact.py",
              "--collect-only", "-q"],
             capture_output=True, text=True, env=clean_env, cwd=str(REPO_ROOT),
         )
         # Parse structured output: assert "1 deselected" appears in last lines (collection-count + deselect-count separately verified, not free-text-string-match in body).
         assert result.returncode == 5  # pytest exit code 5 = no tests collected after deselection
         # OR: parse the summary line for "deselected" presence + count == 1.
         ...
     ```
     Per Murat M-R31-2c.2: subprocess MUST sanitize `PYTEST_ADDOPTS` env var with rationale comment (above); subprocess MUST parse structured pytest output (exit code + summary-line `deselected` count), NOT free-text string-match in the body. NO live_api fire occurs in this NEGATIVE test (it only runs `--collect-only`).

### AC-2c.2-D-OP — Operator-gated live execution + artifact paste (DEFERRED-PENDING-OPERATOR-WINDOW allowed; Path-A residual closes 2b.8 AC-B-OP)

- **Given** dev-agent AC-D landed but `WONDERCRAFT_API_KEY` was absent OR the dev agent should not autonomously incur ~$5.00 cost
- **When** the operator opens a session window
- **Then** operator runs (per A-R1-RESOLVED `--run-live` mechanism, NOT `-m live_api`):
  ```bash
  WONDERCRAFT_API_KEY=<from-env> .venv/Scripts/python.exe -m pytest \
    tests/specialists/wanda/test_wanda_live_api_artifact.py --run-live -v -s
  ```
- **And** pastes into Dev Agent Record §"Operator Gate — AC-2c.2-D-OP":
  - Trial-id + start/end timestamps
  - Wondercraft API cost reported
  - Final artifact path (sha256-named MP3 in fixtures)
  - Sha256 computed locally
  - Voice-ID + script preview
  - LIVE_ARTIFACT_METADATA.md content reproduced
- **And** the artifact + metadata files committed to git (these are evidence artifacts and small enough — verify ≤10 MB MP3 per Wondercraft 8-min default).
- **Cost ceiling per Decision #4:** $5.00 single-artifact ceiling for `create_scripted_podcast`. If the live job exceeds this, abort the test + file `2c-2-live-api-cost-overrun-rca` follow-on. **NOT a 2c.2 close-blocker if deferred** — DEFERRED-PENDING-OPERATOR-WINDOW marker preserved through close; reactivation gate "operator ratifies cost + opens window."
- **AC-D-OP-FALLBACK per Amelia A-R4-2c.2:** if `create_scripted_podcast` exceeds the $5 ceiling on the operator's actual run, operator may fall back to `create_podcast` (shorter / simpler format) at $1-2 ceiling. Live-API artifact marked **"scripted preferred, simple acceptable"** in LIVE_ARTIFACT_METADATA.md. Prevents indefinite DEFERRED-purgatory state if Wondercraft scripted-podcast pricing has drifted upward since story authoring. Sentinel string in metadata: `artifact_format: scripted` OR `artifact_format: simple-fallback` (one of two enums).
- **Cost-vs-2c.1 reconciliation:** 2c.1 AC-B-OP smoke-test ($0.50) and 2c.2 AC-D-OP production-quality ($5.00 scripted OR $1-2 simple-fallback) are **distinct** operator windows with **distinct artifacts**. They MAY be combined into a single operator session (executed back-to-back) but the artifacts MUST be separately stored (2c.1 → `tests/fixtures/specialists/wanda_validation/...`; 2c.2 → `tests/fixtures/specialists/wanda/live_artifacts/...`).

### AC-2c.2-E — Filesystem sha256 ↔ LIVE_ARTIFACT_METADATA.md round-trip (NARROWED per A-R2 BLOCKER resolution)

- **Given** `WandaDispatchReceipt.wanda_audio: dict[str, Any] | None` per `app/models/dispatch/wanda/receipt.py` is **loose-typed** (verified 2026-04-26); dispatch wrapper at `app/specialists/wanda/wondercraft_dispatch.py:169-172` returns `{capability: <code>, receipt: <raw client output or mock dict>}` where receipt key-shape **varies per capability** (EP/DP/AS pass through raw `wondercraft_client.create_*` returns; MB/CM/AH return mock dicts); **NO guarantee** that `parsed.path / duration_sec / voice_id / sha256` keys are present
- **When** the live API artifact lands at AC-D-OP and the operator pastes LIVE_ARTIFACT_METADATA.md companion
- **Then** the round-trip is validated **at the filesystem level**, NOT via receipt-key extraction:
  - LIVE_ARTIFACT_METADATA.md `sha256` field equals `hashlib.sha256(<artifact-bytes>).hexdigest()` recomputed from the on-disk MP3 in the fixture directory.
  - LIVE_ARTIFACT_METADATA.md `artifact_path` field equals the fixture-directory artifact path (relative to repo root).
  - LIVE_ARTIFACT_METADATA.md `artifact_format` field is one of `{"scripted", "simple-fallback"}` per AC-D-OP-FALLBACK enum.
- **Validated via 1 NEW test** that parses LIVE_ARTIFACT_METADATA.md if present + asserts the three filesystem-level round-trip properties above. **Test SKIPS** with reason naming the AC-D-OP DEFERRED-PENDING-OPERATOR-WINDOW state if metadata absent.
- **Per Murat M-R34-2c.2:** if 2c.2 closes with AC-D-OP deferred (this test SKIPPED), `2c-2-ac-e-round-trip-pending-live-artifact` deferred-inventory follow-on auto-files at story close. Test stays in tree as SKIPPED-WITH-REASON; round-trip validation does NOT migrate to a separate story (would orphan the metadata contract).
- **Receipt-key extraction OUT OF SCOPE for 2c.2** per A-R2 narrowing — `parsed.path/duration_sec/voice_id/sha256` strict-typing on the receipt is **deferred** to the receipt-strict-typing follow-on (`2c-2-receipt-strict-typed-artifact-metadata`) which would require coordinated edits across receipt model + dispatch helpers + 2b.8 substrate (out of Decision #1 bounded scope).
- **Test pin:** `tests/specialists/wanda/test_wanda_live_artifact_metadata_round_trip.py` — 1 test (skipped if AC-D-OP defers; not a close-blocker; auto-files deferred-inventory entry at close).

### AC-2c.2-F — Anti-pattern catalog harvest (per R6)

- **Given** the catalog at `docs/dev-guide/specialist-anti-patterns.md` is final-form post-2b.17 + 2b.15 with A1–A13 entries
- **When** 2c.2 close runs
- **Then** **NO new anti-pattern signals expected** at this story (sanctum + L5 + L6 population is mechanical; live-API exercise reuses 2b.8 wiring). If any signals surface during dev (e.g., sidecar-vs-bmb-agent path-naming friction, cost-overrun-handling missing pattern), file as candidate A14 anti-pattern and consult party-mode for inclusion vs. defer to 2c.4 final harvest.

### AC-2c.2-G — TEMPLATE compliance (per R1–R14 v2.4)

R1–R14 v2.4 honored where applicable. **Most rules N/A** (no migration; this is post-migration enrichment). Applicable: R1 bounded scope (Decision #1); R6 framework-drift harvest (one divergence captured at §Epic-doc-vs-runtime cross-check (a)); R7 resolution-trail uniformity preserved (no `_plan` signature change); R8 K-floor recalibration (~1.3× = target 10 / floor 8 honored).

### AC-2c.2-H — D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** Wanda's runtime untouched (`_act` orchestration + dispatch wrapper unchanged); only data substrate (sanctum + skill references) + ONE new test family added; FR16 resolution-trail contract intact.
2. **Anti-pattern harvest:** N/A unless surfaced (per AC-F).
3. **Migration-guide update:** §12.11 (Gary REST-API category) gains a one-line note "Wanda L5/L6 enrichment + live-API exercise at 2c.2; sanctum populated to `_bmad/memory/wanda-sidecar/`."
4. **TEMPLATE compliance:** R1, R6, R7, R8 honored. Numeric anchors recorded: T_sanctum_populate / T_l5_files_authored / T_l6_authored / T_live_test_authored / T_live_artifact (operator-paste).

### AC-2c.2-I — Sprint-status state-flips at filing AND at close

At filing: `migration-2c-2-wanda-l5-l6-expertise-and-live-api: ready-for-dev`. At close: `migration-2c-2-...: done`; epic stays `in-progress` (closes at 2c.4 SLAB-CLOSING). `last_updated` field updated.

---

## File Structure Requirements

### NEW files (PERSISTENT)

```
_bmad/memory/wanda-sidecar/
├── INDEX.md
├── PERSONA.md
├── access-boundaries.md
├── chronology.md
└── L6-operational/
    └── wondercraft-context.md

skills/bmad-agent-wondercraft/references/L5-podcast-production/
├── storytelling-framework.md
├── audio-production-patterns.md
└── narration-length-vs-engagement.md

tests/specialists/wanda/
├── test_wanda_sanctum_populated.py                              # 3 tests (AC-A; parametrize-collapse → 1 K-floor unit)
├── test_wanda_l5_references_present.py                          # 3 tests (AC-B; includes M-R18 honest-add behavior test)
├── test_wanda_l6_operational_context.py                         # 1 test (AC-C)
├── test_wanda_live_api_artifact.py                              # 1 test (AC-D; deselected by default per --run-live opt-in)
├── test_wanda_live_api_marker_skipped_in_default_run.py         # 1 NEGATIVE test (AC-D; PYTEST_ADDOPTS-sanitized subprocess per M-R31)
└── test_wanda_live_artifact_metadata_round_trip.py              # 1 test (AC-E; filesystem sha256 round-trip; skipped if DEFERRED; auto-files follow-on)
```

### MODIFIED files

- `app/specialists/wanda/graph.py` — `WANDA_REFERENCES` tuple extended from 11 to 14 entries (additive, AC-B). NO other changes (Decision #1 + A-R3 reframe permits this minimal extension).
- `docs/dev-guide/specialist-migration-template.md` — section §12.11 gains the AC-H one-line note.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-I.
- `_bmad-output/planning-artifacts/deferred-inventory.md` — `2c-2-mcp-architecture-divergence-from-epic-literal` follow-on filed per §Epic-doc-vs-runtime cross-check (a). `2c-2-ac-d-op-live-wondercraft-evidence` filed if AC-D-OP defers. `2c-2-ac-e-round-trip-pending-live-artifact` auto-filed if AC-D-OP defers (per M-R34). `2c-2-receipt-strict-typed-artifact-metadata` filed at story open per A-R2 narrowing.

### NOT modified (per A-R1 RESOLVED + A-R2 RESOLVED-WITH-NARROWING)

- `pyproject.toml` `[tool.pytest.ini_options].markers` — `live_api` ALREADY registered at lines 62-63 (verified 2026-04-26). NO modification.
- `tests/conftest.py` — `--run-live` flag + `pytest_collection_modifyitems` deselect logic ALREADY in place at lines 68-149. NO modification.
- `app/models/dispatch/wanda/receipt.py` — loose-typed `wanda_audio` field stays (strict-typing of artifact metadata keys deferred per A-R2 narrowing).
- `app/specialists/wanda/wondercraft_dispatch.py` — DO NOT TOUCH (2b.8 architectural pin).

### CONDITIONALLY MODIFIED files (operator-paste landing zone)

- `tests/fixtures/specialists/wanda/live_artifacts/2026-04-26/<sha256>.mp3` — operator-pasted live artifact (AC-D-OP) — committed if AC-D-OP fires.
- `tests/fixtures/specialists/wanda/live_artifacts/2026-04-26/LIVE_ARTIFACT_METADATA.md` — operator-pasted metadata (AC-D-OP) — committed if AC-D-OP fires.

### NOT modified (additional)

- `scripts/api_clients/wondercraft_client.py` — DO NOT TOUCH (substrate stable).
- `app/models/dispatch/wanda/{input,error}.py` — DO NOT TOUCH (2b.15 strict-typed family preserved).
- `app/specialists/wanda_validation/` — DO NOT TOUCH (Path B 2c.1 transient validation tree, retired/discarded at 2c.1 close).

---

## Testing Requirements

**K-target ~1.3× (target 10 / floor 8).** Test count and K-floor accounting per Murat M-R18 honest-count discipline:

| AC | Tests collected | Honest K-floor units |
|---|---|---|
| A | 3 (parametrize-collapsible) | **1** (per M-R18 collapse) |
| B | 3 (incl. M-R18 honest-add behavior test) | **2** (membership-echo collapses to 1; behavior-test counts separately as 1) |
| C | 1 | **1** |
| D-live | 1 (deselected by default per `--run-live`) | **1** |
| D-negative | 1 (subprocess `--collect-only`; PYTEST_ADDOPTS-sanitized per M-R31) | **1** |
| E | 1 (skipped if AC-D-OP defers; auto-files M-R34 follow-on) | **1** |
| **Total** | **10 collected** | **7 firm + 1 conditional (E) = 8 with conditional** |

**Honest K-floor: 8** (with AC-E firing when AC-D-OP completes), **7 firm** (AC-E skipped if deferred). Conforms to ~1.3× K-target (target 10 / floor 8 ≤ 1.25× when AC-E fires; ≤ 1.43× when AC-E defers — both within the K-target band). The M-R18 honest-add `test_read_wanda_references_includes_l5_bodies_in_declared_order` legitimately raises K-floor to 8 by adding an orthogonal property (read-path + ordering behavior), not a membership-echo inflation.

**Regression target at T8:** ≥562 passed / ≥7 skipped placeholder-key (Slab 2b close baseline preserved); +10 collected at file level; deselect-by-default `live_api` mechanism keeps CI green; AC-E may add 1 skip if AC-D-OP defers. Import-linter 3/3 KEPT throughout. Ruff clean. Sandbox-AC PASS (live API verified via shipped Python dep `WondercraftClient`, gated by `pytest.skip(...)` on missing env var + `--run-live` opt-in).

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_

### T1 Readiness

_(Populated at T1)_

### T2–T7 Implementation Notes

_(Populated during implementation)_

### T8 Regression Evidence

_(Populated at T8 with sanctum-populate / L5-author / L6-author / live-test-author timestamps; collection counts; dispatch-family-untouched diff anchor)_

### Operator Gate — AC-2c.2-D-OP Live Wondercraft Evidence

_(Operator pastes here per AC-D-OP)_

### G6 Layered Code-Review (Blind Hunter / Edge Case Hunter / Acceptance Auditor)

_(Single-gate self-conducted per CLAUDE.md; populated at T8)_

### D12 Close Stub

_(Populated at story close per AC-2c.2-H)_

### Completion Notes

_(Populated at story close)_

### File List

_(Populated at story close)_
