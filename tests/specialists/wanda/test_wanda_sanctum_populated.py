from __future__ import annotations

import re
from pathlib import Path

from app.specialists.wanda.graph import SANCTUM_DIR, _read_sanctum_digest

EXPECTED_SANCTUM_FILES = (
    "INDEX.md",
    "PERSONA.md",
    "CREED.md",
    "BOND.md",
    "MEMORY.md",
    "CAPABILITIES.md",
)


def test_sanctum_directory_exists() -> None:
    assert SANCTUM_DIR.is_dir()
    for rel_path in EXPECTED_SANCTUM_FILES:
        path = SANCTUM_DIR / rel_path
        assert path.is_file(), rel_path
        text = path.read_text(encoding="utf-8")
        assert "status: operator-population-pending" in text
        assert "<!-- TODO: operator-populate via First Breath ceremony -->" in text


def test_sanctum_digest_nonempty_post_population() -> None:
    digest = _read_sanctum_digest(SANCTUM_DIR)
    lines = digest.splitlines()
    assert len(lines) == len(EXPECTED_SANCTUM_FILES)
    assert [line.split("\t", 1)[0] for line in lines] == sorted(EXPECTED_SANCTUM_FILES)
    for line in lines:
        rel_path, sha256 = line.split("\t", 1)
        assert rel_path in EXPECTED_SANCTUM_FILES
        assert re.fullmatch(r"[0-9a-f]{64}", sha256)


def test_sanctum_digest_deterministic_under_crlf(tmp_path: Path) -> None:
    crlf_dir = tmp_path / "bmad-agent-wanda"
    lf_dir = tmp_path / "bmad-agent-wanda-lf"
    crlf_dir.mkdir()
    lf_dir.mkdir()
    (crlf_dir / "PERSONA.md").write_bytes(b"# Wanda\r\n\r\nline\r\n")
    (lf_dir / "PERSONA.md").write_bytes(b"# Wanda\n\nline\n")
    assert _read_sanctum_digest(crlf_dir) == _read_sanctum_digest(lf_dir)
