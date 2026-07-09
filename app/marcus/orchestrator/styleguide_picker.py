"""Pre-run HTML style-picker at CD-entry (Leg-D, Fork A — green-light 6/6 2026-07-02).

The operator-facing face on the directive's EXISTING binding surface: a local
card-grid page rendered from the CD-owned styleguide SSOT and SERVED BY the
ephemeral-port localhost ``http.server`` itself (the browser opens
``http://127.0.0.1:<port>/`` — same-origin end-to-end, so the receipt fetch is
never CORS-blocked; a disk copy of the page is still written for
evidence/debug). The pick is captured by that server (one valid POST to the
relative ``/pick`` action, server exits) and written into the run directive's
``gamma_settings[]`` (existing A/B semantics VERBATIM, J-3) plus a
``styleguide_picker_provenance`` audit block — the run's own input artifact
carries the audit trail (Winston). Zero new runtime seams: the consumers are
the REAL ``_gamma_settings_from_directive`` /
``_min_cluster_floor_from_directive`` reads that gary + the Leg-C floor already
exercise in production.

Single-variant picks are legitimate (post ``retire-default-variant-pair``): an
A-only OR B-only directive dispatches EXACTLY ONE deck downstream; both the web
page and the CLI-numbered fallback support skipping either slot (at least one
must be filled).

Store mutations (the directive read-modify-write and the sidecar append) take
an ADVISORY same-host file lock (``msvcrt.locking`` / ``fcntl.flock`` on a
``<store>.lock`` file adjacent to the store). The guarantee is honest-but-
bounded: cooperating writers on the SAME host serialize; it is not a
cross-host or non-cooperating-process guarantee.

Boundary guardrails (binding amendments):

- Stdlib-only (+ pyyaml, a shipped dep). Reads the SSOT yaml DIRECTLY — display
  + selection only; NO ``app.specialists.gary`` import (gary keeps resolution
  semantics; mirrors the ``production_runner`` direct-read precedent).
- D-1/J-1: ``last_used`` is derived from the append-only sidecar
  ``state/config/gamma-styleguide-picks.jsonl`` joined at render time; the
  SSOT's ``presentation.last_used`` stays null FOREVER, and no CD/gary module
  ever imports this file (the Leg-B2 two-store contract).
- D-2: thumbnails are curated provenance — real evidence PNGs copied into
  ``state/config/gamma-styleguide-thumbnails/`` and referenced via
  ``presentation.thumbnail_ref`` under the validator write-gate; a dangling ref
  FAILS loud (AC-6) and a null ref renders "no live render" (S-3).
- D-3: ``presentation.visibility: probe`` guides are hidden by default;
  ``include_probes`` opts in and renders the S-1 warning chip.
- A-1: unknown styleguide name / malformed sidecar line -> ``PickerError``,
  never a silent skip.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import struct
import tempfile
import webbrowser
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, urlparse

import yaml

PICKER_VERSION = "1.0"
REPO_ROOT = Path(__file__).resolve().parents[3]
GAMMA_STYLE_GUIDES_SSOT_PATH = REPO_ROOT / "state" / "config" / "gamma-style-guides.yaml"
GAMMA_STYLEGUIDE_PICKS_PATH = REPO_ROOT / "state" / "config" / "gamma-styleguide-picks.jsonl"

_VARIANT_IDS = ("A", "B")
_NARRATIVE_KEYS = ("summary", "feels_like", "use_when", "avoid_when")
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
# R2: a guide promising 16:9 (aspect 1.777) whose curated render is squarer than
# this floor gets the honesty chip — the render predates the guide's frame.
_SIXTEEN_NINE_MIN_ASPECT = 1.4
_THUMBNAIL_PROVENANCE_CHIP = (
    "render predates this guide's 16:9 frame — representative of palette/line-art, "
    "not layout"
)
# R4: cap the POST body read; a local pick form is tiny, anything bigger is bogus.
MAX_POST_BODY_BYTES = 64 * 1024


class PickerError(RuntimeError):
    """Fail-loud picker error (A-1): unknown guide, malformed store, bad input."""


def _png_dimensions(path: Path) -> tuple[int, int]:
    """Width/height straight from the PNG IHDR chunk (stdlib-only, R2/R10).

    Validates the 8-byte PNG magic AND that the first chunk is IHDR; anything
    else is a LOUD error — a mislabeled file must never render as a thumbnail.
    """
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != _PNG_MAGIC or header[12:16] != b"IHDR":
        raise PickerError(
            f"thumbnail {path} is not a real PNG (bad magic/IHDR header)"
        )
    width, height = struct.unpack(">II", header[16:24])
    if not width or not height:
        raise PickerError(f"thumbnail {path} has degenerate IHDR dimensions {width}x{height}")
    return (width, height)


def _atomic_write_text(path: Path, text: str) -> None:
    """Crash-atomic text write (R-MAJOR-1): temp sibling + fsync + os.replace.

    Writes to a temp file in the SAME directory as ``path`` (so ``os.replace``
    is atomic on both NTFS and POSIX), flushes and ``os.fsync`` the descriptor,
    then atomically renames the temp file over the destination. A crash mid-write
    leaves either the previous file fully intact or the fully-written new file on
    disk — never a truncated directive. The bytes are written verbatim (utf-8,
    ``\\n`` preserved), matching the prior ``write_text(..., newline="\\n")``.
    """
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=path.name + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(text.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
        raise


@contextlib.contextmanager
def _advisory_lock(store_path: Path) -> Iterator[None]:
    """Advisory same-host lock around a store mutation (R8).

    Locks ``<store>.lock`` adjacent to the store via ``msvcrt.locking``
    (Windows) / ``fcntl.flock`` (POSIX). HONEST GUARANTEE: cooperating writers
    on the SAME host serialize; this is not a cross-host or
    non-cooperating-process guarantee. The lock file is left on disk (deleting
    it would be racy).
    """
    lock_path = store_path.parent / (store_path.name + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+b")
    try:
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            if os.name == "nt":
                import msvcrt

                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()


# ------------------------------------------------------------------ roster (AC-1)
def read_pick_events(events_path: Path) -> list[dict[str, Any]]:
    """Read the append-only pick-event ledger. A malformed line is a LOUD error.

    Public reader (S2 P18): external consumers (e.g. the marcus_spoc ceremony's
    last-used-per-course lookup) read the sidecar through this name; the
    ``_read_pick_events`` alias is kept for back-compat.
    """
    if not events_path.exists():
        return []
    events: list[dict[str, Any]] = []
    for lineno, line in enumerate(
        events_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise PickerError(
                f"malformed pick-event sidecar line {lineno} in {events_path}: {exc}"
            ) from exc
        if not isinstance(event, dict):
            raise PickerError(
                f"malformed pick-event sidecar line {lineno} in {events_path}: "
                f"expected an object, got {type(event).__name__}"
            )
        events.append(event)
    return events


# Back-compat private alias (pre-P18 name); prefer `read_pick_events`.
_read_pick_events = read_pick_events


def _last_used_by_guide(events_path: Path) -> dict[str, str]:
    latest: dict[str, str] = {}
    for event in read_pick_events(events_path):
        name = str(event.get("guide_name") or "").strip()
        picked_at = str(event.get("picked_at") or "").strip()
        if not name or not picked_at:
            continue
        if name not in latest or picked_at > latest[name]:
            latest[name] = picked_at
    return latest


def _assert_pickable_guide(
    guide_name: str, guides: dict[str, Any], ssot: Path
) -> dict[str, Any]:
    """A-M1 single-source guard: a guide must be in the SSOT AND production-pickable.

    Membership + lifecycle/visibility invariant enforced in ONE place so the
    directive writer AND the gh-pages selection-code decoder agree byte-for-byte:
    a ``lifecycle: deprecated`` (retired) or ``visibility: probe`` (scaffolding)
    guide can NEVER be bound into a production run. Returns the SSOT record.
    """
    if guide_name not in guides:
        raise PickerError(
            f"picked styleguide {guide_name!r} is not in the SSOT {ssot} "
            f"(known: {sorted(guides)})"
        )
    record = guides[guide_name]
    presentation = record.get("presentation") or {} if isinstance(record, dict) else {}
    lifecycle = (
        str(record.get("lifecycle") or "candidate").strip().lower()
        if isinstance(record, dict)
        else "candidate"
    )
    visibility = str(presentation.get("visibility") or "").strip().lower()
    if lifecycle == "deprecated":
        raise PickerError(
            f"picked styleguide {guide_name!r} is deprecated (retired) and cannot "
            f"be bound into a production directive (A-M1 lifecycle invariant)"
        )
    if visibility == "probe":
        raise PickerError(
            f"picked styleguide {guide_name!r} is a probe (scaffolding) and cannot "
            f"be bound into a production directive (A-M1 visibility invariant)"
        )
    return record


def assert_pickable_guide(
    guide_name: str, *, ssot_path: str | Path | None = None
) -> dict[str, Any]:
    """Public single-source A-M1 guard used by the gh-pages decoder (Q1 anti-drift).

    Loads the SSOT and applies the same membership + lifecycle/visibility rejection
    that :func:`write_pick_to_directive` applies at the mutation point, so a slug
    decoded from a pasted selection code is validated by the identical rule.
    """
    ssot = Path(ssot_path) if ssot_path is not None else GAMMA_STYLE_GUIDES_SSOT_PATH
    guides = _load_ssot_guides(ssot)
    return _assert_pickable_guide(str(guide_name).strip(), guides, ssot)


def _load_ssot_guides(ssot_path: Path) -> dict[str, Any]:
    if not ssot_path.is_file():
        raise PickerError(f"styleguide SSOT not found at {ssot_path}")
    try:
        payload = yaml.safe_load(ssot_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise PickerError(f"failed to parse styleguide SSOT {ssot_path}: {exc}") from exc
    guides = payload.get("style_guides") if isinstance(payload, dict) else None
    if not isinstance(guides, dict) or not guides:
        raise PickerError(f"no style_guides mapping in {ssot_path}")
    return guides


def load_picker_roster(
    *,
    include_probes: bool = False,
    include_deprecated: bool = False,
    ssot_path: str | Path | None = None,
    events_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Load the picker roster from the REAL SSOT + sidecar-joined ``last_used``.

    Probe-marked guides (``presentation.visibility: probe``, D-3) are excluded
    unless ``include_probes`` — scaffolding must not masquerade as an
    intentional style. ``lifecycle: deprecated`` guides are RETIRED and excluded
    from the production roster unless ``include_deprecated`` (audit opt-in) — a
    deprecated style must never be silently pickable for a production run.
    ``last_used`` is joined from the append-only sidecar at render time (D-1);
    the SSOT field stays null forever.
    """
    ssot = Path(ssot_path) if ssot_path is not None else GAMMA_STYLE_GUIDES_SSOT_PATH
    events = Path(events_path) if events_path is not None else GAMMA_STYLEGUIDE_PICKS_PATH
    guides = _load_ssot_guides(ssot)
    last_used = _last_used_by_guide(events)
    roster: list[dict[str, Any]] = []
    for name in sorted(guides):
        record = guides[name]
        if not isinstance(record, dict):
            raise PickerError(f"styleguide record {name!r} must be a mapping")
        presentation = record.get("presentation") or {}
        probe = str(presentation.get("visibility") or "").strip().lower() == "probe"
        if probe and not include_probes:
            continue
        # Session-07 A1: lifecycle is schema; absence defaults to candidate (safe
        # state) so an unmarked record can never masquerade as permanent.
        lifecycle = str(record.get("lifecycle") or "candidate").strip().lower()
        # A retired (`deprecated`) style is hidden from the production roster;
        # `include_deprecated` opts in for audit.
        if lifecycle == "deprecated" and not include_deprecated:
            continue
        narrative = presentation.get("narrative") or {}
        page_settings = record.get("page_settings") or {}
        card_options = (
            page_settings.get("card_options") or {} if isinstance(page_settings, dict) else {}
        )
        roster.append(
            {
                "name": name,
                "display_name": str(presentation.get("display_name") or name).strip(),
                "distinguishing": str(presentation.get("distinguishing") or "").strip(),
                "narrative": {
                    key: str(narrative.get(key) or "").strip() for key in _NARRATIVE_KEYS
                },
                "production_mode": str(record.get("production_mode") or "").strip().lower(),
                "probe": probe,
                "lifecycle": lifecycle,
                "card_dimensions": (
                    str(card_options.get("dimensions") or "").strip()
                    if isinstance(card_options, dict)
                    else ""
                ),
                "thumbnail_ref": presentation.get("thumbnail_ref"),
                "example_url": presentation.get("example_url"),
                "last_used": last_used.get(name),
            }
        )
    return roster


# ------------------------------------------------------------- HTML render (Sally)
_PAGE_CSS = """
body { font-family: system-ui, sans-serif; margin: 0; background: #f5f6f8; color: #1c2733; }
header { position: sticky; top: 0; background: #fff; border-bottom: 2px solid #d6dce3;
  padding: 12px 20px; z-index: 5; }
h1 { margin: 0 0 8px; font-size: 1.2rem; }
.slots { display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
.slot { border: 2px solid #b9c3cd; border-radius: 8px; padding: 6px 12px; background: #eef2f5;
  display: flex; gap: 8px; align-items: center; min-width: 260px; }
.slot.filled { border-color: #2b7a3d; background: #e8f5ec; }
.slot.changed { animation: flash 0.9s ease-out; }
@keyframes flash { 0% { background: #fff3bf; } 100% { background: inherit; } }
.slot-label { font-weight: 700; }
.slot-value { font-family: monospace; }
.slot button { font-size: 0.75rem; cursor: pointer; }
#confirm { font-size: 1rem; padding: 8px 22px; margin-left: 10px; cursor: pointer; }
#confirm:disabled { cursor: not-allowed; opacity: 0.5; }
.receipt { margin-top: 10px; border: 2px solid #2b7a3d; background: #e8f5ec; color: #1d5228;
  border-radius: 8px; padding: 10px 14px; font-family: monospace; white-space: pre-wrap; }
main.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 18px; padding: 20px; }
.card { background: #fff; border: 1px solid #d6dce3; border-radius: 10px; padding: 12px;
  cursor: pointer; position: relative; }
.card:hover { border-color: #4a90d9; }
/* U-1: a clear keyboard focus ring so tab-navigation is visible. */
.card:focus-visible { outline: 3px solid #1a5fb4; outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(26,95,180,0.25); }
.card.armed { outline: 3px solid #d9822b; }
/* U-2: persistent selected-state on the grid when a card fills slot A / B —
   an outline plus a corner badge, distinct from .card.armed (probe arming). */
.card.slot-a { outline: 3px solid #2b7a3d; outline-offset: 2px; }
.card.slot-b { outline: 3px solid #2b5f9e; outline-offset: 2px; }
.card.slot-a::after, .card.slot-b::after { position: absolute; top: 8px; left: 8px;
  width: 26px; height: 26px; border-radius: 50%; color: #fff; font-weight: 800;
  font-size: 0.9rem; display: flex; align-items: center; justify-content: center; }
.card.slot-a::after { content: "A"; background: #2b7a3d; }
.card.slot-b::after { content: "B"; background: #2b5f9e; }
.card img.thumb { width: 100%; height: 190px; object-fit: cover; border-radius: 6px;
  background: #eef2f5; display: block; }
.thumb.placeholder { width: 100%; height: 190px; border-radius: 6px; background:
  repeating-linear-gradient(45deg, #eef2f5, #eef2f5 12px, #e2e8ee 12px, #e2e8ee 24px);
  display: flex; align-items: center; justify-content: center; color: #66727f;
  font-weight: 600; }
.card h2 { font-size: 1.02rem; margin: 10px 0 4px; }
.distinguishing { font-weight: 600; font-size: 0.9rem; margin: 4px 0 8px; }
.chip { font-size: 0.72rem; border-radius: 10px; padding: 2px 8px; display: inline-block; }
.chip-last-used { position: absolute; top: 16px; right: 16px; background: #1c2733;
  color: #eef2f5; }
.chip-probe { background: #b3541e; color: #fff; font-weight: 700; margin-bottom: 6px; }
.chip-candidate { background: #6c4ba0; color: #fff; font-weight: 700; margin-bottom: 6px; }
.chip-deprecated { background: #6b7280; color: #fff; font-weight: 700; margin-bottom: 6px;
  text-decoration: line-through; }
.chip-provenance { background: #6f5614; color: #fff; display: inline-block;
  margin: 6px 0 0; }
.use-when, .avoid-when { font-size: 0.82rem; margin: 3px 0; color: #33414f; }
.example-link { display: inline-block; margin: 6px 0 2px; font-size: 0.82rem;
  color: #1a5fb4; text-decoration: underline; font-weight: 600; }
.instructions { margin: 0 0 8px; font-size: 0.85rem; color: #33414f; }
.pick-hint { color: #b3541e; font-weight: 700; font-size: 0.85rem; margin-left: 8px; }
details { margin-top: 6px; font-size: 0.85rem; }
details summary { cursor: pointer; color: #4a6076; }
"""

_PAGE_JS = """
const slots = { A: null, B: null };
const slotEls = { A: document.getElementById('slot-A'), B: document.getElementById('slot-B') };
const fields = { A: document.getElementById('field-slot-A'),
                 B: document.getElementById('field-slot-B') };
const confirmBtn = document.getElementById('confirm');
const hintEl = document.getElementById('pick-hint');
/* U-3: the slot bar shows the human display name; the hidden field keeps the slug. */
const displayByGuide = {};
for (const card of document.querySelectorAll('.card')) {
  displayByGuide[card.dataset.guide] = card.dataset.display || card.dataset.guide;
}
function flash(v) {  /* S-2: highlight-on-change, never a silent reorder */
  slotEls[v].classList.remove('changed'); void slotEls[v].offsetWidth;
  slotEls[v].classList.add('changed');
}
function showHint(msg) {  /* U-5: no silent dead-click; announce + auto-clear. */
  if (!hintEl) return;
  hintEl.textContent = msg;
  clearTimeout(hintEl._t);
  hintEl._t = setTimeout(() => { hintEl.textContent = ''; }, 2600);
}
function refresh() {
  for (const v of ['A', 'B']) {
    const guide = slots[v];
    slotEls[v].querySelector('.slot-value').textContent =
      guide ? (displayByGuide[guide] || guide) : '(empty)';
    slotEls[v].classList.toggle('filled', !!guide);
    fields[v].value = guide || '';
  }
  /* U-2: persistent selected-state on the grid (distinct from .armed). */
  for (const card of document.querySelectorAll('.card')) {
    card.classList.remove('slot-a', 'slot-b');
    card.setAttribute('aria-pressed', 'false');
  }
  for (const v of ['A', 'B']) {
    if (!slots[v]) continue;
    const card = document.querySelector('.card[data-guide="' + CSS.escape(slots[v]) + '"]');
    if (card) {
      card.classList.add(v === 'A' ? 'slot-a' : 'slot-b');
      card.setAttribute('aria-pressed', 'true');
    }
  }
  confirmBtn.disabled = !(slots.A || slots.B);
}
function selectCard(card, ev) {
  if (ev && (ev.target.closest('details') || ev.target.closest('a'))) return;
  const guide = card.dataset.guide;
  if (card.dataset.probe === '1' && !card.classList.contains('armed')) {
    card.classList.add('armed');  /* S-1: probes need an explicit second click */
    return;
  }
  if (!slots.A) { slots.A = guide; flash('A'); }
  else if (!slots.B) { slots.B = guide; flash('B'); }
  else {  /* U-5: both slots full — no silent no-op; hint + flash. */
    flash('A'); flash('B');
    showHint('Both slots full — clear or swap a slot first');
    return;
  }
  refresh();
}
for (const card of document.querySelectorAll('.card')) {
  card.addEventListener('click', (ev) => selectCard(card, ev));
  /* U-1: keyboard operability — Enter/Space activate like a click. Only when the
     card itself is focused: Enter on a nested link/summary must act natively. */
  card.addEventListener('keydown', (ev) => {
    if (ev.target !== card) return;
    if (ev.key === 'Enter' || ev.key === ' ' || ev.key === 'Spacebar') {
      ev.preventDefault();
      selectCard(card, ev);
    }
  });
}
/* The live-example anchor must open the deck WITHOUT filling a slot. */
for (const link of document.querySelectorAll('a.example-link')) {
  link.addEventListener('click', (ev) => ev.stopPropagation());
}
for (const btn of document.querySelectorAll('.slot-clear')) {
  btn.addEventListener('click', () => {
    slots[btn.dataset.variant] = null; flash(btn.dataset.variant); refresh();
  });
}
for (const btn of document.querySelectorAll('.slot-swap')) {
  btn.addEventListener('click', () => {
    [slots.A, slots.B] = [slots.B, slots.A]; flash('A'); flash('B'); refresh();
  });
}
document.getElementById('pick-form').addEventListener('submit', (ev) => {
  ev.preventDefault();
  const form = ev.target;
  fetch(form.action, { method: 'POST', body: new URLSearchParams(new FormData(form)) })
    .then((r) => { if (!r.ok) throw new Error('pick rejected: HTTP ' + r.status);
                   return r.json(); })
    .then((receipt) => {
      const panel = document.getElementById('receipt');
      panel.hidden = false;
      panel.textContent = 'PICK RECORDED\\n'
        + 'directive: ' + receipt.directive_path + '\\n'
        + 'picks: ' + JSON.stringify(receipt.picks) + '\\n'
        + 'picked_at: ' + receipt.picked_at;
      confirmBtn.replaceWith(panel);  /* the receipt panel replaces the button */
    })
    .catch((err) => { alert(err.message); });
});
refresh();
"""


def _thumbnail_url_path(guide_name: str) -> str:
    """Same-origin server path for a guide's thumbnail (served by do_GET, R1)."""
    return f"/thumbnails/{quote(str(guide_name), safe='')}.png"


def thumbnail_routes(
    roster: list[dict[str, Any]], *, repo_root: Path | None = None
) -> dict[str, Path]:
    """Map same-origin thumbnail URL paths -> on-disk PNGs for the pick server."""
    root = repo_root if repo_root is not None else REPO_ROOT
    return {
        _thumbnail_url_path(entry["name"]): (root / str(entry["thumbnail_ref"])).resolve()
        for entry in roster
        if entry.get("thumbnail_ref")
    }


_PLACEHOLDER_THUMB = '<div class="thumb placeholder">no live render</div>'
_THUMB_UNAVAILABLE_CHIP = (
    '<span class="chip chip-provenance">thumbnail unavailable</span>'
)


def _resolve_thumbnail(entry: dict[str, Any], *, repo_root: Path) -> tuple[str, str | None]:
    """Resolve a curated thumbnail_ref to ``(<img html>, provenance_chip|None)``.

    Fail-loud helper: a wrong extension, a dangling ref, or a non-PNG file raises
    ``PickerError`` (kept loud so the write-gate / direct callers still catch a
    bad SSOT row). ``_render_card`` catches at the call site (A-M2) so one broken
    row degrades to the placeholder instead of 500-ing the whole picker.
    """
    ref = entry.get("thumbnail_ref")
    if not str(ref).lower().endswith(".png"):
        raise PickerError(
            f"styleguide {entry['name']!r} thumbnail_ref {ref!r} must be a .png "
            f"(D-2 curated-render contract; R10 extension check)"
        )
    png = repo_root / str(ref)
    if not png.is_file():
        raise PickerError(
            f"styleguide {entry['name']!r} has a dangling thumbnail_ref {ref!r} "
            f"(AC-6: every rendered thumbnail must resolve to a real on-disk PNG)"
        )
    width, height = _png_dimensions(png)  # R10 magic check; R2 aspect source
    thumb = (
        f'<img class="thumb" src="{escape(_thumbnail_url_path(entry["name"]))}" '
        f'alt="{escape(entry["display_name"])} thumbnail">'
    )
    provenance_chip: str | None = None
    # R2 honesty chip (data-driven, Auditor#1): the guide promises 16:9 but
    # the curated render is squarer — say so on the card, never imply layout.
    promised = str(entry.get("card_dimensions") or "").strip().lower()
    if promised == "16x9" and (width / height) < _SIXTEEN_NINE_MIN_ASPECT:
        provenance_chip = (
            f'<span class="chip chip-provenance">{escape(_THUMBNAIL_PROVENANCE_CHIP)}'
            "</span>"
        )
    return (thumb, provenance_chip)


def _render_card(entry: dict[str, Any], *, repo_root: Path) -> list[str]:
    ref = entry.get("thumbnail_ref")
    provenance_chip: str | None = None
    thumb_warning: str | None = None
    if ref:
        try:
            thumb, provenance_chip = _resolve_thumbnail(entry, repo_root=repo_root)
        except PickerError:
            # A-M2 (Winston, converges w/ Sally #6): a broken thumbnail row must
            # never 500 the whole page. Degrade to the honest placeholder PLUS a
            # visible warning chip so one bad SSOT row can't take down the picker.
            thumb = _PLACEHOLDER_THUMB
            thumb_warning = _THUMB_UNAVAILABLE_CHIP
    else:
        # S-3: explicit placeholder, never a confidently wrong image.
        thumb = _PLACEHOLDER_THUMB
    probe = bool(entry.get("probe"))
    last_used = entry.get("last_used") or "never"
    narrative = entry.get("narrative") or {}
    display_name = entry["display_name"]
    parts = [
        # U-1 (Sally a11y): keyboard-operable card — focusable, button-role,
        # aria-labelled; a keydown (Enter/Space) mirrors the click (see _PAGE_JS).
        # data-display (U-3) carries the human name for the slot bar; the hidden
        # form field keeps the slug for the POST.
        f'<article class="card" tabindex="0" role="button" aria-pressed="false" '
        f'aria-label="{escape(display_name)}" data-guide="{escape(entry["name"])}" '
        f'data-display="{escape(display_name)}" '
        f'data-probe="{1 if probe else 0}">',
        thumb,
        f'<span class="chip chip-last-used">last used: {escape(str(last_used))}</span>',
        f"<h2>{escape(display_name)}</h2>",
    ]
    if provenance_chip:
        parts.append(provenance_chip)
    if thumb_warning:
        parts.append(thumb_warning)
    if probe:
        parts.append(
            '<span class="chip chip-probe">PROBE — scaffolding, not a production '
            "style (click twice to select)</span>"
        )
    # Session-07 A1 (Winston + Dan): candidates are visibly badged — a reviewer
    # always knows which lifecycle tier they are looking at.
    if str(entry.get("lifecycle") or "candidate") == "candidate":
        parts.append(
            '<span class="chip chip-candidate">CANDIDATE — A-corpus only, '
            "not yet promoted (B-corpus stress test pending)</span>"
        )
    # A deprecated style only appears under include_deprecated (audit); badge it
    # unmistakably so it can never be mistaken for a production-eligible style.
    if str(entry.get("lifecycle") or "candidate") == "deprecated":
        parts.append(
            '<span class="chip chip-deprecated">DEPRECATED — retired style, '
            "not for production</span>"
        )
    # Operator request: a live exemplar deck reachable from each card, opened in
    # a NEW TAB. NOT the whole thumbnail (that collides with slot-selection): a
    # small anchor under the title whose click stopPropagation's in the JS so it
    # never fills a slot. A null/absent example_url renders NO link (no dead link).
    example_url = entry.get("example_url")
    if example_url:
        parts.append(
            f'<a class="example-link" href="{escape(str(example_url))}" '
            f'target="_blank" rel="noopener" '
            f'aria-label="Open the live example deck for {escape(display_name)} '
            f'(opens in a new tab)">View live example ↗</a>'
        )
    parts.append(f'<p class="distinguishing">{escape(entry["distinguishing"])}</p>')
    # U-4 (Sally): surface the decision-useful pros/cons on the card FACE, below
    # the distinguishing line, so they're visible without expanding.
    use_when = str(narrative.get("use_when") or "").strip()
    avoid_when = str(narrative.get("avoid_when") or "").strip()
    if use_when:
        parts.append(
            f'<p class="use-when"><strong>Use when:</strong> {escape(use_when)}</p>'
        )
    if avoid_when:
        parts.append(
            f'<p class="avoid-when"><strong>Avoid when:</strong> {escape(avoid_when)}</p>'
        )
    # The fuller narrative (feels_like / summary) stays behind the toggle; the
    # summary is relabelled from the opaque "narrative" to say what's inside.
    parts.append("<details><summary>More about this style</summary>")
    for key in ("summary", "feels_like"):
        value = str(narrative.get(key) or "").strip()
        if value:
            label = key.replace("_", " ")
            parts.append(f"<p><strong>{escape(label)}:</strong> {escape(value)}</p>")
    parts.append("</details>")
    parts.append("</article>")
    return parts


def render_picker_html(
    roster: list[dict[str, Any]],
    *,
    post_url: str,
    repo_root: Path | None = None,
) -> str:
    """Render the static single-page picker (Sally MVP: cards + slot bar + receipt)."""
    root = repo_root if repo_root is not None else REPO_ROOT
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        "<title>Gamma Styleguide Picker</title>",
        f"<style>{_PAGE_CSS}</style>",
        "</head>",
        "<body>",
        "<header>",
        "<h1>Gamma Styleguide Picker — pre-run pick (Fork A)</h1>",
        # U-5 (Sally): a one-line instruction so the pick flow is self-evident.
        '<p class="instructions">Click a style to fill Style A, then another for '
        "Style B — one slot is a valid pick.</p>",
        # U-1 (Sally a11y): the slot bar announces fills to assistive tech.
        '<div class="slots" role="status" aria-live="polite">',
    ]
    for variant in _VARIANT_IDS:
        parts.extend(
            [
                f'<div class="slot" id="slot-{variant}" data-variant="{variant}">',
                f'<span class="slot-label">Style {variant}</span>',
                '<span class="slot-value">(empty)</span>',
                f'<button type="button" class="slot-swap" data-variant="{variant}">'
                "swap</button>",
                f'<button type="button" class="slot-clear" data-variant="{variant}">'
                "clear</button>",
                "</div>",
            ]
        )
    parts.extend(
        [
            f'<form id="pick-form" method="post" action="{escape(post_url)}">',
            '<input type="hidden" name="slot_A" id="field-slot-A" value="">',
            '<input type="hidden" name="slot_B" id="field-slot-B" value="">',
            '<button type="submit" id="confirm" disabled>Confirm</button>',
            "</form>",
            # U-5: inline hint target for the both-slots-full dead-click.
            '<span class="pick-hint" id="pick-hint" role="status" '
            'aria-live="polite"></span>',
            "</div>",
            # U-1 (Sally a11y): the receipt announces "PICK RECORDED" to AT.
            '<div id="receipt" class="receipt" role="status" aria-live="polite" '
            "hidden></div>",
            "</header>",
            '<main class="grid">',
        ]
    )
    for entry in roster:
        parts.extend(_render_card(entry, repo_root=root))
    parts.extend(
        [
            "</main>",
            f"<script>{_PAGE_JS}</script>",
            "</body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(parts)


# ------------------------------------------------- pick capture (Amelia, localhost)
class _PickHandler(BaseHTTPRequestHandler):
    """One-shot pick endpoint. GET serves the page + same-origin thumbnails;
    a VALID POST to the relative ``/pick`` action ends the server (R1)."""

    server: _PickServer  # type: ignore[assignment]

    def _send_bytes(self, body: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler naming
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send_bytes(
                self.server.picker_html.encode("utf-8"), "text/html; charset=utf-8"
            )
            return
        png_path = self.server.thumbnails.get(path)
        if png_path is not None and png_path.is_file():
            self._send_bytes(png_path.read_bytes(), "image/png")
            return
        self._respond(404, {"error": f"unknown path {path!r}"})

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler naming
        if urlparse(self.path).path != "/pick":
            self._respond(404, {"error": f"unknown endpoint {self.path!r}"})
            return
        # R3: reject a non-numeric or negative Content-Length with a clean 400
        # BEFORE any rfile.read — a negative length reaches rfile.read(-N) which
        # blocks until EOF (the header string; a non-negative integer or nothing).
        raw_length = (self.headers.get("Content-Length") or "").strip()
        if raw_length == "":
            length = 0
        elif raw_length.isdigit():
            length = int(raw_length)
        else:
            self._respond(
                400,
                {"error": f"invalid Content-Length header {raw_length!r}"},
            )
            return
        if length > MAX_POST_BODY_BYTES:
            # R4: never slurp an unbounded body; reject oversized + keep serving.
            # P3 (Windows): replying 413 with the client's body still in flight makes the
            # OS abort the connection (ConnectionAbortedError) and can wedge the handler.
            # Drain a BOUNDED window of the incoming body first so the socket closes
            # cleanly — capped so a multi-MB attack body is still refused, never read whole.
            # R2: the drain + the 413 reply are wrapped in suppress(OSError) so the
            # Windows ConnectionAbortedError race can never prevent a clean close —
            # the server must keep serving (it already does after this return).
            self.close_connection = True
            with contextlib.suppress(OSError):
                drain_remaining = min(length, MAX_POST_BODY_BYTES + 128 * 1024)
                while drain_remaining > 0:
                    chunk = self.rfile.read(min(drain_remaining, 65536))
                    if not chunk:
                        break
                    drain_remaining -= len(chunk)
                self._respond(
                    413,
                    {
                        "error": (
                            f"request body {length} bytes exceeds the "
                            f"{MAX_POST_BODY_BYTES}-byte pick-form cap"
                        )
                    },
                )
            return
        fields = parse_qs(self.rfile.read(length).decode("utf-8"))
        picks: dict[str, str] = {}
        for variant in _VARIANT_IDS:
            values = fields.get(f"slot_{variant}") or []
            name = values[0].strip() if values else ""
            if name:
                picks[variant] = name
        if not picks:
            self._respond(400, {"error": "no slot filled; at least Style A or B required"})
            return
        unknown = sorted(n for n in picks.values() if n not in self.server.valid_names)
        if unknown:
            self._respond(400, {"error": f"unknown styleguide name(s): {unknown}"})
            return
        try:
            receipt = self.server.on_pick(picks)
        except Exception as exc:  # fail-loud: surface to page AND to capture_pick
            self.server.pick_error = exc
            self._respond(500, {"error": str(exc)})
            return
        self.server.pick_result = (picks, receipt)
        self._respond(200, receipt)

    def _respond(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - stdlib sig
        pass  # quiet server; the terminal receipt is the operator surface


class _PickServer(HTTPServer):
    """Ephemeral-port server carrying the pick state for the one-shot handler."""

    def __init__(
        self,
        valid_names: frozenset[str],
        on_pick: Callable[[dict[str, str]], dict[str, Any]],
    ) -> None:
        super().__init__(("127.0.0.1", 0), _PickHandler)
        self.valid_names = valid_names
        self.on_pick = on_pick
        self.picker_html = ""
        self.thumbnails: dict[str, Path] = {}
        self.pick_result: tuple[dict[str, str], dict[str, Any]] | None = None
        self.pick_error: Exception | None = None


def _cli_fallback(
    roster: list[dict[str, Any]],
    *,
    on_pick: Callable[[dict[str, str]], dict[str, Any]],
    input_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
) -> tuple[dict[str, str], dict[str, Any]]:
    """DEGRADED FALLBACK only (browser-won't-open path): numbered CLI pick.

    Slot symmetry mirrors the web page (R7): EITHER slot may be skipped (blank),
    so an A-only or B-only single-variant pick is a first-class path — a
    single-variant directive dispatches exactly one deck downstream. At least
    one slot must be filled (mirrors the web 400 on an empty pick).
    """
    print_fn("Browser could not be opened — CLI fallback (numbered pick).")
    for index, entry in enumerate(roster, start=1):
        probe = "  [PROBE — scaffolding]" if entry.get("probe") else ""
        print_fn(
            f"  {index}. {entry['display_name']}  ({entry['name']}){probe}\n"
            f"     {entry['distinguishing']}"
        )
    picks: dict[str, str] = {}
    while True:
        for variant in _VARIANT_IDS:
            prompt = f"Style {variant} number (blank for none): "
            while True:
                raw = input_fn(prompt).strip()
                if not raw:
                    break
                if raw.isdigit() and 1 <= int(raw) <= len(roster):
                    picks[variant] = roster[int(raw) - 1]["name"]
                    break
                print_fn(f"  invalid choice {raw!r}; enter 1-{len(roster)} or blank")
        if picks:
            break
        print_fn("at least one of Style A / Style B must be picked — try again")
    receipt = on_pick(picks)
    print_fn(f"PICK RECORDED: {json.dumps(receipt, sort_keys=True)}")
    return (picks, receipt)


def capture_pick(
    roster: list[dict[str, Any]],
    *,
    on_pick: Callable[[dict[str, str]], dict[str, Any]],
    html_path: str | Path | None = None,
    opener: Callable[[str], bool] = webbrowser.open,
    input_fn: Callable[[str], str] = input,
    print_fn: Callable[[str], None] = print,
    timeout: float | None = 600.0,
    repo_root: Path | None = None,
) -> tuple[dict[str, str], dict[str, Any]]:
    """Capture ONE pick: ephemeral-port stdlib http.server, one valid POST, exit.

    SAME-ORIGIN end-to-end (R1): the server itself serves the rendered page at
    ``http://127.0.0.1:<port>/`` (and the curated thumbnails under
    ``/thumbnails/``), and the browser is opened at that URL — never a
    ``file://`` page fetch()ing localhost (null-origin CORS would block the
    receipt panel). The form action is the RELATIVE ``/pick``. A copy of the
    rendered page is still written to ``html_path`` for evidence/debug (its
    relative thumbnail srcs resolve only when served). ``on_pick`` receives
    ``{variant_id: guide_name}`` and returns the receipt echoed to the page
    (green receipt panel) and to the caller. A single-variant pick (A-only or
    B-only) is legitimate and dispatches exactly one deck downstream. When the
    browser cannot open, the CLI-numbered fallback runs instead (degraded path).
    """
    if not roster:
        raise PickerError(
            "empty roster: nothing to pick from (if only probe-marked guides "
            "exist, re-run with --include-probes / include_probes=True)"
        )
    valid_names = frozenset(entry["name"] for entry in roster)
    server = _PickServer(valid_names, on_pick)
    try:
        html = render_picker_html(roster, post_url="/pick", repo_root=repo_root)
        server.picker_html = html
        server.thumbnails = thumbnail_routes(roster, repo_root=repo_root)
        if html_path is None:
            html_path = (
                Path(tempfile.mkdtemp(prefix="styleguide-picker-")) / "styleguide-picker.html"
            )
        page = Path(html_path)
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(html, encoding="utf-8", newline="\n")
        root_url = f"http://127.0.0.1:{server.server_address[1]}/"
        try:
            opened = bool(opener(root_url))
        except Exception:
            opened = False
        if not opened:
            server.server_close()
            server = None  # type: ignore[assignment]
            return _cli_fallback(
                roster, on_pick=on_pick, input_fn=input_fn, print_fn=print_fn
            )
        timeout_note = "no timeout" if timeout is None else f"timeout {timeout:g}s"
        print_fn(
            f"waiting for your pick at {root_url} ({timeout_note}; Ctrl-C to abort)"
        )
        server.timeout = 0.5
        deadline = None if timeout is None else datetime.now(UTC).timestamp() + timeout
        while server.pick_result is None and server.pick_error is None:
            if deadline is not None and datetime.now(UTC).timestamp() > deadline:
                raise PickerError(f"no pick received within {timeout}s; giving up")
            server.handle_request()
        if server.pick_error is not None:
            raise server.pick_error
        assert server.pick_result is not None
        return server.pick_result
    finally:
        if server is not None:
            server.server_close()


# --------------------------------------------- directive write (AC-2/AC-3/AC-7, J-3)
def write_pick_to_directive(
    directive_path: str | Path,
    picks: dict[str, str],
    *,
    ssot_path: str | Path | None = None,
    picked_at: str | None = None,
    provenance_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write/patch ``gamma_settings[]`` + the provenance block into the directive.

    Existing ``gamma_settings`` semantics VERBATIM (J-3): a picked variant's
    existing entry is patched in place (its other per-variant keys survive —
    they still override the styleguide base layer downstream); an absent entry
    is appended as ``{variant_id, styleguide}``; unpicked variants are left
    untouched. A styleguide name absent from the SSOT is a LOUD error before
    anything is written (A-1); so are duplicate ``variant_id`` rows (R5 — never
    first-match-patch) and a present-but-non-list / non-mapping-entry
    ``gamma_settings`` (R6 — never silently discarded). The read-modify-write
    runs under an advisory same-host file lock (R8). NOTE (R12): the directive
    is re-serialized via a yaml round-trip (``yaml.safe_dump``); YAML comments
    and anchors in the original file are NOT preserved. Returns the provenance
    block.
    """
    ssot = Path(ssot_path) if ssot_path is not None else GAMMA_STYLE_GUIDES_SSOT_PATH
    if not ssot.is_file():
        raise PickerError(f"styleguide SSOT not found at {ssot}")
    ssot_bytes = ssot.read_bytes()
    guides = _load_ssot_guides(ssot)
    if not picks:
        raise PickerError("no picks supplied: at least one variant must name a styleguide")
    normalized: dict[str, str] = {}
    for variant, name in picks.items():
        variant_id = str(variant).strip().upper()
        if variant_id not in _VARIANT_IDS:
            raise PickerError(
                f"pick variant id must be one of {list(_VARIANT_IDS)}; got {variant!r}"
            )
        guide_name = str(name).strip()
        # A-M1 (Winston): enforce the SSOT-membership + lifecycle/visibility
        # invariant at the MUTATION point too (defense-in-depth; the roster-load
        # filter already hides these on the served path). Single-sourced through
        # `_assert_pickable_guide` so the gh-pages decoder applies the identical
        # rule (Q1 anti-drift) — a `deprecated` (retired) or `visibility: probe`
        # (scaffolding) guide must NEVER be bound into a production directive.
        _assert_pickable_guide(guide_name, guides, ssot)
        normalized[variant_id] = guide_name

    directive = Path(directive_path)
    directive.parent.mkdir(parents=True, exist_ok=True)
    with _advisory_lock(directive):  # R8: serialize the read-modify-write
        if directive.is_file():
            loaded = yaml.safe_load(directive.read_text(encoding="utf-8")) or {}
            if not isinstance(loaded, dict):
                raise PickerError(f"directive {directive} is not a YAML mapping")
        else:
            loaded = {}
        raw = loaded.get("gamma_settings")
        if raw is None:
            settings: list[dict[str, Any]] = []
        elif not isinstance(raw, list):
            raise PickerError(
                f"directive {directive} gamma_settings must be a list of mappings, "
                f"got {type(raw).__name__} (R6: never silently discarded)"
            )
        else:
            settings = []
            for index, item in enumerate(raw):
                if not isinstance(item, dict):
                    raise PickerError(
                        f"directive {directive} gamma_settings[{index}] must be a "
                        f"mapping, got {type(item).__name__} (R6: never silently "
                        f"dropped)"
                    )
                settings.append(dict(item))
            seen_variants: set[str] = set()
            for item in settings:
                existing_id = str(item.get("variant_id") or "").strip().upper()
                if existing_id and existing_id in seen_variants:
                    raise PickerError(
                        f"directive {directive} carries duplicate variant_id "
                        f"{existing_id!r} rows in gamma_settings (R5: fail-loud, "
                        f"never first-match-patch)"
                    )
                if existing_id:
                    seen_variants.add(existing_id)
        for variant_id in sorted(normalized):
            entry = next(
                (
                    item
                    for item in settings
                    if str(item.get("variant_id") or "").strip().upper() == variant_id
                ),
                None,
            )
            if entry is None:
                settings.append(
                    {"variant_id": variant_id, "styleguide": normalized[variant_id]}
                )
            else:
                entry["styleguide"] = normalized[variant_id]
        loaded["gamma_settings"] = settings

        stamp = picked_at if picked_at is not None else datetime.now(UTC).isoformat()
        provenance = {
            "picked_at": stamp,
            "picker_version": PICKER_VERSION,
            "ssot_sha256": hashlib.sha256(ssot_bytes).hexdigest(),
            "picks": [
                {"variant_id": variant_id, "styleguide": normalized[variant_id]}
                for variant_id in sorted(normalized)
            ],
            "written_by": "styleguide_picker",
        }
        # A7 (Marcus): the gh-pages paste-back path threads extra provenance
        # (who/from-url/roster-hash/version-count/the code) so an unattributable
        # pick is auditable end-to-end. Additive: local-picker callers pass None.
        if provenance_extra:
            # Guard: extra keys must never clobber the canonical provenance fields
            # (they are the audit anchors — picked_at/version/ssot hash/picks/writer).
            canonical = {"picked_at", "picker_version", "ssot_sha256", "picks", "written_by"}
            clashes = canonical & set(provenance_extra)
            if clashes:
                raise PickerError(
                    f"provenance_extra may not override canonical provenance keys "
                    f"{sorted(clashes)}"
                )
            provenance.update(provenance_extra)
        loaded["styleguide_picker_provenance"] = provenance
        # R-MAJOR-1: crash-atomic write — never truncate-then-write the live run
        # input in place. Temp sibling + fsync + os.replace, still inside the lock.
        _atomic_write_text(directive, yaml.safe_dump(loaded, sort_keys=False))
    return provenance


# ------------------------------------------------- sidecar append (D-1/J-1, AC-4)
def append_pick_event(
    picks: dict[str, str],
    *,
    directive_path: str | Path,
    picked_at: str,
    run_id: str | None = None,
    events_path: str | Path | None = None,
    dedup_key: str | None = None,
    course: str | None = None,
) -> list[dict[str, Any]]:
    """Append one JSONL line per pick to the append-only sidecar (digest-idempotent).

    ``course`` (S2 F-502, ADDITIVE + append-only-safe per the carrier
    invariant): the corpus/course identity the pick was made for, threaded from
    trial-start's ``input_path``. "Last-used-per-course" recommendations derive
    EXCLUSIVELY from this field — never by dereferencing ``directive_path``
    (run-scoped, prunable). Legacy events without the field read honestly as
    "no prior pick for this course".

    STANDALONE utility (J-1/D-1): never imported by CD/gary code; mirrors the
    ``gamma-learned-observations.jsonl`` discipline. The SSOT's
    ``presentation.last_used`` stays null FOREVER — the picker renders the
    sidecar-derived value instead. Replaying an identical event is a no-op
    (the file is never rewritten or shrunk). The read-digests-then-append runs
    under an advisory same-host file lock (R8; same-host cooperating-writer
    guarantee only). Returns the events written.

    Idempotency has TWO layers. By default an event is deduped on its full
    ``event_digest`` (every field, including ``picked_at``) — replaying a byte-
    identical event is a no-op. When ``dedup_key`` is supplied (the paste-back
    commit path), each per-variant event ALSO carries a stable
    ``dedup_key`` = ``f"{dedup_key}:{variant_id}"`` and is deduped on THAT: an
    identical re-confirm mints a fresh ``picked_at`` yet is still a true no-op,
    because the stable ``(run_tag, selection_code)`` identity — not the varying
    timestamp — decides the append. A DIFFERENT code for the same run has a
    different ``dedup_key`` and is a deliberate change (appends; last-write-wins).
    """
    path = Path(events_path) if events_path is not None else GAMMA_STYLEGUIDE_PICKS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with _advisory_lock(path):  # R8: serialize digest-read + append
        prior = read_pick_events(path)
        existing = {
            event.get("event_digest")
            for event in prior
            if event.get("event_digest")
        }
        existing_dedup = {
            event.get("dedup_key") for event in prior if event.get("dedup_key")
        }
        written: list[dict[str, Any]] = []
        lines: list[str] = []
        for variant in sorted(picks):
            variant_id = str(variant).strip().upper()
            event: dict[str, Any] = {
                "guide_name": str(picks[variant]).strip(),
                "variant_id": variant_id,
                "directive_path": Path(directive_path).as_posix(),
                "picked_at": picked_at,
            }
            if run_id:
                event["run_id"] = str(run_id)
            if course:
                event["course"] = str(course)
            variant_dedup = f"{dedup_key}:{variant_id}" if dedup_key else None
            if variant_dedup is not None:
                event["dedup_key"] = variant_dedup
            digest = hashlib.sha256(
                json.dumps(event, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            # Skip on EITHER identity: the exact-event digest, or (when supplied)
            # the stable (run_tag, code) dedup key that survives a fresh timestamp.
            if digest in existing or (
                variant_dedup is not None and variant_dedup in existing_dedup
            ):
                continue
            event["event_digest"] = digest
            existing.add(digest)
            if variant_dedup is not None:
                existing_dedup.add(variant_dedup)
            written.append(event)
            lines.append(json.dumps(event, sort_keys=True, separators=(",", ":")))
        if lines:
            with path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write("\n".join(lines) + "\n")
    return written


# ------------------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directive", type=Path, required=True, help="run directive yaml")
    parser.add_argument("--ssot", type=Path, default=None, help="styleguide SSOT override")
    parser.add_argument(
        "--include-probes",
        action="store_true",
        help="also list probe-marked guides (D-3; warning-chipped, second-click select)",
    )
    parser.add_argument(
        "--include-deprecated",
        action="store_true",
        help="also list deprecated (retired) guides for audit (badged, not for production)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="skip the browser and use the CLI-numbered fallback directly",
    )
    parser.add_argument("--html-out", type=Path, default=None, help="rendered page path")
    parser.add_argument("--run-id", default=None, help="run id recorded on pick events")
    args = parser.parse_args(argv)

    roster = load_picker_roster(
        include_probes=args.include_probes,
        include_deprecated=args.include_deprecated,
        ssot_path=args.ssot,
    )

    def _on_pick(picks: dict[str, str]) -> dict[str, Any]:
        provenance = write_pick_to_directive(args.directive, picks, ssot_path=args.ssot)
        append_pick_event(
            picks,
            directive_path=args.directive,
            picked_at=provenance["picked_at"],
            run_id=args.run_id,
        )
        return {
            "directive_path": Path(args.directive).as_posix(),
            "picks": picks,
            "picked_at": provenance["picked_at"],
        }

    opener = (lambda url: False) if args.no_browser else webbrowser.open
    picks, receipt = capture_pick(
        roster, on_pick=_on_pick, html_path=args.html_out, opener=opener
    )
    # Sally: the launching terminal echoes the same receipt as the page panel.
    print(
        "PICK RECORDED\n"
        f"  directive: {receipt['directive_path']}\n"
        f"  picks: {json.dumps(picks, sort_keys=True)}\n"
        f"  picked_at: {receipt['picked_at']}"
    )
    return 0


__all__ = [
    "GAMMA_STYLEGUIDE_PICKS_PATH",
    "GAMMA_STYLE_GUIDES_SSOT_PATH",
    "PICKER_VERSION",
    "PickerError",
    "append_pick_event",
    "assert_pickable_guide",
    "capture_pick",
    "load_picker_roster",
    "main",
    "read_pick_events",
    "render_picker_html",
    "thumbnail_routes",
    "write_pick_to_directive",
]


if __name__ == "__main__":
    raise SystemExit(main())
