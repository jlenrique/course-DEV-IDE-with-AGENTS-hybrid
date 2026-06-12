"""Renderer/L1 story pins (drift-audit fold; party-amended inventory entry).

Pin A (Murat): the renderable template roster is DERIVED from the manifest —
every non-orchestration node renders in one loop; the four runtime-only
orchestration nodes are excluded by the SHARED predicate, not a hardcoded
list of the names we knew about.

Pin B (Murat, "the vacuous-guard kill shot"): the L1 lockstep check must be
ABLE to fail — a removed template makes regeneration crash and L1 exit
non-zero (STRUCTURAL), and a hand-edited pack fails the regeneration-
determinism SHA leg. Before this story L1 never rendered at all and exited
0 while the renderer was broken.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from app.manifest.loader import load as load_graph_manifest
from app.manifest.schema import is_orchestration_only
from scripts.generators.v42.manifest import (
    MissingSectionTemplateError,
    load_generator_manifest,
)
from scripts.generators.v42.render import render_pack
from scripts.utilities.check_pipeline_manifest_lockstep import (
    DEFAULT_PACK_PATH,
    run_check,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"
TEMPLATE_ROOT = REPO_ROOT / "scripts" / "generators" / "v42" / "templates"


# ---------------------------------------------------------------------------
# Pin A — roster-derived completeness
# ---------------------------------------------------------------------------

def test_every_renderable_node_resolves_a_real_template() -> None:
    graph = load_graph_manifest(MANIFEST)
    renderable = [node.id for node in graph.nodes if not is_orchestration_only(node)]
    generator = load_generator_manifest(MANIFEST)
    generator_ids = [step.id for step in generator.steps]

    assert generator_ids == renderable  # roster equality, manifest-derived
    for step in generator.steps:
        assert (TEMPLATE_ROOT / step.template_name).is_file(), step.id


def test_full_manifest_renders_every_renderable_node_in_one_pass(tmp_path: Path) -> None:
    out = tmp_path / "pack.md"
    render_pack(MANIFEST, out)
    text = out.read_text(encoding="utf-8")
    generator = load_generator_manifest(MANIFEST)
    for step in generator.steps:
        assert f"## {step.id}) {step.label}" in text, step.id
    graph = load_graph_manifest(MANIFEST)
    for node in graph.nodes:
        if is_orchestration_only(node):
            assert f"## {node.id})" not in text, node.id


def test_orchestration_exclusion_uses_shared_predicate_not_a_name_list() -> None:
    """The generator and L1 must classify through ONE predicate. A second
    hardcoded roster is the next drift waiting for the next audit."""
    import inspect

    import scripts.generators.v42.manifest as generator_manifest_module
    import scripts.utilities.check_pipeline_manifest_lockstep as l1_module

    for module in (generator_manifest_module, l1_module):
        source = inspect.getsource(module)
        assert "is_orchestration_only" in source, module.__name__
        assert "directive-composer" not in source, (
            f"{module.__name__} hardcodes an orchestration node name; "
            "classification must flow through app.manifest.schema."
            "is_orchestration_only"
        )


# ---------------------------------------------------------------------------
# Pin B — the guard can fail
# ---------------------------------------------------------------------------

def _copy_templates_without(tmp_path: Path, template_relpath: str) -> Path:
    tmp_root = tmp_path / "templates"
    shutil.copytree(TEMPLATE_ROOT, tmp_root)
    target = tmp_root / template_relpath
    assert target.is_file(), f"fixture setup: {template_relpath} should exist"
    target.unlink()
    return tmp_root

def test_removed_section_template_makes_render_fail_loud(tmp_path: Path) -> None:
    generator = load_generator_manifest(MANIFEST)
    victim = generator.steps[0].template_name  # first renderable section
    crippled_root = _copy_templates_without(tmp_path, victim)

    with pytest.raises(MissingSectionTemplateError, match=generator.steps[0].id):
        render_pack(MANIFEST, tmp_path / "out.md", template_root=crippled_root)


def test_fabricated_template_names_are_gone() -> None:
    """The old _template_name FABRICATED a plausible name for missing
    templates and let Jinja crash later — silent-lie pattern, retired."""
    import inspect

    import scripts.generators.v42.manifest as generator_manifest_module

    source = inspect.getsource(generator_manifest_module)
    assert "MissingSectionTemplateError" in source
    assert 'return f"sections/{step.id}-{_slugify(step.label)}.md.j2"' not in source


def test_l1_exits_structural_when_regeneration_crashes(tmp_path: Path, monkeypatch) -> None:
    """The vacuous-guard kill shot: L1 must FAIL (exit 2), not pass, when
    the pack cannot be regenerated. Crash injected at the render seam —
    equivalent to a removed template reaching L1's regeneration leg."""
    import scripts.utilities.check_pipeline_manifest_lockstep as l1_module

    def _crashing_render(manifest_path, output_path, template_root=None):
        raise MissingSectionTemplateError("synthetic: section template removed")

    import scripts.generators.v42.render as render_module

    monkeypatch.setattr(render_module, "render_pack", _crashing_render)
    exit_code, trace = l1_module.run_check(MANIFEST, DEFAULT_PACK_PATH, None)
    assert exit_code == 2
    assert trace["closure_gate"] == "STRUCTURAL"
    assert any(
        finding["check"] == 9 and "CRASHED" in finding["message"]
        for finding in trace["findings"]
    )


def test_l1_fails_on_hand_edited_pack(tmp_path: Path) -> None:
    """Scenario-E made real: a hand-edit to the committed pack that keeps
    all section ids intact (so checks 1-8 stay green) must still fail the
    regeneration-determinism leg."""
    edited = tmp_path / "edited-pack.md"
    text = DEFAULT_PACK_PATH.read_text(encoding="utf-8")
    edited.write_text(
        text.replace(
            "cross-ref: `docs/workflow/human-in-the-loop.md`",
            "cross-ref: `docs/workflow/human-in-the-loop.md` (hand-edited)",
        ),
        encoding="utf-8",
    )
    exit_code, trace = run_check(MANIFEST, edited, None)
    assert exit_code == 1
    assert any(finding["check"] == 9 for finding in trace["findings"])


def test_l1_passes_on_committed_pack() -> None:
    """Green twin: the committed pack IS the regeneration output."""
    exit_code, trace = run_check(MANIFEST, DEFAULT_PACK_PATH, None)
    assert exit_code == 0, trace
    assert any(
        check["check"] == 9 and check["pass"] for check in trace["l1_checks_run"]
    )
