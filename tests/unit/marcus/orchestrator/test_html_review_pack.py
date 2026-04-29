from __future__ import annotations

import re
from pathlib import Path

from app.marcus.orchestrator.html_review_pack import ReviewPackRow, write_review_pack


def _rows(count: int) -> list[ReviewPackRow]:
    return [
        ReviewPackRow(
            slide_index=index,
            slide_label=f"Slide {index + 1}",
            preview=f"Preview {index + 1}",
            output={"variant": f"v{index + 1}"},
        )
        for index in range(count)
    ]


def test_generator_writes_valid_html_for_n_slides(tmp_path: Path) -> None:
    pack = write_review_pack(trial_id="trial-1", gate_id="G2B", rows=_rows(2), runs_root=tmp_path)
    text = pack.read_text(encoding="utf-8")

    assert text.startswith("<!doctype html>")
    assert text.count("<tr data-gate-id=") == 2


def test_form_fields_are_deterministic(tmp_path: Path) -> None:
    pack = write_review_pack(trial_id="trial-1", gate_id="G2B", rows=_rows(1), runs_root=tmp_path)
    text = pack.read_text(encoding="utf-8")

    assert 'id="G2B-slide-0-approve"' in text
    assert 'name="G2B-slide-0-delta_directive"' in text
    assert 'name="G2B-slide-0-output_digest"' in text


def test_data_attributes_are_present(tmp_path: Path) -> None:
    text = write_review_pack(
        trial_id="trial-1", gate_id="G3B", rows=_rows(1), runs_root=tmp_path
    ).read_text(encoding="utf-8")

    assert 'data-gate-id="G3B"' in text
    assert 'data-slide-index="0"' in text


def test_output_digest_is_non_empty_sha256(tmp_path: Path) -> None:
    text = write_review_pack(
        trial_id="trial-1", gate_id="G2B", rows=_rows(1), runs_root=tmp_path
    ).read_text(encoding="utf-8")

    digest = re.search(r'name="G2B-slide-0-output_digest" value="([0-9a-f]{64})"', text)
    assert digest is not None


def test_skeleton_only_style_and_js_bounds(tmp_path: Path) -> None:
    text = write_review_pack(
        trial_id="trial-1", gate_id="G2B", rows=_rows(1), runs_root=tmp_path
    ).read_text(encoding="utf-8")
    style = re.search(r"<style>\n(.*?)\n</style>", text, flags=re.DOTALL)
    script = re.search(r"<script>\n(.*?)\n</script>", text, flags=re.DOTALL)

    assert "stylesheet" not in text
    assert "react" not in text.lower()
    assert "vue" not in text.lower()
    assert style is not None and len(style.group(1).splitlines()) <= 30
    assert script is not None and len(script.group(1).splitlines()) <= 50
