# Codex dispatch: Slab 5a resume — 5a.3 (amended) → 5a.4 → 5a.5 (M5 ship gate)

**Session:** 2026-04-26 (operator-authorized post-5a.2-close)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:** 5a.1 done (commit per sprint-status); 5a.2 done (commit `9e244c3`).
**Blocker resolved:** 5a.3 T1 halt of 2026-04-26 (operator HALT-PENDING-BASELINE consensus) is **resolved by substrate-aware amendment**. 5a.3 spec has been re-authored; 5a.4 + 5a.5 + governance JSON updated in lockstep.

## What changed since you halted

You halted 5a.3 T1 because:
1. Required `_bmad-output/economics-baselines/primary-repo-baseline-<date>.json` did not exist (legacy code does not capture per-call token data; operator tracks via service-provider invoices only).
2. Spec cited `app/runtime/model_cascade.py` which does not exist on this branch.

Both blockers are **dissolved**, not worked around. The 5a.3 spec is amended to drop the relative-to-legacy reduction bar entirely and reframe as **cost-engineering foundation shipped by the migration** (capability that did not exist on legacy). The amended spec is at `_bmad-output/implementation-artifacts/migration-5a-3-economics-cost-reduction-bar.md` with a **SUBSTRATE-AWARE ADAPTATION** header documenting the operator-ratified decision (mirror of 3.1 substrate-aware adaptation precedent).

## Operator-ratified decisions binding 5a.3 (D1–D9)

These are **not for you to relitigate at T1**. They are pinned in the spec header:

- **D1.** Marcus = frontier-tier model; specialists = right-sized per role with stated rationale per agent.
- **D2.** OpenAI family only (operator's only API key family). Models parameterized via config; no hardcoded model IDs in agent code.
- **D3.** Per-specialist model assignment inferred from specialist-registry + specialist code; you propose; operator ratifies at close (see Dev Agent Record §"Cascade Assignment Ratification").
- **D4.** Richer cost-tracking scope: per-trial cost report + per-agent attribution + drift alerts.
- **D5.** Parameterize-with-defaults for model picks. No model-ID lock at this story; defaults baked into config; operator swaps via config edit.
- **D6.** Pricing table = config file (`runtime/config/openai_pricing.yaml`); manual update when OpenAI prices change.
- **D7.** Soft-cap budget opt-in via env `MARCUS_TRIAL_BUDGET_USD`; default unset = no cap; over-budget logs warning + emits span; **does NOT halt mid-trial**.
- **D8.** Cost-data persistence at `state/config/runs/<trial-id>/cost-report.{json,md}` colocated with the trial.
- **D9.** Drift alert: rolling 5-trial median per agent; ±50% deviation = informational alert; not blocking.

**Default cascade (proposed; you may refine after reading the specialist registry):**
- Marcus: `gpt-5`
- Mid-tier (Irene editorial, Gary slide gen, Vera verification): `gpt-5-mini`
- Narrow-task (Texas tool dispatch, Quinn-R retrieval, Tracy linting): `gpt-5-nano`

## LangSmith credentials provisioned

Operator confirmed in this session:
- **Personal Access Key** = local trial runs.
- **Service Key** = CI/GHA (the trial-replay workflow at `.github/workflows/trial-replay.yml` from 5a.1; you do not need to wire LangSmith into that workflow as part of 5a.3 unless explicitly in scope).
- **Workspace name:** `course-content-production`.
- Free-tier limits (5K traces/mo, 14-day retention) sufficient. Cost-report JSON persisted to disk per D8 gives permanent record independent of LangSmith retention.

Update `.env.example` per AC-5a.3-J file structure (LangSmith vars + optional MARCUS_TRIAL_BUDGET_USD comment guidance). Operator's local `.env` is already populated with the key; you do not modify the live `.env`.

## Sequence to ship

1. **5a.3** (this dispatch) — re-run T1 against the amended spec; substrate verification expected to pass cleanly (the amendment IS the substrate adaptation). Implement per ACs A–L. Operator ratifies cascade assignment at close per D3.
2. **5a.4** — invariant matrix + FR64 catalog final. Spec updated to reflect amended 5a.3 framing (capability-shipped, not relative-reduction). Already at `ready-for-dev`.
3. **5a.5** — M5 ship verdict. 6-agent party-mode (Winston + Murat + Paige + Quinn-R + Amelia + **Dr. Quinn** for strategic framing — fixed roster per epic 5a.5 binding). Spec amended to drop ≥50% reduction language from prompt template; cost-engineering-foundation evidence is now the basis for the cost-related portion of the M5 verdict.

## Carry-forward riders to surface at 5a.5

When you reach 5a.5, the M5 verdict path **must** address these inherited conditional states:

- **M2 conditional** from 2c.4 (if still unresolved at 5a.5 open).
- **M3 conditional** from 3.6 (if still unresolved).
- **M4 conditional** from 4.7 (if still unresolved).
- **5a.2 control-plane-parity rider** — production-clone-launch parity is NOT proven; only control-plane parity. The M5 verdict path either resolves this pre-vote (operator launches a real new clone trial via a real `app.marcus.cli trial start` launcher) or carries it forward as a SHIP-WITH-RIDERS rider with the launcher follow-on filed to deferred-inventory.
- **5a.3 cascade ratification** — if D3 cascade-assignment-ratification did not happen at 5a.3 close, surface at 5a.5.

The M5 verdict enum allows SHIP / SHIP-WITH-RIDERS / SHIP-CONDITIONAL / ITERATE / ROLLBACK / ABSTAIN per agent + 5-enum consensus (ABSTAIN excluded). Operator wants honest scope binding, not over-claiming. SHIP-WITH-RIDERS is acceptable; SHIP-CONDITIONAL with named-window is acceptable.

## Operator preferences (reminder)

- "Do it right" — no band-aids, only rational trade-offs that get named in writing (riders, deferred-inventory entries, anti-pattern catalog).
- Substrate verification at T1 is non-negotiable but *fast* — don't re-derive substrate decisions already pinned in the amended spec header.
- Sandbox-AC discipline: dev-agent ACs use shipped Python deps (`langsmith`, `pyyaml`, `psycopg`, etc.); CLI checks reserved for operator-gated AC blocks. The amended 5a.3 spec has already been validated PASS by `scripts/utilities/validate_migration_story_sandbox_acs.py`.
- Run `.venv/Scripts/python.exe -m pytest <slice> -q --tb=short` for the story-owned slice; repo-wide pytest remains environment-tainted on operator's Windows machine and is documented as such (5a.1 close note + 5a.2 close note).
- Per-story D12 close protocol (4-line for single-gate; 5-line for dual-gate). Sprint-status state-flips at filing AND close.

## What unblocks you immediately

1. Read the amended 5a.3 spec (especially the SUBSTRATE-AWARE ADAPTATION header + D1–D9 + Decision #1 deliverables).
2. Verify substrate items in T1 Readiness Block §2 against the live tree (the amendment expects all listed paths to NOT exist; you create them).
3. Read the specialist registry (path noted in T1 §4) to inform per-specialist cascade entries.
4. Implement per ACs; ratify cascade assignment with operator at close per D3.
5. Proceed to 5a.4 once 5a.3 is `done` in sprint-status; proceed to 5a.5 once 5a.4 is `done`.

## What to escalate, if needed

- If `langsmith` python dep cannot read traces from the operator's `course-content-production` workspace at T1, fall back to synthetic trace fixture per AC-G note ("operator-window-conditional pattern") and surface in Dev Agent Record. Do not block.
- If the proposed default cascade conflicts with a specialist's actual reasoning needs you observe in code (e.g., narrow-task specialist actually needs frontier reasoning for a specific subtask), propose the deviation with rationale in the cascade YAML rationale field; operator decides at close.
- If you discover a substrate divergence that contradicts the amended spec, halt and surface — same discipline as 3.1 / 5a.2 patterns. Do not silent-edit.

## Verification gates at 5a.3 close

- `pytest tests/unit/runtime tests/integration/runtime tests/migration/test_5a_3_characterization_baseline_present.py -q --tb=short` — all pass.
- `ruff check app/runtime app/models/runtime tests/unit/runtime tests/integration/runtime tests/migration/test_5a_3_characterization_baseline_present.py` — clean.
- `lint-imports --config pyproject.toml` — 9 KEPT (or higher if you add a new contract).
- `scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-5a-3-economics-cost-reduction-bar.md` — PASS (already PASSing on amended spec).
- Cascade YAML + pricing YAML + characterization-baseline Markdown all present + valid.
- Sprint-status state-flip to `done` with close comment noting 2026-04-26 amendment.

## Final note

This amendment is exactly the discipline at 3.1 substrate-aware adaptation: when spec and substrate disagree, halt, name the disagreement, get operator ratification, re-author. That happened. The amended spec is the contract. Build against it without second-guessing the operator-ratified decisions — and surface honestly if implementation reveals further substrate gaps.

Slab 5a finishes when 5a.5 ships its M5 verdict. You have a clean runway from here. Good hunting.
