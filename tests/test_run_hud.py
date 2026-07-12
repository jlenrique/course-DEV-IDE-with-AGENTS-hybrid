"""Retirement smoke test for the legacy ``run_hud`` HUD generator.

Story 35.8 retired the legacy static-HTML HUD generator (AD-8 / AD-12). The
1466-line generator, its ``hud_data_sources`` data layer, and the silent
wrong-run coordination.db fallback are deleted; ``run_hud`` is now a
deprecation stub. This test pins the two things that survive the retirement:

1. the deprecation CLI exits non-zero and points the operator at the new HUD
   (``app.hud.server`` / ``trial hud``); and
2. ``PIPELINE_STEPS`` — the manifest-derived import surface still consumed by
   ``check_pipeline_manifest_lockstep.py`` and the lockstep pins — remains
   exposed and manifest-shaped.

The former panel/rendering/reader-injection tests (and the two 35.0
``retired-by-35.8`` skips) retire with the generator they exercised.
"""

from __future__ import annotations

import pytest

from scripts.utilities import run_hud as hud


def test_run_hud_cli_is_a_deprecation_stub(capsys: pytest.CaptureFixture[str]) -> None:
    """``main()`` returns non-zero and points at the new HUD surface."""
    exit_code = hud.main([])

    assert exit_code != 0
    assert exit_code == hud.DEPRECATION_EXIT_CODE

    err = capsys.readouterr().err
    assert "RETIRED" in err
    assert "35.8" in err
    # The pointer names the replacement HUD surfaces the operator should use.
    assert "app.hud.server" in err
    assert "trial hud" in err


def test_pipeline_steps_import_surface_survives() -> None:
    """``PIPELINE_STEPS`` stays exposed and manifest-shaped for the L1 check."""
    steps = hud.PIPELINE_STEPS

    assert isinstance(steps, list)
    assert steps, "manifest-derived PIPELINE_STEPS must be non-empty"
    for step in steps:
        assert {"id", "name", "gate"} <= step.keys()


def test_legacy_generator_surface_is_gone() -> None:
    """The deleted HTML/reader surface must not silently reappear."""
    for removed in ("collect_hud_data", "render_html", "_query_active_run_id"):
        assert not hasattr(hud, removed), f"retired symbol {removed!r} reappeared"
