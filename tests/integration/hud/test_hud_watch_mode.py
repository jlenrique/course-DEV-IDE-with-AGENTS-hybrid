from __future__ import annotations

from pathlib import Path

import yaml

from scripts.utilities import run_hud as hud


def test_hud_watch_mode_writes_two_snapshots(tmp_path: Path, capsys) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "run-constants.yaml").write_text(
        yaml.dump({"RUN_ID": "WATCH-RUN"}), encoding="utf-8"
    )
    output = tmp_path / "run-hud.html"

    hud.main(
        [
            "--bundle-dir",
            str(bundle),
            "--output",
            str(output),
            "--watch",
            "0",
            "--max-iterations",
            "2",
            "--no-adhoc-panel",
        ]
    )

    assert output.exists()
    html = output.read_text(encoding="utf-8")
    assert "WATCH-RUN" in html
    assert "banner-live" in html
    out = capsys.readouterr().out
    assert "HUD snapshot 1" in out
    assert "HUD snapshot 2" in out
