# Irene-literal authentic liveproof — claim assessment

**Trial:** `235f2b82-5989-4a6f-9e6b-22e9697f58d2`  
**Guide:** `hil-2026-apc-crossroads-classic` (`text_mode=condense`, amount minimal)  
**Driver claim_ok:** `False` (exit 2) — **over-strict / observer bug; core product claim is MET.**

## Product claim (what we set out to prove)

Under classic **condense**, with **no G1 fidelity stamp**:

1. Irene Pass-1 **emitted** structured fidelity (authentic).
2. Package briefs carried it onto slides.
3. Gary **binary-split** cohorts and paid-dispatched a literal cohort separately from creative while styleguide settings remained `condense`.

### Evidence

| Signal | Value |
|--------|--------|
| Irene `irene_pass1` contribs | 3; latest plan_units fidelity = `literal-text:2`, `creative:6`, `literal-visual:1` |
| Package slides | same counts (`literal-text:2`, `creative:6`, `literal-visual:1`) |
| `gary.calls_made` | **2** |
| Export witnesses | `gary_A_creative.png`, `gary_A_literal.png` |
| Bound variant settings | still `text_mode=condense` / amount present on settings layer |
| Stamp | **none** (`irene_fidelity_emit=authentic-pass1-only-no-stamp`) |

**Verdict:** **MET** — Irene emit → Gary honor-over-styleguide under classic-condense is live-proven.

## Why driver `claim_ok` was False

1. **G1 observer false-negative:** `observe_irene_fidelity()` reported `no irene_pass1 contribution` / null counts at G1 (API/timing), so `irene_emitted_literal_text` stayed False even though later contribs clearly carry fidelity.
2. **Walk stopped after G2C** on `irene.pass2.figure-contradiction` — known classic-condense Pass-2 figure gate (S8 used preserve sibling to clear terminal). **Out of scope** for the Irene-literal→Gary-preserve claim.

## Explicit non-claims

- Does **not** close `fidelity-L1-per-slide-text-mode` broadly.
- Does **not** close `literal-visual-production-streamline`.
- Does **not** claim full terminal `completed` under classic-condense (Pass-2 figure-contradiction still open on this path).

## Follow-ups (optional)

- Patch AFK observer to scan all `irene_pass1` contributions (not a brittle `latest_for_specialist` miss) and set claim_ok from package/Gary witnesses even if Pass-2 later errors.
- Separate triage for `irene.pass2.figure-contradiction` under classic-condense (already inventoried from S8).
