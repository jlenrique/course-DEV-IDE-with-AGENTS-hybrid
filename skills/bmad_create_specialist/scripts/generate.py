"""Generate scaffold-conformant specialist packages from templates."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

ALLOWED_MCP_TOOLS: frozenset[str] = frozenset(
    {"none", "gamma", "elevenlabs", "canvas", "kling", "wondercraft"}
)
NAME_PATTERN: re.Pattern[str] = re.compile(r"^[a-z][a-z0-9_]*$")
EXPERTISE_TIER_PATTERN: re.Pattern[str] = re.compile(r"^L[3-7]-[a-z0-9]+(?:-[a-z0-9]+)*$")
GENERATOR_DENYLIST: frozenset[str] = frozenset({"bmad-agent-audra", "bmad-agent-cora"})
TEMPLATE_VAR_PATTERN: re.Pattern[str] = re.compile(r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}")


class GeneratorInputError(RuntimeError):
    """Named generator failure for predictable stderr surfaces."""


@dataclass(frozen=True)
class EmissionItem:
    """One planned output file."""

    relative_path: Path
    content: str


@dataclass(frozen=True)
class GenerationResult:
    """Summary of generation output."""

    planned_files: tuple[Path, ...]
    written_files: tuple[Path, ...]
    dry_run: bool


@dataclass(frozen=True)
class GenerationRequest:
    """Structured generator request (CLI or programmatic)."""

    name: str
    mcp_tool: str
    expertise_tier: str
    from_skill: Path | None = None
    dry_run: bool = False
    force: bool = False
    repo_root: Path | None = None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _templates_dir(repo_root: Path) -> Path:
    hyphen_dir = repo_root / "skills" / "bmad-create-specialist" / "templates"
    underscore_dir = repo_root / "skills" / "bmad_create_specialist" / "templates"
    if hyphen_dir.is_dir():
        return hyphen_dir
    if underscore_dir.is_dir():
        return underscore_dir
    raise GeneratorInputError(
        "template directory missing under skills/bmad-create-specialist/templates"
    )


def _class_name(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def _render_template(content: str, context: dict[str, str]) -> str:
    """Replace known {{var}} tokens while preserving unknown literals."""

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return context.get(key, match.group(0))

    return TEMPLATE_VAR_PATTERN.sub(_replace, content)


def _validate_name(name: str) -> None:
    if not NAME_PATTERN.fullmatch(name):
        raise GeneratorInputError(
            f"name {name!r} fails required pattern {NAME_PATTERN.pattern!r}"
        )


def _validate_mcp_tool(mcp_tool: str) -> None:
    if mcp_tool not in ALLOWED_MCP_TOOLS:
        raise GeneratorInputError(
            f"mcp tool {mcp_tool!r} must be one of {sorted(ALLOWED_MCP_TOOLS)}"
        )


def _validate_expertise_tier(expertise_tier: str) -> None:
    if not EXPERTISE_TIER_PATTERN.fullmatch(expertise_tier):
        raise GeneratorInputError(
            f"expertise tier {expertise_tier!r} fails pattern {EXPERTISE_TIER_PATTERN.pattern!r}"
        )


def _validate_from_skill(from_skill: Path | None, repo_root: Path) -> None:
    if from_skill is None:
        return
    resolved = from_skill.resolve()
    skills_root = (repo_root / "skills").resolve()
    if not resolved.is_dir():
        raise GeneratorInputError(f"from-skill path does not exist: {from_skill}")
    if not resolved.is_relative_to(skills_root):
        raise GeneratorInputError(
            f"from-skill path {from_skill} must be under {skills_root}"
        )
    if not resolved.name.startswith("bmad-agent-"):
        raise GeneratorInputError(
            f"from-skill path {from_skill} must target skills/bmad-agent-*/"
        )
    if not (resolved / "SKILL.md").is_file():
        raise GeneratorInputError(f"from-skill path {from_skill} must contain SKILL.md")
    if resolved.name in GENERATOR_DENYLIST:
        raise GeneratorInputError(
            f"skill directory {from_skill} is DISSOLVED per DR-2 (Category D). "
            "If the dissolution decision should be reversed, raise at party-mode "
            "consensus per DR-2 section reversal protocol."
        )


def _assert_within_repo(path: Path, repo_root: Path) -> None:
    resolved = path.resolve()
    root = repo_root.resolve()
    if not resolved.is_relative_to(root):
        raise GeneratorInputError(f"target path escapes workspace root: {path}")


def _planned_items(
    *,
    name: str,
    mcp_tool: str,
    expertise_tier: str,
    repo_root: Path,
) -> list[EmissionItem]:
    templates_dir = _templates_dir(repo_root)
    class_name = _class_name(name)
    context = {
        "name": name,
        "class_name": class_name,
        "mcp_tool": mcp_tool,
        "expertise_tier": expertise_tier,
        "specialist_id": name,
    }

    mapping = [
        ("__init__.py.template", Path("app") / "specialists" / name / "__init__.py"),
        ("graph.py.template", Path("app") / "specialists" / name / "graph.py"),
        ("state.py.template", Path("app") / "specialists" / name / "state.py"),
        (
            "model_config.yaml.template",
            Path("app") / "specialists" / name / "model_config.yaml",
        ),
        (
            "expertise/README.md.template",
            Path("app") / "specialists" / name / "expertise" / "README.md",
        ),
        (
            "test_state_shape.py.template",
            Path("tests") / "specialists" / name / f"test_{name}_state_shape.py",
        ),
        (
            "golden_envelope.json.template",
            Path("tests") / "fixtures" / "specialists" / name / "golden_envelope.json",
        ),
        (
            "golden_return.json.template",
            Path("tests") / "fixtures" / "specialists" / name / "golden_return.json",
        ),
        (
            "test_scaffold_integration.py.template",
            Path("tests")
            / "integration"
            / "scaffold_conformance"
            / f"test_scaffold_{name}.py",
        ),
    ]

    items: list[EmissionItem] = []
    for template_rel, output_rel in mapping:
        template_path = templates_dir / template_rel
        if not template_path.is_file():
            raise GeneratorInputError(f"template missing: {template_path}")
        rendered = _render_template(template_path.read_text(encoding="utf-8"), context)
        items.append(EmissionItem(relative_path=output_rel, content=rendered))
    return items


def _validate_plan_shapes(items: list[EmissionItem]) -> None:
    expected = set(SCAFFOLD_NODE_IDS)
    for item in items:
        suffix = item.relative_path.suffix
        if suffix == ".py":
            ast.parse(item.content, filename=str(item.relative_path))
        elif suffix in {".yaml", ".yml"}:
            yaml.safe_load(item.content)
        elif suffix == ".json":
            json.loads(item.content)
        if item.relative_path.name == "graph.py":
            present = {name for name in expected if f'"{name}"' in item.content}
            if present != expected:
                missing = sorted(expected - present)
                raise GeneratorInputError(
                    f"graph template missing scaffold node ids in {item.relative_path}: {missing}"
                )
            if "resume_from_verdict" not in item.content:
                raise GeneratorInputError(
                    f"graph template must import resume_from_verdict in {item.relative_path}"
                )
        if (
            item.relative_path.name == "state.py"
            and ("ClassVar" not in item.content or "_SPECIALIST_ID" not in item.content)
        ):
            raise GeneratorInputError(
                f"state template must pin specialist id via ClassVar in {item.relative_path}"
            )


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _write_items_atomic(
    *,
    items: list[EmissionItem],
    repo_root: Path,
    force: bool,
    name: str,
) -> tuple[Path, ...]:
    specialist_dir = repo_root / "app" / "specialists" / name
    if specialist_dir.exists() and not force:
        raise GeneratorInputError(
            f"name collision: {specialist_dir} already exists (use --force to overwrite)"
        )

    for item in items:
        _assert_within_repo(repo_root / item.relative_path, repo_root)

    backups: dict[Path, str] = {}
    created: list[Path] = []

    try:
        for item in items:
            destination = repo_root / item.relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                if destination.is_dir():
                    raise GeneratorInputError(
                        f"destination is a directory, expected file: {destination}"
                    )
                if not force:
                    raise GeneratorInputError(
                        f"destination already exists without --force: {destination}"
                    )
                backups[destination] = destination.read_text(encoding="utf-8")
            _write_text(destination, item.content)
            created.append(destination)
    except Exception as exc:  # pragma: no cover - covered through failure tests
        for destination in reversed(created):
            if destination in backups:
                destination.write_text(backups[destination], encoding="utf-8")
            elif destination.exists():
                destination.unlink()
        raise GeneratorInputError(f"atomic emission failed: {exc}") from exc

    return tuple(repo_root / item.relative_path for item in items)


def generate_specialist(
    request: GenerationRequest,
) -> GenerationResult:
    root = (request.repo_root or _repo_root()).resolve()
    _validate_name(request.name)
    _validate_mcp_tool(request.mcp_tool)
    _validate_expertise_tier(request.expertise_tier)
    _validate_from_skill(request.from_skill, root)

    items = _planned_items(
        name=request.name,
        mcp_tool=request.mcp_tool,
        expertise_tier=request.expertise_tier,
        repo_root=root,
    )
    _validate_plan_shapes(items)
    planned = tuple(root / item.relative_path for item in items)

    if request.dry_run:
        return GenerationResult(planned_files=planned, written_files=tuple(), dry_run=True)

    written = _write_items_atomic(
        items=items,
        repo_root=root,
        force=request.force,
        name=request.name,
    )
    return GenerationResult(planned_files=planned, written_files=written, dry_run=False)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a scaffold-conformant specialist")
    parser.add_argument("--name", required=True, help="specialist name")
    parser.add_argument("--mcp", required=True, help="MCP tool hint")
    parser.add_argument("--expertise-tier", required=True, help="expertise tier label")
    parser.add_argument("--from-skill", type=Path, default=None, help="optional source skill path")
    parser.add_argument("--dry-run", action="store_true", help="validate and print plan only")
    parser.add_argument("--force", action="store_true", help="overwrite existing generated files")
    return parser


def parse_args(argv: list[str] | None = None) -> GenerationRequest:
    args = _build_parser().parse_args(argv)
    return GenerationRequest(
        name=args.name,
        mcp_tool=args.mcp,
        expertise_tier=args.expertise_tier,
        from_skill=args.from_skill,
        dry_run=args.dry_run,
        force=args.force,
    )


def main(argv: list[str] | None = None) -> int:
    request = parse_args(argv)
    try:
        result = generate_specialist(request)
    except GeneratorInputError as exc:
        print(f"GeneratorInputError: {exc}", file=sys.stderr)
        return 1

    heading = "DRY-RUN planned emission tree:" if result.dry_run else "Generated files:"
    print(heading)
    relative_paths = [str(path.relative_to(_repo_root())) for path in result.planned_files]
    print(json.dumps(relative_paths, indent=2))

    if result.dry_run:
        print(f"Validated scaffold node ids: {sorted(SCAFFOLD_NODE_IDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
