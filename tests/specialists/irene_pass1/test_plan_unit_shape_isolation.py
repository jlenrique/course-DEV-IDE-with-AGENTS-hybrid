"""R5 (Auditor#3) — PlanUnit-name conflation pin.

Two DIFFERENT "plan unit" notions coexist and must never be conflated:

- ``app.marcus.lesson_plan.schema.PlanUnit`` — a Pydantic model with
  ``extra="forbid"`` (the Marcus lesson-plan schema family);
- irene_pass1's ``plan_units`` — an UNTYPED list-of-dicts shape (the Pass-1
  LLM output vocabulary) that the floor engine annotates with engine-owned
  keys (``floor_subdivision_index``) and ``source_refs``.

If a future refactor ran irene_pass1 plan_units through the Pydantic
``PlanUnit`` (extra="forbid"), every floored plan would explode on the
engine-owned annotation keys. These tests pin the isolation:

1. ``cluster_floor`` performs NO ``app.marcus`` import (static AST scan — the
   module docstring's "PURE leaf" claim, enforced);
2. nothing bound in the ``cluster_floor`` module namespace ORIGINATES in
   ``app.marcus`` (runtime complement to the AST scan; catches a re-export
   smuggled through an allowed intermediary). NOTE the guard is scoped to the
   MODULE, not the package: ``app.specialists.irene_pass1.__init__`` imports
   ``graph`` -> ``_act`` -> ``app.marcus.lesson_plan.collateral_spec``, a
   legitimate M3-allowed edge, so a whole-package sys.modules probe would
   false-positive on that unrelated import;
3. a plan_unit dict carrying ``floor_subdivision_index`` + ``source_refs`` +
   arbitrary extra keys flows through the honoring path unharmed — the exact
   dict that ``PlanUnit.model_validate`` (extra="forbid") REJECTS.
"""

from __future__ import annotations

import ast
import types
from pathlib import Path

import pydantic
import pytest

import app.specialists.irene_pass1.cluster_floor as cluster_floor_module
from app.specialists.irene_pass1 import cluster_floor as cf

CLUSTER_FLOOR_PATH = Path(cluster_floor_module.__file__)


def test_cluster_floor_has_no_app_marcus_import_static_scan() -> None:
    tree = ast.parse(CLUSTER_FLOOR_PATH.read_text(encoding="utf-8"))
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            offenders.extend(
                alias.name for alias in node.names if alias.name.startswith("app.marcus")
            )
        elif isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
            "app.marcus"
        ):
            offenders.append(node.module or "")
    assert not offenders, (
        "cluster_floor.py must stay a PURE leaf with no app.marcus import "
        f"(PlanUnit-conflation guard); found {offenders!r}"
    )


def test_cluster_floor_namespace_binds_nothing_from_app_marcus() -> None:
    """Runtime complement to the AST scan: no object bound in the floor
    engine's module namespace originates in ``app.marcus`` (in particular no
    ``app.marcus.lesson_plan`` schema class such as ``PlanUnit``)."""
    offenders: list[str] = []
    for name, value in vars(cluster_floor_module).items():
        if isinstance(value, types.ModuleType):
            origin = value.__name__
        else:
            origin = getattr(value, "__module__", None)
        if isinstance(origin, str) and origin.startswith("app.marcus"):
            offenders.append(f"{name} (from {origin})")
    assert not offenders, (
        "cluster_floor binds objects originating in app.marcus "
        f"(PlanUnit-conflation guard): {offenders!r}"
    )


def test_untyped_plan_unit_dicts_flow_through_honoring() -> None:
    """The honoring path accepts the untyped dict shape — including keys the
    Pydantic ``PlanUnit`` (extra='forbid') would reject — and never routes it
    through the lesson_plan schema."""
    units = [
        {
            "unit_id": "x1",
            "title": "Head",
            "learning_objective": "lo",
            "cluster_id": "c-x",
            "cluster_role": "head",
            "cluster_position": "establish",
            "cluster_interstitial_count": 1,
            "parent_slide_id": None,
            "source_refs": ["a first plain claim anchor"],
            "floor_subdivision_index": 0,  # engine-owned annotation
            "totally_unknown_extra_key": {"nested": True},  # extra='forbid' bait
        },
        {
            "unit_id": "x2",
            "title": "Beat",
            "learning_objective": "lo",
            "cluster_id": "c-x",
            "cluster_role": "interstitial",
            "cluster_position": "develop",
            "parent_slide_id": "x1",
            "source_refs": ["a second plain claim anchor"],
            "floor_subdivision_index": 0,
            "totally_unknown_extra_key": None,
        },
    ]
    honored, receipt = cf.consume_min_cluster_floor({"min_cluster_floor": 2}, units)
    assert receipt.consulted and cf.count_clusters(honored) == 2
    # content (extra keys included) survives byte-identical
    assert cf.flatten_plan_content(honored) == cf.flatten_plan_content(units)
    # and the Pydantic PlanUnit would REJECT this dict — proving the two
    # notions are genuinely different shapes (the conflation this pins against).
    # Imported INSIDE the test (deliberate): app.marcus.lesson_plan must never
    # ride this test module's import graph.
    from app.marcus.lesson_plan.schema import PlanUnit

    with pytest.raises(pydantic.ValidationError):
        PlanUnit.model_validate(units[0])
