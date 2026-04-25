from __future__ import annotations

import hashlib
from pathlib import Path

from app.specialists.kira.graph import _read_sanctum_digest


def test_kira_empty_sanctum_digest_is_deterministic(tmp_path: Path) -> None:
    digest_a = _read_sanctum_digest(sanctum_dir=tmp_path)
    digest_b = _read_sanctum_digest(sanctum_dir=tmp_path)
    assert digest_a == ""
    assert digest_b == ""
    assert (
        hashlib.sha256(digest_a.encode("utf-8")).hexdigest()
        == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_kira_nonempty_sanctum_sorted_by_as_posix(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("a", encoding="utf-8")
    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "b.md").write_text("b", encoding="utf-8")
    digest = _read_sanctum_digest(sanctum_dir=tmp_path)
    rel_paths = [line.split("\t", 1)[0] for line in digest.split("\n")]
    assert rel_paths == ["a.md", "dir/b.md"]
