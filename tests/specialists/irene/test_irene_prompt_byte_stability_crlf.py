"""Murat MF3 cross-platform binding — CRLF vs LF reference files yield byte-identical prompts.

Path.read_text(encoding="utf-8") with default newline=None normalizes CRLF→LF
on read regardless of on-disk newline form. This test injects a CRLF reference
fixture + compares against an LF baseline to confirm cross-platform stability.
"""

from __future__ import annotations

from pathlib import Path

from app.specialists.irene.graph import _read_pass_2_references


def test_crlf_reference_file_yields_lf_normalized_output(tmp_path: Path) -> None:
    """CRLF on disk → LF in read text → byte-identical to LF baseline."""
    refs_dir_lf = tmp_path / "lf"
    refs_dir_crlf = tmp_path / "crlf"
    refs_dir_lf.mkdir()
    refs_dir_crlf.mkdir()
    body = "Line 1\nLine 2\nLine 3\n"
    body_crlf = body.replace("\n", "\r\n")
    # Two refs in the fixed-order tuple — using a 2-name override to stay scoped.
    name_a = "pass-2-procedure.md"
    name_b = "pass-2-authoring-template.md"
    (refs_dir_lf / name_a).write_text(body, encoding="utf-8", newline="")
    (refs_dir_lf / name_b).write_text(body, encoding="utf-8", newline="")
    # Write CRLF bytes by bypassing universal-newlines translation:
    (refs_dir_crlf / name_a).write_bytes(body_crlf.encode("utf-8"))
    (refs_dir_crlf / name_b).write_bytes(body_crlf.encode("utf-8"))
    out_lf = _read_pass_2_references(
        references_dir=refs_dir_lf, names=(name_a, name_b)
    )
    out_crlf = _read_pass_2_references(
        references_dir=refs_dir_crlf, names=(name_a, name_b)
    )
    assert out_lf == out_crlf
    assert "\r\n" not in out_lf  # LF normalization confirmed.


def test_missing_reference_file_emits_deterministic_placeholder(tmp_path: Path) -> None:
    """Missing references emit `<reference-missing: NAME>` deterministically."""
    out = _read_pass_2_references(
        references_dir=tmp_path, names=("does-not-exist.md",)
    )
    assert "<reference-missing: does-not-exist.md>" in out
    out_again = _read_pass_2_references(
        references_dir=tmp_path, names=("does-not-exist.md",)
    )
    assert out == out_again
