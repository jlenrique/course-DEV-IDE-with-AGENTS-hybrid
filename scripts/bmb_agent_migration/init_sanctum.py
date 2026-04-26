#!/usr/bin/env python3
"""
BMB sanctum scaffold — generic.

Creates `_bmad/memory/<skill-name>/` from a skill directory that follows the
BMB conformance pattern (Texas-style): `assets/*-template.md`,
`references/*.md` (first-breath.md + BMB seeds + agent-specific), and
`scripts/*.py`. Epic 26 canonical scaffold — all per-agent `init-sanctum.py`
files are thin forwarders to this script.

Version: 0.2 (2026-04-17). Post-pilot fleet-wide fix cycle (Story 26-4).

Usage:
    python scripts/bmb_agent_migration/init_sanctum.py --skill-path <path> [--dry-run]

Arguments:
    --skill-path   Path to the skill directory (contains SKILL.md, assets/, references/, scripts/).
                   Skill name is derived from the directory basename.
    --project-root Optional override for the repo root (default: auto-discover via .git).
    --dry-run      Print the tree that would be created; do not write anything.
    --force        Permit overwriting an existing sanctum (default: fail-closed).

Behavior:
    1. Validates the skill directory shape (assets/ + references/ present).
    2. Loads config from (in priority order, later overrides earlier):
         - `_bmad/core/config.yaml`  (BMB core config — canonical user_name source)
         - `_bmad/config.yaml`       (repo-level override, optional)
         - `_bmad/config.user.yaml`  (user-level override, optional)
    3. Discovers `assets/*-template.md` and renders each to the sanctum with {var} substitution.
    4. Renders `references/*.md` into `<sanctum>/references/` with the same known-variable
       whitelist (unknown `{...}` tokens survive unchanged). Excludes SKILL_ONLY_FILES.
    5. Copies `scripts/*.py` into `<sanctum>/scripts/` except `init-sanctum.py`.
    6. Auto-generates `CAPABILITIES.md` by scanning references frontmatter for `code:` + `name:`.
    7. Creates `sessions/` and `capabilities/` subdirectories.

Variable substitution (whitelist — foreign `{...}` tokens preserved):
    {user_name}                — from config overlay, default "friend"
    {communication_language}   — from config overlay, default "English"
    {document_output_language} — from config overlay, default "English"
    {birth_date}               — today's date (YYYY-MM-DD)
    {project_root}             — absolute path to repo root
    {sanctum_path}             — POSIX-relative `_bmad/memory/<skill-name>` (portable)
    {skill_name}               — basename of --skill-path
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

SCAFFOLD_VERSION = "0.2"

# Files that stay in the skill bundle (used during First Breath, not migrated to sanctum).
# Additional skill-only files can be added via `.bmb-scaffold-config.yaml` in the skill dir
# (key: `skill_only_files: [filename, ...]`). Kept minimal intentionally.
DEFAULT_SKILL_ONLY_FILES = {"first-breath.md"}

# Scripts never migrated regardless of agent (both hyphen and underscore variants
# appear across the fleet — exclude defensively so a forwarder named either way
# is never copied recursively into its own sanctum).
SCRIPT_EXCLUSIONS = {"init-sanctum.py", "init_sanctum.py"}


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    raise FileNotFoundError(f"No .git directory found above {start}")


def parse_yaml_config(path: Path) -> dict:
    """Minimal YAML parser (top-level scalars and simple lists)."""
    config: dict = {}
    if not path.exists():
        return config
    current_list_key = None
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            raw = line.rstrip("\n")
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("- ") and current_list_key:
                config[current_list_key].append(stripped[2:].strip().strip("'\""))
                continue
            current_list_key = None
            if ":" in stripped:
                key, _, value = stripped.partition(":")
                value = value.strip().strip("'\"")
                key = key.strip()
                if value == "":
                    config[key] = []
                    current_list_key = key
                else:
                    config[key] = value
    return config


def parse_frontmatter(path: Path) -> dict:
    meta: dict = {}
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return meta
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return meta
    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip("'\"")
    return meta


def discover_template_files(assets_dir: Path) -> list[Path]:
    if not assets_dir.exists():
        return []
    return sorted(p for p in assets_dir.glob("*-template.md") if p.is_file())


def substitute_vars(content: str, variables: dict[str, str]) -> str:
    for key, value in variables.items():
        content = content.replace("{" + key + "}", value)
    return content


def resolve_skill_only_files(skill_path: Path) -> set[str]:
    config = parse_yaml_config(skill_path / ".bmb-scaffold-config.yaml")
    extras = set(config.get("skill_only_files", []) or [])
    return DEFAULT_SKILL_ONLY_FILES | extras


def resolve_evolvable(skill_path: Path) -> bool:
    config = parse_yaml_config(skill_path / ".bmb-scaffold-config.yaml")
    raw = config.get("evolvable", "true")
    return str(raw).strip().lower() not in {"false", "0", "no"}


def discover_capabilities(references_dir: Path, skill_only: set[str]) -> list[dict]:
    capabilities: list[dict] = []
    seen_codes: dict[str, str] = {}  # code -> source file (for duplicate detection)
    for md_file in sorted(references_dir.glob("*.md")):
        if md_file.name in skill_only:
            continue
        meta = parse_frontmatter(md_file)
        name = meta.get("name")
        code = meta.get("code")
        if name and code:
            if code in seen_codes:
                raise ValueError(
                    f"Duplicate capability code '{code}' in {md_file.name}; "
                    f"already declared by {seen_codes[code]}. "
                    "Codes must be unique — capability dispatch is ambiguous otherwise."
                )
            seen_codes[code] = md_file.name
            capabilities.append({
                "name": name,
                "description": meta.get("description", ""),
                "code": code,
                "source": f"./references/{md_file.name}",
            })
        elif code and not name:
            # Declared `code:` but no `name:` — clear intent to register a capability
            # but missing the display name. Surface loudly.
            print(
                f"WARNING: {md_file.name} declares 'code: {code}' but has no 'name:'. "
                "Capability will NOT be registered — add 'name:' or remove 'code:'.",
                file=sys.stderr,
            )
        # Note: `name:` alone (no `code:`) is intentional for informational refs
        # (delegation registries, knowledge docs) — not warned.
    return capabilities


_SCRIPT_PURPOSE_RE = re.compile(
    r'^\s*(?P<q>"""|\'\'\')\s*(?P<body>[^\n\'"]+)',
    re.MULTILINE,
)


def script_purpose(script_path: Path) -> str:
    """Extract a one-line purpose from a Python script's module docstring.

    Falls back to a sentinel that signals the author to add documentation.
    """
    try:
        content = script_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "_(unreadable)_"
    match = _SCRIPT_PURPOSE_RE.search(content)
    if match:
        return match.group("body").strip().rstrip(".")
    return "_(add module docstring)_"


def render_capabilities_md(
    capabilities: list[dict],
    evolvable: bool,
    scripts_in_sanctum: list[str],
    scripts_dir: Path | None = None,
) -> str:
    lines = [
        "# Capabilities",
        "",
        "## Built-in",
        "",
        "| Code | Name | Description | Source |",
        "|------|------|-------------|--------|",
    ]
    if capabilities:
        for cap in capabilities:
            lines.append(
                f"| [{cap['code']}] | {cap['name']} | {cap['description']} | `{cap['source']}` |"
            )
    else:
        lines.append("| _(none discovered — add `name:` + `code:` frontmatter to reference files to register)_ | | | |")

    if evolvable:
        lines.extend([
            "",
            "## Learned",
            "",
            "_Capabilities added by the owner over time. Prompts live in `capabilities/`._",
            "",
            "| Code | Name | Description | Source | Added |",
            "|------|------|-------------|--------|-------|",
            "",
            "## How to Add a Capability",
            "",
            'Tell me "I want you to be able to do X" and we\'ll create it together.',
            "I'll write the prompt, save it to `capabilities/`, and register it here.",
            "Next session, I'll know how.",
            "Load `./references/capability-authoring.md` for the full creation framework.",
        ])

    lines.extend([
        "",
        "## Tools",
        "",
        "### Scripts",
        "",
        "| Script | Purpose |",
        "|--------|---------|",
    ])
    if scripts_in_sanctum:
        for name in scripts_in_sanctum:
            purpose = (
                script_purpose(scripts_dir / name)
                if scripts_dir is not None and (scripts_dir / name).exists()
                else "_(add module docstring)_"
            )
            lines.append(f"| `./scripts/{name}` | {purpose} |")
    else:
        lines.append("| _(no scripts migrated)_ | |")

    lines.extend([
        "",
        "### User-Provided Tools",
        "",
        "_MCP servers, APIs, or services the owner has made available._",
    ])

    return "\n".join(lines) + "\n"


def plan_actions(
    skill_path: Path,
    sanctum_path: Path,
    variables: dict[str, str],
    skill_only: set[str],
    evolvable: bool,
) -> dict:
    """Produce a plan describing what the real run would do."""
    assets_dir = skill_path / "assets"
    references_dir = skill_path / "references"
    scripts_dir = skill_path / "scripts"

    templates = discover_template_files(assets_dir)
    references = sorted(
        p.name for p in references_dir.glob("*.md")
        if p.is_file() and p.name not in skill_only
    ) if references_dir.exists() else []
    scripts = sorted(
        p.name for p in scripts_dir.glob("*.py")
        if p.is_file() and p.name not in SCRIPT_EXCLUSIONS
    ) if scripts_dir.exists() else []

    sanctum_files = []
    for tmpl in templates:
        # Strip "-template" suffix, uppercase the stem, always restore lowercase ".md".
        # Previous version left ".MD" for any template not already ending in ".md" —
        # fragile on case-sensitive filesystems.
        stem = tmpl.stem.replace("-template", "")
        sanctum_files.append(stem.upper() + ".md")

    # Guard against collisions (case-insensitive FS would silently overwrite).
    if len(set(sanctum_files)) != len(sanctum_files):
        seen: dict[str, str] = {}
        for tmpl, out in zip(templates, sanctum_files):
            if out in seen:
                raise ValueError(
                    f"Template output name collision: '{tmpl.name}' and "
                    f"'{seen[out]}' both render to '{out}'. Rename one template."
                )
            seen[out] = tmpl.name

    capabilities = discover_capabilities(references_dir, skill_only) if references_dir.exists() else []
    capabilities_preview = render_capabilities_md(capabilities, evolvable, scripts, scripts_dir if scripts_dir.exists() else None)

    return {
        "sanctum_path": sanctum_path,
        "templates": [t.name for t in templates],
        "sanctum_files": sanctum_files,
        "references_copied": references,
        "scripts_copied": scripts,
        "capabilities": capabilities,
        "capabilities_preview": capabilities_preview,
        "variables": variables,
        "evolvable": evolvable,
    }


def print_plan(plan: dict, skill_name: str) -> None:
    print(f"BMB Sanctum Scaffold v{SCAFFOLD_VERSION} — DRY RUN")
    print(f"Skill: {skill_name}")
    print(f"Target sanctum: {plan['sanctum_path']}")
    print()
    print("Would create directories:")
    print(f"  {plan['sanctum_path']}/")
    print(f"  {plan['sanctum_path']}/sessions/")
    print(f"  {plan['sanctum_path']}/capabilities/")
    print(f"  {plan['sanctum_path']}/references/")
    print(f"  {plan['sanctum_path']}/scripts/")
    print()
    print(f"Would render {len(plan['templates'])} templates from assets/:")
    for tmpl, out in zip(plan["templates"], plan["sanctum_files"]):
        print(f"  {tmpl} -> {out}")
    print()
    print(f"Would copy {len(plan['references_copied'])} reference files:")
    for ref in plan["references_copied"]:
        print(f"  references/{ref}")
    print()
    print(f"Would copy {len(plan['scripts_copied'])} scripts:")
    for s in plan["scripts_copied"]:
        print(f"  scripts/{s}")
    print()
    print(f"Would discover {len(plan['capabilities'])} capabilities via frontmatter:")
    for cap in plan["capabilities"]:
        print(f"  [{cap['code']}] {cap['name']}")
    print()
    print("Variable substitutions:")
    for k, v in plan["variables"].items():
        print(f"  {{{k}}} -> {v}")


def execute_plan(plan: dict, skill_path: Path, force: bool) -> int:
    sanctum_path: Path = plan["sanctum_path"]

    if sanctum_path.exists() and not force:
        has_content = any(sanctum_path.iterdir()) if sanctum_path.is_dir() else False
        if has_content and (sanctum_path / "INDEX.md").exists():
            print(f"Sanctum already exists at {sanctum_path}")
            print("Agent has already been born. Skipping First Breath scaffolding.")
            print("Pass --force to overwrite (destructive).")
            return 0

    sanctum_path.mkdir(parents=True, exist_ok=True)
    (sanctum_path / "sessions").mkdir(exist_ok=True)
    (sanctum_path / "capabilities").mkdir(exist_ok=True)

    # EC-B fix: on --force re-render of an existing sanctum, purge stale files
    # that no longer correspond to a skill-bundle source. Covers:
    # - Top-level *.md that aren't in plan["sanctum_files"] + CAPABILITIES.md
    #   (e.g., a PERSONA-template.md renamed in assets/ would otherwise leave
    #   an orphan PERSONA.md alongside the new name).
    # - references/*.md that aren't in plan["references_copied"] (upstream deletion drift).
    # - scripts/*.py that aren't in plan["scripts_copied"] (upstream deletion drift).
    # Never touches sessions/ or capabilities/ (operator-authored content).
    if force:
        expected_top = set(plan["sanctum_files"]) | {"CAPABILITIES.md"}
        for p in sanctum_path.glob("*.md"):
            if p.name not in expected_top:
                p.unlink()
        expected_refs = set(plan["references_copied"])
        refs_dir = sanctum_path / "references"
        if refs_dir.exists():
            for p in refs_dir.glob("*.md"):
                if p.name not in expected_refs:
                    p.unlink()
        expected_scripts = set(plan["scripts_copied"])
        scripts_sanctum_dir = sanctum_path / "scripts"
        if scripts_sanctum_dir.exists():
            for p in scripts_sanctum_dir.glob("*.py"):
                if p.name not in expected_scripts:
                    p.unlink()

    assets_dir = skill_path / "assets"
    references_dir = skill_path / "references"
    scripts_dir = skill_path / "scripts"

    # Render references (V2-3 fix: substitute known variables so {sanctum_path} etc.
    # don't survive as literal curly-brace text in sanctum refs. Because substitute_vars
    # only replaces the 6 known-key tokens, any foreign {...} token survives unchanged —
    # so activation-time templates authored by the agent's references are preserved.)
    sanctum_refs = sanctum_path / "references"
    sanctum_refs.mkdir(exist_ok=True)
    for name in plan["references_copied"]:
        src = references_dir / name
        rendered = substitute_vars(src.read_text(encoding="utf-8"), plan["variables"])
        (sanctum_refs / name).write_text(rendered, encoding="utf-8")

    # Copy scripts (selective)
    sanctum_scripts = sanctum_path / "scripts"
    sanctum_scripts.mkdir(exist_ok=True)
    for name in plan["scripts_copied"]:
        shutil.copy2(scripts_dir / name, sanctum_scripts / name)

    # Render templates
    for tmpl_name, out_name in zip(plan["templates"], plan["sanctum_files"]):
        src = assets_dir / tmpl_name
        rendered = substitute_vars(src.read_text(encoding="utf-8"), plan["variables"])
        (sanctum_path / out_name).write_text(rendered, encoding="utf-8")

    # Render CAPABILITIES.md (overwrites template output if one was named CAPABILITIES.md — intentional)
    (sanctum_path / "CAPABILITIES.md").write_text(plan["capabilities_preview"], encoding="utf-8")

    # .gitkeep for empty dirs so git tracks them
    for sub in ("sessions", "capabilities"):
        keep = sanctum_path / sub / ".gitkeep"
        if not keep.exists() and not any((sanctum_path / sub).iterdir()):
            keep.write_text("", encoding="utf-8")

    print(f"BMB Sanctum Scaffold v{SCAFFOLD_VERSION} — COMPLETE")
    print(f"Sanctum written to: {sanctum_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    # Windows default cp1252 stdout crashes on non-ASCII in print_plan (e.g., user_name=José).
    # Reconfigure to UTF-8 with replacement so the tool never crashes on its own output.
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except AttributeError:
            pass  # older Python; tolerated — tests inject PYTHONIOENCODING=utf-8

    parser = argparse.ArgumentParser(description=f"BMB sanctum scaffold v{SCAFFOLD_VERSION}")
    parser.add_argument("--skill-path", type=Path, required=True,
                        help="Path to the skill directory (contains SKILL.md + assets/ + references/).")
    parser.add_argument("--project-root", type=Path, default=None,
                        help="Repo root override (default: auto-discover via .git).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the plan without writing.")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite an existing sanctum.")
    args = parser.parse_args(argv)

    skill_path = args.skill_path.resolve()
    if not skill_path.exists():
        print(f"ERROR: skill path does not exist: {skill_path}", file=sys.stderr)
        return 2
    if not (skill_path / "SKILL.md").exists():
        print(f"ERROR: no SKILL.md at {skill_path}", file=sys.stderr)
        return 2

    project_root = (args.project_root or find_repo_root(skill_path)).resolve()
    bmad_dir = project_root / "_bmad"
    memory_dir = bmad_dir / "memory"

    skill_name = skill_path.name
    sanctum_path = memory_dir / skill_name

    # EC-A guard: refuse to scaffold into a workspace that isn't an ancestor of
    # the skill. Prevents typo-level --project-root mistakes from polluting a
    # foreign workspace (e.g., `--project-root C:/Windows` silently mkdir-ing
    # into system directories). Uses string-prefix on resolved paths because
    # Path.is_relative_to is Py3.9+ — be explicit for clarity.
    try:
        skill_path.relative_to(project_root)
    except ValueError:
        print(
            f"ERROR: --skill-path ({skill_path}) is not inside --project-root ({project_root}).\n"
            "  The scaffold would mkdir into an unrelated workspace. Refusing.",
            file=sys.stderr,
        )
        return 2

    # Load config (V2-1 fix: read _bmad/core/config.yaml as the BMB-canonical base).
    # Overlay order (later overrides earlier):
    #   _bmad/core/config.yaml   — canonical user_name / communication_language source
    #   _bmad/config.yaml        — repo-level override (if present)
    #   _bmad/config.user.yaml   — user-level override (if present)
    config: dict = {}
    for cfg in (
        bmad_dir / "core" / "config.yaml",
        bmad_dir / "config.yaml",
        bmad_dir / "config.user.yaml",
    ):
        config.update(parse_yaml_config(cfg))

    # V2-2 fix: sanctum_path must substitute to a repo-relative POSIX path
    # (portable across OSes; previously absolute — Windows drive letters leaked
    # into committed sanctum files).
    sanctum_relative = sanctum_path.relative_to(project_root).as_posix()

    today = date.today().isoformat()
    variables = {
        "user_name": config.get("user_name", "friend"),
        "communication_language": config.get("communication_language", "English"),
        "document_output_language": config.get("document_output_language", "English"),
        "birth_date": today,
        "project_root": str(project_root),
        "sanctum_path": sanctum_relative,
        "skill_name": skill_name,
    }

    skill_only = resolve_skill_only_files(skill_path)
    evolvable = resolve_evolvable(skill_path)

    plan = plan_actions(skill_path, sanctum_path, variables, skill_only, evolvable)

    # Warn loudly when the shape doesn't match what downstream migrations expect.
    # These are not errors — some agents legitimately ship with fewer assets — but
    # the BMB pattern assumes a 6-file sanctum + ≥1 capability, so surface the gap.
    if len(plan["templates"]) < 6:
        print(
            f"WARNING: only {len(plan['templates'])} template(s) in assets/ — "
            "BMB canonical pattern expects 6 (INDEX/PERSONA/CREED/BOND/MEMORY/CAPABILITIES).",
            file=sys.stderr,
        )
    if len(plan["capabilities"]) == 0:
        print(
            "WARNING: no capabilities discovered in references/ — add 'name:' + 'code:' "
            "frontmatter to capability reference files so CAPABILITIES.md auto-populates.",
            file=sys.stderr,
        )

    if args.dry_run:
        print_plan(plan, skill_name)
        return 0

    return execute_plan(plan, skill_path, args.force)


if __name__ == "__main__":
    raise SystemExit(main())
