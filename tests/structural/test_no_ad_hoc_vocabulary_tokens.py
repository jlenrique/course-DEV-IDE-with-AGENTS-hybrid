"""FR-O4 guard: no ad-hoc decision-card vocabulary tokens."""

from __future__ import annotations

import ast
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from app.models.decision_cards import REGISTRY_PATH, load_vocabulary_registry

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = [
    REPO_ROOT / "app" / "marcus" / "orchestrator",
    REPO_ROOT / "app" / "marcus" / "cli",
]
TARGET_CALLS = {"emit_decision_card", "register_decision_card", "emit_verdict"}
TARGET_KWARGS = {"decision", "directive", "gate_decision"}
TOKEN_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[-_][a-z0-9]+)+$")


@dataclass(frozen=True)
class VocabularyOffense:
    path: Path
    line: int
    token: str


def _flat_registry_tokens(registry_path: Path = REGISTRY_PATH) -> set[str]:
    registry = load_vocabulary_registry(registry_path)
    tokens: set[str] = set()
    for namespace in registry["namespaces"].values():
        for value in namespace["tokens"].values():
            if isinstance(value, list):
                tokens.update(value)
    return tokens


def _call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


def _string_literals(nodes: Iterable[ast.AST]) -> Iterable[ast.Constant]:
    for node in nodes:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node


def find_ad_hoc_vocabulary_tokens(
    paths: Iterable[Path],
    *,
    allowed_tokens: set[str] | None = None,
) -> list[VocabularyOffense]:
    """Find suspicious vocabulary-looking strings in decision-card emit calls."""
    allowed = allowed_tokens if allowed_tokens is not None else _flat_registry_tokens()
    offenses: list[VocabularyOffense] = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            call_name = _call_name(node)
            kwarg_values = [kw.value for kw in node.keywords if kw.arg in TARGET_KWARGS]
            should_scan_args = call_name in TARGET_CALLS
            should_scan_kwargs = bool(kwarg_values)
            if not should_scan_args and not should_scan_kwargs:
                continue
            values = list(node.args if should_scan_args else []) + kwarg_values
            for value in values:
                for literal in _string_literals(ast.walk(value)):
                    token = literal.value
                    if TOKEN_PATTERN.match(token) and token not in allowed:
                        offenses.append(VocabularyOffense(path, literal.lineno, token))
    return offenses


def _scan_paths() -> list[Path]:
    paths: list[Path] = []
    for root in SCAN_ROOTS:
        if root.exists():
            paths.extend(root.rglob("*.py"))
    specialists_root = REPO_ROOT / "app" / "specialists"
    paths.extend(specialists_root.glob("*/graph.py"))
    gate_shims = REPO_ROOT / "app" / "marcus" / "cli" / "gate_shims"
    if gate_shims.exists():
        paths.extend(gate_shims.rglob("*.py"))
    return sorted(set(paths))


def test_clean_baseline_has_no_ad_hoc_vocabulary_tokens() -> None:
    offenses = find_ad_hoc_vocabulary_tokens(_scan_paths())
    assert offenses == []


def test_injected_ad_hoc_token_fails(tmp_path: Path) -> None:
    target = tmp_path / "bad.py"
    target.write_text(
        "def emit_decision_card(**kwargs): pass\n"
        "emit_decision_card(decision='silent-approve')\n",
        encoding="utf-8",
    )
    offenses = find_ad_hoc_vocabulary_tokens([target], allowed_tokens={"confirm"})
    assert offenses == [VocabularyOffense(target, 2, "silent-approve")]
