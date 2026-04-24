from __future__ import annotations

from pathlib import Path

from skills.bmad_create_specialist.scripts import generate


def test_dry_run_from_skill_writes_nothing(temp_repo_root: Path, make_request) -> None:
    from_skill = temp_repo_root / "skills" / "bmad-agent-content-creator"
    request = make_request(
        name="irene",
        expertise_tier="L5-narration-pass-2",
        from_skill=from_skill,
        dry_run=True,
        repo_root=temp_repo_root,
    )
    result = generate.generate_specialist(request)

    assert result.dry_run
    assert result.written_files == tuple()
    assert len(result.planned_files) == 9
    assert not (temp_repo_root / "app" / "specialists" / "irene").exists()


def test_dry_run_manifest_is_deterministic(temp_repo_root: Path, make_request) -> None:
    request = make_request(dry_run=True, repo_root=temp_repo_root)
    first = generate.generate_specialist(request).planned_files
    second = generate.generate_specialist(request).planned_files
    assert first == second
