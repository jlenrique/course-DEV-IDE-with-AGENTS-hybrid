from __future__ import annotations

import time

from scripts.utilities.check_manifest_lockstep import main


def test_lockstep_perf_budget() -> None:
    diff_files = [f"docs/notes/file-{idx}.md" for idx in range(10)]
    started = time.perf_counter()
    assert main(diff_files) == 0
    elapsed = time.perf_counter() - started
    assert elapsed <= 60.0
