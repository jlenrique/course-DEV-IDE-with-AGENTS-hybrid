from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.cora.graph import DevGraphManifest


def test_valid_dev_graph_manifest_parses() -> None:
    manifest = DevGraphManifest.model_validate(
        {
            "schema_version": "1.0",
            "thread_namespace": "dev/{story_id}",
            "dev_nodes": [
                {
                    "id": "plan_story",
                    "label": "Plan Story",
                    "handler": "app.cora.handlers.plan_story:plan_story",
                }
            ],
            "dev_edges": [{"from": "__start__", "to": "plan_story"}],
        }
    )

    assert manifest.thread_namespace == "dev/{story_id}"


def test_invalid_dev_graph_manifest_raises() -> None:
    with pytest.raises(ValidationError):
        DevGraphManifest.model_validate(
            {
                "schema_version": "1.0",
                "thread_namespace": "run/{story_id}",
                "dev_nodes": [
                    {
                        "id": "plan_story",
                        "label": "Plan Story",
                        "handler": "app.cora.handlers.plan_story:plan_story",
                        "unexpected": True,
                    }
                ],
            }
        )
