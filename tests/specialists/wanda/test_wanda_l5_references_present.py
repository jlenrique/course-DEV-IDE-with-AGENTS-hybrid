from __future__ import annotations

from app.specialists.wanda.graph import (
    WANDA_REFERENCES,
    WANDA_REFERENCES_DIR,
    _read_wanda_references,
)

L5_REFERENCES = (
    "L5-podcast-production/storytelling-framework.md",
    "L5-podcast-production/audio-production-patterns.md",
    "L5-podcast-production/narration-length-vs-engagement.md",
)


def test_l5_directory_and_three_files_exist() -> None:
    l5_dir = WANDA_REFERENCES_DIR / "L5-podcast-production"
    assert l5_dir.is_dir()
    for rel_path in L5_REFERENCES:
        path = WANDA_REFERENCES_DIR / rel_path
        assert path.is_file(), rel_path
        substantive_lines = [
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        assert len(substantive_lines) >= 40


def test_wanda_references_tuple_contains_l5_paths() -> None:
    assert len(WANDA_REFERENCES) == 14
    for rel_path in L5_REFERENCES:
        assert rel_path in WANDA_REFERENCES


def test_read_wanda_references_includes_l5_bodies_in_declared_order() -> None:
    refs = _read_wanda_references()
    l5_offsets = []
    for rel_path in L5_REFERENCES:
        header = f"### Reference: {rel_path}"
        offset = refs.index(header)
        l5_offsets.append(offset)
        first_body_line = next(
            line
            for line in (WANDA_REFERENCES_DIR / rel_path)
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
        assert first_body_line in refs
    assert l5_offsets == sorted(l5_offsets)
