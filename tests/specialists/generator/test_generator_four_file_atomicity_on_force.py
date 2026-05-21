from __future__ import annotations

from pathlib import Path

import pytest

from skills.bmad_create_specialist.scripts import generate


def test_force_rolls_back_on_mid_emission_failure(
    temp_repo_root: Path, make_request, monkeypatch
) -> None:
    generate.generate_specialist(make_request(repo_root=temp_repo_root))
    state_path = temp_repo_root / "app" / "specialists" / "toytest" / "state.py"
    original_state = state_path.read_text(encoding="utf-8")

    counter = {"writes": 0}
    original_write = generate._write_text

    def _failing_write(path: Path, content: str) -> None:
        counter["writes"] += 1
        if counter["writes"] == 3:
            raise OSError("simulated mid-write failure")
        original_write(path, content)

    monkeypatch.setattr(generate, "_write_text", _failing_write)

    with pytest.raises(generate.GeneratorInputError, match="atomic emission failed"):
        generate.generate_specialist(make_request(force=True, repo_root=temp_repo_root))

    assert state_path.read_text(encoding="utf-8") == original_state
