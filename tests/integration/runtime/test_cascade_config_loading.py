from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.runtime.cascade_config import load_cascade


def test_load_cascade_returns_validated_config() -> None:
    cascade = load_cascade()

    assert cascade.marcus.model == "gpt-5"
    assert "irene" in cascade.specialists


def test_load_cascade_rejects_unknown_keys(tmp_path: Path) -> None:
    target = tmp_path / "model_cascade.yaml"
    target.write_text(
        "\n".join(
            [
                "marcus:",
                "  model: gpt-5",
                "  rationale: test",
                "specialists:",
                "  irene:",
                "    model: gpt-5",
                "    rationale: test",
                "    surprise: nope",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_cascade(target)


def test_cascade_digest_is_stable_across_repeated_reads() -> None:
    first = load_cascade()
    second = load_cascade()

    assert first.sha256_digest == second.sha256_digest
