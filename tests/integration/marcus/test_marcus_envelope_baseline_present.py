from __future__ import annotations

import json
from pathlib import Path


def test_marcus_envelope_baseline_present() -> None:
    baseline_dir = Path("tests/fixtures/marcus/baseline_envelope/2026-04-26")
    envelope_path = baseline_dir / "envelope.json"
    metadata_path = baseline_dir / "BASELINE_METADATA.md"

    assert envelope_path.is_file()
    assert metadata_path.is_file()

    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    metadata = metadata_path.read_text(encoding="utf-8")

    assert envelope["schema_version"] == "m3-trial-envelope.v1"
    for field in (
        "trial-id:",
        "corpus-path:",
        "capture-command:",
        "capture-environment-hash:",
        "rebaseline-protocol:",
    ):
        assert field in metadata
