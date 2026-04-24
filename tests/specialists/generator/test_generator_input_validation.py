from __future__ import annotations

from pathlib import Path

import pytest

from skills.bmad_create_specialist.scripts import generate


@pytest.mark.parametrize(
    "name",
    ["", "BadName", "_hidden", "with-hyphen", "../escape", "1starts_with_digit"],
)
def test_invalid_name_rejected(name: str, temp_repo_root: Path, make_request) -> None:
    request = make_request(name=name, repo_root=temp_repo_root)
    with pytest.raises(generate.GeneratorInputError):
        generate.generate_specialist(request)


def test_name_collision_without_force_is_rejected(temp_repo_root: Path, make_request) -> None:
    generate.generate_specialist(make_request(repo_root=temp_repo_root))
    with pytest.raises(generate.GeneratorInputError, match="name collision"):
        generate.generate_specialist(make_request(repo_root=temp_repo_root))


@pytest.mark.parametrize("mcp_tool", ["", "MCP", "not-real", "openai"])
def test_invalid_mcp_tool_rejected(mcp_tool: str, temp_repo_root: Path, make_request) -> None:
    with pytest.raises(generate.GeneratorInputError, match="must be one of"):
        generate.generate_specialist(
            make_request(mcp_tool=mcp_tool, repo_root=temp_repo_root)
        )


@pytest.mark.parametrize("tier", ["L2-foo", "L8-foo", "l3-foo", "L3", "L3--foo", "L3-"])
def test_invalid_expertise_tier_rejected(tier: str, temp_repo_root: Path, make_request) -> None:
    with pytest.raises(generate.GeneratorInputError, match="fails pattern"):
        generate.generate_specialist(
            make_request(expertise_tier=tier, repo_root=temp_repo_root)
        )
