# Epic 42 — Operator Surface Next-Pass (2026-07-16)

**Status:** in-progress (green-lit 2026-07-16; `party-greenlight-post-trial-bc747b51-arc-2026-07-16.md`)
**Class:** S — operator-facing runtime surfaces (CLI HIL + HUD). Honest successor to **Epic 35 — Operator HUD v1** (closed 2026-07-12).
**Dev posture:** fresh-Claude-dev-agent, per-story fresh context. 42-2/42-3/42-4/42-5 touch `block_mode_trigger_paths` (`operator_surface` assembler, `app/hud/**`, `app/notify/**`) → pipeline-manifest lockstep regime + Cora block-mode hook.

## Why this epic exists

The `bc747b51` production trial exposed that the operator could not reliably **read** the run's HIL surfaces or **reach** the HUD while a paid run was live:

- After G0 confirm, enrichment printed a sheaf of `NOT grounded` log lines then a JSON blob and returned to PowerShell; the operator typed `c` at the shell (`CommandNotFoundException`). The run was fine — the **surface** failed the reviewability bar.
- The HUD (`--hud on`) tore down when `trial start` returned at the G0E pause (port 8791 no longer LISTENING) — the operator flew without a live HUD for most gates.
- The operator wants a **public, read-only** HUD browsable from any computer at a stable URL, and a standing readout of **all ~16 run-defining toggles** plus a pre-walk confirm-or-change surface.
- The gate `next_action.command` hardcodes `--verb approve`, pre-framing the operator's verdict.

Thesis: *the operator must be able to see the run's state and act on it without decoding JSON or guessing which shell he's in, from wherever he is.*

## Stories

| Story | Title | Gate | Depends | Lockstep |
|---|---|---|---|---|
| **42-1** | Tabular HIL projection + neutral next-action verb (C+G) | single | — | no (CLI display + `next_action.py`) |
| **42-2** | HUD lifecycle survives gate pause (D) | single | — | **yes** (`app/hud/**`, `app/notify/**`, start-path) |
| **42-3** | Full run-settings standing readout — ~16 toggles (F.a) | dual | — | **yes** (`operator_surface` assembler) |
| **42-4** | Public read-only HUD at a stable URL (E) | dual | 42-2 | **yes** (`app/hud/**` + ops) |
| **42-5** | Pre-walk settings confirm-or-change gate (F.b) | dual | 42-3 | **yes** (start-path HIL pause + assembler) |

**DAG:** 42-1 and 42-2 are independent and can open first. 42-3 → 42-5 (the readout must exist before the confirm gate projects it). 42-4 depends on 42-2's lifecycle fix but carries its own security/non-leak bar and can land a hair later without blocking the others.

## Epic-level acceptance

- E42-AC1 (reviewability): every operator-facing HIL review surface — CLI gate printouts, enrichment advisories, decision-card prompts — projects into **tables/containers**, replayable against the frozen `bc747b51` `g0-enrichment.json` + `operator-surface.json`; the gate next-action never preselects a verb. (42-1)
- E42-AC2 (availability): the HUD stays alive across start-walk → gate pause → resume; teardown only on terminal status + explicit stop (+ grace). A public read-only page is reachable from any browser at a stable URL, leaking no secrets/nonces/digests/source text. (42-2, 42-4)
- E42-AC3 (completeness): the HUD shows all ~16 run-defining toggles as a standing readout for the whole run, and a pre-walk surface lets the operator confirm-or-change them before the walk proceeds. (42-3, 42-5)

## Non-leak bar (42-4, binding)

The tunneled/public surface is **read-only** and MUST NOT expose: resume commands/nonces/digests, private source text, credentials/tokens, or any operator-only secret. Identity-aware access (Cloudflare Access identity or emailed single-use PIN; never anonymous quick-tunnel / reusable Basic-Auth). Preferred path: named Cloudflare Tunnel + Access on one stable custom hostname; acceptable fallback: Tailscale Serve with a stable `*.ts.net` name. Localhost stays authority.

## Retrospective

optional; consult `deferred-inventory.md` §HUD Next-Pass at close.

## References

- `_bmad-output/planning-artifacts/party-greenlight-post-trial-bc747b51-arc-2026-07-16.md`
- `_bmad-output/implementation-artifacts/evidence/operator-hil-display-requirements-2026-07-16.md` §§1–5
- `_bmad-output/planning-artifacts/epics-operator-hud-2026-07-11.md` (Epic 35 — the projection-contract substrate this extends)
- `_bmad-output/planning-artifacts/deferred-inventory.md` §HUD Next-Pass + §Named-But-Not-Filed (the six reactivated rows)
- Frozen run: `state/config/runs/bc747b51-7009-4742-9f65-8de6abc29ca4/`
