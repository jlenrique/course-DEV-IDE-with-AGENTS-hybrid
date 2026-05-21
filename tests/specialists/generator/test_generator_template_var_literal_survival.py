from __future__ import annotations

from pathlib import Path

from skills.bmad_create_specialist.scripts import generate


def test_unknown_template_vars_survive_literal_in_output(
    temp_repo_root: Path, make_request
) -> None:
    template_path = (
        temp_repo_root
        / "skills"
        / "bmad-create-specialist"
        / "templates"
        / "expertise"
        / "README.md.template"
    )
    template_path.write_text(
        template_path.read_text(encoding="utf-8") + "\nunknown={{retrieval_provider}}\n",
        encoding="utf-8",
    )

    generate.generate_specialist(make_request(repo_root=temp_repo_root))
    output_path = temp_repo_root / "app" / "specialists" / "toytest" / "expertise" / "README.md"
    assert "{{retrieval_provider}}" in output_path.read_text(encoding="utf-8")
