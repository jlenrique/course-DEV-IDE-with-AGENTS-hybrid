from __future__ import annotations

from pathlib import Path

import pytest

from skills.bmad_create_specialist.scripts import generate


def test_from_skill_must_exist(temp_repo_root: Path, make_request) -> None:
    request = make_request(
        from_skill=temp_repo_root / "skills" / "bmad-agent-missing",
        repo_root=temp_repo_root,
    )
    with pytest.raises(generate.GeneratorInputError, match="does not exist"):
        generate.generate_specialist(request)


def test_from_skill_must_be_under_skills_root(temp_repo_root: Path, make_request) -> None:
    outside = temp_repo_root.parent / "outside_skill"
    outside.mkdir(parents=True, exist_ok=True)
    (outside / "SKILL.md").write_text("# outside", encoding="utf-8")
    request = make_request(from_skill=outside, repo_root=temp_repo_root)
    with pytest.raises(generate.GeneratorInputError, match="must be under"):
        generate.generate_specialist(request)


def test_from_skill_must_have_bmad_agent_prefix(temp_repo_root: Path, make_request) -> None:
    invalid = temp_repo_root / "skills" / "my-custom-skill"
    invalid.mkdir(parents=True)
    (invalid / "SKILL.md").write_text("# skill", encoding="utf-8")
    request = make_request(from_skill=invalid, repo_root=temp_repo_root)
    with pytest.raises(generate.GeneratorInputError, match="bmad-agent"):
        generate.generate_specialist(request)
