from pathlib import Path


def test_clone_fork_notice_present_for_all_sanctum_dirs() -> None:
    memory_root = Path("_bmad/memory")
    sanctum_dirs = [p for p in memory_root.iterdir() if p.is_dir()]

    missing = [
        p.name
        for p in sanctum_dirs
        if not (p / "CLONE-FORK-NOTICE.md").is_file()
    ]

    assert not missing, f"Missing CLONE-FORK-NOTICE.md for: {', '.join(sorted(missing))}"
