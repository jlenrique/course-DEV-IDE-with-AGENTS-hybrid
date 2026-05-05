from __future__ import annotations

import json

from app.marcus.utils.cp1252_fixture_compare import (
    compare_fixture_bytes,
    main,
)


def test_compare_fixture_bytes_accepts_equal_utf8_bytes(tmp_path):
    expected = tmp_path / "expected.yaml"
    actual = tmp_path / "actual.yaml"
    text = "description: screenshot margin\u202fmarker\n"
    expected.write_bytes(text.encode("utf-8"))
    actual.write_bytes(text.encode("utf-8"))

    verdict = compare_fixture_bytes(expected, actual)

    assert verdict.equivalent is True
    assert verdict.byte_count_a == verdict.byte_count_b
    assert verdict.first_divergence_offset is None
    assert verdict.divergence_context == ""


def test_compare_fixture_bytes_detects_cp1252_reencoded_drift(tmp_path):
    expected = tmp_path / "expected.yaml"
    actual = tmp_path / "actual.yaml"
    text = "description: quoted \u201creading\u201d with dash \u2014\n"
    expected.write_bytes(text.encode("utf-8"))
    actual.write_bytes(text.encode("cp1252"))

    verdict = compare_fixture_bytes(expected, actual)

    assert verdict.equivalent is False
    assert verdict.first_divergence_offset is not None
    assert "\ufffd" in verdict.divergence_context


def test_compare_fixture_bytes_normalizes_crlf_for_comparison_only(tmp_path):
    expected = tmp_path / "expected.yaml"
    actual = tmp_path / "actual.yaml"
    expected.write_bytes(b"run_id: trial\nsources:\n")
    actual.write_bytes(b"run_id: trial\r\nsources:\r\n")

    verdict = compare_fixture_bytes(expected, actual)

    assert verdict.equivalent is True
    assert verdict.byte_count_a != verdict.byte_count_b
    assert verdict.first_divergence_offset is None


def test_compare_fixture_bytes_preserves_nnbsp_utf8_round_trip(tmp_path):
    expected = tmp_path / "expected.yaml"
    actual = tmp_path / "actual.yaml"
    text = "locator: macos screenshot\u202fnote.png\n"
    expected.write_bytes(text.encode("utf-8"))
    actual.write_bytes(text.encode("utf-8"))

    verdict = compare_fixture_bytes(expected, actual)

    assert verdict.equivalent is True
    assert b"\xe2\x80\xaf" in actual.read_bytes()


def test_cli_reports_json_verdict_and_exit_code(tmp_path, capsys):
    expected = tmp_path / "expected.yaml"
    actual = tmp_path / "actual.yaml"
    expected.write_text("name: caf\u00e9\n", encoding="utf-8")
    actual.write_text("name: cafe\n", encoding="utf-8")

    exit_code = main([expected.as_posix(), actual.as_posix()])

    captured = capsys.readouterr()
    verdict = json.loads(captured.out)
    assert exit_code == 1
    assert verdict["equivalent"] is False
    assert verdict["first_divergence_offset"] is not None
