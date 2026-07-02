"""Leg-D — HTML style-picker at CD-entry (Fork A, pre-run operator surface).

Murat's AC regime (green-light record 2026-07-02, binding):

- AC-1: roster renders from the REAL SSOT loader (no fixture dict); probe-marked
  guides (``presentation.visibility: probe``, D-3) are hidden by default and
  included flagged under ``include_probes=True``.
- AC-4: sidecar append idempotency + the hermetic write-gate validator PASSES
  after EVERY write-back test (M-2 rider).
- AC-5: non-CD-writer boundary — CD-owned SSOT bytes are byte-identical pre/post
  picker + sidecar operations.
- AC-6: every rendered thumbnail_ref resolves to a real on-disk PNG; a dangling
  ref FAILS loud; a null ref renders the explicit "no live render" placeholder
  (S-3), never a confidently wrong image.
- A-1 fail-loud: unknown styleguide name on directive-patch raises; a malformed
  sidecar line raises (never a silent skip).
- J-1/D-1 boundary: the sidecar writer is standalone — no CD/gary module imports
  the picker; the SSOT's ``presentation.last_used`` stays null forever.
- CLI-numbered fallback when the browser cannot open.
- Localhost capture: real ephemeral-port http.server, one POST, server exits.

RED-first: this file was authored before ``app/marcus/orchestrator/
styleguide_picker.py`` existed (ModuleNotFoundError RED recorded in Dev Notes).
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest
import yaml

from app.marcus.orchestrator.styleguide_picker import (
    GAMMA_STYLE_GUIDES_SSOT_PATH,
    GAMMA_STYLEGUIDE_PICKS_PATH,
    PickerError,
    append_pick_event,
    capture_pick,
    load_picker_roster,
    render_picker_html,
    write_pick_to_directive,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
SEED_GUIDES = {
    "classic-freeform-x-cards",
    "hil-2026-apc-blueprint-classic",
    "hil-2026-apc-studio-image-card",
}
PROBE_GUIDES = {"leg-c-part3-floor-probe", "leg-c-part3-floor-toohigh"}


def _assert_ssot_write_gate_green() -> None:
    """M-2 rider: the hermetic write-gate validator passes after every write."""
    from app.specialists.gary.styleguide_library import load_style_guides
    from scripts.utilities.validate_gamma_style_guides import validate_style_guides

    errors = validate_style_guides(load_style_guides(GAMMA_STYLE_GUIDES_SSOT_PATH))
    assert errors == [], f"SSOT write-gate went RED after a picker write: {errors}"


# --------------------------------------------------------------------------- AC-1
def test_roster_loads_from_real_ssot_and_hides_probes_by_default() -> None:
    roster = load_picker_roster()
    names = {entry["name"] for entry in roster}
    assert names >= SEED_GUIDES
    assert not (PROBE_GUIDES & names), "probe guides must be hidden by default (D-3)"
    for entry in roster:
        assert entry["display_name"].strip()
        assert entry["distinguishing"].strip(), "distinguishing must be always-visible (Sally)"
        assert entry["probe"] is False


def test_roster_include_probes_flags_probe_entries() -> None:
    roster = load_picker_roster(include_probes=True)
    by_name = {entry["name"]: entry for entry in roster}
    assert set(by_name) >= PROBE_GUIDES
    for probe in PROBE_GUIDES:
        assert by_name[probe]["probe"] is True
    for seed in SEED_GUIDES:
        assert by_name[seed]["probe"] is False


def test_roster_joins_last_used_from_sidecar_not_ssot(tmp_path: Path) -> None:
    """D-1: last_used is sidecar-derived at render time; SSOT last_used stays null."""
    events = tmp_path / "picks.jsonl"
    append_pick_event(
        {"A": "classic-freeform-x-cards"},
        directive_path=tmp_path / "d.yaml",
        picked_at="2026-07-02T01:00:00+00:00",
        events_path=events,
    )
    roster = load_picker_roster(events_path=events)
    by_name = {entry["name"]: entry for entry in roster}
    assert by_name["classic-freeform-x-cards"]["last_used"] == "2026-07-02T01:00:00+00:00"
    assert by_name["hil-2026-apc-blueprint-classic"]["last_used"] is None
    # The CD-owned SSOT field itself stays null FOREVER.
    ssot = yaml.safe_load(GAMMA_STYLE_GUIDES_SSOT_PATH.read_text(encoding="utf-8"))
    for record in ssot["style_guides"].values():
        assert (record.get("presentation") or {}).get("last_used") is None


# --------------------------------------------------------------------------- AC-6
def test_every_rendered_thumbnail_ref_resolves_to_real_png() -> None:
    roster = load_picker_roster(include_probes=True)
    html = render_picker_html(roster, post_url="http://127.0.0.1:1/pick")
    seen_thumb = 0
    for entry in roster:
        ref = entry["thumbnail_ref"]
        if ref is None:
            continue
        seen_thumb += 1
        png = REPO_ROOT / ref
        assert png.is_file(), f"{entry['name']}: dangling thumbnail_ref {ref}"
        assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", f"{ref} is not a real PNG"
        assert png.resolve().as_uri() in html
    assert seen_thumb == 3, "the 3 seed guides must carry curated thumbnails (D-2)"


def test_dangling_thumbnail_ref_fails_loud() -> None:
    roster = load_picker_roster()
    roster[0]["thumbnail_ref"] = "state/config/gamma-styleguide-thumbnails/does-not-exist.png"
    with pytest.raises(PickerError, match="thumbnail"):
        render_picker_html(roster, post_url="http://127.0.0.1:1/pick")


def test_null_thumbnail_renders_no_live_render_placeholder() -> None:
    """S-3: missing thumbnail -> explicit placeholder, never a wrong image."""
    roster = load_picker_roster(include_probes=True)
    html = render_picker_html(roster, post_url="http://127.0.0.1:1/pick")
    assert "no live render" in html


def test_render_carries_slot_bar_probe_chip_and_receipt_panel() -> None:
    """Sally S-1/S-2 + slot-bar/receipt structure pins (static single page MVP)."""
    roster = load_picker_roster(include_probes=True)
    html = render_picker_html(roster, post_url="http://127.0.0.1:9999/pick")
    assert "Style A" in html and "Style B" in html  # slot bar pinned above the grid
    assert 'name="slot_A"' in html and 'name="slot_B"' in html  # real form fields
    assert 'action="http://127.0.0.1:9999/pick"' in html
    assert html.lower().count("<details") >= len(roster)  # narrative behind a toggle
    assert "PROBE" in html  # S-1 warning chip on probe cards
    assert 'id="receipt"' in html  # green receipt panel target
    assert "disabled" in html  # Confirm disabled until >=1 slot filled


# --------------------------------------------------------------------------- AC-4
def test_sidecar_append_is_idempotent(tmp_path: Path) -> None:
    events = tmp_path / "picks.jsonl"
    kwargs = dict(
        directive_path=tmp_path / "d.yaml",
        picked_at="2026-07-02T01:00:00+00:00",
        events_path=events,
    )
    first = append_pick_event({"A": "classic-freeform-x-cards"}, **kwargs)
    second = append_pick_event({"A": "classic-freeform-x-cards"}, **kwargs)
    assert len(first) == 1 and second == []
    lines = [ln for ln in events.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["guide_name"] == "classic-freeform-x-cards"
    assert event["variant_id"] == "A"
    assert event["picked_at"] == "2026-07-02T01:00:00+00:00"
    _assert_ssot_write_gate_green()


def test_sidecar_records_run_id_when_present(tmp_path: Path) -> None:
    events = tmp_path / "picks.jsonl"
    written = append_pick_event(
        {"A": "classic-freeform-x-cards", "B": "hil-2026-apc-studio-image-card"},
        directive_path=tmp_path / "d.yaml",
        picked_at="2026-07-02T02:00:00+00:00",
        run_id="run-123",
        events_path=events,
    )
    assert len(written) == 2
    events_read = [
        json.loads(ln) for ln in events.read_text(encoding="utf-8").splitlines() if ln.strip()
    ]
    assert all(e["run_id"] == "run-123" for e in events_read)
    _assert_ssot_write_gate_green()


def test_malformed_sidecar_line_fails_loud(tmp_path: Path) -> None:
    """A-1: corruption in the append-only ledger is a loud error, never skipped."""
    events = tmp_path / "picks.jsonl"
    events.write_text('{"guide_name": "x"}\nNOT-JSON{{{\n', encoding="utf-8")
    with pytest.raises(PickerError, match="line 2"):
        load_picker_roster(events_path=events)
    with pytest.raises(PickerError, match="line 2"):
        append_pick_event(
            {"A": "classic-freeform-x-cards"},
            directive_path=tmp_path / "d.yaml",
            picked_at="2026-07-02T01:00:00+00:00",
            events_path=events,
        )


# --------------------------------------------------------------------------- AC-5
def test_cd_owned_ssot_bytes_identical_pre_post_picker_ops(tmp_path: Path) -> None:
    before = GAMMA_STYLE_GUIDES_SSOT_PATH.read_bytes()
    directive = tmp_path / "directive.yaml"
    events = tmp_path / "picks.jsonl"
    roster = load_picker_roster(events_path=events)
    render_picker_html(roster, post_url="http://127.0.0.1:1/pick")
    provenance = write_pick_to_directive(directive, {"A": "classic-freeform-x-cards"})
    append_pick_event(
        {"A": "classic-freeform-x-cards"},
        directive_path=directive,
        picked_at=provenance["picked_at"],
        events_path=events,
    )
    after = GAMMA_STYLE_GUIDES_SSOT_PATH.read_bytes()
    assert before == after, "picker/sidecar ops must never touch the write-gated SSOT"
    _assert_ssot_write_gate_green()


# ------------------------------------------------------------------- A-1 fail-loud
def test_unknown_styleguide_name_on_directive_patch_fails_loud(tmp_path: Path) -> None:
    with pytest.raises(PickerError, match="no-such-style"):
        write_pick_to_directive(tmp_path / "d.yaml", {"A": "no-such-style"})
    assert not (tmp_path / "d.yaml").exists(), "a failed pick must not write a directive"


def test_bad_variant_id_fails_loud(tmp_path: Path) -> None:
    with pytest.raises(PickerError, match="variant"):
        write_pick_to_directive(tmp_path / "d.yaml", {"C": "classic-freeform-x-cards"})


def test_empty_picks_fail_loud(tmp_path: Path) -> None:
    with pytest.raises(PickerError, match="pick"):
        write_pick_to_directive(tmp_path / "d.yaml", {})


# ------------------------------------------------------- localhost capture (Amelia)
def _post_form(url: str, fields: dict[str, str]) -> dict:
    body = urllib.parse.urlencode(fields).encode("utf-8")
    request = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def test_capture_pick_serves_one_post_then_exits(tmp_path: Path) -> None:
    roster = load_picker_roster()
    html_path = tmp_path / "picker.html"
    opened_urls: list[str] = []
    result: dict = {}

    def _run() -> None:
        picks, receipt = capture_pick(
            roster,
            on_pick=lambda picks: {"directive_path": "d.yaml", "picks": picks},
            html_path=html_path,
            opener=lambda url: opened_urls.append(url) or True,
            timeout=30.0,
        )
        result["picks"] = picks
        result["receipt"] = receipt

    worker = threading.Thread(target=_run)
    worker.start()
    try:
        # The rendered page on disk carries the real endpoint in the form action.
        for _ in range(100):
            if html_path.exists():
                break
            worker.join(0.05)
        html = html_path.read_text(encoding="utf-8")
        action = html.split('action="', 1)[1].split('"', 1)[0]
        receipt = _post_form(
            action, {"slot_A": "classic-freeform-x-cards", "slot_B": ""}
        )
    finally:
        worker.join(timeout=30)
    assert not worker.is_alive(), "server must exit after one accepted POST"
    assert result["picks"] == {"A": "classic-freeform-x-cards"}
    assert receipt["picks"] == {"A": "classic-freeform-x-cards"}
    assert opened_urls and opened_urls[0].startswith("file://")


def test_capture_pick_rejects_unknown_guide_then_accepts_valid(tmp_path: Path) -> None:
    roster = load_picker_roster()
    html_path = tmp_path / "picker.html"
    result: dict = {}

    def _run() -> None:
        picks, _ = capture_pick(
            roster,
            on_pick=lambda picks: {"picks": picks},
            html_path=html_path,
            opener=lambda url: True,
            timeout=30.0,
        )
        result["picks"] = picks

    worker = threading.Thread(target=_run)
    worker.start()
    try:
        for _ in range(100):
            if html_path.exists():
                break
            worker.join(0.05)
        html = html_path.read_text(encoding="utf-8")
        action = html.split('action="', 1)[1].split('"', 1)[0]
        with pytest.raises(urllib.error.HTTPError) as excinfo:
            _post_form(action, {"slot_A": "no-such-style"})
        assert excinfo.value.code == 400
        _post_form(action, {"slot_A": "hil-2026-apc-studio-image-card"})
    finally:
        worker.join(timeout=30)
    assert result["picks"] == {"A": "hil-2026-apc-studio-image-card"}


def test_cli_fallback_when_browser_cannot_open(tmp_path: Path) -> None:
    roster = load_picker_roster()
    answers = iter(["1", "3"])  # Style A = first numbered guide, Style B = third
    printed: list[str] = []
    picks, receipt = capture_pick(
        roster,
        on_pick=lambda picks: {"directive_path": "d.yaml", "picks": picks},
        html_path=tmp_path / "picker.html",
        opener=lambda url: False,  # browser cannot open -> degraded fallback
        input_fn=lambda prompt: next(answers),
        print_fn=printed.append,
    )
    ordered = [entry["name"] for entry in roster]
    assert picks == {"A": ordered[0], "B": ordered[2]}
    assert receipt["picks"] == picks
    assert any(ordered[0] in line for line in printed), "numbered roster must be printed"


def test_cli_fallback_blank_b_slot_single_select(tmp_path: Path) -> None:
    roster = load_picker_roster()
    answers = iter(["2", ""])  # single-select fast path: Style B left empty
    picks, _ = capture_pick(
        roster,
        on_pick=lambda picks: {"picks": picks},
        html_path=tmp_path / "picker.html",
        opener=lambda url: False,
        input_fn=lambda prompt: next(answers),
        print_fn=lambda line: None,
    )
    ordered = [entry["name"] for entry in roster]
    assert picks == {"A": ordered[1]}


# ------------------------------------------------------------------ J-1/D-1 boundary
def test_picker_never_imported_by_cd_or_gary_code() -> None:
    """J-1/D-1: the sidecar writer is standalone; no specialist module imports it."""
    specialist_root = REPO_ROOT / "app" / "specialists"
    offenders = [
        path
        for path in specialist_root.rglob("*.py")
        if "styleguide_picker" in path.read_text(encoding="utf-8", errors="ignore")
    ]
    assert offenders == [], f"specialist code must never import the picker: {offenders}"


def test_default_sidecar_path_is_the_ratified_store() -> None:
    assert GAMMA_STYLEGUIDE_PICKS_PATH == (
        REPO_ROOT / "state" / "config" / "gamma-styleguide-picks.jsonl"
    )
