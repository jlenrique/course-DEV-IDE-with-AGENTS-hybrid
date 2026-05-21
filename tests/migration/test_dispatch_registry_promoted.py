from __future__ import annotations

from pathlib import Path

import yaml


def test_dispatch_registry_status_no_longer_interim() -> None:
    for path in (
        Path("state/config/dispatch-registry.yaml"),
        Path("runtime/graphs/v42/dispatch-registry-snapshot.yaml"),
    ):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert payload["_status"] != "interim", f"{path} still carries interim status"
