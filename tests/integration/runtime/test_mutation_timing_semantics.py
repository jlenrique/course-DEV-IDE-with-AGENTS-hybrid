from __future__ import annotations

from uuid import UUID

import pytest

from app.runtime.sanctum_watcher import (
    SanctumWatcher,
    clear_sanctum_warning_registry,
    get_sanctum_warnings,
)

TRIAL_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")


@pytest.mark.parametrize(
    ("timing", "expected_warning_count"),
    [("before", 0), ("during", 1), ("after", 0)],
)
def test_mutation_timing_semantics(tmp_path, timing: str, expected_warning_count: int) -> None:
    clear_sanctum_warning_registry()
    sanctum_root = tmp_path / "_bmad" / "memory" / "wanda-sidecar"
    sanctum_root.mkdir(parents=True)
    target = sanctum_root / "CAPABILITIES.md"
    target.write_text("baseline\n", encoding="utf-8")

    watcher = SanctumWatcher(sanctum_root=sanctum_root.parent)

    if timing == "before":
        target.write_text("before\n", encoding="utf-8")
        watcher.handle_path(target)
        watcher.begin_invocation(TRIAL_ID)
    elif timing == "during":
        watcher.begin_invocation(TRIAL_ID)
        target.write_text("during\n", encoding="utf-8")
        watcher.handle_path(target)
    else:
        watcher.begin_invocation(TRIAL_ID)
        watcher.finish_invocation()
        target.write_text("after\n", encoding="utf-8")
        watcher.handle_path(target)

    assert len(get_sanctum_warnings(TRIAL_ID)) == expected_warning_count
