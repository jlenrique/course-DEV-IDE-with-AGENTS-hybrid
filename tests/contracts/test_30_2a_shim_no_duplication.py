"""AC-C.1 — CLI shim has no duplicated ``prepare_irene_packet`` function body.

AST-walks ``scripts/utilities/prepare-irene-packet.py`` and asserts the
three shim-discipline invariants together (one collecting test, three
sub-assertions):

1. It imports ``prepare_irene_packet`` from ``marcus.intake.pre_packet``.
2. It does NOT define its own ``prepare_irene_packet`` ``FunctionDef``
   at module level (would indicate the contributor copied rather than
   moved — the classic "lift but also leave the original" anti-pattern).
3. The ``main(argv)`` CLI glue function still exists.
"""

from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT: Path = Path(__file__).parent.parent.parent.resolve()
_SHIM_PATH: Path = _REPO_ROOT / "scripts" / "utilities" / "prepare-irene-packet.py"


def test_shim_discipline_invariants() -> None:
    """AC-C.1 — shim imports lifted function, does not redefine, retains main."""
    tree = ast.parse(
        _SHIM_PATH.read_text(encoding="utf-8"),
        filename=str(_SHIM_PATH),
    )

    # (1) Imports prepare_irene_packet from marcus.intake.pre_packet.
    imports = [
        (node.module, [alias.name for alias in node.names])
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    ]
    assert any(
        module == "app.marcus.intake.pre_packet" and "prepare_irene_packet" in names
        for module, names in imports
    ), (
        f"Expected `from marcus.intake.pre_packet import prepare_irene_packet`; "
        f"shim imports: {imports}"
    )

    # (2) Does NOT define its own prepare_irene_packet at module level.
    redefinitions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        and node.name == "prepare_irene_packet"
    ]
    assert not redefinitions, (
        "Shim at scripts/utilities/prepare-irene-packet.py must NOT define "
        "its own prepare_irene_packet — it should ONLY import from "
        "marcus.intake.pre_packet (AC-C.1 / 30-2a lift discipline)."
    )

    # (3) Retains main(argv) CLI glue.
    main_defs = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    assert len(main_defs) == 1, (
        "Shim must retain exactly one module-level `main(argv)` function "
        f"(found {len(main_defs)})."
    )
