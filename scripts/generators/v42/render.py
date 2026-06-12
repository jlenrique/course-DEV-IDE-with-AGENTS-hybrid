"""Render v4.2 pack from pipeline manifest and templates."""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.generators.v42.env import make_env
from scripts.generators.v42.manifest import load_generator_manifest
from scripts.utilities.workflow_policy import load_workflow_policy


def render_pack(
    manifest_path: Path,
    output_path: Path,
    template_root: Path | None = None,
) -> None:
    """Render pack markdown at the requested output path.

    ``template_root`` overrides the bundled templates directory — the seam
    Pin B's template-removal red-tests exercise (renderer/L1 story).
    """
    generator_manifest = load_generator_manifest(manifest_path, template_root)
    workflow_policy = load_workflow_policy()
    env = make_env(template_root)
    template = env.get_template("layout/pack.md.j2")
    content = template.render(
        steps=generator_manifest.steps,
        workflow_policy=workflow_policy,
        **workflow_policy,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8", newline="\n")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render v4.2 prompt pack from manifest")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main() -> int:
    args = _parser().parse_args()
    render_pack(args.manifest, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
