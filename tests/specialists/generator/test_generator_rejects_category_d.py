from __future__ import annotations

from pathlib import Path

import pytest

from skills.bmad_create_specialist.scripts import generate


@pytest.mark.parametrize("denied_name", ["bmad-agent-audra", "bmad-agent-cora"])
def test_generator_rejects_category_d_skill_dirs(
    denied_name: str, temp_repo_root: Path, make_request
) -> None:
    from_skill = temp_repo_root / "skills" / denied_name
    request = make_request(from_skill=from_skill, repo_root=temp_repo_root)
    with pytest.raises(generate.GeneratorInputError, match="DISSOLVED per DR-2"):
        generate.generate_specialist(request)

    assert not (temp_repo_root / "app" / "specialists" / "toytest").exists()
