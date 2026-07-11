---
name: Operator HUD — Flight Deck
description: Read-only dark-cockpit instrument panel for Marcus-SPOC production runs on a dedicated second monitor.
status: final
created: 2026-07-11
updated: 2026-07-11
sources:
  - _bmad-output/planning-artifacts/briefs/brief-operator-hud-revival-2026-07-11/brief.md
  - _bmad-output/planning-artifacts/briefs/brief-operator-hud-revival-2026-07-11/addendum.md
  - _bmad-output/planning-artifacts/hud-revival-party-assessment-and-plan-2026-07-11.md
colors:
  # Single dark mode. The HUD lives on a dedicated second monitor and is a
  # cockpit, not a document — there is no light theme.
  surface-base: '#0F172A'
  surface-raised: '#1E293B'
  surface-inset: '#0B1120'
  border-hairline: '#293548'
  ink-primary: '#E2E8F0'
  ink-secondary: '#94A3B8'
  ink-dim: '#64748B'
  active: '#38BDF8'
  active-ink: '#06263A'
  status-nominal: '#22C55E'
  status-nominal-dim: '#166534'
  status-caution: '#FBBF24'
  status-caution-ink: '#1C1403'
  status-warning: '#EF4444'
  status-warning-ink: '#FFFFFF'
  status-wait: '#A78BFA'
  status-wait-ink: '#1E1633'
  status-idle: '#64748B'
typography:
  annunciator:
    fontFamily: "'Segoe UI', system-ui, sans-serif"
    fontSize: 20px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: 0.06em
  zone-title:
    fontFamily: "'Segoe UI', system-ui, sans-serif"
    fontSize: 13px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: 0.08em
  body:
    fontFamily: "'Segoe UI', system-ui, sans-serif"
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  meta:
    fontFamily: "'Segoe UI', system-ui, sans-serif"
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.4'
  numeral:
    fontFamily: "'Segoe UI', system-ui, sans-serif"
    fontSize: 16px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: 0.01em
  mono:
    fontFamily: "'Cascadia Mono', Consolas, monospace"
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.5'
rounded:
  sm: 4px
  md: 6px
  lg: 8px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 24px
  '6': 32px
  gutter: 16px
components:
  annunciator-strip:
    background: '{colors.status-caution}'
    foreground: '{colors.status-caution-ink}'
    radius: '0'
    typography: '{typography.annunciator}'
  annunciator-strip-nominal:
    background: '{colors.surface-inset}'
    foreground: '{colors.ink-dim}'
  annunciator-strip-warning:
    background: '{colors.status-warning}'
    foreground: '{colors.status-warning-ink}'
  annunciator-strip-wait:
    background: '{colors.status-wait}'
    foreground: '{colors.status-wait-ink}'
  status-badge:
    radius: '{rounded.sm}'
    typography: '{typography.zone-title}'
  modality-chip:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    border: '1px solid {colors.border-hairline}'
    radius: '{rounded.full}'
    typography: '{typography.meta}'
  health-tile:
    background: '{colors.surface-raised}'
    border: '1px solid {colors.border-hairline}'
    radius: '{rounded.md}'
    value-typography: '{typography.numeral}'
    staleness-typography: '{typography.meta}'
  map-node-active:
    background: '{colors.active}'
    foreground: '{colors.active-ink}'
    radius: '{rounded.md}'
  map-node-nominal:
    background: 'transparent'
    foreground: '{colors.ink-dim}'
    marker: '{colors.status-nominal-dim}'
  gate-briefing-card:
    background: '{colors.surface-raised}'
    border-left: '3px solid {colors.status-caution}'
    radius: '{rounded.lg}'
  specialist-chip:
    background: '{colors.surface-raised}'
    border: '1px solid {colors.border-hairline}'
    radius: '{rounded.md}'
    monogram-typography: '{typography.zone-title}'
  command-block:
    background: '{colors.surface-inset}'
    foreground: '{colors.ink-primary}'
    border: '1px solid {colors.active}'
    radius: '{rounded.md}'
    typography: '{typography.mono}'
  state-trace:
    background: '{colors.surface-inset}'
    foreground: '{colors.ink-secondary}'
    typography: '{typography.mono}'
    radius: '{rounded.md}'
  stale-veil:
    border: '1px dashed {colors.status-caution}'
    stamp-foreground: '{colors.status-caution}'
    stamp-typography: '{typography.meta}'
  notification-toast:
    background: '{colors.surface-raised}'
    foreground: '{colors.ink-primary}'
    border: '1px solid {colors.border-hairline}'
    border-left: '3px solid {colors.status-caution}'
    radius: '{rounded.lg}'
    typography: '{typography.body}'
---

## Brand & Style

The Operator HUD is an **aviation dark cockpit**: a read-only instrument panel that sits on the operator's second monitor for the length of an hours-long Marcus-SPOC production run. The governing aesthetic is *quiet competence* — when the run is nominal, the panel is dim, desaturated, and nearly silent; the single bright object on screen is the active step. Brightness is information. Anything luminous is either *where the run is* or *what is wrong*.

This is deliberately not a dashboard in the BI sense — no decorative charts, no gradients-as-branding, no celebration states. It is closer to an aircraft's EICAS display or NASA Open MCT: a status hierarchy (annunciator → tiles → drill-down) rendered in a restrained slate palette the April HUD already established. Continuity with that idiom is intentional: the operator already reads slate/cyan/green/amber/red fluently, and ~98 render pins survive on it.

Every status is encoded three ways — **color + shape + symbol** — never color alone. Every number on the panel admits its age. The HUD would rather show an amber "STALE" veil than a confident lie.

## Colors

The palette is the April HUD's slate base, pushed toward cockpit discipline. One background family, one ink family, one accent, four status hues.

- **Slate surfaces (`{colors.surface-base}` / `{colors.surface-raised}` / `{colors.surface-inset}`)** — the cockpit at night. `surface-base` is the page; `surface-raised` is tiles and cards; `surface-inset` is recessed instrument wells (command blocks, the state-trace window, the nominal annunciator).
- **Ink ramp (`{colors.ink-primary}` / `{colors.ink-secondary}` / `{colors.ink-dim}`)** — nominal content sits low on this ramp on purpose. Completed steps and healthy tiles render in `ink-dim`/`ink-secondary`; only the content the operator must read *now* earns `ink-primary`.
- **Active Cyan (`{colors.active}`)** — exactly one meaning: *live / current / here*. The active map node, the current-step briefing border, the next-action command border. Never used for chrome, headings-at-large, or links.
- **Nominal Green (`{colors.status-nominal}`, dim variant `{colors.status-nominal-dim}`)** — pass/healthy. In flight, green appears almost exclusively in its dim variant (markers on completed steps, quiet tile rings); full-brightness green is reserved for moments the operator is actively reading a checklist (pre-flight items turning green one by one).
- **Caution Amber (`{colors.status-caution}`)** — the master-caution hue: paused-at-gate, health threshold crossed, and everything STALE. Amber always arrives with a shape (left border, veil, badge) and a symbol (⏸, ⚠, ⧗).
- **Warning Red (`{colors.status-warning}`)** — paused-at-error and failed. Red is scarce by design; if the panel shows red, something needs the operator.
- **Wait Violet (`{colors.status-wait}`)** — *waiting on an external party* (provider batch). Distinct from amber because nothing is wrong and no verdict is owed; the run is legitimately parked on someone else's queue.
- **Idle Slate (`{colors.status-idle}`)** — registered / not-started / pending.

**Contrast floors:** attention-state text (anything the operator must act on — annunciator text, briefing prose, command blocks, badge labels, stamps) holds ≥4.5:1 against its surface; status markers and shapes hold ≥3:1. The paired inks (`status-caution-ink` on amber, `status-warning-ink` on red, `status-wait-ink` on violet, `active-ink` on cyan) exist to keep filled elements at the text floor. **The nominal dim ramp is deliberately exempt:** `ink-dim` on `surface-base` (~3.7:1) is sub-AA by design — dimness *is* the "nothing needs you" signal at arm's-length instrument scale, and every dim element has a bright counterpart state when it needs attention.

Avoid: gradients (the April progress-bar gradient retires), any fourth accent, red or amber used decoratively, and any hue carrying a meaning not listed here.

## Typography

System sans (`Segoe UI` stack) for everything human; `Cascadia Mono`/Consolas for everything machine. The ramp is flat and small — a cockpit is read at a glance from arm's length, so hierarchy comes from weight, tracking, and luminance, not from large display sizes.

- **`annunciator`** — the one loud voice. Uppercase, tracked, bold; used only inside the annunciator strip.
- **`zone-title`** — uppercase tracked labels for zones, badges, and monograms.
- **`body` / `meta`** — briefing prose and staleness stamps ("as of 14:32:07 · 3s ago").
- **`numeral`** — instrument readouts (token burn, cost, credits, step N/total). Always `font-variant-numeric: tabular-nums` so values don't jitter as they tick.
- **`mono`** — run IDs, digests, node IDs, file paths, the state-trace, and the copy-paste command block. If the operator might paste it, it is mono.

## Layout & Spacing

A fixed vertical band stack on a 4px scale (`{spacing.1}`–`{spacing.6}`, `{spacing.gutter}` between zones):

1. **Annunciator strip** — full-width, always present, top of page.
2. **Identity header** — run ID, lesson, preset, status badge, modality chips, notifications chip, elapsed time, and the **freshness meter** (snapshot-age readout with the subtle sweep — the one standing motion on the page).
3. **Health strip** — one row of instrument tiles.
4. **Main deck** — two columns: the you-are-here map (left, ~60%) and the context panel (right, ~40%: pre-flight board, current-step briefing, or gate/error briefing).
5. **State-trace well** — full-width, collapsed by default.

The page is designed for a single landscape monitor at ≥1440px; below 1100px the main deck stacks (map above context panel). Nothing critical may live below the fold at 1440×900: annunciator, header, health strip, the active map node, and the briefing's next-action block must all be visible without scrolling (the five-second rule is a layout constraint, not an aspiration).

## Elevation & Depth

No shadows. Depth is tonal only: `surface-inset` reads as recessed instrument wells, `surface-raised` as tiles, hairline borders (`{colors.border-hairline}`) as panel seams. The single "lifted" treatment is the briefing card's 3px status-colored left border. Blinking is banned; motion is limited to a subtle sweep on the freshness meter and the annunciator's one-time 300ms luminance step-up when it changes state (suppressed under reduced-motion).

## Shapes

Tool-grade corners: `{rounded.sm}` for badges and inline chips, `{rounded.md}` for tiles, nodes, and command blocks, `{rounded.lg}` for briefing cards. `{rounded.full}` is reserved for modality chips — the three always-on mode indicators read as physical switches. Status shapes are part of the encoding vocabulary: gates are ⏸ inside a square badge, errors ⛔ inside a diagonal-cut badge, external waits ⧖ inside a circle, checks ✓, staleness ⧗ with a dashed border.

## Components

- **Annunciator strip** — full-width band stating the single current blocking condition in `{typography.annunciator}`. Nominal: `{components.annunciator-strip-nominal}` showing a quiet "IN FLIGHT — 08 · Irene Pass 2" in `ink-dim`. Paused-at-gate: amber fill (`{components.annunciator-strip}`). Paused-at-error / failed: red (`{components.annunciator-strip-warning}`). Provider batch: violet (`{components.annunciator-strip-wait}`). Always color + leading symbol + text.
- **Status badge** — the envelope status verbatim (`paused-at-gate`), uppercase `zone-title`, paired symbol on the left. Fill follows the cockpit rule: nominal statuses (`registered`, `in-flight`, `completed`) take the dim treatment (`{colors.status-nominal-dim}` fill or hairline outline, `ink-secondary`-range ink); attention statuses (`paused-at-gate`, `paused-at-error`, `waiting_for_provider_batch`, `failed`) take the full-brightness status hue with its paired ink. One per header; never truncated.
- **Modality chip** — pill (`{components.modality-chip}`) for BATCH, DETECTIVE, and the selected styleguide slug. Active chip: filled dot in `{colors.ink-primary}` (the BATCH chip's dot uses `{colors.status-wait}` — violet already means the provider-batch family) and border brightened to `{colors.ink-dim}`; inactive chips render dim with a hollow dot — presence is constant, activation is the signal. Chips never use green (green means pass, not "switched on") and never cyan (cyan means *here*).
- **Health tile** — `{components.health-tile}`: label (`zone-title`, dim), value (`numeral`), sub-line, and a mandatory staleness stamp ("14s ago") in `meta`. Threshold crossed: amber ring + ⚠. Feed dead: the whole tile takes the **stale veil** (`{components.stale-veil}` — dashed amber border, content dimmed to 60%, "STALE · last good 14:32:07" stamp).
- **Map node** — one row per step: status marker (shape+symbol), node ID in `mono`, label in `body`. Nominal-completed rows use `{components.map-node-nominal}` (dim green marker, dim ink). The active node is the brightest object on the page: `{components.map-node-active}` cyan fill. Gate nodes carry a square ⏸ marker. When the active node is a paused gate, **amber replaces cyan** — amber fill plus an offset amber outline glow; master caution outranks the active accent, and one node never wears two hues.
- **Gate briefing card** — `{components.gate-briefing-card}`: gate ID + focus, the decision being asked, evidence/artifacts under judgment inline (variant thumbnails at G2B, voice rows at G4A), drafted-proposal line with confidence, and the **command block**. Error briefings reuse the card with a red left border; batch briefings with violet.
- **Command block** — `{components.command-block}`: the exact copy-paste next action (`gate decide --trial-id … --decision-card-digest …`) in `mono`, cyan hairline border, one command per block, fully selectable text. No buttons — the border says "this is the thing you take."
- **Specialist chip** — `{components.specialist-chip}`: two-letter monogram (IR, GA, TX…) in `zone-title`, status ring + corner glyph (✓ idle-done, ▶ active, ⚠ degraded, ⏸ awaiting). Expands to a briefing card of that specialist's current state. [ASSUMPTION] Monogram chips are the team's iconography call — the operator may swap for pictographic icons at the UX-gate review.
- **State-trace well** — `{components.state-trace}`: scrolling mono feed of app-state changes and Marcus↔specialist traffic, newest last, read-only.
- **Pre-flight check row** — checklist line: shape marker (○ pending in `{colors.status-idle}` → ◐ running in `{colors.active}` → ✓ pass in `{colors.status-nominal}` / ✕ fail in `{colors.status-warning}`), check name, one-line result, duration. Heartbeat rows add the dependency name, latency, and a quota/credit reading with a confidence tag (`direct` / `proxy` / `unknown` — never a false green).
- **Notification toast** — `{components.notification-toast}`: top-right overlay card, event copy in `body`, timestamp in `meta`. Left border takes the hue of the event's meaning (amber for gate/stall/threshold, red for error, violet for batch-resumed). The toast mirrors the annunciator and never replaces it; it is the only overlay element on the page.

## Do's and Don'ts

| Do | Don't |
|---|---|
| Encode every status as color + shape + symbol | Rely on hue alone anywhere, ever |
| Keep nominal dim; reserve brightness for the active step and anomalies | Light the whole panel up when everything is fine |
| Stamp every tile and briefing with its age | Show a value without admitting when it was last true |
| Flip dead feeds to the explicit stale veil | Let the last-known value keep rendering as current truth |
| Render unrecognized states as literal "UNRECOGNIZED" in idle slate | Guess, coerce, or hide a state the schema doesn't know |
| One command per command block, exact and complete | Paraphrase a command or split it across lines the operator must reassemble |
| Use violet for external waits | Use amber/red for a healthy batch wait — nothing is wrong |
| Respect reduced-motion; limit motion to the freshness sweep | Blink, pulse, bounce, or animate attention |
