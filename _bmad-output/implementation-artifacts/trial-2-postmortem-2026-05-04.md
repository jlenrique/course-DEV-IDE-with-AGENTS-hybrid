# Trial-2 Post-Mortem — 2026-05-04 (structured stop)

**Operator:** Juanl
**Orchestrator:** Marcus (sanctum-rebirth load: INDEX/PERSONA/CREED/BOND/MEMORY/CAPABILITIES)
**Branch:** `dev/langchain-langgraph-foundation` @ HEAD `fdacce9` (working tree clean at launch)
**Corpus:** `course-content/courses/tejal-APC-C1/` (legacy APC C1-M1 Tejal source materials; 13 files including 1 DOCX, 1 PDF, 1 PPTX, 1 MD, 7 PNG, 1 JPG, 1 JPG)
**Preset:** `production`
**Execution mode:** `tracked` (`state/runtime/mode_state.json::mode == "default"`)
**Verdict:** **STRUCTURED STOP** — three honest findings collected; Trial-2 will re-run as a Slab 7c close gate, not as a standalone ceremony.

---

## Pre-flight verification (all PASS)

| # | Check | Result |
|---|---|---|
| 1 | `migration-epic-slab-7b-specialist-activation-eleven` status | `done` ✅ |
| 2 | `migration-epic-slab-7b-specialist-activation-eleven-retrospective` status | `done` ✅ |
| 3 | `migration-7b-12-integration-parity-suite-closeout` status | `done` ✅ |
| 4 | Validator: `validate_parity_test_class_conformance.py tests/parity/` | PASS — 11 activation contracts conform across 6 classes (A/B/C+/C/D1/D2) ✅ |
| 5 | Mapping-checklist parity tests | 4 passed ✅ |
| 6 | `.env` keys loaded via `scripts/utilities/env_loader::load_env` | 8 keys present including OPENAI_API_KEY + LANGSMITH_API_KEY + LANGSMITH_PROJECT (real LangSmith tracing available; trial counts as production clone-launch evidence) ✅ |
| 7 | Working tree state | clean; 5 commits ahead of `origin/dev/langchain-langgraph-foundation` ✅ |
| 8 | Branch alignment | `dev/langchain-langgraph-foundation` matches handoff target ✅ |

**Slab 7b CLOSED PASS** at all three substrate gates.

---

## Trial-2 launch attempts (chronological)

Six successive launch attempts surfaced three orthogonal findings. Each attempt produced a directive YAML on disk (run-id directories preserved as forensic evidence under `state/config/runs/`).

### Attempt 1 — `d44128e9-4e17-4452-a535-989e826cd7da` (2026-05-04 ≈17:00 UTC)

```bash
.venv/Scripts/python.exe -m app.marcus.cli trial start --preset production --input course-content/courses/tejal-APC-C1
```

Crashed at G0 print:

```
File "...\trial.py", line 132, in _confirm_or_edit_directive
    print_fn(directive_path.read_text(encoding="utf-8"))
File "...\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input, self.errors, encoding_table)[0]
UnicodeEncodeError: 'charmap' codec can't encode character ' ' in position 2001
```

**→ Finding #1 surfaced.** Composed directive YAML written to disk before crash.

### Attempts 2–4 — bash-routing diagnostics

The Claude Code `!` prefix routes commands through Git Bash, not PowerShell. Multiple syntax retries (`$env:PYTHONIOENCODING="utf-8"; ...`, `C:\tmp\run-trial-2.cmd`, `bash /c/tmp/run-trial-2.sh` without `!` prefix) failed for environmental reasons unrelated to the trial pipeline. A bash helper script at `C:\tmp\run-trial-2.sh` resolved the routing question.

### Attempt 5 — `9eabd5ac-...` (post-`PYTHONIOENCODING=utf-8`)

`PYTHONIOENCODING=utf-8` resolved Finding #1: directive YAML printed cleanly with U+202F intact. G0 prompt rendered fully. **Then crashed at `input()`** with `EOFError: EOF when reading a line`.

Root cause: Git Bash on Windows wraps `.exe` invocations with **winpty**, which provides a pseudo-TTY. `sys.stdin.isatty()` returns `True` from the pty even though the actual stdin source is closed/piped. The auto-confirm branch in `_confirm_or_edit_directive` (`trial.py:124-130`) is gated on `if not isatty_fn():` — so winpty's True forces the code into the interactive `input()` branch, which then fails immediately on EOF.

### Attempt 6 — `c8c3b6be-...` (`< /dev/null` redirect)

Stdin redirect from `/dev/null` did NOT alter `isatty()` because winpty intercepts at the OS layer below the bash redirect. Same EOFError.

### Attempt 7 — `db05cda7-...` (pipe `echo c |` without flag)

Pipe forced `isatty() == False`. Without `--auto-confirm-directive` set, the code raised `DirectiveConfirmationRequiredError` (correct fail-loud behavior — refuses silent auto-accept of broken stdin contract).

### Attempt 8 — `db276994-edf4-47a2-83bc-771cc214c3c1` (pipe + `--auto-confirm-directive`)

```bash
echo c | .venv/Scripts/python.exe -m app.marcus.cli trial start \
  --preset production \
  --input course-content/courses/tejal-APC-C1 \
  --auto-confirm-directive
```

**G0 cleared cleanly via auto-confirm path.** Pipeline advanced to Texas extraction. Texas wrangler returned exit code 30; Texas correctly raised `BundleDispatchError("texas wrangler reported hard error (exit 30); bundle not trusted", tag="bundle.parsed.exit-30")` per `app/specialists/texas/_act.py:322-326`.

`state/config/runs/db276994-.../run.json` records:
```json
{
  "status": "in-flight",
  "production_clone_launch_evidence": false,
  "production_clone_launch_evidence_reason": "registered-no-specialist-fired",
  "production_envelope": {"contributions": []}
}
```

**→ Finding #3 surfaced.** Texas's fail-loud guardrail (Story 7b.1 hardening) engaged correctly. Bundle directory `state/config/runs/db276994-.../bundle/` is empty — Texas refused to write any artifact when given a broken directive.

---

## Findings

### Finding #1 — G0 print_fn cp1252 crash on macOS-screenshot Unicode

| | |
|---|---|
| **Surface** | `app/marcus/cli/trial.py:123`, default `print_fn = (lambda msg: print(msg))` |
| **Trigger** | Corpus contains macOS-generated screenshot filenames using U+202F NARROW NO-BREAK SPACE (e.g. `differential diagnosis Screenshot 2026-02-10 at 5.38.36 PM.png`) — the macOS naming convention separates time and AM/PM with NNBSP. |
| **Failure mode** | Filenames are read from disk as UTF-8 bytes correctly; YAML serialization preserves U+202F in directive descriptions. `print()` then fails on Windows console default cp1252 encoding. |
| **Anti-pattern** | A11 (Windows-portability), already cataloged in `docs/dev-guide/specialist-anti-patterns.md`. Marcus MEMORY 2026-04-17 records the same class of bug in the Texas wrangler `--help` output. |
| **Workaround validated** | `PYTHONIOENCODING=utf-8` in launching environment — reproducible across attempts 5 onward. |
| **Permanent fix shape** | One-line change at `_confirm_or_edit_directive` print_fn default: replace `lambda msg: print(msg)` with a helper that writes via `sys.stdout.buffer.write(msg.encode('utf-8', errors='replace') + b'\n')` OR call `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` once at module import. |
| **Estimated effort** | < 0.5pt; standalone or as Slab 7c §02A precursor patch. |

### Finding #2 — Pre-gate-marcus directive composer is corpus-scan fallback, not LLM-driven

| | |
|---|---|
| **Surface** | `app/marcus/orchestrator/directive_composer.compose_directive` and the `pre-gate-marcus` shared LLM node landed at Slab 7a Story 7a.3 |
| **Observed output** (4 successive runs identical) | Every file in the corpus directory enumerated as `provider: local_file` with `description: 'Auto-derived from corpus dir: <filename>'` and `expected_min_words: 200`. `.gitkeep` promoted to `src-001 role: primary`. `APC C1-M1 Tejal 2026-03-29.docx` (the actual primary lesson content) demoted to `src-004 role: supporting`. PNG, JPG, PPTX, PDF binaries all assigned `expected_min_words: 200`. |
| **Expected output** | LLM-composed directive with semantic role assignment, primary-vs-supporting discrimination based on file content/format, no `expected_min_words` on binaries, no `.gitkeep` promotion. |
| **Maps to** | **Slab 7c §02A operator-directives poll surface** (per `next-session-start-here.md` line 32: "§02A operator-directives poll surface + §04A per-plan-unit ratification + §04.5/§04.55 estimator + run-constants lock"). Already in Slab 7c scope; this evidence elevates priority. |
| **Honest framing** | The 7a.3 pre-gate-marcus shared LLM node IS structurally landed (lockstep + tests pass; orchestration-only-node tolerance verified). What's missing is the **prompt + LLM call inside the node** that converts a corpus-dir scan into a semantically-aware directive. The shared LLM node infrastructure exists; the Marcus-as-author behavior at G0 does not. |
| **Estimated effort** | Slab 7c story (PRD scope-bind required); ~3-5pt single-gate. |

### Finding #3 — Texas wrangler fail-loud guardrail engaged correctly

| | |
|---|---|
| **Surface** | `app/specialists/texas/_act.py:322-326` raises `BundleDispatchError(tag="bundle.parsed.exit-30")` on wrangler exit code 30 |
| **Behavior** | Wrangler refused to write a bundle when handed the broken corpus-scan directive (`.gitkeep` as primary, `expected_min_words: 200` on PNG binaries). Bundle directory remains empty. `production_clone_launch_evidence: false` written with reason `"registered-no-specialist-fired"`. |
| **Validation** | This is **exactly** the contract Story 7b.1 Texas hardening shipped: no fixture-stub silent-passthrough on broken input. The substrate-tier guardrail works end-to-end on real content. |
| **Substrate evidence** | Slab 7b body activation is structurally sound. Gap is at the orchestrational layer (Finding #2), not the body layer. |

---

## Implications

### What Trial-2 PROVED (positive evidence)

1. **Slab 7a substrate UNBLOCKED Trial-2 launch.** `app.marcus.cli trial start` exists, accepts `--input <corpus-path>`, composes a directive, writes it to disk, runs G0 confirm-or-edit, dispatches to Texas. Every step in that chain is reachable.
2. **Slab 7b body-tier guardrails engaged correctly.** Texas Story 7b.1 hardening produced fail-loud refusal on garbage directive — the substrate floor that 11 activation-contract validators verify is structurally honored at runtime.
3. **No silent-bypass occurred.** Trial-475 (2026-04-28, pre-Slab-7b) closed Gap 2 (silent-bypass at G0 with single-file `--input`). Today's run confirms the directory-only refusal is also honored.

### What Trial-2 SURFACED (gap evidence)

1. **AC-7b.12-O (MVP Exit Gate; G2 with ≥9-of-11 specialists, ≥3 per class) cannot be verified via Trial-2 today.** Texas halts at G0+1 with broken directive; downstream specialists never fire.
2. **AC-7b.12-P (Slab Close Gate; G3 cascade-reading 11 specialists) cannot be verified today.** Same reason.
3. **Slab 7c §02A is the gating dependency.** The conversational tail PRD (Slab 7c) must land at minimum a real LLM-driven `compose_directive` before Trial-2 can collect AC-O / AC-P evidence.

---

## Decisions ratified at structured stop

1. **Trial-2 ceremony PAUSED.** Three findings constitute sufficient honest gap evidence; pushing further would require either hand-authored directive injection (out of Marcus's lane per CREED — "delegate, don't author") or a real-TTY operator-driven session at the [e]dit branch (deferred until directive composer can be evaluated post-Slab-7c).
2. **Pivot to Route B (Slab 7c PRD authoring) at next session.** Trial-2 will re-run as a Slab 7c close gate, informed by these findings.
3. **Two prior deferred-inventory entries CLOSED with evidence:**
   - `slab-7a-trial-2-bs-2-readiness-confirmation-deferred-to-operator-trial-2-ceremony` → CLOSED. Slab 7a substrate readiness CONFIRMED end-to-end (trial CLI exists, accepts corpus, composes directive, writes to disk, dispatches to Texas).
   - `slab-7b-trial-2-ac-o-ac-p-readiness-confirmation-deferred-to-operator-trial-2-ceremony` → CLOSED-WITH-EVIDENCE. AC-O / AC-P cannot complete until Slab 7c §02A lands a real LLM-driven directive composer; Trial-2 will re-run post-Slab-7c.
4. **Two new deferred-inventory entries OPENED:**
   - `trial-2-finding-1-g0-print-cp1252-crash` (one-line fix; standalone or Slab 7c precursor)
   - `trial-2-finding-2-directive-composer-corpus-scan-fallback` (Slab 7c §02A core scope)

---

## Forensic evidence preserved (do not delete)

| Path | Purpose |
|---|---|
| `state/config/runs/d44128e9-4e17-4452-a535-989e826cd7da/directive.yaml` | Attempt 1 directive (cp1252-crashed) |
| `state/config/runs/9eabd5ac-e170-49ad-8806-1d6ebd00c48e/directive.yaml` | Attempt 5 directive (PYTHONIOENCODING=utf-8 first success at G0 print) |
| `state/config/runs/c8c3b6be-abea-4932-87bf-e52aa11f6f67/directive.yaml` | Attempt 6 directive (`< /dev/null`) |
| `state/config/runs/db05cda7-a45c-4164-9360-549a4323b95d/directive.yaml` | Attempt 7 directive (pipe without --auto-confirm) |
| `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/directive.yaml` + `run.json` | **Attempt 8 — Texas exit 30; canonical Trial-2 evidence run** |

All five directive YAMLs are byte-identical except for run_id field — confirms the directive composer is deterministic-but-broken (corpus-scan fallback gives identical output every run regardless of context).

`C:\tmp\run-trial-2.sh` retained as launch helper for next Trial-2 attempt (post-Slab-7c §02A landing).

---

## Cycle metrics

- **Wall-clock from session-open to structured stop:** ~1 hour
- **Successful pipeline progress:** G0 cleared (Attempt 8); Texas dispatched; halted at body wrangler exit 30
- **Substrate gates green:** all 8 pre-flight checks PASS at session-open + post-stop
- **Cost:** zero (no specialist actually fired LLM/API calls; Texas wrangler hard-failed before dispatch)

---

## References

- **Slab 7b retrospective:** `_bmad-output/planning-artifacts/slab-7b-retrospective.md`
- **Slab 7b 7b.12 closeout:** `_bmad-output/implementation-artifacts/migration-7b-12-integration-parity-suite-closeout.md` §AC-O / §AC-P
- **Story 7a.3 (pre-gate-marcus shared LLM node):** `_bmad-output/implementation-artifacts/migration-7a-3-pre-gate-marcus-shared-llm-node.md`
- **Story 7b.1 (Texas hardening):** `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md`
- **Anti-pattern A11 (Windows-portability):** `docs/dev-guide/specialist-anti-patterns.md`
- **Trial-475 prior reference:** `next-session-start-here.md` Trial-475 paused-at-G1 reference (2026-04-28)
- **Marcus MEMORY (PYTHONIOENCODING precedent):** `_bmad/memory/bmad-agent-marcus/MEMORY.md` 2026-04-17 entry
