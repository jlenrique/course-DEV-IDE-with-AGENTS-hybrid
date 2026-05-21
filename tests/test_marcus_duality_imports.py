"""30-1 handshake smoke + single-source-of-truth cross-ref (AC-T.2, AC-T.16).

Asserts the five imports 30-2a relies on all resolve with the correct
constant values, and that the literal string ``"marcus-orchestrator"``
is NOT duplicated in ``marcus/orchestrator/write_api.py`` source
(W-3 rider — single source of truth lives in the orchestrator package).
"""

from __future__ import annotations

import typing
from pathlib import Path


def test_30_2a_unblock_handshake_resolves() -> None:
    """AC-T.2 — the five imports 30-2a depends on all resolve."""
    from app.marcus.facade import get_facade  # noqa: F401 — import smoke
    from app.marcus.intake import INTAKE_MODULE_IDENTITY
    from app.marcus.lesson_plan.log import WriterIdentity  # noqa: F401
    from app.marcus.orchestrator import NEGOTIATOR_SEAM, ORCHESTRATOR_MODULE_IDENTITY
    from app.marcus.orchestrator.write_api import (
        UnauthorizedFacadeCallerError,  # noqa: F401
        emit_pre_packet_snapshot,  # noqa: F401
    )

    assert INTAKE_MODULE_IDENTITY == "marcus-intake"
    assert ORCHESTRATOR_MODULE_IDENTITY == "marcus-orchestrator"
    # 30-3a upgraded NEGOTIATOR_SEAM from string sentinel to structural marker;
    # str() preserves the grep-discoverable contract.
    assert str(NEGOTIATOR_SEAM) == "marcus-negotiator"
    assert callable(get_facade)


def test_module_identities_are_writer_identity_literal_members() -> None:
    """AC-T.16 — INTAKE + ORCHESTRATOR identities are WriterIdentity Literal members.

    Pins the three-place string-drift hazard: the string
    ``"marcus-orchestrator"`` lives in (a) ORCHESTRATOR_MODULE_IDENTITY,
    (b) write_api.py guard check via import, (c) the 31-2 WriterIdentity
    Literal. This test asserts (a) is a subset of (c).
    """
    from app.marcus.intake import INTAKE_MODULE_IDENTITY
    from app.marcus.lesson_plan.log import WriterIdentity
    from app.marcus.orchestrator import ORCHESTRATOR_MODULE_IDENTITY

    literal_members = typing.get_args(WriterIdentity)
    assert INTAKE_MODULE_IDENTITY in literal_members
    assert ORCHESTRATOR_MODULE_IDENTITY in literal_members


def test_write_api_does_not_duplicate_orchestrator_literal_in_code() -> None:
    """AC-T.16 (W-3 rider) — ``"marcus-orchestrator"`` does not appear as a
    code-level literal in write_api.py. The module imports
    ORCHESTRATOR_MODULE_IDENTITY from marcus.orchestrator instead.

    Uses AST to strip docstrings (mentions in docstrings are documentation,
    not runtime drift risks). Only flags literal string nodes at code level.
    """
    import ast

    source_path = Path(__file__).parent.parent / "app" / "marcus" / "orchestrator" / "write_api.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    offenders: list[int] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value == "marcus-orchestrator"
        ):
            offenders.append(getattr(node, "lineno", -1))

    # The module docstring itself is allowed to mention the literal as
    # documentation; filter it by matching against ast.get_docstring.
    module_docstring = ast.get_docstring(tree, clean=False) or ""
    has_mention = "marcus-orchestrator" in module_docstring
    has_docstring_expr = (
        bool(tree.body)
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
    )
    if has_mention and has_docstring_expr:
        docstring_lineno = tree.body[0].value.lineno  # type: ignore[union-attr]
        offenders = [ln for ln in offenders if ln != docstring_lineno]

    assert not offenders, (
        f"write_api.py has code-level literal \"marcus-orchestrator\" at "
        f"lines {offenders}. Import ORCHESTRATOR_MODULE_IDENTITY from "
        "marcus.orchestrator instead (W-3 single-source-of-truth rider)."
    )
