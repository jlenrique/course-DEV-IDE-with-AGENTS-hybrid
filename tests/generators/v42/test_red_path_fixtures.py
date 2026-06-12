"""Red-path fixture tests for v4.2 generator."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from scripts.generators.v42.manifest import MissingSectionTemplateError
from scripts.generators.v42.render import render_pack

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "tests/generators/v42/fixtures"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_red_path_missing_section(tmp_path: Path) -> None:
    manifest = yaml.safe_load((FIXTURES / "manifest_fixture.yaml").read_text(encoding="utf-8"))
    manifest["steps"].append(
        {
            "id": "99",
            "label": "Missing Section",
            "gate": False,
            "gate_code": None,
            "sub_phase_of": None,
            "insertion_after": "04.55",
            "hud_tracked": True,
            "pack_section_anchor": "99)",
            "pack_version": "v4.2",
            "rationale": "Intentional red path.",
        }
    )
    mpath = tmp_path / "missing.yaml"
    mpath.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    # Renderer/L1 story 2026-06-12: the fabricate-then-TemplateNotFound late
    # crash is retired; missing templates raise EARLY with the step named.
    with pytest.raises(MissingSectionTemplateError, match="'99'"):
        render_pack(mpath, tmp_path / "out.md")


def test_red_path_reordered_layout_fails_sha_check(tmp_path: Path) -> None:
    base = tmp_path / "base.md"
    render_pack(FIXTURES / "manifest_fixture.yaml", base)
    manifest = yaml.safe_load((FIXTURES / "manifest_fixture.yaml").read_text(encoding="utf-8"))
    manifest["steps"] = list(reversed(manifest["steps"]))
    mpath = tmp_path / "reordered.yaml"
    mpath.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    out = tmp_path / "reordered.md"
    render_pack(mpath, out)
    assert _sha(base) != _sha(out)


def test_red_path_hardcoded_body_ignores_manifest_mutation(tmp_path: Path) -> None:
    out1 = tmp_path / "one.md"
    render_pack(FIXTURES / "manifest_fixture.yaml", out1)
    manifest = yaml.safe_load((FIXTURES / "manifest_fixture.yaml").read_text(encoding="utf-8"))
    manifest["steps"][1]["label"] = "Operator Directives Changed"
    mpath = tmp_path / "mut.yaml"
    mpath.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    out2 = tmp_path / "two.md"
    render_pack(mpath, out2)
    assert _sha(out1) != _sha(out2)
