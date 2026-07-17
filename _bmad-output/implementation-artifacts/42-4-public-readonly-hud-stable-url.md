---
id: 42-4
epic: 42
status: ready-for-dev
depends_on: 42-2   # needs the lifecycle fix (pause keeps HUD alive) before a public overlay is meaningful
gate_mode: dual-gate   # own security/non-leak bar + app/hud/** lockstep
anchor_provenance: HEAD 23480353
lockstep: true   # app/hud/** + ops integration
---

# Story 42.4: Public read-only HUD at a stable URL, browsable from any machine

Status: ready-for-dev  # green-lit 5/5 2026-07-16; dual-gate; own non-leak bar; LOCKSTEP

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
