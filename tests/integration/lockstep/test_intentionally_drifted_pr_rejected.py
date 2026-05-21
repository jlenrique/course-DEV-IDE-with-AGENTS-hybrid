from __future__ import annotations

import pytest

from scripts.utilities.check_manifest_lockstep import (
    CompileError,
    LockstepError,
    ManifestDriftError,
    check_lockstep,
)


def test_drift_in_pipeline_manifest_yaml_rejected() -> None:
    with pytest.raises(ManifestDriftError, match="state/config/pipeline-manifest.yaml"):
        check_lockstep(["state/config/pipeline-manifest.yaml"])


def test_drift_in_l1_script_rejected() -> None:
    with pytest.raises(
        ManifestDriftError,
        match="scripts/utilities/check_pipeline_manifest_lockstep.py",
    ):
        check_lockstep(["scripts/utilities/check_pipeline_manifest_lockstep.py"])


def test_lockstep_error_classes_discriminated(tmp_path, monkeypatch) -> None:
    with pytest.raises(LockstepError):
        check_lockstep(["state/config/pipeline-manifest.yaml"])

    def _boom(*args, **kwargs):
        raise CompileError("boom")

    monkeypatch.setattr(
        "scripts.utilities.check_manifest_lockstep._compile_dev_graph_if_available",
        _boom,
    )
    with pytest.raises(CompileError):
        check_lockstep([])
