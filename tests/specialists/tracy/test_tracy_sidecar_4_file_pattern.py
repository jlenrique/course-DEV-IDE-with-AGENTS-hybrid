from __future__ import annotations

from tests.parity._sanctum_parity_base import REPO_ROOT

SIDE_CAR_FILES = {
    "INDEX.md",
    "PERSONA.md",
    "chronology.md",
    "access-boundaries.md",
}


def test_tracy_sidecar_has_exact_four_file_class_c_plus_pattern() -> None:
    sidecar = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-tracy"
    assert sidecar.is_dir()
    present = {path.name for path in sidecar.iterdir() if path.is_file()}
    assert present == SIDE_CAR_FILES


def test_tracy_sidecar_content_mentions_retrieval_contract() -> None:
    index_text = (REPO_ROOT / "_bmad" / "memory" / "bmad-agent-tracy" / "INDEX.md").read_text(
        encoding="utf-8"
    )
    assert "RetrievalIntent" in index_text
    assert "provider_hints" in index_text
