"""String-level tests for the Storyboard-A chooser HTML emitter (no browser)."""

from __future__ import annotations

from app.gates.section_07c.chooser_html_emitter import render_chooser_html


def _fixture() -> list[dict]:
    return [
        {
            "slide_id": "intro",
            "slide_index": 0,
            "variants": [
                {"variant": "A", "image_url": "https://cdn.example/intro-A.png"},
                {"variant": "B", "image_url": "https://cdn.example/intro-B.png"},
            ],
        },
        {
            "slide_id": "outro",
            "slide_index": 1,
            "variants": [
                {"variant": "A", "image_url": "https://cdn.example/outro-A.png"},
                {"variant": "B", "image_url": "https://cdn.example/outro-B.png"},
            ],
        },
    ]


def test_returns_complete_html_document() -> None:
    html = render_chooser_html(_fixture(), run_tag="trial42")
    assert html.lstrip().lower().startswith("<!doctype html>")
    assert "</html>" in html


def test_no_external_dependencies() -> None:
    html = render_chooser_html(_fixture(), run_tag="trial42")
    # Inline-only: no external <link href> stylesheets or <script src>.
    assert "<link" not in html.lower()
    assert 'src="http' not in html.lower() or "<img" in html  # imgs allowed, scripts not
    assert "<script src" not in html.lower()


def test_variant_cards_present_per_slide() -> None:
    html = render_chooser_html(_fixture(), run_tag="trial42")
    for slide_index in (0, 1):
        for variant in ("A", "B"):
            sel = f'class="variant-card" data-slide="{slide_index}" data-variant="{variant}"'
            assert sel in html, f"missing card selector attrs for {slide_index}/{variant}"


def test_variant_images_present() -> None:
    html = render_chooser_html(_fixture(), run_tag="trial42")
    assert 'src="https://cdn.example/intro-A.png"' in html
    assert 'src="https://cdn.example/outro-B.png"' in html


def test_status_chip_per_slide() -> None:
    html = render_chooser_html(_fixture(), run_tag="trial42")
    assert '<span class="status-chip" data-slide="0"' in html
    assert '<span class="status-chip" data-slide="1"' in html
    assert "Not chosen yet" in html


def test_row_header_text() -> None:
    html = render_chooser_html(_fixture(), run_tag="trial42")
    assert "Slide 0 of 2 — intro" in html
    assert "Slide 1 of 2 — outro" in html


def test_sticky_bar_and_copy_button() -> None:
    html = render_chooser_html(_fixture(), run_tag="trial42")
    assert 'id="picked-count"' in html
    assert "of 2" in html
    assert '<button id="copy-selections"' in html
    assert "disabled" in html


def test_selection_code_element_present() -> None:
    html = render_chooser_html(_fixture(), run_tag="trial42")
    assert '<code id="selection-code"' in html


def test_js_builds_run_tag_code_prefix() -> None:
    html = render_chooser_html(_fixture(), run_tag="trial42")
    # The JS must build a code with the SBA-{run_tag}- prefix.
    assert "SBA-trial42-" in html


def test_run_tag_is_escaped_into_js_safely() -> None:
    # A run_tag with HTML-special chars must not break the document.
    html = render_chooser_html(_fixture(), run_tag="ab<&>cd")
    assert "<!doctype html>" in html.lower()
    # The raw unescaped sequence must not appear verbatim in markup.
    assert "ab<&>cd" not in html
