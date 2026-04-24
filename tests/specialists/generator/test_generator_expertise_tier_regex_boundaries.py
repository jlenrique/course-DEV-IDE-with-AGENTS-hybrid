from __future__ import annotations

from pathlib import Path

import pytest

from skills.bmad_create_specialist.scripts import generate


@pytest.mark.parametrize("tier", ["L3-ai", "L4-motion-ops", "L7-long-suffix"])
def test_expertise_tier_valid_examples(tier: str, temp_repo_root: Path, make_request) -> None:
    safe_name = f"tier_{tier.lower().replace('-', '_')}"
    result = generate.generate_specialist(
        make_request(
            expertise_tier=tier,
            name=safe_name,
            repo_root=temp_repo_root,
        )
    )
    assert len(result.written_files) == 9


@pytest.mark.parametrize("tier", ["L3--foo", "L3-", "L8-x", "L3", "l3-foo"])
def test_expertise_tier_invalid_boundary_examples(
    tier: str, temp_repo_root: Path, make_request
) -> None:
    with pytest.raises(generate.GeneratorInputError):
        generate.generate_specialist(
            make_request(expertise_tier=tier, name="badtier", repo_root=temp_repo_root)
        )
