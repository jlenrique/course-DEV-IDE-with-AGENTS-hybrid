from __future__ import annotations

import ast
import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
CLASSIFICATION_DOC = REPO_ROOT / "docs" / "dev-guide" / "pytest-xdist-classification.md"


def _pytest_options() -> dict[str, object]:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["tool"]["pytest"][
        "ini_options"
    ]


def test_pytest_addopts_default_to_xdist_non_serial_subset() -> None:
    options = _pytest_options()
    addopts = str(options["addopts"])
    assert "-p no:randomly" in addopts
    assert "-n auto" in addopts
    assert "--dist loadfile" in addopts
    assert "not live and not serial" in addopts


def test_serial_marker_registered_in_pytest_config() -> None:
    markers = _pytest_options()["markers"]
    assert any(str(marker).startswith("serial:") for marker in markers)


def test_every_serial_marker_is_documented() -> None:
    doc = CLASSIFICATION_DOC.read_text(encoding="utf-8")
    serial_marked: list[str] = []
    for path in (REPO_ROOT / "tests").rglob("test_*.py"):
        source = path.read_text(encoding="utf-8")
        if "pytest.mark.serial" not in source:
            continue
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                decorators = [ast.unparse(item) for item in node.decorator_list]
                if any("pytest.mark.serial" in decorator for decorator in decorators):
                    serial_marked.append(f"{path.relative_to(REPO_ROOT).as_posix()}::{node.name}")
    assert serial_marked
    for nodeid in serial_marked:
        assert re.search(re.escape(nodeid), doc), nodeid
