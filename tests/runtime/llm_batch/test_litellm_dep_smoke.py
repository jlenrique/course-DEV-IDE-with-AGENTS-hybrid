"""A0 hermetic smoke: LiteLLM is a declared, importable project dependency."""

from __future__ import annotations

import importlib.metadata
from pathlib import Path


def test_litellm_importable() -> None:
    import litellm  # noqa: F401 — import is the assertion


def test_litellm_version_matches_a0_pin() -> None:
    version = importlib.metadata.version("litellm")
    assert version.startswith("1.90"), (
        f"expected litellm 1.90.x (A0 pin litellm>=1.90.2,<2); got {version!r}"
    )


def test_llm_batch_package_documents_naming_trap() -> None:
    import app.runtime.llm_batch as llm_batch

    doc = llm_batch.__doc__ or ""
    assert "batch_completion" in doc
    assert "create_batch" in doc
    assert "technical-litellm-batch-hookup-research-2026-07-10" in doc
    assert "B1" in doc


def test_pyproject_declares_litellm_dependency() -> None:
    root = Path(__file__).resolve().parents[3]
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert "litellm>=" in text
    assert "1.90.2" in text
