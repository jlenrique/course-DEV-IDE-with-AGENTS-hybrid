from __future__ import annotations

from pathlib import Path

from skills.bmad_create_specialist.scripts import generate


def test_parse_args_maps_flags_to_request() -> None:
    request = generate.parse_args(
        [
            "--name",
            "toytest",
            "--mcp",
            "none",
            "--expertise-tier",
            "L5-toy",
            "--dry-run",
        ]
    )
    assert request.name == "toytest"
    assert request.mcp_tool == "none"
    assert request.expertise_tier == "L5-toy"
    assert request.dry_run is True


def test_main_returns_0_for_dry_run(temp_repo_root: Path, monkeypatch) -> None:
    monkeypatch.setattr(generate, "_repo_root", lambda: temp_repo_root)
    exit_code = generate.main(
        [
            "--name",
            "toytest",
            "--mcp",
            "none",
            "--expertise-tier",
            "L5-toy",
            "--dry-run",
        ]
    )
    assert exit_code == 0


def test_main_returns_1_for_invalid_request(temp_repo_root: Path, monkeypatch) -> None:
    monkeypatch.setattr(generate, "_repo_root", lambda: temp_repo_root)
    exit_code = generate.main(
        [
            "--name",
            "InvalidName",
            "--mcp",
            "none",
            "--expertise-tier",
            "L5-toy",
        ]
    )
    assert exit_code == 1
