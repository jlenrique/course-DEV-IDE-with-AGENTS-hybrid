from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.manifest.schema import NodeSpec


def test_node_spec_accepts_no_fold_fields() -> None:
    node = NodeSpec(id="n1")

    assert node.fold_with is None
    assert node.fold_target is None


def test_node_spec_accepts_fold_with() -> None:
    node = NodeSpec(id="n1", fold_with="G1")

    assert node.fold_with == "G1"
    assert node.fold_target is None


def test_node_spec_accepts_fold_target() -> None:
    node = NodeSpec(id="n1", fold_target="subgraph:g1")

    assert node.fold_with is None
    assert node.fold_target == "subgraph:g1"


def test_node_spec_rejects_fold_with_and_fold_target() -> None:
    with pytest.raises(
        ValidationError,
        match="node n1: fold_with and fold_target are mutually exclusive",
    ):
        NodeSpec(id="n1", fold_with="G1", fold_target="subgraph:g1")
