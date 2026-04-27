"""AC-L (Winston W3) — compiler rejects unknown model_id when registry is present.

Pairs negative-path with positive-path coverage in one file (Amelia T4 nit).

Story 2a.1 commit `2a336df` made `_validate_model_ids_in_model_config_refs`
ADDITIVE-only — skips when registry absent OR config not parseable as
SpecialistModelConfig. The positive path (real registry + real config + unknown
model_id) MUST still raise. This test pins that property so a future regression
to "permissive everywhere" is caught immediately.

Invokes the validator function directly rather than the full `compile()` to keep
the test focused on the AC-L surface (PipelineManifest construction is a Slab-1
substrate concern, already covered at Story 1.4 close).
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from app.manifest.compiler import _validate_model_ids_in_model_config_refs
from app.manifest.exceptions import CompileError
from app.manifest.schema import NodeSpec

REPO_ROOT: Path = Path(__file__).resolve().parents[3]


def _write_specialist_model_config(
    target_path: Path,
    *,
    specialist_id: str,
    default_model: str,
) -> None:
    """Author a SpecialistModelConfig YAML at the target path."""
    yaml_body = textwrap.dedent(
        f"""\
        specialist_id: "{specialist_id}"
        default_model: "{default_model}"
        per_node_overrides:
          act: "{default_model}"
        temperature_default: 0.0
        """
    )
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(yaml_body, encoding="utf-8")


def test_known_model_id_validator_accepts_irene_default() -> None:
    """Positive path: Irene's shipped model_config.yaml resolves to gpt-5 (registry-known).

    Validator does NOT raise on the live Irene model_config.yaml that this story
    just authored — confirming the validator is functional + the file is valid.
    """
    nodes = [
        NodeSpec(
            id="irene_act",
            specialist_id="irene",
            model_config_ref="app/specialists/irene/model_config.yaml",
        )
    ]
    # Should NOT raise.
    _validate_model_ids_in_model_config_refs(nodes, REPO_ROOT)


def test_validator_rejects_unknown_model_id_when_registry_present(
    tmp_path: Path,
) -> None:
    """Negative path (Winston W3): unknown model_id + registry present → CompileError.

    Constructs a synthetic config under tmp_path/specialists_negative/ but uses
    the real REPO_ROOT for registry resolution + node-config-ref construction.
    """
    # Place the bogus config inside the repo so model_config_ref resolves.
    bogus_dir = REPO_ROOT / "tests" / "fixtures" / "specialists" / "test_compiler_neg"
    bogus_path = bogus_dir / "model_config.yaml"
    try:
        _write_specialist_model_config(
            bogus_path,
            specialist_id="bogus",
            default_model="gpt-bogus-9.9",  # NOT in app/models/registry.yaml
        )
        nodes = [
            NodeSpec(
                id="bogus_act",
                specialist_id="bogus",
                model_config_ref="tests/fixtures/specialists/test_compiler_neg/model_config.yaml",
            )
        ]
        with pytest.raises(CompileError, match="gpt-bogus-9.9"):
            _validate_model_ids_in_model_config_refs(nodes, REPO_ROOT)
    finally:
        # Clean up — fixture-style; do not pollute the repo across tests.
        if bogus_path.exists():
            bogus_path.unlink()
        if bogus_dir.exists():
            bogus_dir.rmdir()


def test_validator_skips_when_node_has_no_model_config_ref() -> None:
    """Validator is a no-op when no node references a model_config (additive-only)."""
    nodes = [NodeSpec(id="bare_node")]
    # Should NOT raise even with REPO_ROOT registry available — additive-only rule.
    _validate_model_ids_in_model_config_refs(nodes, REPO_ROOT)
