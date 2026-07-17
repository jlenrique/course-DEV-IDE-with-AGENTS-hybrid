---
id: 42-4
epic: 42
status: ready-for-dev
depends_on: 42-2   # needs the lifecycle fix (pause keeps HUD alive) before a public overlay is meaningful
gate_mode: dual-gate   # own security/non-leak bar + app/hud/** lockstep
anchor_provenance: HEAD 23480353
baseline_commit: 8d485ace  # dev-open baseline 2026-07-17 (post-42-5; last Epic-42 story)
lockstep: true   # app/hud/** + ops integration
---

# Story 42.4: Public read-only HUD at a stable URL, browsable from any machine

Status: done  # 2026-07-17 dev complete (app-side hermetic) + dual-gate review PASS; tunnel/identity leg operator-gated live evidence

## Dev Agent Record

**Dev complete 2026-07-17 (fresh Claude dev agent). Baseline `8d485ace`. Status → review → done (operator-gated tunnel leg owed).**

### File List
- `app/hud/public.py` (A) — distinct public overlay app + `build_public_view` **positive allowlist** (copies only enumerated fields per section; unknown/future fields dropped by default). `create_public_hud_app` takes NO `launch_nonce` (structurally can't serve it), own port (8792), 3 GET routes, `/healthz` without nonce, `/projection` = scrubbed view (never `snapshot.raw`), unrecognized→secret-free `_offline_page`.
- `app/marcus/orchestrator/preflight.py` (M, additive) — `PublicOverlayConfig.from_env` (tunnel mode/token/name/hostname/port from env, never hardcoded), `tunnel_argv` (cloudflared named-tunnel / tailscale serve — NEVER `--url` quick-tunnel), `launch_public_overlay` + `_spawn_child` (CREATE_NO_WINDOW on win32, registers 42-2's `_status_aware_teardown`, NEVER-raises, unconfigured→no-op).
- `docs/admin-guide.md` (M) §Public Read-Only HUD Overlay + `docs/operator/hud-guide.md` (M, pointer) — the operator Cloudflare/Tailscale setup recipe + validation checklist.
- `tests/hud/test_public_surface_readonly_and_nonleak.py` (A, 15) + TW-7c-4 allowlist.
- **`app/hud/server.py` NOT touched** — the overlay is a new `app/hud/**` module → satisfies the lockstep glob with zero blast radius on the authority server.

### Completion Notes
- The public surface serves a positive-allowlist scrub — drops `launch_nonce`, `next_action.command` (resume paste), decision-card digests, error message text, preflight item outputs, deliverable paths, `envelope_digest`, `manifest_digest`, `operator_id`, `specialist.model/cost`, `trace.detail`, notifications-echo. Localhost (8791) stays authority; the tunnel fronts the SEPARATE public app (8792), so the nonce-bearing authority `/healthz` + raw `/projection` are never tunnel-reachable (defense-in-depth beyond the tunnel ACL). Identity-aware (Cloudflare Access / Tailscale ACL), never anonymous/shared-password.

### Change Log
- 2026-07-17: public read-only HUD overlay (`app/hud/public.py` positive-allowlist) + tunnel plumbing (operator-gated) + operator recipe; done.

## Senior Developer Review (AI) — 2026-07-17 — DUAL-GATE (security)

**Reviewer:** orchestrator, inline adversarial (hermetic; no windows). **Outcome: APPROVE (operator-gated tunnel leg owed).**

**Security core (non-leak):** VERIFIED — `build_public_view` is a genuine POSITIVE allowlist (`_copy_allowed(section, ALLOWED_*)` per section; a fresh dict, never `snapshot.raw`), so any un-named/future field is dropped by default — the safe direction. The public app has no `launch_nonce` parameter (structurally can't serve it) and runs on a separate port, so the authority server's nonce/raw surfaces are never tunnel-reachable. The **teeth-check test** (`test_local_authority_server_does_echo_secrets_teeth_check`) proves the local authority DOES carry the sentinels — so the non-leak assertions are non-vacuous. Excellent test discipline for a security bar.

**Convention conformance:** follows the hud-guide service contract (GET-only, read-only/zero-mutation, localhost authority, no wrong-run fallback → `_offline_page`/foreign-veil); tunnel config from env (never hardcoded); no-quick-tunnel refusal; CREATE_NO_WINDOW on the tunnel child; reuses 42-2's status-aware lifecycle owner; NEVER-raises (unconfigured/failed → reach degrades, run never does).

**Verification:** 15 hermetic tests pass (non-leak allowlist `test_build_public_view_drops_every_forbidden_sentinel` + teeth-check + read-only + no-quick-tunnel + idle/foreign veil + windowless spawn + localhost-preserved); `tests/hud`+`tests/notify` 145 pass; lockstep exit 0; ruff clean; import-linter 18/0 (HUD1 layer fence held); TW-7c-4 pass; diff scope = `public.py` (new) + `preflight.py` + docs + tests — **server.py untouched, no other trigger-path source**; baseline-diff net-new 0 (the 1 fail is the known inherited `test_health_tiles_prefer_persisted_cost_report`).

**Findings:** none blocking. **Operator-gated live evidence owed:** the actual Cloudflare Tunnel + Access (or Tailscale Serve) stand-up, identity enforcement, and second-device reachability at the stable hostname — per `verify-via-shipped-deps`, operator runs it against the admin-guide recipe. This lands in the Epic-42 live-test.

## Story

As the operator on a one-monitor, always-online machine,
I want a public, read-only HUD page at an unchanging URL I can open from any browser or phone,
so that I can watch and review a live run without the full-screen local HUD obscuring the working surface it's meant to support — while the authoritative HUD stays on localhost and no secrets ever cross the wire.

## Provenance & Dependencies (BINDING)

- **Epic authority:** `epics-operator-surface-next-pass-2026-07-16.md` §42-4 (E42-AC2 availability, public surface) + the **non-leak bar**.
- **Green-light:** party record P-6 (split from D/42-2 — own security/infra failure domain; must not block the hermetic lifecycle fix) + the Murat non-leak AC.
- **Requirement (do not fork):** `deferred-inventory.md` §HUD Next-Pass `hud-stable-public-live-url` (the full operator-preferred path is specified there) + `evidence/operator-hil-display-requirements-2026-07-16.md` §3 (reaffirmed: public read-only, any computer, unchanging URL).
- **Depends on 42-2:** the pause-survives lifecycle fix — a public overlay is only useful if the underlying HUD stays alive across pauses.
- **Non-waivable activation trigger (from the inventory):** build + validate this before the next production Marcus-SPOC trial directly steered by Juanl; do not begin that trial with only the local full-screen HUD.

## T1 Readiness (BINDING readings before any code)

1. **Lockstep gate FIRST:** `docs/dev-guide/pipeline-manifest-regime.md` — `app/hud/**` is a trigger glob.
2. `deferred-inventory.md` §HUD Next-Pass `hud-stable-public-live-url` — the FULL requirement: Cloudflare Tunnel + Access on one stable custom hostname (preferred); Tailscale Serve with a stable `*.ts.net` name (acceptable fallback); no anonymous quick-tunnel; identity-aware access (Cloudflare Access identity/MFA or emailed single-use PIN allowlisted to the operator; never reusable Basic-Auth); localhost stays authority; read-only overlay; lifecycle coupled to the run.
3. `app/hud/server.py` — the GET-only localhost server (bind, zero-lie raw-file serve). The public surface is an OUTBOUND overlay of this, not a second authority.
4. `app/marcus/orchestrator/preflight.py` `launch_hud_server` (+ 42-2's lifecycle owner) — where run start launches/health-checks the HUD; the tunnel launch/health-check couples here.
5. The exact non-leak inventory (evidence note + deferred entry): never expose resume commands/nonces/digests, private source text, credentials/tokens, or operator-only secrets on the public surface.

## Acceptance Criteria

1. **Public read-only page, stable hostname.** The HUD is reachable from any browser at ONE stable custom hostname via an outbound secure overlay (named Cloudflare Tunnel + Access preferred; Tailscale Serve `*.ts.net` fallback). Localhost remains the authority; the public surface is a READ-ONLY overlay. The hostname is reserved and stable run-to-run.
2. **Non-leak bar (BINDING, Murat).** The public surface exposes NONE of: resume commands / nonces / launch digests, private source/corpus text, credentials/tokens, or any operator-only secret. A test/inspection enumerates the public-surface content against a denylist and fails if any forbidden field could render. Resume affordances and secrets stay localhost-only.
3. **Identity-aware access.** Access is restricted to the operator's approved identity — Cloudflare Access (account login + MFA, or emailed single-use PIN allowlisted to the operator), or the operator's tailnet (Tailscale). NEVER an anonymous quick-tunnel URL; NEVER a reusable shared/Basic-Auth password.
4. **Lifecycle coupled to the run (with 42-2).** Run start launches + health-checks the HUD + tunnel; pauses keep them alive (42-2); terminal status stops them after a short grace. When no run is active the stable hostname honestly shows `HUD offline / no active run`. A fresh run takes over the SAME canonical hostname; a newer run supersedes an older one.
5. **Localhost authority preserved.** With the tunnel down or unconfigured, the local HUD is unchanged and fully functional (the overlay is additive; its failure degrades reach, never the run or the local surface). NEVER-raises preserved.
6. **Operator setup is documented + validated.** `docs/` (admin/operator guide) gains the exact setup recipe (Cloudflare Tunnel + Access named-hostname steps; Tailscale fallback) and a validation checklist. The story's live-validation leg confirms the operator can reach the read-only page from a second device under identity, with the denylist inspection clean.

## Scope Fences (hard NO)

- **NO write path on the public surface** — read-only overlay, always. No resume/verdict actions exposed remotely.
- **NO anonymous quick-tunnel, NO reusable shared password / Basic-Auth** — identity-aware only.
- **NO GitHub Pages deploy, stale snapshot, or HA layer** — not required for this operator need (per the inventory).
- **NO change to what the local HUD SERVES or its authority** — the overlay mirrors, it does not replace.
- **NO secret/nonce/digest/source-text on the wire** — the non-leak bar is non-waivable.
- **NO coupling that makes 42-2's hermetic lifecycle fix depend on tunnel infra** (P-6) — 42-4 consumes 42-2, not the reverse.

## Lockstep declaration

| Scoped file | Trigger-path entry? | Touched? |
|---|---|---|
| `app/hud/server.py` / `app/hud/**` | **trigger glob** | likely (public overlay wiring, read-only guard) |
| `app/marcus/orchestrator/preflight.py` | not listed | likely (tunnel launch/health-check at run start, alongside 42-2's owner) |
| `docs/admin-guide.md` / operator guide | not listed | yes (setup recipe + validation checklist) |

**Verdict: lockstep regime TRIGGERED** (`app/hud/**`) + an infra/security bar. Read `pipeline-manifest-regime.md` at T1; Cora block-mode hook; the non-leak denylist inspection is an explicit review gate. This story has a real live-validation leg (operator-gated, per `verify-via-shipped-deps` — the tunnel/identity setup is operator-gated evidence pasted into completion notes).

## Dev Notes

- Prefer the named Cloudflare Tunnel + Access path (the operator-preferred). The app-side change is: (a) a read-only guard so the tunneled surface can never serve a write/secret field (defense-in-depth beyond the tunnel ACL), and (b) tunnel launch/health-check coupling to the run lifecycle owner (shared with 42-2). Keep the tunnel process under the same NEVER-raises + grace-teardown discipline as the HUD child.
- The non-leak guard should be a positive allowlist of renderable fields on the public surface (safer than a denylist) — enumerate exactly what the read-only page may show (status, gate, progress, settings readout from 42-3, ambient roster/trace WITHOUT source text or digests), and drop everything else.
- Operator access coaching: provide the grounded recipe (proven steps) per the `agents-coach-operator-access` memory — do not hand-wave the Cloudflare/Tailscale setup.
- Tests: `tests/hud/test_public_surface_readonly_and_nonleak.py` — the allowlist/denylist inspection (AC-2), read-only guard rejects any write route, idle `HUD offline` honesty, localhost-authority-preserved when tunnel absent. The tunnel/identity integration itself is operator-gated live evidence.

## References

- `deferred-inventory.md` §HUD Next-Pass `hud-stable-public-live-url` (full requirement)
- `evidence/operator-hil-display-requirements-2026-07-16.md` §3
- `epics-operator-surface-next-pass-2026-07-16.md` (§non-leak bar, P-6)
- memory `agents-coach-operator-access`
- `docs/dev-guide/pipeline-manifest-regime.md`

## Green-Light Round Record (2026-07-16)

**Verdict: 5/5 GREEN** — Winston fenced E's blast radius (infra + identity + secrets ≠ D's hermetic fix; P-6 split); Murat made the non-leak bar an explicit enumerated allowlist AC, not "we'll be careful"; Sally held the "reachable from any computer at an unchanging URL" promise; John kept it from blocking the rest of the epic (depends on 42-2, own bar, lands a hair later). Dual-gate (lockstep + security). Status → ready-for-dev.
