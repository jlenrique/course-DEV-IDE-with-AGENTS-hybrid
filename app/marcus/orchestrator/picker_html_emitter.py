"""Static gh-pages styleguide Picker — emitter + selection-code decoder.

Arc ``styleguide-picker-gh-pages-publish`` (green-light record 2026-07-03). This
is the RETURN-PATH twin of ``app.gates.section_07c.chooser_html_emitter``: it
renders a static, dependency-free page a client opens on the PUBLIC gh-pages site,
picks (i) which styleguide(s) and (ii) 1 OR 2 versions, and copies a SELECTION
CODE the page builds. The client pastes that code back to ``marcus_spoc``, which
decodes it here into ``{"A": slug, "B": slug?}`` and threads it into the EXISTING
``write_pick_to_directive`` / ``append_pick_event`` marcus-side (the static page
is inert — Q3 write-locus).

Single-sourcing (Q1/A8): the roster loader, card CSS, slug-membership +
lifecycle/visibility (A-M1) validation, and thumbnail-honesty helpers are IMPORTED
from ``styleguide_picker`` so the two transports (localhost POST + gh-pages
copy/paste) can NEVER drift. Only the selection-code GRAMMAR is frozen here, in
ONE place, referenced by BOTH the embedded JS encoder and the Python decoder.

Grammar (A2/A4/A5), frozen at :data:`SELECTION_CODE_GRAMMAR`::

    SGP-{run_tag}-A:{slug}[ B:{slug}]

space-separated slots; slot A REQUIRED (1 version); slot B OPTIONAL (2 versions).
Slots are keyed by LABEL (``A:`` / ``B:``), never by position (A4 — zero
mis-mapping). The run_tag is baked into the page at render time and the decoder
HARD-REJECTS a code carrying any other run_tag (A3 — a stale/foreign code can
never decode into this run).
"""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path
from typing import Any

from app.marcus.orchestrator.styleguide_picker import (
    _PAGE_CSS as _PICKER_PAGE_CSS,
)
from app.marcus.orchestrator.styleguide_picker import (
    _SIXTEEN_NINE_MIN_ASPECT,
    _THUMBNAIL_PROVENANCE_CHIP,
    GAMMA_STYLE_GUIDES_SSOT_PATH,
    PickerError,
    _assert_pickable_guide,
    _load_ssot_guides,
    _png_dimensions,
)

__all__ = [
    "PICKER_ENCODER_JS",
    "SELECTION_CODE_GRAMMAR",
    "build_selection_code",
    "decode_picker_selection_code",
    "render_picker_static_html",
]

# ------------------------------------------------------------------ grammar (ONE place)
# The FROZEN selection-code grammar. Both the JS encoder (`PICKER_ENCODER_JS`) and
# the Python decoder (`decode_picker_selection_code`) — and the parity-twin
# `build_selection_code` — reference this shape. Do NOT restate it elsewhere.
SELECTION_CODE_GRAMMAR = "SGP-{run_tag}-A:{slug}[ B:{slug}]"

_CODE_PREFIX = "SGP-"
_MAX_CODE_LEN = 256
# Whitelist for the WHOLE code (A5): letters/digits, the slot separator ':', slug
# '-'/'_', and whitespace (only leading/trailing + single inter-slot spaces survive).
_CODE_CHARSET_RE = re.compile(r"^[A-Za-z0-9:_\-\s]+$")
# run_tag charset (A3): baked-in tags are hex-ish; no ':' / '-' / whitespace.
_RUN_TAG_RE = re.compile(r"^[A-Za-z0-9_]+$")
# Per-slot regex (A5): strict lowercase slug, no coercion.
_SLOT_RE = re.compile(r"^([AB]):([a-z0-9\-]{1,64})$")


def _validate_run_tag(run_tag: str) -> str:
    """Producer-side ``run_tag`` guard (fail-loud) — the mirror of the decoder's A3.

    ``run_tag`` is baked into every emitted code AND into the publish path/receipt
    name. An unvalidated tag fails LATE and dangerously: a hyphen mis-splits the
    decoder's ``partition("-")`` (every client code then rejected), a ``/`` or
    ``..`` becomes path traversal in the publish subdir, and a ``</script>``
    payload is NOT neutralised by ``json.dumps`` when injected into the inline
    ``<script>``. Enforcing :data:`_RUN_TAG_RE` (``^[A-Za-z0-9_]+$``) at the TOP of
    every producer closes all three at the source. Raises :class:`PickerError`.
    """
    tag = str(run_tag)
    if not _RUN_TAG_RE.match(tag):
        raise PickerError(
            f"run_tag {run_tag!r} is malformed (allowed: letters, digits, '_'). A "
            f"hyphen, '/', '..', or markup here would corrupt the selection code, "
            f"the publish path, or the inline <script> — rejected at the producer"
        )
    return tag


def build_selection_code(run_tag: str, picks: dict[str, str]) -> str:
    """Python TWIN of the JS ``buildSelectionCode`` (parity/anti-drift only).

    Emits the canonical ``SGP-{run_tag}-A:{slug}[ B:{slug}]`` code for a
    ``{"A": slug, "B": slug?}`` map. Slot A is required. This twin exists so the
    golden fixture and the embedded JS encoder can be asserted byte-identical.
    """
    _validate_run_tag(run_tag)
    slot_a = str(picks.get("A") or "").strip()
    if not slot_a:
        raise PickerError("selection requires slot A (1 version minimum)")
    parts = [f"A:{slot_a}"]
    slot_b = str(picks.get("B") or "").strip()
    if slot_b:
        parts.append(f"B:{slot_b}")
    return f"{_CODE_PREFIX}{run_tag}-" + " ".join(parts)


def decode_picker_selection_code(
    code: str,
    *,
    expected_run_tag: str,
    ssot_path: str | Path | None = None,
) -> dict[str, str]:
    """Decode a pasted selection code into ``{"A": slug, "B": slug?}`` — FAIL-LOUD.

    Applies the full A5 reject matrix (prefix, charset, length cap BEFORE parsing,
    per-slot regex, slot-A-required, duplicate-label, strict case, embedded
    whitespace, empty), the A3 run_tag binding (``expected_run_tag`` REQUIRED;
    stale/foreign tag hard-rejected), the A4 label-keyed mapping (never
    positional), the B==A paste-error guard, and the A-M1 slug membership +
    lifecycle/visibility invariant (single-sourced via ``_assert_pickable_guide``).
    NEVER silently coerces; every rejection raises :class:`PickerError`.
    """
    if not isinstance(code, str):
        raise PickerError(f"selection code must be a string, got {type(code).__name__}")
    # A5: hard length cap BEFORE any parsing (bound the untrusted input up front).
    if len(code) > _MAX_CODE_LEN:
        raise PickerError(
            f"selection code is {len(code)} chars; the hard length cap is "
            f"{_MAX_CODE_LEN} (rejected before parsing)"
        )
    # empty / whitespace-only.
    if not code.strip():
        raise PickerError("selection code is empty / whitespace-only")
    trimmed = code.strip()  # trim ONLY leading/trailing whitespace.
    # A5 charset whitelist.
    if not _CODE_CHARSET_RE.match(trimmed):
        raise PickerError(
            "selection code carries an illegal character (allowed: letters, digits, "
            "':', '-', '_', single spaces)"
        )
    # A5 literal prefix (STRICT case — no lowercasing to force a match).
    if not trimmed.startswith(_CODE_PREFIX):
        raise PickerError(
            f"selection code must start with the literal {_CODE_PREFIX!r} prefix"
        )
    rest = trimmed[len(_CODE_PREFIX):]
    run_tag, sep, body = rest.partition("-")
    if not sep or not body:
        raise PickerError(
            "malformed selection code: expected 'SGP-<run_tag>-<slots>'"
        )
    # A3 run_tag charset (it is inside the untrusted string).
    if not _RUN_TAG_RE.match(run_tag):
        raise PickerError(
            f"selection code run-tag {run_tag!r} is malformed (allowed: letters, "
            f"digits, '_')"
        )
    # A3 run_tag binding: required arg, hard-reject a mismatch with a distinct msg.
    if not expected_run_tag:
        raise PickerError("expected_run_tag is required to decode a selection code")
    if run_tag != expected_run_tag:
        raise PickerError(
            f"stale/foreign selection code: code is for run {run_tag!r}, this run is "
            f"{expected_run_tag!r}"
        )
    # A5 per-slot parse — split on SINGLE spaces; an empty token means embedded /
    # doubled whitespace (never trimmed away) and is rejected.
    slots: dict[str, str] = {}
    for token in body.split(" "):
        match = _SLOT_RE.match(token)
        if not match:
            raise PickerError(
                f"malformed slot token {token!r}: each slot must be '<A|B>:<slug>' "
                f"(strict lowercase slug, single inter-slot spaces, no embedded "
                f"whitespace)"
            )
        label, slug = match.group(1), match.group(2)
        if label in slots:  # A5 duplicate slot label.
            raise PickerError(f"duplicate slot label {label!r} in selection code")
        slots[label] = slug
    # A5 slot A required.
    if "A" not in slots:
        raise PickerError("selection code has no slot A (version A is required)")
    # B==A: almost always a paste error; reject rather than dispatch a degenerate A/B.
    if "B" in slots and slots["B"] == slots["A"]:
        raise PickerError(
            "slot B is identical to slot A — likely a paste error; pick two distinct "
            "styles for two versions or one style for one version"
        )
    # A-M1 slug membership + lifecycle/visibility (single-sourced with the writer).
    ssot = Path(ssot_path) if ssot_path is not None else GAMMA_STYLE_GUIDES_SSOT_PATH
    guides = _load_ssot_guides(ssot)
    for label in sorted(slots):
        _assert_pickable_guide(slots[label], guides, ssot)
    # A4: keyed by LABEL, never by position.
    return {label: slots[label] for label in sorted(slots)}


# ---------------------------------------------------------------- JS encoder (A5 tooth)
# The PURE encoder — extracted as a top-level function (NOT buried in a click
# handler) so it is headless/node-testable and asserted byte-identical to the
# Python twin. Embedded verbatim in the emitted page AND exported for the parity
# test. Mirrors `build_selection_code` above (grammar single-sourced by shape).
PICKER_ENCODER_JS = """\
function buildSelectionCode(runTag, picks) {
  var parts = [];
  if (picks.A) { parts.push('A:' + picks.A); }
  if (picks.B) { parts.push('B:' + picks.B); }
  return 'SGP-' + runTag + '-' + parts.join(' ');
}
"""


# ------------------------------------------------------------------- extra page CSS
_EMITTER_EXTRA_CSS = """
.version-control { display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
  margin: 6px 0; }
.version-control fieldset { border: 2px solid #b9c3cd; border-radius: 8px;
  padding: 4px 12px; display: flex; gap: 14px; margin: 0; }
.version-control legend { font-weight: 700; padding: 0 6px; }
.version-control label { cursor: pointer; font-weight: 600; }
#version-note { font-weight: 700; color: #1d5228; }
.codebox { display: flex; flex-direction: column; gap: 6px; margin-top: 8px; }
#selection-code { width: 100%; min-height: 44px; font-family: monospace;
  font-size: 0.95rem; padding: 8px; border: 2px solid #b9c3cd; border-radius: 8px;
  resize: vertical; background: #fff; color: #1c2733; }
#copy-code { font-size: 1rem; padding: 8px 22px; cursor: pointer; align-self: start; }
#copy-code[aria-disabled="true"], #copy-code:disabled { cursor: not-allowed;
  opacity: 0.5; }
#copy-why { color: #b3541e; font-weight: 600; font-size: 0.85rem; }
#copy-status { color: #1d5228; font-weight: 700; font-size: 0.9rem; }
@media (max-width: 520px) {
  main.grid { grid-template-columns: 1fr; }
  #selection-code { font-size: 0.85rem; }
}
"""


def _static_thumbnail(entry: dict[str, Any], *, repo_root: Path | None) -> tuple[str, str | None]:
    """SAME-ORIGIN RELATIVE thumbnail html + optional 16:9 honesty chip (A6).

    Mirrors ``styleguide_picker._resolve_thumbnail`` (imports its PNG-validation
    and aspect-floor helpers) but references ``thumbnails/{slug}.png`` RELATIVELY
    — the publisher copies the curated PNG into the pack's ``thumbnails/`` dir. A
    missing/invalid ref degrades to the honest placeholder (never a 500, never a
    confidently-wrong image).
    """
    ref = entry.get("thumbnail_ref")
    slug = str(entry["name"])
    placeholder = '<div class="thumb placeholder">no live render</div>'
    if not ref:
        return (placeholder, None)
    if repo_root is None or not str(ref).lower().endswith(".png"):
        return (placeholder, '<span class="chip chip-provenance">thumbnail unavailable</span>')
    png = repo_root / str(ref)
    if not png.is_file():
        return (placeholder, '<span class="chip chip-provenance">thumbnail unavailable</span>')
    try:
        width, height = _png_dimensions(png)
    except PickerError:
        return (placeholder, '<span class="chip chip-provenance">thumbnail unavailable</span>')
    thumb = (
        f'<img class="thumb" src="thumbnails/{escape(slug, quote=True)}.png" '
        f'alt="{escape(entry["display_name"])} thumbnail">'
    )
    chip: str | None = None
    promised = str(entry.get("card_dimensions") or "").strip().lower()
    if promised == "16x9" and (width / height) < _SIXTEEN_NINE_MIN_ASPECT:
        chip = (
            f'<span class="chip chip-provenance">{escape(_THUMBNAIL_PROVENANCE_CHIP)}</span>'
        )
    return (thumb, chip)


def _render_static_card(entry: dict[str, Any], *, repo_root: Path | None) -> list[str]:
    """A picker card for the STATIC page: relative thumbnail + lifecycle chips (A6)."""
    thumb, chip = _static_thumbnail(entry, repo_root=repo_root)
    probe = bool(entry.get("probe"))
    lifecycle = str(entry.get("lifecycle") or "candidate")
    display_name = entry["display_name"]
    narrative = entry.get("narrative") or {}
    parts = [
        f'<article class="card" tabindex="0" role="button" aria-pressed="false" '
        f'aria-label="{escape(display_name)}" data-guide="{escape(entry["name"])}" '
        f'data-display="{escape(display_name)}" '
        f'data-lifecycle="{escape(lifecycle)}" data-probe="{1 if probe else 0}">',
        thumb,
        f"<h2>{escape(display_name)}</h2>",
    ]
    if chip:
        parts.append(chip)
    if probe:
        parts.append(
            '<span class="chip chip-probe">PROBE — scaffolding, not a production '
            "style</span>"
        )
    if lifecycle == "candidate":
        parts.append(
            '<span class="chip chip-candidate">CANDIDATE — trial style, not yet '
            "promoted</span>"
        )
    if lifecycle == "deprecated":
        parts.append(
            '<span class="chip chip-deprecated">DEPRECATED — retired style, '
            "not for production</span>"
        )
    parts.append(f'<p class="distinguishing">{escape(str(entry.get("distinguishing") or ""))}</p>')
    use_when = str(narrative.get("use_when") or "").strip()
    if use_when:
        parts.append(f'<p class="use-when"><strong>Use when:</strong> {escape(use_when)}</p>')
    parts.append("</article>")
    return parts


def _page_js(run_tag: str) -> str:
    """The page interaction script (A1 versions control + A2 copy robustness)."""
    run_tag_js = json.dumps(str(run_tag))
    return (
        PICKER_ENCODER_JS
        + """
(function () {
  var RUN_TAG = """
        + run_tag_js
        + """;
  var slots = { A: null, B: null };
  var versionCount = 1;
  var codeEl = document.getElementById('selection-code');
  var copyBtn = document.getElementById('copy-code');
  var whyEl = document.getElementById('copy-why');
  var statusEl = document.getElementById('copy-status');
  var noteEl = document.getElementById('version-note');
  var slotEls = { A: document.getElementById('slot-A'), B: document.getElementById('slot-B') };
  var slotBWrap = document.getElementById('slot-B-wrap');
  var radios = document.querySelectorAll('input[name="version-count"]');
  var displayByGuide = {};
  var cards = document.querySelectorAll('.card');
  for (var i = 0; i < cards.length; i++) {
    displayByGuide[cards[i].getAttribute('data-guide')] =
      cards[i].getAttribute('data-display') || cards[i].getAttribute('data-guide');
  }

  function currentPicks() {
    var p = { A: slots.A };
    if (versionCount === 2 && slots.B) { p.B = slots.B; }
    return p;
  }

  function syncRadios() {
    for (var i = 0; i < radios.length; i++) {
      radios[i].checked = (Number(radios[i].value) === versionCount);
    }
    slotBWrap.hidden = (versionCount !== 2);
    noteEl.textContent = versionCount === 2
      ? 'Two versions (an A/B pair)'
      : 'One version (a single deck)';
  }

  function render() {
    for (var v = 0; v < 2; v++) {
      var key = v === 0 ? 'A' : 'B';
      var guide = slots[key];
      var valEl = slotEls[key].querySelector('.slot-value');
      valEl.textContent = guide ? (displayByGuide[guide] || guide) : '(empty)';
      slotEls[key].classList.toggle('filled', !!guide);
    }
    for (var i = 0; i < cards.length; i++) {
      cards[i].classList.remove('slot-a', 'slot-b');
      cards[i].setAttribute('aria-pressed', 'false');
    }
    if (slots.A) {
      var ca = document.querySelector('.card[data-guide="' + CSS.escape(slots.A) + '"]');
      if (ca) { ca.classList.add('slot-a'); ca.setAttribute('aria-pressed', 'true'); }
    }
    if (versionCount === 2 && slots.B) {
      var cb = document.querySelector('.card[data-guide="' + CSS.escape(slots.B) + '"]');
      if (cb) { cb.classList.add('slot-b'); cb.setAttribute('aria-pressed', 'true'); }
    }
    // SOP-204: '2 versions' selected but only slot A filled emits a 1-version code
    // while the page says 'Two versions'. Block the copy + say exactly what to do.
    var incompleteAB = (versionCount === 2 && !slots.B);
    var canCopy = !!slots.A && !incompleteAB;
    codeEl.value = canCopy ? buildSelectionCode(RUN_TAG, currentPicks()) : '';
    copyBtn.disabled = !canCopy;
    copyBtn.setAttribute('aria-disabled', canCopy ? 'false' : 'true');
    if (!slots.A) {
      whyEl.textContent = 'Pick at least one style to enable copying.';
    } else if (incompleteAB) {
      whyEl.textContent = 'You chose 2 versions but only picked one style — pick a '
        + 'second style, or switch to 1 version.';
    } else {
      whyEl.textContent = '';
    }
  }

  function setVersion(n, fromCardPick) {
    if (n === 1 && slots.B) {
      if (!fromCardPick &&
          !window.confirm('Switch to one version? Your second style will be removed.')) {
        syncRadios();
        return;
      }
      slots.B = null;
    }
    versionCount = n;
    statusEl.textContent = '';
    syncRadios();
    render();
  }

  function selectCard(guide) {
    if (guide === slots.A) { slots.A = null; render(); return; }
    if (guide === slots.B) { slots.B = null; render(); return; }
    if (!slots.A) { slots.A = guide; }
    else if (versionCount === 2 && !slots.B) { slots.B = guide; }
    else if (versionCount === 1) { versionCount = 2; slots.B = guide; syncRadios(); }
    else { slots.B = guide; }
    statusEl.textContent = '';
    render();
  }

  for (var i = 0; i < cards.length; i++) {
    (function (card) {
      var guide = card.getAttribute('data-guide');
      card.addEventListener('click', function () { selectCard(guide); });
      card.addEventListener('keydown', function (ev) {
        if (ev.target !== card) { return; }
        if (ev.key === 'Enter' || ev.key === ' ' || ev.key === 'Spacebar') {
          ev.preventDefault(); selectCard(guide);
        }
      });
    })(cards[i]);
  }
  for (var i = 0; i < radios.length; i++) {
    radios[i].addEventListener('change', function () { setVersion(Number(this.value), false); });
  }

  copyBtn.addEventListener('click', function () {
    if (!slots.A) { return; }
    var code = codeEl.value;
    function manual() {
      codeEl.focus(); codeEl.select();
      statusEl.textContent = 'The code is selected above — press Ctrl/Cmd-C to copy, '
        + 'then paste it into your chat with Marcus.';
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(code).then(function () {
        statusEl.textContent = '✓ Copied! Now paste this into your chat with Marcus.';
      }).catch(function () { manual(); });
    } else { manual(); }
  });

  syncRadios();
  render();
})();
"""
    )


def render_picker_static_html(
    roster: list[dict[str, Any]],
    *,
    run_tag: str,
    repo_root: Path | None = None,
) -> str:
    """Render the STATIC, dependency-free gh-pages picker page.

    A card grid + slot bar (reusing the localhost picker's CSS), an explicit
    ``role="radiogroup"`` "1 version / 2 versions" control (A1), an always-visible
    readonly selection-code textarea + a copy button that is inert-disabled until
    slot A is filled (A2), and lifecycle/probe honesty chips (A6). The run_tag is
    baked in (A3) so the embedded encoder can only emit THAT tag. Thumbnails are
    same-origin RELATIVE refs the publisher fills in.
    """
    _validate_run_tag(run_tag)
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>Gamma Styleguide Picker — {escape(str(run_tag))}</title>",
        f"<style>{_PICKER_PAGE_CSS}{_EMITTER_EXTRA_CSS}</style>",
        "</head>",
        "<body>",
        "<header>",
        "<h1>Gamma Styleguide Picker</h1>",
        '<p class="instructions">Choose a style below, then how many versions you '
        "want. Copy the selection code and paste it back to Marcus.</p>",
        # A1: explicit versions control (radiogroup), count stated IN WORDS.
        '<div class="version-control">',
        '<fieldset role="radiogroup" aria-label="How many versions">',
        "<legend>Versions</legend>",
        '<label><input type="radio" name="version-count" value="1" checked> '
        "1 version</label>",
        '<label><input type="radio" name="version-count" value="2"> 2 versions</label>',
        "</fieldset>",
        '<span id="version-note" role="status" aria-live="polite">One version '
        "(a single deck)</span>",
        "</div>",
        # slot bar (A/B). Slot B is hidden until 2 versions.
        '<div class="slots" role="status" aria-live="polite">',
        '<div class="slot" id="slot-A" data-variant="A">'
        '<span class="slot-label">Version A</span> '
        '<span class="slot-value">(empty)</span></div>',
        '<span id="slot-B-wrap" hidden>'
        '<div class="slot" id="slot-B" data-variant="B">'
        '<span class="slot-label">Version B</span> '
        '<span class="slot-value">(empty)</span></div></span>',
        "</div>",
        # A2: always-visible selectable code + copy button + why/status.
        '<div class="codebox">',
        '<label for="selection-code"><strong>Your selection code</strong></label>',
        '<textarea id="selection-code" readonly aria-live="polite" '
        'placeholder="Pick a style to build your code"></textarea>',
        '<button type="button" id="copy-code" aria-disabled="true" disabled>'
        "Copy my selection code</button>",
        '<span id="copy-why" role="status" aria-live="polite">Pick at least one '
        "style to enable copying.</span>",
        '<span id="copy-status" role="status" aria-live="polite"></span>',
        "</div>",
        "</header>",
        '<main class="grid">',
    ]
    for entry in roster:
        parts.extend(_render_static_card(entry, repo_root=repo_root))
    parts.extend(
        [
            "</main>",
            f"<script>{_page_js(run_tag)}</script>",
            "</body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(parts)
