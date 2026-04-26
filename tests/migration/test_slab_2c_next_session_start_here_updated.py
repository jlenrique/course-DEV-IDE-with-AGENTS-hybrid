from __future__ import annotations

import re
from pathlib import Path


def test_next_session_start_here_reflects_slab_2c_close() -> None:
    handoff_path = Path("next-session-start-here.md")

    text = handoff_path.read_text(encoding="utf-8")

    assert handoff_path.is_file()
    assert re.search(r"Slab 2c.*closed|Slab 2c.*CLOSED", text)
    assert re.search(r"^Deferred inventory status:", text, flags=re.MULTILINE)
