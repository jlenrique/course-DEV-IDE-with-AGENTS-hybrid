from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIR = (
    REPO_ROOT / "tests" / "fixtures" / "specialists" / "wanda" / "live_artifacts" / "2026-04-26"
)
METADATA = ARTIFACT_DIR / "LIVE_ARTIFACT_METADATA.md"


def _metadata_fields(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def test_live_artifact_metadata_round_trip() -> None:
    if not METADATA.is_file():
        pytest.skip("AC-D-OP DEFERRED-PENDING-OPERATOR-WINDOW; live artifact metadata absent")
    fields = _metadata_fields(METADATA)
    artifact_path = REPO_ROOT / fields["artifact_path"]
    assert artifact_path.is_file()
    assert fields["artifact_format"] in {"scripted", "simple-fallback"}
    assert fields["sha256"] == hashlib.sha256(artifact_path.read_bytes()).hexdigest()
