---
id: 42-8
epic: 42
status: ready-for-dev   # operator-directed 2026-07-17: add an ngrok-reserved (stable, no-login) public tunnel mode to 42-4
depends_on: 42-4
gate_mode: single-gate   # additive tunnel mode; app/hud/** + preflight (lockstep glob) but hermetic + additive
lockstep: true   # app/hud/** glob + preflight tunnel plumbing
---

# Story 42.8: ngrok-reserved public HUD tunnel mode — one stable, no-login read-only URL

Status: ready-for-dev  # operator directive: stable anonymous public URL via ngrok reserved domain

## Story

As the operator,
I want the public read-only HUD reachable at ONE stable URL (an ngrok reserved domain) with no viewer login,
so that I can open the same URL from any device during a run — nothing proprietary is shown and the HUD is read-only.

## Operator directive (2026-07-17)

The operator chose a **plain, stable, no-login public URL** over the identity-gated Cloudflare/Tailscale defaults 42-4 shipped: *"a plain anonymous public URL is fine — nothing proprietary will be displayed on the HUD, and the HUD is read-only… take the ngrok-reserved approach so we have a stable URL."* The operator makes the rules; 42-4's identity-gate + no-anonymous default was a design default, now overridden for this mode.

## What to add (additive tunnel mode; keep the existing modes)

Extend 42-4's `PublicOverlayConfig` / `tunnel_argv` / `launch_public_overlay` (`app/marcus/orchestrator/preflight.py`) with an **`ngrok` mode** alongside the existing `cloudflare`/`tailscale`:
- `HUD_TUNNEL_MODE=ngrok` + `HUD_TUNNEL_NGROK_DOMAIN=<reserved-domain>` (the operator's reserved ngrok domain, e.g. `marcus-hud.ngrok-free.app` or a custom reserved subdomain) + `HUD_TUNNEL_NGROK_AUTHTOKEN` (or rely on `ngrok config add-authtoken` having been run; read from env, never hardcoded).
- Launch: `ngrok http --domain=<reserved-domain> 8792` (bin overridable via `HUD_TUNNEL_NGROK_BIN`; the reserved `--domain` makes the URL STABLE run-to-run — no random per-run URL).
- The public URL = `https://<reserved-domain>`, surfaced to the operator at run start (stdout/log + the local HUD identity panel) so it's visible each run.

## Acceptance criteria

1. **ngrok mode launches the reserved-domain tunnel** fronting the public app (localhost:8792 from 42-4). Stable URL = the reserved domain, constant run-to-run.
2. **No viewer login / identity gate** in this mode (operator's choice) — but the surface stays READ-ONLY and the 42-4 positive-allowlist non-leak scrub STAYS (harmless belt-and-suspenders; nothing proprietary, but keep the scrub). No write path, ever.
3. **Config from env, never hardcoded;** authtoken/domain read from env. Absent config → ngrok mode inert (localhost HUD unchanged), like the other modes. NEVER-raises (a tunnel fault degrades reach only).
4. **Lifecycle + windowless (reuse 42-2/42-4):** the ngrok child registers 42-2's status-aware teardown (survives pause, torn down on terminal + grace) and spawns with `CREATE_NO_WINDOW` on win32. Localhost stays authority.
5. **URL surfaced:** the stable URL is printed/logged at launch + shown on the local HUD, so the operator can hand it out.
6. **Operator setup recipe** for the ngrok path added to `docs/admin-guide.md §Public Read-Only HUD Overlay` (install ngrok, `ngrok config add-authtoken`, reserve a domain in the ngrok dashboard, set the 3 env vars). Note the **ngrok-free interstitial** quirk (free-tier anonymous visitors see a one-click "you are about to visit" ngrok warning page before the HUD; bypassable via the `ngrok-skip-browser-warning` request header or a paid plan — acceptable for a self-viewed read-only HUD; document it so it's not a surprise).

## Scope fences (hard NO)

- NO removal of the existing cloudflare/tailscale modes — ngrok is ADDITIVE (operator picks via `HUD_TUNNEL_MODE`).
- NO write path on the public surface (read-only always).
- NO hardcoded domain/authtoken — env only.
- Keep the 42-4 non-leak scrub (don't relax it — it's free defense even though nothing proprietary is shown).
- Only `app/hud/**` + `preflight.py` + docs + tests.

## Tests (hermetic)
Extend `tests/hud/test_public_surface_readonly_and_nonleak.py` (or a sibling): (a) `HUD_TUNNEL_MODE=ngrok` + domain → `tunnel_argv` = `ngrok http --domain=<domain> 8792` (no random URL); (b) absent config → inert; (c) ngrok child registers the status-aware teardown + CREATE_NO_WINDOW on win32 (mock the spawn); (d) the read-only + non-leak scrub still holds in ngrok mode; (e) URL-surfacing (the reserved domain is logged/emitted). Register any new test in TW-7c-4 allowlist.

## Validation
- New tests green; `tests/hud/` + `tests/notify/` green; lockstep exit 0; ruff; import-linter 18/0; baseline-diff net-new=0.
- `git diff --name-only` = app/hud/** + preflight.py + docs + tests. No other trigger-path source.
- Operator-gated live leg: the actual ngrok reserved-domain stand-up + second-device reachability at the stable URL (operator runs it against the recipe).

## References
- `_bmad-output/implementation-artifacts/42-4-public-readonly-hud-stable-url.md` (the overlay this extends)
- Operator directive 2026-07-17 (this session); [[feedback_operator_makes_the_rules_no_forbidden_framing]]
- `docs/admin-guide.md §Public Read-Only HUD Overlay`

## Green-Light
Operator-directed (2026-07-17) — that is the green-light. Additive tunnel mode; single-gate; fresh-Claude-dev-agent.
