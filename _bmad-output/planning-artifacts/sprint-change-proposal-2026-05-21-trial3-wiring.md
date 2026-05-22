# Sprint Change Proposal — Trial-3-Blocking §02A Composer Wiring + UTF-8 Launcher Fix

**Authored at:** 2026-05-21 (post-Trial-3 launch attempt cancelled at G0; operator directive: "get the core wiring working and move through a CLI-only trial ASAP")
**Skill:** `bmad-correct-course` (Batch mode; template-of-record = sprint-change-proposal-2026-05-19.md)
**Operator strategic approval:** GRANTED 2026-05-21 (option `(b) NEW Trial-3-blocking-only SCP` selected from disposition pair in next-session-start-here.md §Immediate next action)
**Branch:** `trial/3-2026-05-21` @ `22dd6bb` (working tree clean; origin synced)
**Scope classification:** **Moderate** (substrate-amendment to tripwire allowlist + targeted production wiring fix + small launcher hardening; NOT a PRD/epic restructure)
**Sibling artifact:** `_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-19.md` (ratified 2026-05-19; remains queued for post-Trial-3 dispatch — NOT folded into this SCP)

---

## Section 1: Issue Summary

**Problem statement.** Trial-3 launch attempt 2026-05-21T19:51 against fresh corpus `course-content/courses/tejal-apc-c1-m1-p2-trends/` (committed at `7d3fab2`) was cancelled at G0 (verb `x`) after the composed directive revealed the **legacy naive corpus-scan composer** ([app/marcus/orchestrator/directive_composer.py](../../app/marcus/orchestrator/directive_composer.py)) had been invoked instead of the **LLM-driven §02A composer** ([app/composers/section_02a/composer.py](../../app/composers/section_02a/composer.py)). The directive showed Trial-2 finding #2's signature: `role: primary` on the alphabetically-first file, uniform `expected_min_words: 200`, naive `Auto-derived from corpus dir: <filename>` descriptions.

Root cause: [app/marcus/cli/trial.py:17-24](../../app/marcus/cli/trial.py#L17-L24) imports `compose_directive` + `materialize_directive` from `app.marcus.orchestrator.directive_composer` (Story 7a.1 deliverable). The LLM-driven §02A composer (Story 7c.3a deliverable that closed Trial-2 finding #2) exists at `app.composers.section_02a.composer` with 5 test files but is consumed ONLY by its own tests + gate-side poll-surface helpers in [app/gates/section_02a/](../../app/gates/section_02a/) — never by the trial-CLI runtime path.

**Secondary issue.** Operator launched Trial-3 from `cmd.exe`; the hot-start launcher prelude `$env:PYTHONIOENCODING="utf-8"` is PowerShell syntax and is silently no-op under CMD. The trial CLI does not set UTF-8 encoding itself, re-introducing the Trial-2 finding #1 cp1252-crash vector for any Unicode-bearing corpus content. Story 7c.2 closure did not reach the CMD invocation path.

**Forensic evidence preserved.**
- Cancelled-trial run dir: `state/config/runs/bef9a2c6-8305-44db-9194-9204f684f25e/{trial-cancelled-at-g0.json,directive.yaml}` (gitignored)
- Directive digest of the broken-fallback output: `777d385ba40553ae3452e891c984f9d21234f985cba43652860d31d6610c1a10`
- Deferred-inventory entry: §`trial-3-blocker-section-02a-composer-not-wired-into-trial-cli` + §`trial-3-blocker-trial-cli-utf-8-launcher-wrapper-cmd` (filed 2026-05-21 at commit `22dd6bb`)
- Related architectural finding filed concurrently: §`marcus-interactive-experience-not-delivered-by-slab-7c` (post-Trial-3 reactivation; NOT covered by this SCP)

**Trigger category (per `bmad-correct-course` checklist 1.2):** Critical regression discovered at production-equivalent runtime launch; substrate gap between an authored module and the CLI integration that was supposed to consume it. AM-11 launch-permission token (52/52 GREEN) did NOT cover this regression because it tests preflight + readiness fixtures, not the composer-actually-invoked-at-trial-start path. Same audit-without-runtime-verification class of defect that Trial-2 finding #2 originally surfaced; reoccurred at the higher integration level.

---

## Section 2: Impact Analysis

**Epic impact:** None. No Epic scope, sequencing, or AC changes. Trial-3 launch is unblocked by this proposal but the Epic-15 reactivation gate, Slab-7c closure, and post-Trial-3 deferred-inventory remain unchanged.

**PRD impact:** None.

**Architecture impact:** **Yes, narrowly scoped.**
- [tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py::PERMITTED_PYTHON_DIFFS](../../tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py) — add ONE path (`app/marcus/cli/trial.py`)
- [app/marcus/cli/trial.py](../../app/marcus/cli/trial.py) — replace legacy composer import + call site with §02A composer + adapter glue; add unconditional UTF-8 encoding setup at module entry
- No M5 import-linter contract semantics changes
- No `state/config/pipeline-manifest.yaml` changes
- No 30-1 contract suite changes

**UI/UX impact:** Trial-3 operator surface UNCHANGED. The G0 prompt still emits `[c/e/s/x]` (raw CLI). The Marcus-conversational-mediation gap is filed as a SEPARATE post-Trial-3 architecture follow-on (see deferred-inventory entry `marcus-interactive-experience-not-delivered-by-slab-7c`); this SCP does NOT address that gap.

**Other artifacts:**
- Deferred-inventory entries `trial-3-blocker-section-02a-composer-not-wired-into-trial-cli` + `trial-3-blocker-trial-cli-utf-8-launcher-wrapper-cmd` will be CLOSED post-execution with strikethrough + `CLOSED-AT-<commit>` markers.
- `next-session-start-here.md` Immediate-next-action block will be replaced post-execution with Trial-3 launch readiness or Trial-3 postmortem authoring (per outcome).
- The 2026-05-19 SCP is UNTOUCHED — it remains queued for post-Trial-3 dispatch as a separate motion.

**Trial-3 launch impact:** This proposal directly unblocks Trial-3. Post-execution, Trial-3 can re-launch against the committed corpus at `7d3fab2` without additional substrate work.

**Forensic-comparison protocol impact:** the broad-regression baseline at `_bmad-output/implementation-artifacts/broad-regression-baseline-2026-05-07.md` is UNCHANGED by this proposal (no path-pin re-application; no Slice A/D work). The baseline at 88 failures remains the Trial-3 forensic-comparison reference.

---

## Section 3: Recommended Approach

**Selected path:** **Direct Adjustment with bounded substrate amendment.** One allowlist extension (1 path) + one production-code fix (call-site replacement + UTF-8 hardening) + verification commits.

**Rejected alternatives:**
- **Extend the 2026-05-19 SCP:** rejected by operator at next-session-start-here.md disposition pair — separating scope keeps the 5/19 motion's ratification clean and lets this Trial-3-blocking work move on its own clock.
- **Pre-Trial-3 stop-and-build Marcus-interactive surface:** rejected by operator directive — Trial-3 ships against the CLI surface as-is; Marcus-interactive becomes a post-Trial-3 Epic.
- **Patch the legacy composer to be smarter:** rejected — the legacy composer is a deprecated Story-7a.1 fallback; the §02A composer is the canonical authored deliverable. Re-rooting on the legacy path would invalidate the entire Slab-7c §02A work.

**Effort estimate:** Low (~1-2 hours total: 1 substrate amendment commit + 1 wiring fix commit + verification battery + 1 docs-only closure commit).
**Risk level:** Low. The §02A composer is independently tested (5 test files); the adapter shape is determined by the existing call-site contract in trial.py. The allowlist extension is bounded to a single path; the freeze predicate is preserved for all other paths.

**Trade-off accepted:** Trial-3 launches against the bare CLI (no Marcus-conversational mediation). The architectural gap is named in deferred-inventory and queued for post-Trial-3 Epic-scope work, not silently kept.

---

## Section 4: Detailed Change Proposals

### 4.1 — TW-7c-4 allowlist amendment

**File:** [tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py](../../tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py)

**Change (lines 9-18):** Add ONE path to `PERMITTED_PYTHON_DIFFS`:

```python
PERMITTED_PYTHON_DIFFS = {
    *HARNESS_PATHS,
    "scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py",
    "tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py",
    "tests/trial/test_trial3_readiness.py",
    # Trial-3-blocking wiring fix 2026-05-21 (sprint-change-proposal-2026-05-21-trial3-wiring.md):
    # §02A composer was authored at Story 7c.3a but never wired into the trial CLI;
    # legacy directive_composer (Story 7a.1 fallback) was still being invoked at G0.
    # Bounded allowlist extension authorizes the wiring fix + UTF-8 launcher hardening.
    # Freeze predicate intact for all other paths.
    "app/marcus/cli/trial.py",
}
```

**Rationale.** Single-path extension. The path is the trial CLI entrypoint; the freeze's purpose (prevent live-dispatch substrate creep into Trial-3) is preserved because this fix REPLACES a known-broken integration with a known-tested module that already passed Story 7c.3a code review.

### 4.2 — Wiring fix in trial.py (§02A composer + adapter)

**File:** [app/marcus/cli/trial.py](../../app/marcus/cli/trial.py)

The two composers have different API signatures, so this is NOT a single-line import swap. Required changes:

**(a) Imports (lines 17-24):**

OLD:
```python
from app.marcus.orchestrator.directive_composer import (
    compose_directive,
    materialize_directive,
)
```

NEW:
```python
import hashlib

from app.composers.section_02a._cache import ComposerCache
from app.composers.section_02a.composer import compose, write_directive_yaml
from app.models.adapter import make_chat_model
```

**(b) Adapter helper (insert before `start_trial`):**

```python
def _compose_section_02a_directive(
    *,
    corpus_dir: Path,
    run_dir: Path,
) -> tuple[Path, str]:
    """Adapter: invoke LLM-driven §02A composer; return (directive_path, sha256_digest).

    Bridges the legacy materialize_directive(...) -> (path, digest) call-site contract
    to the §02A composer's compose(...) + write_directive_yaml(...) split.
    """
    chat_handle = make_chat_model("marcus")
    directive = compose(corpus_dir, llm=chat_handle.chat, cache=ComposerCache())
    directive_path = run_dir / "directive.yaml"
    write_directive_yaml(directive, directive_path)
    digest = hashlib.sha256(directive_path.read_bytes()).hexdigest()
    return directive_path, digest
```

**(c) Call site (lines 226-231):**

OLD:
```python
if input_path.is_dir():
    composed = compose_directive(
        corpus_path=input_path,
        run_id=str(effective_trial_id),
    )
    directive_path, directive_digest = materialize_directive(composed, run_dir)
```

NEW:
```python
if input_path.is_dir():
    directive_path, directive_digest = _compose_section_02a_directive(
        corpus_dir=input_path,
        run_dir=run_dir,
    )
```

**Note on `effective_trial_id` divergence.** The §02A composer's `Directive` model carries its own internally-generated `run_id=uuid4()` separate from the trial CLI's `effective_trial_id`. This is a known divergence inherited from the §02A composer's standalone design; not addressed by this SCP. Filed as a follow-on consideration in the post-Trial-3 retrospective.

**Verification:**
- `make_chat_model("marcus")` returns a `ChatModelHandle` NamedTuple (per [app/models/adapter.py:44-52](../../app/models/adapter.py#L44-L52)) with attributes `(chat: ChatOpenAI, entry: ModelResolutionEntry)`. The composer expects a `BaseChatModel`; `ChatOpenAI` is a `BaseChatModel` subclass — `.chat` is the correct attribute. The `.entry` field is intentionally discarded by this adapter (the trial CLI does not currently exercise NFR-X4 `RunState.model_resolution_trail` append; filed as a follow-on observation for the post-Trial-3 retrospective).
- The §02A composer's test suite (5 files at `tests/composers/section_02a/`) must continue to PASS unchanged.
- The Trial-2 forensic regression test (`tests/composers/section_02a/test_composer_trial_2_finding_2_regression.py`) must PASS — it asserts the new composer does NOT emit the broken-fallback directive shape.

### 4.3 — UTF-8 launcher hardening

**File:** [app/marcus/cli/trial.py](../../app/marcus/cli/trial.py)

Insert into `_load_env_if_available` (or as a sibling helper invoked at the top of `start_trial`):

```python
def _ensure_utf8_io() -> None:
    """Force UTF-8 stdio regardless of OS default codepage.

    Closes Trial-2 finding #1 cp1252 crash vector for any invocation path
    (PowerShell, CMD, IDE terminal). Idempotent; safe to call repeatedly.
    """
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass
```

Invoke `_ensure_utf8_io()` as the first line of `start_trial` (before `_load_env_if_available()`).

**Rationale.** Makes the CLI UTF-8-safe regardless of invocation shell. Operator can drop the `$env:PYTHONIOENCODING="utf-8"` prelude entirely; documentation update is a docs-only follow-on (not in this SCP scope).

### 4.4 — Deferred-inventory closure markers (post-execution docs commit)

**File:** [_bmad-output/planning-artifacts/deferred-inventory.md](../../_bmad-output/planning-artifacts/deferred-inventory.md)

After the wiring fix lands and Trial-3 re-launch verifies G0 emits a non-broken directive, add closure markers to:
- `trial-3-blocker-section-02a-composer-not-wired-into-trial-cli` → strikethrough + `CLOSED 2026-05-21 via sprint-change-proposal-2026-05-21-trial3-wiring.md (commit <sha>)`
- `trial-3-blocker-trial-cli-utf-8-launcher-wrapper-cmd` → same closure marker

The `marcus-interactive-experience-not-delivered-by-slab-7c` entry remains OPEN (post-Trial-3 reactivation trigger).

---

## Section 5: Implementation Handoff

**Scope classification:** **Moderate.** Bounded substrate amendment (1 path) + production code fix (~20-30 LOC including adapter helper) + small launcher hardening (~10 LOC) + docs-only closure commit. Direct implementation by orchestrator.

**Sequencing (multi-commit for forensic clarity):**

1. **Commit C1 — Substrate amendment.** TW-7c-4 allowlist extension (§4.1). Single commit; HEREDOC message referencing this SCP. Verify TW-7c-4 PASSES on clean tree before proceeding.
2. **Commit C2 — Wiring fix + UTF-8 hardening.** Bundled diff covering §4.2 + §4.3. Adapter helper + call-site replacement + UTF-8 helper.
3. **Verification battery between C2 and re-launch:**
   - `pytest tests/composers/section_02a/ -v` (must be GREEN; 5 test files unchanged behavior)
   - `pytest tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py -v` (must PASS; new path in allowlist)
   - `pytest tests/trial/test_trial3_readiness.py tests/test_preflight_check.py tests/marcus_capabilities/test_preflight_receipt_contract.py -v` (AM-11 token; must remain 52/52 GREEN)
   - Quick broad-regression stability check: `pytest -p no:randomly --co -q | wc -l` ≥ previous count (no test loss); full broad-regression measurement optional but recommended.
4. **Trial-3 re-launch (operator-driven).** From PowerShell or CMD:
   ```
   .\.venv\Scripts\python.exe -m app.marcus.cli trial start --preset production --input course-content/courses/tejal-apc-c1-m1-p2-trends/
   ```
   At G0, verify the directive shows:
   - Slides (`slides/slide-*.md`) classified as `role: primary` (LLM judgment, not alphabetical)
   - Quiz file classified as `role: supporting`
   - `expected_min_words` content-aware (varies per file) or absent on non-prose files
   - Description does NOT contain "Auto-derived from corpus dir" boilerplate
5. **Commit C3 — Deferred-inventory closures + next-session-start-here refresh.** Post-Trial-3 (regardless of trial outcome). Docs-only.
6. **Push** after C1+C2 (per push-cadence policy) and again after C3.

**Verification gates (binding):**
- After C1: TW-7c-4 must PASS on clean tree (substrate amendment is inert).
- After C2: TW-7c-4 still PASSES (the new path is now allowlisted); §02A composer test suite still PASSES (5 files); AM-11 token still 52/52.
- After re-launch: directive at G0 must NOT match the Trial-2 finding #2 broken-fallback signature.

**Abort tripwire during execution:** if AM-11 token drops below 52/52 OR any new test failure appears that wasn't in the pre-amendment 88 baseline, revert C2 only — KEEP C1 (substrate amendment is independent and reversible separately).

**Handoff recipients:**
- **Orchestrator (this agent)** executes C1 + C2 + verification + C3.
- **Operator** approves this proposal explicitly before C1 lands AND drives the Trial-3 re-launch interactively.
- **Party-mode (Winston + Amelia + Murat + John)** ratifies this proposal as a substrate-amendment round per BMAD sprint governance §2 and §4.

**Success criteria:**
- TW-7c-4 PASS post-amendment AND post-wiring-fix
- §02A composer test suite GREEN unchanged
- AM-11 launch-permission token 52/52 GREEN unchanged
- Trial-3 re-launch produces a non-broken directive at G0
- Origin synced; working tree clean; push-cadence honored
- Two trial-3-blocker deferred-inventory entries closed with commit-SHA markers; `marcus-interactive-experience-not-delivered-by-slab-7c` entry remains OPEN

---

## Section 6: Approval + Routing

**Operator approval status:** GRANTED 2026-05-21 (strategic direction: "get the core wiring working and move through a CLI-only trial ASAP — then get to building out the promised but not delivered Marcus 'interactive' experience"). Operator option (b) selected from next-session-start-here disposition pair.

**Party-mode ratification status:** **RATIFIED 2026-05-21 Round 1, 4-of-4 APPROVE-with-amendments.** No impasse; Quinn/John escalation chain not invoked. Amendments tabulated in §7 below.

**Post-ratification action:** orchestrator applies C1 → C2b → C2a → verify → re-launch (operator-driven) → C3 → push, with amendment fold-in per §7.

---

## Section 7: Round 1 Verdicts + Ratified Amendments

**Convened:** 2026-05-21 Round 1 (single round; no impasse).

| Voice | Verdict | Amendments |
|---|---|---|
| 🏗️ Winston (Architect) | APPROVE-with-amendments | W-A1, W-A2 |
| 💻 Amelia (Dev) | APPROVE-with-amendments | AM-A1, AM-A2, AM-A3, AM-A4, AM-A5 |
| 🧪 Murat (TEA) | APPROVE-with-amendments | M-A1 (CRITICAL — would be REJECT if unaddressed), M-A2, M-A3, M-A4, M-A5 |
| 📋 John (PM) | APPROVE-with-amendments | J-A1, J-A2, J-A3 (non-blocking) |

### Ratified amendment set (binding for execution)

- **W-A1.** Move the adapter helper out of `app/marcus/cli/trial.py` and into a NEW module `app/composers/section_02a/cli_adapter.py` exporting public `compose_and_write(corpus_dir: Path, run_dir: Path, *, llm: BaseChatModel | None = None) -> tuple[Path, str]`. The §02A module owns its own call-shape bridge; future consumers (workflow runner, Marcus-interactive Epic) reuse without copy-paste. Inside the adapter, default-resolve `llm` via `make_chat_model("marcus").chat` when caller passes `None`. **Allowlist consequence:** §4.1 becomes +2 paths (`app/marcus/cli/trial.py` + `app/composers/section_02a/cli_adapter.py`).
- **W-A2.** Inline code-comment in `cli_adapter.py` flagging the two known seams: (a) the §02A composer's `Directive.run_id = uuid4()` vs the caller's `effective_trial_id`; (b) `ChatModelHandle.entry` (the NFR-X4 `model_resolution_trail` audit record) is intentionally discarded by this adapter. Both with `TODO(post-trial-3-retro)` markers.
- **AM-A1, AM-A2.** Authoring clarifications only — confirm `os`, `sys`, and `pathlib.Path` are already imported in `trial.py`; no new top-level imports beyond `hashlib` and the adapter import. No behavior change.
- **AM-A3.** Split C2 → **C2b** (UTF-8 launcher hardening; lower risk; lands first) + **C2a** (wiring fix; lands second). Independent revert paths. Combined with M-A3 below, both must atomically revert together with C1 if abort fires.
- **AM-A4.** Pre-C2a grep audit: `grep -rn "compose_directive\|materialize_directive" tests/` to surface any existing test that mocks the legacy composer; fold mock updates into C2a or file as a follow-on if non-trivial.
- **AM-A5.** Folded into J-A1(a) below — single follow-on entry covers the divergence.
- **M-A1 (CRITICAL).** Add new integration test `tests/marcus_cli/test_compose_section_02a_directive_adapter.py` asserting the wiring contract: (a) `make_chat_model("marcus")` is called exactly once when `llm=None`; (b) the `.chat` attribute is what's passed as the `llm` kwarg to `compose(...)`; (c) the returned `(path, digest)` tuple matches the legacy contract; (d) the digest is `sha256(directive_path.read_bytes()).hexdigest()`. Mock `make_chat_model` and `compose` — this is a wiring-contract test, not end-to-end. Lands in C2a with the adapter.
- **M-A2.** Pin the dry-run gate between C1 and C2b: `pytest tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py -v` — require all test functions GREEN; specifically confirm `test_live_dispatch_python_scope_is_bounded` passes (line-65 predicate intact). Both line-56 and line-65 assertions remain active.
- **M-A3.** Abort-tripwire amendment: if C2a OR C2b regresses, atomic-backout of **C1 + C2b + C2a** as a unit. The TW-7c-4 allowlist must not be left extended without the diff that justifies it. (Replaces the original "revert C2 only, keep C1" protocol.)
- **M-A4.** After successful Trial-3 G0 directive composition, capture the post-fix directive's sha256 to `state/config/runs/<trial-3-run-id>/directive-digest.txt` for forensic-reproducibility binding. Reference this digest in the Trial-3 postmortem Shape A Q5 as the new baseline for future-Trial-N composer-regression detection.
- **M-A5.** Drop the misleading `pytest -p no:randomly --co -q | wc -l` collection-count check from §5 verification. Replace with `pytest --collect-only -q` (verify collection succeeds without errors). Failure-count re-measurement is explicitly deferred to post-Trial-3 unless an unexpected new failure surfaces during the AM-11 / §02A suite / TW-7c-4 battery.
- **J-A1.** Before Trial-3 re-launch, file TWO follow-on entries in `deferred-inventory.md`:
  - **(a)** `trial-cli-effective-trial-id-vs-section-02a-composer-run-id-divergence` — reactivation trigger: post-Trial-3 retrospective.
  - **(b)** `trial-cli-model-resolution-trail-not-appended-from-adapter` — reactivation trigger: post-Trial-3 retrospective.
  Filed in C3 (docs commit) at the latest; must exist on disk before the operator re-launches Trial-3.
- **J-A2.** C3 commit message must include a one-line directive-digest comparison (old broken `777d385b…` vs new sha256) plus a 3-line directive excerpt showing slide=primary. Operator verifies "did this work?" in <10 seconds from `git log -1`.
- **J-A3 (NON-BLOCKING).** Sally (UX) and Mary (analyst) absent from Round 1; flag for Trial-3 postmortem Shape B participation.

### Execution sequencing (post-amendment)

1. **C1** — TW-7c-4 allowlist +2 paths (W-A1 consequence).
2. **Dry-run gate** (M-A2) — `pytest tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py -v` GREEN.
3. **C2b** — UTF-8 launcher hardening (§4.3 only). Lower risk; lands first per AM-A3.
4. **AM-A4 grep audit** — surface legacy-composer mocks in `tests/`.
5. **C2a** — New `app/composers/section_02a/cli_adapter.py` module (W-A1) + `trial.py` wiring swap + new integration test (M-A1) + any mock updates from AM-A4. Bundled commit.
6. **Verification battery:** AM-11 token 52/52; §02A composer suite GREEN; TW-7c-4 GREEN; collection-success check (M-A5 replacement); new adapter test GREEN.
7. **Operator-driven Trial-3 re-launch** against `course-content/courses/tejal-apc-c1-m1-p2-trends/`.
8. **M-A4** — capture post-fix directive sha256 to run-dir.
9. **C3** — docs commit: two follow-on inventory entries (J-A1) + two trial-3-blocker closures + J-A2 digest-comparison commit-message format.
10. **Abort tripwire (M-A3):** if any verification gate or re-launch produces a regression, atomically revert C1 + C2b + C2a as a unit; preserve M-A4 evidence; revisit at next session.

Estimated effort post-amendment: **~2-3 hours wall-clock** (up from the original 1-2 hours estimate; growth driven by W-A1 new-module + M-A1 new integration test + AM-A4 mock audit + M-A4 digest capture).
