"""Headless-browser proof of the picker page interaction (A1/A2, RED-first).

Playwright-gated: if playwright (or a working chromium) is unavailable the whole
module SKIPS with a clear marker — no new heavy dependency is added by this arc.
The Python-twin + node parity tests in ``test_picker_html_emitter.py`` still cover
the encoder tooth when this module skips.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.marcus.orchestrator.picker_html_emitter import (
    build_selection_code,
    render_picker_static_html,
)

pytest.importorskip(
    "playwright.sync_api", reason="playwright not installed; headless proof skipped"
)

from playwright.sync_api import sync_playwright  # noqa: E402

RUN_TAG = "abc12345"


def _roster() -> list[dict]:
    def _entry(name: str, display: str, lifecycle: str = "permanent") -> dict:
        return {
            "name": name,
            "display_name": display,
            "distinguishing": "d",
            "narrative": {},
            "probe": False,
            "lifecycle": lifecycle,
            "card_dimensions": "",
            "thumbnail_ref": None,
            "example_url": None,
            "last_used": None,
        }

    return [_entry("alpha-style", "Alpha"), _entry("beta-style", "Beta")]


@pytest.fixture(scope="module")
def _browser():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            yield browser
            browser.close()
    except Exception as exc:  # pragma: no cover - environment gate
        pytest.skip(f"chromium unavailable for headless proof: {exc}")


def _load(page, tmp_path: Path) -> None:
    html = render_picker_static_html(_roster(), run_tag=RUN_TAG)
    page_file = tmp_path / "index.html"
    page_file.write_text(html, encoding="utf-8")
    page.goto(page_file.as_uri())


def test_headless_copy_button_disabled_until_pick(_browser, tmp_path: Path) -> None:
    page = _browser.new_page()
    try:
        _load(page, tmp_path)
        copy = page.locator("#copy-code")
        assert copy.get_attribute("aria-disabled") == "true"
        assert copy.is_disabled()
    finally:
        page.close()


def test_headless_single_version_pick_builds_code(_browser, tmp_path: Path) -> None:
    page = _browser.new_page()
    try:
        _load(page, tmp_path)
        page.locator('.card[data-guide="alpha-style"]').click()
        code_val = page.locator("#selection-code").input_value()
        assert code_val == build_selection_code(RUN_TAG, {"A": "alpha-style"})
        assert not page.locator("#copy-code").is_disabled()
    finally:
        page.close()


def test_headless_two_version_pick_auto_flips_and_builds_ab(_browser, tmp_path: Path) -> None:
    page = _browser.new_page()
    try:
        _load(page, tmp_path)
        page.locator('.card[data-guide="alpha-style"]').click()
        page.locator('.card[data-guide="beta-style"]').click()
        code_val = page.locator("#selection-code").input_value()
        assert code_val == build_selection_code(
            RUN_TAG, {"A": "alpha-style", "B": "beta-style"}
        )
    finally:
        page.close()


def test_headless_two_versions_one_style_blocks_copy_then_unblocks(
    _browser, tmp_path: Path
) -> None:
    """SOP-204: '2 versions' + only slot A must BLOCK copy + warn; filling B unblocks."""
    page = _browser.new_page()
    try:
        _load(page, tmp_path)
        # choose 2 versions FIRST, then pick a single style
        page.locator('input[name="version-count"][value="2"]').check()
        page.locator('.card[data-guide="alpha-style"]').click()
        copy = page.locator("#copy-code")
        assert copy.is_disabled(), "copy must be blocked while 2 versions has only slot A"
        why = page.locator("#copy-why").text_content() or ""
        assert "2 versions" in why.lower()
        assert page.locator("#selection-code").input_value() == ""
        # now fill slot B -> copy enabled, emits the full A/B code
        page.locator('.card[data-guide="beta-style"]').click()
        assert not copy.is_disabled()
        assert page.locator("#selection-code").input_value() == build_selection_code(
            RUN_TAG, {"A": "alpha-style", "B": "beta-style"}
        )
    finally:
        page.close()
