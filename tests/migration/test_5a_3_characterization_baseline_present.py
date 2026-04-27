from __future__ import annotations

from pathlib import Path


def test_5a_3_characterization_baseline_present() -> None:
    root = Path(__file__).resolve().parents[2] / "_bmad-output" / "economics-baselines"
    matches = sorted(root.glob("migrated-runtime-characterization-*.md"))
    assert matches, "expected migrated-runtime characterization baseline artifact"

    content = matches[-1].read_text(encoding="utf-8")
    for heading in (
        "## Total",
        "## Per-Agent",
        "## Per-Model",
        "## Cascade Rationale",
        "## Optimization Headroom",
    ):
        assert heading in content
    assert "C1-M1-PRES-20260419B" in content
