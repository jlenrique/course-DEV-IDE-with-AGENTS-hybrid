from __future__ import annotations

from app.marcus.cli.trial import _utf8_safe_print


def test_utf8_safe_print_round_trips_nnbsp_with_capsys(capsys):
    _utf8_safe_print("operator review contains U+202F: left\u202fright")

    captured = capsys.readouterr()
    assert "left\u202fright" in captured.out
    assert captured.out.endswith("\n")
