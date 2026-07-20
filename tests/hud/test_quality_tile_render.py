"""Story Q4.3 — HUD ``quality`` tile render (Epic Q4, RED-first pins).

The HUD is a READ-ONLY consumer of the Story Q4.1 ``QualitySection`` shipped on
``operator-surface.json``. It NEVER recomputes quality (QLW-4) — it renders ONLY
the honest fields the section carries. Two mechanisms had to be wired because the
HUD does not auto-render present optional sections:

  * AC1 — ``app.hud.public.build_public_view`` is a POSITIVE allowlist; an
          un-enumerated ``quality`` section is dropped until ``ALLOWED_QUALITY``
          exists. This pins the passthrough.
  * AC2 — a dedicated ``_quality_panel`` render function surfaces Band + top-N
          leaks + trend + ranked_leak_count/coverage_gaps + the scorecard
          staleness stamp on the completed deck.
  * AC3 — zero-lie / fail-soft (QLW-8): ``available=False`` / absent / None /
          malformed / partial → an explicit "unavailable" render, NEVER a
          fabricated band, NEVER silent-absence-reads-green, NEVER a crash.
  * AC4 — QLW-4: the HUD render path does NOT import ``app.quality`` / does not
          recompute (subprocess sys.modules guard + static source scan).
  * AC5 — QLW-12: the honest posture (incl. an OWED/uncalibrated read) renders;
          never a fresh-naive number (the tile carries no ``/100`` at all).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

import pytest

from app.hud.public import ALLOWED_QUALITY, build_public_view
from app.hud.render import render_zones
from app.hud.render.client import POLL_JS
from app.hud.render.page import _quality_panel
from tests.hud import _render_fixtures as fx

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLIENT_PY = _REPO_ROOT / "app" / "hud" / "render" / "client.py"


# --------------------------------------------------------------------------
# Fixtures — a completed projection carrying a quality tile (lenient dict).
# --------------------------------------------------------------------------


def _quality_available() -> dict[str, Any]:
    return {
        "as_of": fx.NOW,
        "available": True,
        "band": "D",
        "ranked_leak_count": 7,
        "top_leaks": [
            "calibration: fresh-naive holdout OWED (uncalibrated)",
            "coverage-honesty: 2 dimensions unmeasured",
            "lane-discipline: 1 cross-lane leak",
        ],
        "coverage_gaps": 2,
        "trend": "flat",
        "scorecard_as_of": "2026-07-19",
    }


def _completed_with_quality(quality: Any) -> dict[str, Any]:
    proj = fx.completed()
    proj["quality"] = quality
    return proj


def _completed_deck(quality: Any) -> str:
    return render_zones(fx.ok_data(_completed_with_quality(quality)))["main-deck"]


# ==========================================================================
# AC1 — allowlist passthrough (previously dropped by the positive allowlist)
# ==========================================================================


def test_quality_section_survives_build_public_view() -> None:
    projection = {
        **fx.completed(),
        "quality": _quality_available(),
    }
    view = build_public_view(projection)
    assert "quality" in view, "quality section dropped by the public allowlist"
    q = view["quality"]
    # Every honest field is copied through (and nothing extra invented).
    assert q["available"] is True
    assert q["band"] == "D"
    assert q["ranked_leak_count"] == 7
    assert q["coverage_gaps"] == 2
    assert q["trend"] == "flat"
    assert q["scorecard_as_of"] == "2026-07-19"
    assert q["top_leaks"][0].startswith("calibration:")
    assert set(q).issubset(set(ALLOWED_QUALITY))


def test_allowlist_quality_enumerates_only_honest_fields() -> None:
    # The tile carries NO /100 score and no secret; the allowlist matches the
    # Q4.1 QualitySection field set exactly.
    assert set(ALLOWED_QUALITY) == {
        "available",
        "band",
        "ranked_leak_count",
        "top_leaks",
        "coverage_gaps",
        "trend",
        "scorecard_as_of",
        "as_of",
    }


# ==========================================================================
# AC2 — the render panel surfaces the honest posture on the completed deck
# ==========================================================================


def test_completed_deck_renders_quality_tile() -> None:
    deck = _completed_deck(_quality_available())
    assert "quality-tile" in deck
    assert "Project quality" in deck
    assert "band D" in deck  # band rendered verbatim (worst-across-dims, per QLW-9)
    assert "flat" in deck  # trend
    assert "ranked leaks" in deck and ">7<" in deck  # ranked_leak_count
    assert "coverage gaps" in deck and ">2<" in deck  # coverage_gaps
    assert "scorecard as of 2026-07-19" in deck  # staleness stamp
    # top leaks surfaced
    assert "calibration: fresh-naive holdout OWED (uncalibrated)" in deck


def test_quality_tile_carries_no_fabricated_percent_score() -> None:
    deck = _completed_deck(_quality_available())
    # The tile is posture-only — no /100 headline anywhere (report.py design).
    # FIX 6: assert the real intent — no "/100" score headline — rather than a
    # bare "100", which false-fails on a legitimate ranked_leak_count==100, a
    # date, or a leak label that happens to contain "100" (matches the adjacent
    # deck-level check).
    assert "/100" not in deck
    tile = deck.split("quality-tile", 1)[1].split("</section>", 1)[0]
    assert "/100" not in tile


def test_quality_tile_no_percent_false_fail_on_legit_100() -> None:
    # FIX 6 (regression pin): a real 100-valued field / a leak label carrying
    # "100" must NOT trip the no-fabricated-score guard. Only "/100" is forbidden.
    quality = _quality_available()
    quality["ranked_leak_count"] = 100
    quality["top_leaks"] = ["coverage-honesty: dimension 100 unmeasured (2026-01-00)"]
    deck = _completed_deck(quality)
    tile = deck.split("quality-tile", 1)[1].split("</section>", 1)[0]
    assert "100" in tile  # the legitimate count / label survives
    assert "/100" not in tile  # ... but still no fabricated /100 headline


# ==========================================================================
# AC3 — zero-lie / fail-soft (QLW-8): unavailable + malformed never lie/crash
# ==========================================================================


def test_available_false_renders_explicit_unavailable() -> None:
    deck = _completed_deck(
        {"as_of": fx.NOW, "available": False, "top_leaks": []}
    )
    assert "quality-tile" in deck
    assert "unavailable" in deck.lower()
    # NEVER a fabricated band / green posture.
    assert "band A" not in deck
    assert "band D" not in deck


def test_absent_quality_section_renders_explicit_unavailable() -> None:
    proj = fx.completed()
    proj.pop("quality", None)
    deck = render_zones(fx.ok_data(proj))["main-deck"]
    # Silent-absence-reads-green is forbidden: the tile states absence honestly.
    assert "quality-tile" in deck
    assert "unavailable" in deck.lower()


def test_malformed_quality_section_never_crashes() -> None:
    for bad in (
        None,
        "garbage-string",
        ["not", "a", "mapping"],
        123,
        {"as_of": fx.NOW, "available": True},  # partial: band missing
        {"available": True, "band": None, "ranked_leak_count": 5},  # None band
        {"available": "yes", "band": "D"},  # truthy-but-nonbool available
    ):
        deck = _completed_deck(bad)
        assert "quality-tile" in deck  # renders SOMETHING, honestly, no crash


def test_quality_panel_unit_unavailable_and_available() -> None:
    # Direct unit exercise of the pure panel function.
    unavail = _quality_panel({"proj": {"quality": {"available": False}}, "now": fx.NOW})
    assert "unavailable" in unavail.lower()
    assert "band" not in unavail.replace("aria-label", "")  # no fabricated band row

    avail = _quality_panel(
        {"proj": {"quality": _quality_available()}, "now": fx.NOW}
    )
    assert "band D" in avail
    assert "flat" in avail


# ==========================================================================
# AC4 — QLW-4: the HUD render path does NOT import app.quality / recompute
# ==========================================================================


def test_hud_render_path_does_not_import_app_quality_subprocess() -> None:
    """Import ONLY the HUD render surface in a fresh interpreter; assert that
    ``app.quality`` was never pulled in (the HUD renders, it never recomputes)."""
    script = textwrap.dedent(
        """
        import sys
        import app.hud.public  # noqa: F401
        import app.hud.render.page  # noqa: F401
        import app.hud.render  # noqa: F401
        leaked = [m for m in sys.modules if m == "app.quality" or m.startswith("app.quality.")]
        if leaked:
            print("LEAKED:" + ",".join(sorted(leaked)))
            sys.exit(1)
        print("CLEAN")
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"HUD render path imported app.quality.\n"
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    assert "CLEAN" in result.stdout


def test_hud_render_source_names_no_app_quality_import() -> None:
    """Static teeth: neither the allowlist nor the render module imports app.quality."""
    for rel in ("app/hud/public.py", "app/hud/render/page.py"):
        src = (_REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "import app.quality" not in src, rel
        assert "from app.quality" not in src, rel


# ==========================================================================
# AC5 — QLW-12: calibration honesty renders; never a fresh-naive number
# ==========================================================================


def test_uncalibrated_posture_renders_honestly_not_a_naive_number() -> None:
    quality = _quality_available()
    quality["trend"] = "uncalibrated"
    quality["top_leaks"] = [
        "calibration: fresh-naive holdout OWED — posture uncalibrated",
    ]
    deck = _completed_deck(quality)
    assert "uncalibrated" in deck
    assert "calibration: fresh-naive holdout OWED" in deck
    # Honest posture, no invented precision.
    assert "/100" not in deck


# ==========================================================================
# FIX 2 — top_leaks must be type-defensive (Edge HIGH + Blind MED)
# ==========================================================================


def test_top_leaks_truthy_non_iterable_does_not_crash() -> None:
    # A truthy non-iterable (``top_leaks: 5``) must NOT ``TypeError`` and take
    # the whole completed render down — it degrades to no leak rows.
    deck = _completed_deck(
        {"as_of": fx.NOW, "available": True, "band": "C", "top_leaks": 5}
    )
    assert "quality-tile" in deck
    assert "top leaks" not in deck  # non-list → no leak block, no crash


def test_top_leaks_bare_string_is_not_char_iterated() -> None:
    # A bare string must NOT be char-iterated into 16 single-character rows.
    label = "calibration OWED"
    deck = _completed_deck(
        {"as_of": fx.NOW, "available": True, "band": "C", "top_leaks": label}
    )
    assert "quality-tile" in deck
    # No per-character artifact rows (each char would be its own <div class="artifact">).
    assert deck.count('<div class="artifact">') < len(label)
    # And the string was treated as "not a list of leaks" → no leak block at all.
    assert "top leaks" not in deck


def test_top_leaks_drops_none_entries() -> None:
    # None entries are dropped (the LOW "None-label" finding); real labels survive.
    deck = _completed_deck(
        {
            "as_of": fx.NOW,
            "available": True,
            "band": "C",
            "top_leaks": [None, "real leak", None],
        }
    )
    assert "real leak" in deck
    # A dropped None never renders as the literal ``None`` label row.
    leaks_region = deck.split("top leaks", 1)[1] if "top leaks" in deck else ""
    assert ">None<" not in leaks_region


# ==========================================================================
# FIX 3 — the ``available`` gate must be strict ``is True``
# ==========================================================================


def test_available_string_false_renders_unavailable() -> None:
    # ``available="false"`` is a truthy string — it must NOT read as available.
    deck = _completed_deck({"as_of": fx.NOW, "available": "false", "band": "A"})
    assert "quality-tile" in deck
    assert "unavailable" in deck.lower()
    assert "band A" not in deck  # never a fabricated available posture


def test_available_truthy_int_renders_unavailable() -> None:
    # ``available=1`` is truthy but not the boolean ``True`` → unavailable.
    deck = _completed_deck({"as_of": fx.NOW, "available": 1, "band": "A"})
    assert "quality-tile" in deck
    assert "unavailable" in deck.lower()
    assert "band A" not in deck


def test_available_yes_renders_unavailable_not_available() -> None:
    # FIX 3: a non-True value ("yes") is NOT a valid available flag — the tile
    # must render the honest UNAVAILABLE state, never band D.
    deck = _completed_deck({"as_of": fx.NOW, "available": "yes", "band": "D"})
    assert "quality-tile" in deck
    assert "unavailable" in deck.lower()
    assert "band D" not in deck


# ==========================================================================
# FIX 4 — band D (worst) must be visually distinct from C; QLW-9 at the HUD
# ==========================================================================


def _band_deck(band: Any) -> str:
    return _completed_deck({"as_of": fx.NOW, "available": True, "band": band})


def test_band_d_emits_critical_class_distinct_from_c() -> None:
    d_deck = _band_deck("D")
    c_deck = _band_deck("C")
    # Band D (worst committed band) is a RED/critical chip, NOT the same amber
    # ``warn`` as C.
    assert '<span class="chip crit"><span class="dot"></span> band D' in d_deck
    assert '<span class="chip warn"><span class="dot"></span> band D' not in d_deck
    # Band C stays amber ``warn`` — the two are visually distinct.
    assert '<span class="chip warn"><span class="dot"></span> band C' in c_deck
    assert "chip crit" not in c_deck.split("quality-tile", 1)[1].split("</section>", 1)[0]


def test_unknown_band_never_emits_green_on_class() -> None:
    # QLW-9: a garbage / unknown band must NEVER read as the green ``on`` class
    # (a corrupt band can never look cleaner than a committed red).
    for garbage in ("z", "??", "unknown", "banana", "1"):
        deck = _band_deck(garbage)
        tile = deck.split("quality-tile", 1)[1].split("</section>", 1)[0]
        # the band chip carries the NEUTRAL (empty) class, never ``on``.
        assert 'chip on"><span class="dot"></span> band' not in tile
        assert 'chip on "><span class="dot"></span> band' not in tile


def test_critical_class_uses_red_not_green() -> None:
    # The critical chip must be visually red — never green (QLW-9 zero-lie).
    from app.hud.render.styles import CSS

    assert ".chip.crit" in CSS
    # the crit rule references the warning red, never a nominal green.
    crit_rule = CSS.split(".chip.crit", 1)[1].split("}", 1)[0]
    assert "#EF4444" in crit_rule
    assert "#22C55E" not in crit_rule and "#166534" not in crit_rule


# ==========================================================================
# FIX 5 — CSS for ``.quality-tile`` and ``.quality-tile.unavailable``
# ==========================================================================


def test_styles_define_quality_tile_rules() -> None:
    from app.hud.render.styles import CSS

    assert ".quality-tile" in CSS, "no container rule for the quality tile"
    assert ".quality-tile.unavailable" in CSS, "no emphasis rule for the honest unavailable state"


# ==========================================================================
# FIX 1 — client-side (poll) renderer parity: the tile must survive a re-render
# ==========================================================================


def test_client_source_wires_quality_panel() -> None:
    # Always-on string pin: the client poll renderer defines a quality panel and
    # the ``completed`` land-brief branch invokes it, so a poll-driven re-render
    # keeps the tile (server-render parity — the operator watching live sees it).
    assert "qualityPanel" in POLL_JS
    assert "quality-tile" in POLL_JS
    # the completed branch (land-brief) must concatenate the quality panel.
    land = POLL_JS.split("land-brief", 1)[1]
    assert "qualityPanel(d)" in land


#: The auto-start tail of the poll IIFE — stripped in the harness so no
#: ``fetch``/``setInterval`` fires and ``context`` can be returned for testing.
_AUTOSTART = "  poll();\n  setInterval(poll, POLL_MS);\n})();"


def _run_client_context(quality: Any, node: str) -> str:
    """Execute the REAL client poll JS ``context()`` for a completed projection
    carrying ``quality`` and return the produced HTML (Node harness).

    The transform lifts the byte-identical ``POLL_JS`` constant, replaces its
    auto-start tail with a ``return {context, qualityPanel}`` so the IIFE hands
    back its inner functions, then drives ``context`` on a completed projection.
    """
    import json
    import tempfile

    assert _AUTOSTART in POLL_JS, "poll IIFE auto-start tail changed — update harness"
    body = POLL_JS.replace(
        _AUTOSTART,
        "  return { context: context, qualityPanel: qualityPanel };\n})();",
    ).strip()
    module_js = (
        "const __api = " + body + "\n"
        "const q = JSON.parse(process.argv[2]);\n"
        "const d = { envelope: { status: 'completed',"
        " completed_at: '2026-07-11T14:02:11+00:00' },"
        " deliverables: { components: { deck: true }, export_paths: [],"
        " total_cost_usd: 0.31 }, quality: q };\n"
        "process.stdout.write(__api.context(d, '2026-07-11T12:00:00+00:00'));\n"
    )
    with tempfile.NamedTemporaryFile(
        "w", suffix=".js", delete=False, encoding="utf-8"
    ) as fh:
        fh.write(module_js)
        harness_path = fh.name
    try:
        result = subprocess.run(
            [node, harness_path, json.dumps(quality)],
            capture_output=True,
            text=True,
        )
    finally:
        Path(harness_path).unlink(missing_ok=True)
    assert result.returncode == 0, (
        f"client harness crashed.\nstdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    return result.stdout


def test_client_completed_render_includes_quality_tile() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not available — string-parity pin covers this env")
    html = _run_client_context(
        {
            "available": True,
            "band": "D",
            "ranked_leak_count": 7,
            "top_leaks": ["calibration: OWED (uncalibrated)"],
            "coverage_gaps": 2,
            "trend": "flat",
            "scorecard_as_of": "2026-07-19",
        },
        node,
    )
    assert "quality-tile" in html
    assert "Project quality" in html
    assert "band D" in html
    assert "calibration: OWED (uncalibrated)" in html
    assert "flat" in html
    # zero-lie parity: band D is critical/red, never the same amber as C.
    assert '<span class="chip crit"><span class="dot"></span> band D' in html


def test_client_completed_render_unavailable_and_failsoft() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not available — string-parity pin covers this env")
    # available=False → explicit unavailable, never green.
    html = _run_client_context({"available": False}, node)
    assert "quality-tile" in html
    assert "unavailable" in html.lower()
    # truthy-but-not-True → unavailable (strict-is-True parity with the server).
    html2 = _run_client_context({"available": "yes", "band": "A"}, node)
    assert "unavailable" in html2.lower()
    assert "band A" not in html2
    # garbage band never green; truthy non-iterable top_leaks never crashes.
    html3 = _run_client_context(
        {"available": True, "band": "banana", "top_leaks": 5}, node
    )
    assert "quality-tile" in html3
    assert 'chip on"><span class="dot"></span> band' not in html3
