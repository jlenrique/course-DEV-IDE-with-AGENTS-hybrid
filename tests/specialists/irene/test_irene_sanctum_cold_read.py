"""AC-F — Sanctum cold-read at `_plan` node + reference-name shape (Story 2a.2).

Two tests per spec AC-F pin (MF7-augmented):
1. Empty-sanctum digest is deterministic across two reads (same string).
2. Non-empty sanctum produces sorted-by-as_posix listing in stable order
   (Murat MF3 cross-platform binding).

Empty-sanctum is the activation-baseline case for 2a.2 (D2 SYNTHESIS verdict).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from app.specialists.irene.graph import _read_sanctum_digest


def test_empty_sanctum_digest_is_deterministic_empty_string(tmp_path: Path) -> None:
    """Empty sanctum dir → empty string (sha256 of "" is the deterministic hash)."""
    digest_a = _read_sanctum_digest(sanctum_dir=tmp_path)
    digest_b = _read_sanctum_digest(sanctum_dir=tmp_path)
    assert digest_a == ""
    assert digest_b == ""
    # Empty-string sha256 is the deterministic empty-fingerprint constant.
    assert (
        hashlib.sha256(digest_a.encode("utf-8")).hexdigest()
        == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_nonempty_sanctum_sorted_by_as_posix(tmp_path: Path) -> None:
    """Sanctum files are listed in sorted order by their POSIX-form relative path.

    Cross-platform stability binding (Murat MF3): without explicit
    `key=lambda p: p.as_posix()`, Path sort can differ between Windows
    backslash vs POSIX slash separators.
    """
    # Create three files; file naming chosen so sort order matters
    # ("a-b.txt" sorts BEFORE "a/b.txt" on POSIX vs after on Windows).
    (tmp_path / "alpha.md").write_text("first content", encoding="utf-8")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "nested.md").write_text("nested content", encoding="utf-8")
    (tmp_path / "zeta.md").write_text("last content", encoding="utf-8")
    digest = _read_sanctum_digest(sanctum_dir=tmp_path)
    lines = digest.split("\n")
    # Expected POSIX-sorted order: alpha.md, subdir/nested.md, zeta.md
    rel_paths = [line.split("\t", 1)[0] for line in lines]
    assert rel_paths == ["alpha.md", "subdir/nested.md", "zeta.md"]
    # Each line carries the sha256 of file bytes (64 hex chars after \t).
    for line in lines:
        rel, sha = line.split("\t", 1)
        assert len(sha) == 64
        assert all(c in "0123456789abcdef" for c in sha)
