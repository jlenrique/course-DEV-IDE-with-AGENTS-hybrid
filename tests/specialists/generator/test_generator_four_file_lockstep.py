from __future__ import annotations

from pathlib import Path

from skills.bmad_create_specialist.scripts import generate


def test_four_file_lockstep_outputs_exist(temp_repo_root: Path, make_request) -> None:
    generate.generate_specialist(make_request(repo_root=temp_repo_root))

    assert (temp_repo_root / "app" / "specialists" / "toytest" / "state.py").is_file()
    assert (
        temp_repo_root
        / "tests"
        / "specialists"
        / "toytest"
        / "test_toytest_state_shape.py"
    ).is_file()
    assert (
        temp_repo_root
        / "tests"
        / "fixtures"
        / "specialists"
        / "toytest"
        / "golden_envelope.json"
    ).is_file()
    assert (
        temp_repo_root
        / "tests"
        / "fixtures"
        / "specialists"
        / "toytest"
        / "golden_return.json"
    ).is_file()


def test_force_overwrite_updates_existing_lockstep_files(
    temp_repo_root: Path, make_request
) -> None:
    generate.generate_specialist(make_request(repo_root=temp_repo_root))
    state_file = temp_repo_root / "app" / "specialists" / "toytest" / "state.py"
    state_file.write_text("# stale", encoding="utf-8")

    generate.generate_specialist(make_request(force=True, repo_root=temp_repo_root))
    assert "# stale" not in state_file.read_text(encoding="utf-8")
