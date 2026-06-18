from __future__ import annotations

import pytest

from scripts.utilities.check_manifest_lockstep import check_lockstep


@pytest.mark.parametrize(
    ("changed", "companions"),
    [
        (
            ["state/config/pipeline-manifest.yaml"],
            ["scripts/utilities/check_pipeline_manifest_lockstep.py"],
        ),
        (
            ["scripts/utilities/run_hud.py"],
            ["state/config/pipeline-manifest.yaml"],
        ),
        (
            [
                "docs/workflow/"
                "production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md"
            ],
            ["state/config/pipeline-manifest.yaml"],
        ),
        (
            ["state/config/learning-event-schema.yaml"],
            ["scripts/utilities/learning_event_capture.py"],
        ),
    ],
)
def test_companion_assertion_per_path(changed: list[str], companions: list[str]) -> None:
    check_lockstep(changed + companions)
