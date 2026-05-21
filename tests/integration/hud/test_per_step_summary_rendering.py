from __future__ import annotations

from pathlib import Path

import yaml

from scripts.utilities import run_hud as hud


def _bundle(tmp_path: Path) -> Path:
    b = tmp_path / "bundle"
    b.mkdir()
    (b / "run-constants.yaml").write_text(
        yaml.safe_dump({"RUN_ID": "HUD-RUN", "EXPERIENCE_PROFILE": "visual-led"}),
        encoding="utf-8",
    )
    (b / "operator-directives.md").write_text("focus_directives:\n- test\n", encoding="utf-8")
    gates = b / "gates"
    gates.mkdir()
    (gates / "gate-04-result.yaml").write_text(
        yaml.safe_dump(
            {
                "step_id": "04",
                "result": "fail",
                "summary": "Needs remediation",
                "blockers": ["missing packet"],
            }
        ),
        encoding="utf-8",
    )
    return b


def test_render_includes_per_step_details_blocks(tmp_path: Path) -> None:
    data = hud.collect_hud_data(bundle_dir=_bundle(tmp_path))
    html = hud.render_html(data)

    assert 'class="step-content-summary"' in html
    assert 'id="step-summary-02A"' in html
    assert "Artifact source" in html
    assert "Freshness" in html
    assert "operator-directives.md" in html


def test_current_and_blocker_steps_open_by_default(tmp_path: Path) -> None:
    data = hud.collect_hud_data(bundle_dir=_bundle(tmp_path))
    html = hud.render_html(data)

    assert (
        'id="step-summary-04" class="step-content-summary" '
        'data-step-summary-id="step-summary-04" data-auto-open="urgent" open'
    ) in html
    assert (
        'id="step-summary-02A" class="step-content-summary" '
        'data-step-summary-id="step-summary-02A">'
    ) in html


def test_session_storage_uses_stable_step_summary_ids(tmp_path: Path) -> None:
    data = hud.collect_hud_data(bundle_dir=_bundle(tmp_path))
    html = hud.render_html(data)

    assert "data-step-summary-id" in html
    assert "var key = el.getAttribute('data-step-summary-id') || el.id || String(i);" in html
    assert "sessionStorage.setItem('hud_details'" in html
    assert "try {" in html
    assert "Ignoring corrupt hud_details sessionStorage" in html
    assert "data-auto-open') === 'urgent'" in html


def test_html_escapes_windows_paths_in_summary(tmp_path: Path) -> None:
    b = _bundle(tmp_path)
    (b / "preflight-results.json").write_text('{"C:\\\\temp\\\\a&b":"value"}', encoding="utf-8")
    data = hud.collect_hud_data(bundle_dir=b)
    html = hud.render_html(data)

    assert "C:\\temp\\a&b" not in html
    assert "C:\\temp\\a&amp;b" in html
    assert "operator-directives.md" in html
