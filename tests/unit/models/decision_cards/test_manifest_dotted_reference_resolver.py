from __future__ import annotations

from pathlib import Path

import pytest

from app.manifest.compiler import compile
from app.manifest.exceptions import ManifestSchemaImportError
from app.manifest.refs import resolve_dotted_ref
from app.manifest.schema import EdgeSpec, NodeSpec, PipelineManifest
from app.models.decision_cards import DecisionCard, DecisionCardBase


def _manifest_with_schema_ref(schema_ref: str) -> PipelineManifest:
    return PipelineManifest.model_validate(
        {
            "schema_version": "0.1-test",
            "lane": "run_graph",
            "entrypoint": "01",
            "frozen_graph_version": "v-test",
            "nodes": [
                NodeSpec(id="01", specialist_id="alpha"),
                NodeSpec(id="02", specialist_id="beta"),
            ],
            "edges": [
                EdgeSpec.model_validate(
                    {
                        "from": "__start__",
                        "to": "01",
                        "decision_card_schema": schema_ref,
                    }
                ),
                EdgeSpec.model_validate({"from": "01", "to": "02"}),
            ],
        }
    )


def test_valid_dotted_reference_imports() -> None:
    refs = [
        "app.models.decision_cards.g1:G1Card",
        "app.models.decision_cards.g2c:G2CCard",
        "app.models.decision_cards.g3:G3Card",
        "app.models.decision_cards.g4:G4Card",
    ]
    for dotted_ref in refs:
        resolved = resolve_dotted_ref(
            dotted_ref,
            expected_base_class=(DecisionCard, DecisionCardBase),
        )
        assert issubclass(resolved, (DecisionCard, DecisionCardBase))


def test_invalid_dotted_reference_fails_compile(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "graphs" / "v-test").mkdir(parents=True)
    manifest = _manifest_with_schema_ref("app.models.decision_cards.g99:G99Card")
    with pytest.raises(ManifestSchemaImportError):
        compile(manifest, repo_root=tmp_path)
