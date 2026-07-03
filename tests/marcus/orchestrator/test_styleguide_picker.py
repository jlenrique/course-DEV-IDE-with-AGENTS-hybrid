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
import re
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
    "hil-2026-apc-crossroads-classic",
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


def test_roster_carries_lifecycle_and_candidate_badge_renders() -> None:
    """Session-07 A1: lifecycle rides the roster; candidates get a visible badge.

    Registry membership is volatile (the session-07 `videographic-glance-track`
    candidate was DEPRECATED 2026-07-03 in the "start over" reset), so the badge
    machinery is exercised against a synthetic candidate entry rather than pinning
    live SSOT content. Live permanents keep their tier.
    """
    badge = '<span class="chip chip-candidate">'
    roster = load_picker_roster(include_probes=True)
    by_name = {entry["name"]: entry for entry in roster}
    for seed in SEED_GUIDES | PROBE_GUIDES:
        assert by_name[seed]["lifecycle"] == "permanent"

    # Badge machinery: a synthetic candidate renders exactly one badge.
    synthetic = dict(by_name["hil-2026-apc-crossroads-classic"])
    synthetic["lifecycle"] = "candidate"
    html = render_picker_html([synthetic], post_url="http://127.0.0.1:1/pick")
    assert html.count(badge) == 1
    assert "CANDIDATE — A-corpus only" in html

    # Permanent-only roster renders no badge (the CSS class alone is not a badge).
    permanents = [by_name[s] for s in SEED_GUIDES]
    html = render_picker_html(permanents, post_url="http://127.0.0.1:1/pick")
    assert badge not in html


def test_roster_hides_deprecated_by_default_and_opts_in_for_audit() -> None:
    """A `lifecycle: deprecated` guide is retired from the production roster and
    only appears (badged) under include_deprecated. Regression guard for the
    2026-07-03 videographic deprecation."""
    default_names = {e["name"] for e in load_picker_roster(include_probes=True)}
    assert "videographic-glance-track" not in default_names, (
        "deprecated guide must be hidden from the default production roster"
    )

    audit = load_picker_roster(include_probes=True, include_deprecated=True)
    audit_by = {e["name"]: e for e in audit}
    assert audit_by["videographic-glance-track"]["lifecycle"] == "deprecated"

    html = render_picker_html(
        [audit_by["videographic-glance-track"]], post_url="http://127.0.0.1:1/pick"
    )
    assert '<span class="chip chip-deprecated">' in html
    assert "DEPRECATED — retired style" in html


def test_roster_joins_last_used_from_sidecar_not_ssot(tmp_path: Path) -> None:
    """D-1: last_used is sidecar-derived at render time; SSOT last_used stays null."""
    events = tmp_path / "picks.jsonl"
    append_pick_event(
        {"A": "hil-2026-apc-crossroads-classic"},
        directive_path=tmp_path / "d.yaml",
        picked_at="2026-07-02T01:00:00+00:00",
        events_path=events,
    )
    roster = load_picker_roster(events_path=events)
    by_name = {entry["name"]: entry for entry in roster}
    assert by_name["hil-2026-apc-crossroads-classic"]["last_used"] == "2026-07-02T01:00:00+00:00"
    assert by_name["hil-2026-apc-studio-image-card"]["last_used"] is None
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
        # R1: thumbnails render as SAME-ORIGIN server paths (a file:// img on an
        # http page is blocked by the browser), served by do_GET.
        assert f'src="/thumbnails/{entry["name"]}.png"' in html
    assert seen_thumb == 7, (
        "all 7 active styles carry a curated thumbnail after the session-09 roster build: "
        "crossroads-classic, crossroads-digital-collage, crossroads-magazine, "
        "crossroads-blueprint, crossroads-bread-and-butter, videographic-glance, "
        "studio-image-card."
    )


def test_dangling_thumbnail_ref_degrades_to_placeholder_and_rest_renders() -> None:
    """A-M2 (Winston, converges w/ Sally #6): a dangling/broken thumbnail_ref must
    NOT 500 the whole picker — it degrades to the honest placeholder plus a visible
    'thumbnail unavailable' warning chip, and the rest of the roster still renders."""
    roster = load_picker_roster()
    assert len(roster) >= 2, "need a sibling row to prove the rest still renders"
    roster[0]["thumbnail_ref"] = "state/config/gamma-styleguide-thumbnails/does-not-exist.png"
    # Never raises for a bad thumbnail row.
    html = render_picker_html(roster, post_url="http://127.0.0.1:1/pick")
    assert "no live render" in html  # the degraded placeholder
    assert "thumbnail unavailable" in html  # the visible warning chip
    # The broken card still renders (its heading is present) AND so do the others.
    for entry in roster:
        assert f'data-guide="{entry["name"]}"' in html
    # A sibling with a real curated render still serves its same-origin thumbnail.
    assert 'src="/thumbnails/' in html


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
    first = append_pick_event({"A": "hil-2026-apc-crossroads-classic"}, **kwargs)
    second = append_pick_event({"A": "hil-2026-apc-crossroads-classic"}, **kwargs)
    assert len(first) == 1 and second == []
    lines = [ln for ln in events.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["guide_name"] == "hil-2026-apc-crossroads-classic"
    assert event["variant_id"] == "A"
    assert event["picked_at"] == "2026-07-02T01:00:00+00:00"
    _assert_ssot_write_gate_green()


def test_sidecar_records_run_id_when_present(tmp_path: Path) -> None:
    events = tmp_path / "picks.jsonl"
    written = append_pick_event(
        {"A": "hil-2026-apc-crossroads-classic", "B": "hil-2026-apc-studio-image-card"},
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
            {"A": "hil-2026-apc-crossroads-classic"},
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
    provenance = write_pick_to_directive(directive, {"A": "hil-2026-apc-crossroads-classic"})
    append_pick_event(
        {"A": "hil-2026-apc-crossroads-classic"},
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
        write_pick_to_directive(tmp_path / "d.yaml", {"C": "hil-2026-apc-crossroads-classic"})


def test_empty_picks_fail_loud(tmp_path: Path) -> None:
    with pytest.raises(PickerError, match="pick"):
        write_pick_to_directive(tmp_path / "d.yaml", {})


# ------------------------------------------------ SHOULD-6 provenance_extra collision
@pytest.mark.parametrize(
    "canonical_key",
    ["picked_at", "picker_version", "ssot_sha256", "picks", "written_by"],
)
def test_provenance_extra_cannot_clobber_canonical_keys(
    tmp_path: Path, canonical_key: str
) -> None:
    directive = tmp_path / "d.yaml"
    with pytest.raises(PickerError, match="(?i)provenance_extra|canonical|override"):
        write_pick_to_directive(
            directive,
            {"A": "hil-2026-apc-crossroads-classic"},
            provenance_extra={canonical_key: "evil"},
        )


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
        # R1: the browser is pointed at the SERVER root; the rendered page (on
        # disk and served) carries the RELATIVE /pick action, resolved same-origin.
        for _ in range(100):
            if html_path.exists() and opened_urls:
                break
            worker.join(0.05)
        html = html_path.read_text(encoding="utf-8")
        action = html.split('action="', 1)[1].split('"', 1)[0]
        assert action == "/pick"
        receipt = _post_form(
            urllib.parse.urljoin(opened_urls[0], action),
            {"slot_A": "hil-2026-apc-crossroads-classic", "slot_B": ""},
        )
    finally:
        worker.join(timeout=30)
    assert not worker.is_alive(), "server must exit after one accepted POST"
    assert result["picks"] == {"A": "hil-2026-apc-crossroads-classic"}
    assert receipt["picks"] == {"A": "hil-2026-apc-crossroads-classic"}
    assert opened_urls and opened_urls[0].startswith("http://127.0.0.1:")


def test_capture_pick_rejects_unknown_guide_then_accepts_valid(tmp_path: Path) -> None:
    roster = load_picker_roster()
    html_path = tmp_path / "picker.html"
    opened_urls: list[str] = []
    result: dict = {}

    def _run() -> None:
        picks, _ = capture_pick(
            roster,
            on_pick=lambda picks: {"picks": picks},
            html_path=html_path,
            opener=lambda url: opened_urls.append(url) or True,
            timeout=30.0,
        )
        result["picks"] = picks

    worker = threading.Thread(target=_run)
    worker.start()
    try:
        for _ in range(100):
            if html_path.exists() and opened_urls:
                break
            worker.join(0.05)
        html = html_path.read_text(encoding="utf-8")
        action = html.split('action="', 1)[1].split('"', 1)[0]
        pick_url = urllib.parse.urljoin(opened_urls[0], action)
        with pytest.raises(urllib.error.HTTPError) as excinfo:
            _post_form(pick_url, {"slot_A": "no-such-style"})
        assert excinfo.value.code == 400
        _post_form(pick_url, {"slot_A": "hil-2026-apc-studio-image-card"})
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


# ---------------------------------------- 3-lane remediation R1-R14 (2026-07-02)
class _LiveCapture:
    """Run ``capture_pick`` on a worker thread and expose the opened URL/page."""

    def __init__(self, roster: list[dict], tmp_path: Path) -> None:
        self.html_path = tmp_path / "picker.html"
        self.opened: list[str] = []
        self.printed: list[str] = []
        self.result: dict = {}

        def _run() -> None:
            try:
                picks, receipt = capture_pick(
                    roster,
                    on_pick=lambda picks: {"picks": picks},
                    html_path=self.html_path,
                    opener=lambda url: self.opened.append(url) or True,
                    print_fn=self.printed.append,
                    timeout=30.0,
                )
                self.result["picks"] = picks
                self.result["receipt"] = receipt
            except Exception as exc:  # surfaced by the asserting test
                self.result["error"] = exc

        self.worker = threading.Thread(target=_run)
        self.worker.start()
        for _ in range(200):
            if self.opened and self.html_path.exists():
                break
            self.worker.join(0.05)

    @property
    def base_url(self) -> str:
        return self.opened[0]

    @property
    def pick_url(self) -> str:
        return urllib.parse.urljoin(self.base_url, "/pick")

    def finish(self) -> None:
        self.worker.join(timeout=30)
        assert not self.worker.is_alive(), "server must exit after one accepted POST"


def test_server_serves_page_same_origin_with_relative_pick_action(tmp_path: Path) -> None:
    """R1 (Blind#1 CORS): the browser opens the page FROM the pick server.

    A ``file://`` page fetch()ing ``http://127.0.0.1`` is null-origin — the
    browser blocks reading the response and the operator never sees the receipt
    panel. Same-origin end-to-end: the opener gets the SERVER root URL, do_GET
    serves the rendered page bytes, and the form action is the RELATIVE /pick.
    """
    roster = load_picker_roster()
    live = _LiveCapture(roster, tmp_path)
    try:
        assert live.opened and re.match(r"^http://127\.0\.0\.1:\d+/$", live.base_url), (
            f"browser must be pointed at the server root, got {live.opened}"
        )
        with urllib.request.urlopen(live.base_url, timeout=10) as response:
            assert response.status == 200
            served = response.read()
        # do_GET serves the rendered page bytes; the disk copy is evidence/debug.
        assert served == live.html_path.read_bytes()
        html = served.decode("utf-8")
        assert 'action="/pick"' in html, "form action must be same-origin-relative /pick"
        # Thumbnails ride the same origin too (file:// img on an http page is blocked).
        thumb_srcs = re.findall(r'src="(/thumbnails/[^"]+)"', html)
        assert thumb_srcs, "seed thumbnails must be served from the pick server"
        thumb_url = urllib.parse.urljoin(live.base_url, thumb_srcs[0])
        with urllib.request.urlopen(thumb_url, timeout=10) as response:
            assert response.status == 200
            assert response.headers.get("Content-Type") == "image/png"
            assert response.read()[:8] == b"\x89PNG\r\n\x1a\n"
        receipt = _post_form(live.pick_url, {"slot_A": "hil-2026-apc-crossroads-classic"})
    finally:
        live.finish()
    assert live.result.get("picks") == {"A": "hil-2026-apc-crossroads-classic"}
    assert receipt["picks"] == {"A": "hil-2026-apc-crossroads-classic"}


def test_16x9_promise_with_portrait_render_carries_provenance_chip() -> None:
    """R2 (Auditor#1 J-2/D-2 honesty): a guide promising 16:9 whose curated render
    is not 16:9 gets an explicit provenance chip — data-driven (SSOT dimensions +
    PNG IHDR aspect), never a hardcoded card name.

    Decoupled from any specific registry guide: the original blueprint-classic subject
    was removed in the session-09 declutter, so the chip machinery is proven here with a
    committed PORTRAIT fixture (aspect < 1.4) cloned onto a real 16x9 roster entry, plus a
    real-16x9-landscape negative control. This keeps the coverage independent of roster churn."""
    roster = load_picker_roster(include_probes=True)
    template = next(
        e
        for e in roster
        if str(e.get("card_dimensions") or "").strip().lower() == "16x9" and e["thumbnail_ref"]
    )
    chip = "render predates this guide"
    # Positive: a 16x9 promise pointed at the portrait fixture (120x168, aspect 0.71 < 1.4).
    mismatch = {
        **template,
        "name": "synthetic-16x9-portrait",
        "thumbnail_ref": "tests/fixtures/thumbnails/portrait_16x9_mismatch.png",
    }
    # Negative control: the same 16x9 promise keeps its real 16:9 landscape render → NO chip.
    match = {**template, "name": "synthetic-16x9-landscape"}
    html = render_picker_html([mismatch, match], post_url="/pick")
    assert html.count(chip) == 1, "exactly the portrait-render entry must carry the chip"
    for card in html.split("<article")[1:]:
        guide = card.split('data-guide="', 1)[1].split('"', 1)[0]
        assert (chip in card) == (guide == "synthetic-16x9-portrait"), guide


def test_capture_pick_prints_waiting_notice(tmp_path: Path) -> None:
    """R3 (Blind#2): a visible 'waiting' notice before handle_request blocks."""
    roster = load_picker_roster()
    live = _LiveCapture(roster, tmp_path)
    try:
        _post_form(live.pick_url, {"slot_A": "hil-2026-apc-crossroads-classic"})
    finally:
        live.finish()
    assert any(
        "waiting for your pick at http://127.0.0.1:" in line and "Ctrl-C" in line
        for line in live.printed
    ), f"waiting notice missing from {live.printed}"


def test_oversized_post_rejected_413_then_keeps_serving(tmp_path: Path) -> None:
    """R4 (Blind#3): Content-Length is capped; oversized -> 413 and keep serving."""
    roster = load_picker_roster()
    live = _LiveCapture(roster, tmp_path)
    try:
        with pytest.raises(urllib.error.HTTPError) as excinfo:
            _post_form(live.pick_url, {"slot_A": "x" * (70 * 1024)})
        assert excinfo.value.code == 413
        _post_form(live.pick_url, {"slot_A": "hil-2026-apc-crossroads-classic"})
    finally:
        live.finish()
    assert live.result.get("picks") == {"A": "hil-2026-apc-crossroads-classic"}


def test_duplicate_variant_id_in_existing_directive_fails_loud(tmp_path: Path) -> None:
    """R5 (Edge#1): duplicate variant_id rows -> PickerError, never first-match-patch."""
    directive = tmp_path / "d.yaml"
    original = {
        "gamma_settings": [
            {"variant_id": "A", "styleguide": "one"},
            {"variant_id": "a", "styleguide": "two"},  # dup after normalization
        ]
    }
    directive.write_text(yaml.safe_dump(original), encoding="utf-8")
    with pytest.raises(PickerError, match="duplicate"):
        write_pick_to_directive(directive, {"A": "hil-2026-apc-crossroads-classic"})
    assert yaml.safe_load(directive.read_text(encoding="utf-8")) == original


def test_gamma_settings_non_list_fails_loud(tmp_path: Path) -> None:
    """R6 (Edge#2): present-but-non-list gamma_settings -> PickerError, never
    silently discarded/overwritten."""
    directive = tmp_path / "d.yaml"
    original = {"gamma_settings": {"variant_id": "A", "styleguide": "one"}}
    directive.write_text(yaml.safe_dump(original), encoding="utf-8")
    with pytest.raises(PickerError, match="gamma_settings"):
        write_pick_to_directive(directive, {"A": "hil-2026-apc-crossroads-classic"})
    assert yaml.safe_load(directive.read_text(encoding="utf-8")) == original


def test_gamma_settings_non_mapping_entry_fails_loud(tmp_path: Path) -> None:
    """R6 rider: a non-mapping list entry is the same silent-drop class."""
    directive = tmp_path / "d.yaml"
    directive.write_text(yaml.safe_dump({"gamma_settings": ["A"]}), encoding="utf-8")
    with pytest.raises(PickerError, match="gamma_settings"):
        write_pick_to_directive(directive, {"A": "hil-2026-apc-crossroads-classic"})


def test_cli_fallback_a_blank_b_only_single_select(tmp_path: Path) -> None:
    """R7 (Edge#3): post retire-default-variant-pair, B-only is legitimate — the
    CLI fallback supports it symmetrically with the web path."""
    roster = load_picker_roster()
    answers = iter(["", "2"])  # skip Style A, pick only Style B
    picks, receipt = capture_pick(
        roster,
        on_pick=lambda picks: {"picks": picks},
        html_path=tmp_path / "picker.html",
        opener=lambda url: False,
        input_fn=lambda prompt: next(answers),
        print_fn=lambda line: None,
    )
    ordered = [entry["name"] for entry in roster]
    assert picks == {"B": ordered[1]}
    assert receipt["picks"] == picks


def test_cli_fallback_requires_at_least_one_pick(tmp_path: Path) -> None:
    """R7 rider: both slots blank -> re-prompt (mirrors the web 400), never empty."""
    roster = load_picker_roster()
    answers = iter(["", "", "1", ""])  # blank round -> re-prompt -> A picked
    printed: list[str] = []
    picks, _ = capture_pick(
        roster,
        on_pick=lambda picks: {"picks": picks},
        html_path=tmp_path / "picker.html",
        opener=lambda url: False,
        input_fn=lambda prompt: next(answers),
        print_fn=printed.append,
    )
    ordered = [entry["name"] for entry in roster]
    assert picks == {"A": ordered[0]}
    assert any("at least one" in line for line in printed)


def test_web_capture_b_only_pick(tmp_path: Path) -> None:
    """R7 web-path pin: skipping A and picking only B is a valid single-variant
    directive (dispatches exactly one deck downstream)."""
    roster = load_picker_roster()
    live = _LiveCapture(roster, tmp_path)
    try:
        receipt = _post_form(
            live.pick_url, {"slot_A": "", "slot_B": "hil-2026-apc-studio-image-card"}
        )
    finally:
        live.finish()
    assert live.result.get("picks") == {"B": "hil-2026-apc-studio-image-card"}
    assert receipt["picks"] == {"B": "hil-2026-apc-studio-image-card"}


def test_advisory_lock_two_sequential_writers(tmp_path: Path) -> None:
    """R8 (Edge#5): sidecar append + directive read-modify-write take an advisory
    same-host lock (lock file adjacent); two sequential writers both land."""
    directive = tmp_path / "d.yaml"
    events = tmp_path / "picks.jsonl"
    for stamp, guide in (
        ("2026-07-02T03:00:00+00:00", "hil-2026-apc-crossroads-classic"),
        ("2026-07-02T03:01:00+00:00", "hil-2026-apc-crossroads-blueprint"),
    ):
        write_pick_to_directive(directive, {"A": guide})
        append_pick_event(
            {"A": guide}, directive_path=directive, picked_at=stamp, events_path=events
        )
    lines = [ln for ln in events.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 2
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    entries_a = [e for e in loaded["gamma_settings"] if e["variant_id"] == "A"]
    assert entries_a == [
        {"variant_id": "A", "styleguide": "hil-2026-apc-crossroads-blueprint"}
    ]
    # The advisory guarantee is same-host + lock-file-adjacent (documented honest).
    assert (tmp_path / "d.yaml.lock").exists()
    assert (tmp_path / "picks.jsonl.lock").exists()


def test_thumbnail_ref_wrong_extension_or_magic_degrades_to_placeholder(tmp_path: Path) -> None:
    """R10 (Edge#4) helper stays fail-loud, but A-M2 catches at the _render_card
    call site: a wrong extension OR a non-PNG file degrades to the placeholder +
    warning chip instead of 500-ing the page. The ``_png_dimensions`` /
    ``_resolve_thumbnail`` helpers themselves remain loud (see the unit tests)."""
    from app.marcus.orchestrator.styleguide_picker import _resolve_thumbnail

    roster = load_picker_roster()
    jpg = tmp_path / "thumb.jpg"
    jpg.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 25)
    entry = dict(roster[0])
    entry["thumbnail_ref"] = "thumb.jpg"
    # The helper is still loud (write-gate / direct callers rely on it)...
    with pytest.raises(PickerError, match=r"(?i)\.png"):
        _resolve_thumbnail(entry, repo_root=tmp_path)
    # ...but rendering degrades rather than raising.
    html = render_picker_html([entry], post_url="/pick", repo_root=tmp_path)
    assert "no live render" in html and "thumbnail unavailable" in html

    fake_png = tmp_path / "thumb.png"
    fake_png.write_bytes(b"definitely-not-a-png-header-bytes")
    entry2 = dict(roster[0])
    entry2["thumbnail_ref"] = "thumb.png"
    with pytest.raises(PickerError, match="PNG"):
        _resolve_thumbnail(entry2, repo_root=tmp_path)
    html2 = render_picker_html([entry2], post_url="/pick", repo_root=tmp_path)
    assert "no live render" in html2 and "thumbnail unavailable" in html2


def test_empty_roster_error_mentions_include_probes() -> None:
    """R11 (Edge#6): the empty-roster error coaches the probe-only case."""
    with pytest.raises(PickerError, match="include-probes"):
        capture_pick([], on_pick=lambda picks: {}, opener=lambda url: True)


def test_cli_fallback_excludes_probe_guides_by_default(tmp_path: Path) -> None:
    """R14 (Auditor#3): the CLI fallback's numbered roster honors D-3 default-hidden."""
    roster = load_picker_roster()  # default view: probes hidden
    answers = iter(["1", ""])
    printed: list[str] = []
    picks, _ = capture_pick(
        roster,
        on_pick=lambda picks: {"picks": picks},
        html_path=tmp_path / "picker.html",
        opener=lambda url: False,
        input_fn=lambda prompt: next(answers),
        print_fn=printed.append,
    )
    joined = "\n".join(printed)
    for probe in PROBE_GUIDES:
        assert probe not in joined, f"probe {probe} leaked into the CLI roster"
    assert picks["A"] not in PROBE_GUIDES


# ================= 3-seat review remediation (2026-07-03) ====================
# ------------------------------------------------------ R-MAJOR-1 (Murat, atomic)
def test_directive_write_is_crash_atomic_and_byte_identical(tmp_path: Path) -> None:
    """R-MAJOR-1: the directive write goes through a temp sibling + os.replace, and
    the bytes are IDENTICAL to the prior in-place write_text(yaml.safe_dump(...)).

    Byte-identity is the guard the consumer round-trip tests rely on: the atomic
    path must never normalize the YAML output or trailing newline/encoding.
    """
    directive = tmp_path / "directive.yaml"
    write_pick_to_directive(directive, {"A": "hil-2026-apc-crossroads-classic"})
    produced = directive.read_bytes()
    loaded = yaml.safe_load(produced.decode("utf-8"))
    expected = yaml.safe_dump(loaded, sort_keys=False).encode("utf-8")
    assert produced == expected, "atomic write must reproduce the exact safe_dump bytes"
    # No stray temp files are left behind in the directory.
    leftovers = [p.name for p in tmp_path.iterdir() if p.name.endswith(".tmp")]
    assert leftovers == [], f"atomic write leaked temp files: {leftovers}"


# ----------------------------------------------------- A-M1 (Winston, lifecycle)
def test_write_pick_refuses_probe_and_deprecated_names(tmp_path: Path) -> None:
    """A-M1: the lifecycle/visibility invariant is enforced at the MUTATION point —
    a `visibility: probe` or `lifecycle: deprecated` guide can never be bound into
    a production directive, even by a direct caller. Nothing is written on refusal."""
    directive = tmp_path / "d.yaml"
    with pytest.raises(PickerError, match="probe"):
        write_pick_to_directive(directive, {"A": "leg-c-part3-floor-probe"})
    assert not directive.exists(), "a refused probe pick must not write a directive"
    with pytest.raises(PickerError, match="deprecated"):
        write_pick_to_directive(directive, {"A": "videographic-glance-track"})
    assert not directive.exists(), "a refused deprecated pick must not write a directive"


# --------------------------------------------------------- R-4 fail-loud teeth
def test_capture_pick_timeout_expiry_raises(tmp_path: Path) -> None:
    """R-4(a): no pick before the deadline -> PickerError, never a silent hang."""
    roster = load_picker_roster()
    with pytest.raises(PickerError, match="no pick received"):
        capture_pick(
            roster,
            on_pick=lambda picks: {"picks": picks},
            html_path=tmp_path / "picker.html",
            opener=lambda url: True,  # "browser opened"; no client ever POSTs
            print_fn=lambda line: None,
            timeout=0.5,
        )


def test_on_pick_raising_yields_500_and_capture_pick_reraises(tmp_path: Path) -> None:
    """R-4(b): an on_pick exception surfaces as a 500 to the page AND re-raises out
    of capture_pick (fail-loud both directions)."""
    roster = load_picker_roster()
    html_path = tmp_path / "picker.html"
    opened: list[str] = []
    result: dict = {}

    def _boom(picks: dict) -> dict:
        raise RuntimeError("on_pick exploded")

    def _run() -> None:
        try:
            capture_pick(
                roster,
                on_pick=_boom,
                html_path=html_path,
                opener=lambda url: opened.append(url) or True,
                print_fn=lambda line: None,
                timeout=30.0,
            )
        except Exception as exc:  # captured for the assertion below
            result["error"] = exc

    worker = threading.Thread(target=_run)
    worker.start()
    try:
        for _ in range(200):
            if opened and html_path.exists():
                break
            worker.join(0.05)
        pick_url = urllib.parse.urljoin(opened[0], "/pick")
        with pytest.raises(urllib.error.HTTPError) as excinfo:
            _post_form(pick_url, {"slot_A": "hil-2026-apc-crossroads-classic"})
        assert excinfo.value.code == 500
    finally:
        worker.join(timeout=30)
    assert isinstance(result.get("error"), RuntimeError)
    assert "on_pick exploded" in str(result["error"])


def test_unknown_get_path_and_wrong_post_endpoint_are_404(tmp_path: Path) -> None:
    """R-4(c): do_GET 404 for an unknown path/thumbnail; do_POST 404 for the wrong
    endpoint. The server keeps serving and a later valid pick still lands."""
    roster = load_picker_roster()
    live = _LiveCapture(roster, tmp_path)
    try:
        for bad in ("/thumbnails/does-not-exist.png", "/nonsense"):
            with pytest.raises(urllib.error.HTTPError) as gexc:
                urllib.request.urlopen(
                    urllib.parse.urljoin(live.base_url, bad), timeout=10
                )
            assert gexc.value.code == 404, bad
        with pytest.raises(urllib.error.HTTPError) as pexc:
            _post_form(urllib.parse.urljoin(live.base_url, "/wrong"), {"slot_A": "x"})
        assert pexc.value.code == 404
        _post_form(live.pick_url, {"slot_A": "hil-2026-apc-crossroads-classic"})
    finally:
        live.finish()
    assert live.result.get("picks") == {"A": "hil-2026-apc-crossroads-classic"}


def test_png_dimensions_degenerate_ihdr_fails_loud(tmp_path: Path) -> None:
    """R-4(d): _png_dimensions stays fail-loud — a 0x0 IHDR is a LOUD error even
    though the file carries a valid PNG magic + IHDR chunk name."""
    import struct

    from app.marcus.orchestrator.styleguide_picker import _png_dimensions

    degenerate = tmp_path / "zero.png"
    degenerate.write_bytes(
        b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0d" + b"IHDR" + struct.pack(">II", 0, 0)
    )
    with pytest.raises(PickerError, match="degenerate"):
        _png_dimensions(degenerate)


# --------------------------------------------- R-3 (Content-Length guard, Murat)
def test_negative_content_length_rejected_400_before_read(tmp_path: Path) -> None:
    """R-3: a non-numeric/negative Content-Length is a clean 400 BEFORE any
    rfile.read (a negative length reaches rfile.read(-N) which blocks to EOF)."""
    roster = load_picker_roster()
    live = _LiveCapture(roster, tmp_path)
    try:
        request = urllib.request.Request(
            live.pick_url,
            data=b"slot_A=x",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": "-5",
            },
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as excinfo:
            urllib.request.urlopen(request, timeout=10)
        assert excinfo.value.code == 400
        # Server keeps serving: a valid pick still lands.
        _post_form(live.pick_url, {"slot_A": "hil-2026-apc-crossroads-classic"})
    finally:
        live.finish()
    assert live.result.get("picks") == {"A": "hil-2026-apc-crossroads-classic"}


# ---------------------------------------------- live-exemplar link (operator ask)
def test_example_url_renders_new_tab_anchor_and_null_renders_none() -> None:
    """A style with example_url renders a new-tab anchor (target=_blank +
    rel=noopener) to that URL; a style with a null example_url renders no anchor
    (no dead link). The anchor is NOT the whole thumbnail (slot-selection guarded)."""
    roster = load_picker_roster()
    by_name = {e["name"]: e for e in roster}
    with_url = dict(by_name["hil-2026-apc-crossroads-classic"])
    url = with_url["example_url"]
    assert url, "seed guide must carry a live example deck"
    html = render_picker_html([with_url], post_url="/pick")
    assert f'href="{url}"' in html
    assert 'class="example-link"' in html
    assert 'target="_blank"' in html
    assert 'rel="noopener"' in html
    assert "View live example" in html
    # The anchor is a distinct element, NOT wrapping the thumbnail image/placeholder.
    assert "<a class=\"example-link\"" in html

    without_url = dict(by_name["hil-2026-apc-studio-image-card"])
    assert without_url["example_url"] is None
    html2 = render_picker_html([without_url], post_url="/pick")
    # The CSS rule for .example-link is always in the stylesheet; assert the
    # ANCHOR element and its visible text are absent (no dead link).
    assert '<a class="example-link"' not in html2
    assert "View live example" not in html2


def test_sally_a11y_and_usability_render_pins() -> None:
    """Sally U-1/U-3/U-4/U-5: keyboard/a11y, display-name slot bar, surfaced
    pros/cons, instructions + selected-state machinery are present in the page."""
    roster = load_picker_roster()
    html = render_picker_html(roster, post_url="/pick")
    # U-1: every card is keyboard-operable and labelled.
    assert 'tabindex="0"' in html
    assert 'role="button"' in html
    assert "aria-label=" in html
    assert ":focus-visible" in html  # visible focus ring CSS
    assert 'aria-live="polite"' in html  # slot bar + receipt announce
    # U-2: grid selected-state classes exist (distinct from .card.armed).
    assert ".card.slot-a" in html and ".card.slot-b" in html
    assert "'slot-a'" in html or "slot-a" in html  # JS toggles the class
    # U-3: the human display name rides the card for the slot bar text.
    assert "data-display=" in html
    # U-4: pros/cons surfaced on the face + relabelled details summary.
    assert "Use when:" in html and "Avoid when:" in html
    assert "More about this style" in html  # details now holds summary/feels_like
    assert "<summary>narrative</summary>" not in html  # old opaque label gone
    assert 'aria-pressed="false"' in html  # selected state exposed to AT (Sally nit)
    # U-5: instruction line + no silent dead-click hint target.
    assert "one slot is a valid pick" in html
    assert 'id="pick-hint"' in html
