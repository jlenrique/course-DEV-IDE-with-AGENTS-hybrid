from __future__ import annotations

import pytest

from app.marcus.cli.trial import _confirm_or_edit_directive


@pytest.mark.parametrize(
    "unicode_marker",
    [
        "\u202f",
        "\u00a0",
        "\u2014",
        "\u2018",
        "\u2019",
        "\u201c",
        "\u201d",
    ],
)
def test_g0_default_print_fn_handles_cp1252_hostile_unicode(
    tmp_path,
    monkeypatch,
    capsys,
    unicode_marker,
):
    monkeypatch.delenv("PYTHONIOENCODING", raising=False)
    directive_path = tmp_path / "directive.yaml"
    directive_text = f"run_id: trial\nsources:\n- locator: left{unicode_marker}right\n"
    directive_path.write_text(directive_text, encoding="utf-8")

    verdict = _confirm_or_edit_directive(
        directive_path=directive_path,
        auto_confirm_directive=False,
        input_fn=lambda _prompt: "s",
        edit_fn=lambda _path: None,
        isatty_fn=lambda: True,
    )

    captured = capsys.readouterr()
    assert verdict == "saved-only"
    assert f"left{unicode_marker}right" in captured.out
