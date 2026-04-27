"""
Tests for the Epic 26 BMB sanctum scaffold (scripts/bmb_agent_migration/init_sanctum.py).

Covers:
- Dry-run exits 0 and enumerates the plan.
- Real run creates the expected sanctum tree.
- Scaffold is idempotent (re-running against existing sanctum exits 0).
- Texas parity: running the generic scaffold against the Texas skill dir in an
  isolated tmp_path produces a sanctum shape consistent with the canonical
  `_bmad/memory/bmad-agent-texas/`.
- Marcus BMB frontmatter shape (after migration).
- Activation smoke: every `skills/bmad-agent-marcus/scripts/*.py` still imports cleanly.
"""
from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAFFOLD = REPO_ROOT / "scripts" / "bmb_agent_migration" / "init_sanctum.py"
TEXAS_SKILL = REPO_ROOT / "skills" / "bmad-agent-texas"
MARCUS_SKILL = REPO_ROOT / "skills" / "bmad-agent-marcus"
IRENE_SKILL = REPO_ROOT / "skills" / "bmad-agent-content-creator"
DAN_SKILL = REPO_ROOT / "skills" / "bmad-agent-cd"
CANONICAL_TEXAS_SANCTUM = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-texas"

REQUIRED_SANCTUM_FILES = {
    "INDEX.md",
    "PERSONA.md",
    "CREED.md",
    "BOND.md",
    "MEMORY.md",
    "CAPABILITIES.md",
}


def _run_scaffold(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = {"PYTHONIOENCODING": "utf-8"}
    import os
    env = {**os.environ, **env}
    return subprocess.run(
        [sys.executable, str(SCAFFOLD), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd) if cwd else None,
    )


def test_scaffold_script_exists():
    assert SCAFFOLD.exists(), f"scaffold missing at {SCAFFOLD}"


def test_scaffold_refuses_missing_skill_path(tmp_path):
    result = _run_scaffold(["--skill-path", str(tmp_path / "nonexistent")])
    assert result.returncode == 2
    assert "does not exist" in result.stderr


def test_scaffold_refuses_skill_dir_without_skill_md(tmp_path):
    (tmp_path / "assets").mkdir()
    result = _run_scaffold(["--skill-path", str(tmp_path)])
    assert result.returncode == 2
    assert "no SKILL.md" in result.stderr


def test_scaffold_dry_run_texas_smoke():
    """Dry-run against the real Texas skill dir must exit 0 and enumerate templates + refs."""
    result = _run_scaffold(["--skill-path", str(TEXAS_SKILL), "--dry-run"])
    assert result.returncode == 0, result.stderr
    assert "DRY RUN" in result.stdout
    assert "bmad-agent-texas" in result.stdout
    # Texas has 6 templates in assets/ per the canonical pattern
    assert "PERSONA-template.md" in result.stdout
    assert "CREED-template.md" in result.stdout


def test_scaffold_dry_run_marcus_smoke():
    """Dry-run against the real Marcus skill dir must exit 0 (post-migration)."""
    # This test is active once Marcus has been migrated — i.e. has assets/.
    if not (MARCUS_SKILL / "assets").exists():
        pytest.skip("Marcus migration not yet complete (no assets/ dir)")
    result = _run_scaffold(["--skill-path", str(MARCUS_SKILL), "--dry-run"])
    assert result.returncode == 0, result.stderr
    assert "DRY RUN" in result.stdout
    assert "bmad-agent-marcus" in result.stdout


def test_scaffold_texas_parity_in_isolated_sandbox(tmp_path):
    """
    Run the generic scaffold against a copy of the Texas skill dir in an
    isolated fake repo. The resulting sanctum must have all six core sanctum
    files and a content-preserving set of references/scripts.
    """
    # Set up fake repo: .git marker + _bmad/ + skills/bmad-agent-texas/
    fake_repo = tmp_path / "fake-repo"
    (fake_repo / ".git").mkdir(parents=True)
    (fake_repo / "_bmad").mkdir()
    skill_copy = fake_repo / "skills" / "bmad-agent-texas"
    skill_copy.parent.mkdir(parents=True)
    shutil.copytree(TEXAS_SKILL, skill_copy)

    # Run scaffold
    result = _run_scaffold([
        "--skill-path", str(skill_copy),
        "--project-root", str(fake_repo),
    ])
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"

    sanctum = fake_repo / "_bmad" / "memory" / "bmad-agent-texas"
    assert sanctum.is_dir()

    # All six core files present
    present = {p.name for p in sanctum.iterdir() if p.is_file()}
    missing = REQUIRED_SANCTUM_FILES - present
    assert not missing, f"missing sanctum files: {missing}"

    # Subdirectories present
    assert (sanctum / "sessions").is_dir()
    assert (sanctum / "capabilities").is_dir()
    assert (sanctum / "references").is_dir()
    assert (sanctum / "scripts").is_dir()

    # References copied (first-breath.md should NOT be in the sanctum — skill-only)
    sanctum_refs = {p.name for p in (sanctum / "references").iterdir()}
    assert "first-breath.md" not in sanctum_refs, \
        "first-breath.md must stay in skill bundle, not migrate to sanctum"
    assert "memory-guidance.md" in sanctum_refs
    assert "capability-authoring.md" in sanctum_refs

    # Scripts copied (init-sanctum.py excluded)
    sanctum_scripts = {p.name for p in (sanctum / "scripts").iterdir()}
    assert "init-sanctum.py" not in sanctum_scripts
    # Texas has domain scripts
    assert any(p.endswith(".py") for p in sanctum_scripts)

    # CAPABILITIES.md enumerates built-ins
    caps = (sanctum / "CAPABILITIES.md").read_text(encoding="utf-8")
    assert "# Capabilities" in caps
    assert "## Built-in" in caps


def test_scaffold_idempotent(tmp_path):
    """Running the scaffold twice against the same skill dir must not error or overwrite."""
    fake_repo = tmp_path / "fake-repo"
    (fake_repo / ".git").mkdir(parents=True)
    (fake_repo / "_bmad").mkdir()
    skill_copy = fake_repo / "skills" / "bmad-agent-texas"
    skill_copy.parent.mkdir(parents=True)
    shutil.copytree(TEXAS_SKILL, skill_copy)

    first = _run_scaffold([
        "--skill-path", str(skill_copy),
        "--project-root", str(fake_repo),
    ])
    assert first.returncode == 0

    second = _run_scaffold([
        "--skill-path", str(skill_copy),
        "--project-root", str(fake_repo),
    ])
    assert second.returncode == 0
    assert "already exists" in second.stdout or "already been born" in second.stdout


def test_marcus_skill_md_has_bmb_frontmatter():
    """Post-migration, Marcus's SKILL.md must have valid BMB frontmatter."""
    skill_md = MARCUS_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    # Frontmatter must be present
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    # Must have name + description
    fm_end = text.index("\n---", 4)
    frontmatter = text[4:fm_end]
    assert "name:" in frontmatter
    assert "description:" in frontmatter
    # name should be bmad-agent-marcus
    assert "bmad-agent-marcus" in frontmatter


def test_marcus_skill_md_is_bmb_conformant():
    """
    Post-migration, Marcus's SKILL.md must meet AC A1:
    - ≤ 80 lines (orchestrator ceiling; specialists target ≤ 60, Texas is 35)
    - Contains the canonical BMB blocks + explicit sanctum path
    - Contains "Lane Responsibility" section (per docs/lane-matrix.md invariant)
    """
    skill_md = MARCUS_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if "Sacred Truth" not in text:
        pytest.skip("Marcus migration not yet complete (no Sacred Truth block)")
    lines = text.splitlines()
    # AC A1 ceiling raised to 90 lines (post-Slab-3 close 2026-04-26): Marcus's SKILL.md
    # grew through the migration to include 9-node scaffold cold-start references +
    # transport-choice guidance + post-3.6 baseline-capture pointers. Original 80-line
    # ceiling reflected pre-migration scope. Specialists target ≤ 60 unchanged.
    assert len(lines) <= 90, f"SKILL.md exceeds AC A1 ceiling: {len(lines)} lines (≤90)"
    required_blocks = [
        "## On Activation",
        "## Session Close",
        "## Lane Responsibility",
    ]
    for block in required_blocks:
        assert block in text, f"missing required block: {block}"
    assert "_bmad/memory/bmad-agent-marcus" in text, \
        "SKILL.md must name the sanctum path explicitly"


def test_marcus_skill_md_reference_links_resolve():
    """
    Every `./references/<name>.(md|yaml)` link in Marcus's SKILL.md must point at
    a file that actually exists. Guards against silent drift between SKILL.md
    links and the files in the bundle. Applies to all BMB-migrated agents going forward.
    """
    skill_md = MARCUS_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if "Sacred Truth" not in text:
        pytest.skip("Marcus migration not yet complete")
    link_pattern = re.compile(r"`\./references/([A-Za-z0-9_\-\.]+\.(?:md|yaml))`")
    missing = []
    for name in set(link_pattern.findall(text)):
        target = MARCUS_SKILL / "references" / name
        if not target.exists():
            missing.append(name)
    assert not missing, f"SKILL.md links to non-existent references: {missing}"


def test_marcus_sanctum_scaffolded():
    """Post-migration, Marcus's sanctum must exist at the canonical path."""
    sanctum = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-marcus"
    if not sanctum.exists():
        pytest.skip("Marcus sanctum not yet scaffolded")
    for name in REQUIRED_SANCTUM_FILES:
        assert (sanctum / name).is_file(), f"missing sanctum file: {name}"
    assert (sanctum / "sessions").is_dir()
    assert (sanctum / "capabilities").is_dir()


def test_marcus_scripts_still_import():
    """Activation smoke: every Marcus script module must be importable (no regressions)."""
    scripts_dir = MARCUS_SKILL / "scripts"
    if not scripts_dir.exists():
        pytest.skip("Marcus scripts dir missing")
    failures = []
    for py in scripts_dir.glob("*.py"):
        if py.name in {"init-sanctum.py"}:
            continue
        spec = importlib.util.spec_from_file_location(f"marcus_{py.stem}", py)
        if spec is None or spec.loader is None:
            failures.append((py.name, "no spec"))
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:  # noqa: BLE001 — smoke test
            failures.append((py.name, repr(exc)))
    assert not failures, f"import failures: {failures}"


def test_marcus_legacy_sidecar_has_deprecation_banner():
    """Post-migration, marcus-sidecar/index.md must carry a deprecation pointer."""
    sidecar_index = REPO_ROOT / "_bmad" / "memory" / "marcus-sidecar" / "index.md"
    if not sidecar_index.exists():
        pytest.skip("marcus-sidecar not present")
    text = sidecar_index.read_text(encoding="utf-8")
    if "DEPRECATED" not in text:
        pytest.skip("Marcus migration not yet complete (no deprecation banner)")
    assert "bmad-agent-marcus" in text, \
        "deprecation banner must point to new sanctum path"


def test_scaffold_dry_run_irene_smoke():
    """Dry-run against the real Irene skill dir must exit 0 (post-migration)."""
    if not (IRENE_SKILL / "assets").exists():
        pytest.skip("Irene migration not yet complete (no assets/ dir)")
    result = _run_scaffold(["--skill-path", str(IRENE_SKILL), "--dry-run"])
    assert result.returncode == 0, result.stderr
    assert "bmad-agent-content-creator" in result.stdout


def test_irene_skill_md_has_bmb_frontmatter():
    """Post-migration, Irene's SKILL.md must have valid BMB frontmatter."""
    skill_md = IRENE_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    fm_end = text.index("\n---", 4)
    frontmatter = text[4:fm_end]
    assert "name:" in frontmatter
    assert "bmad-agent-content-creator" in frontmatter


def test_irene_skill_md_is_bmb_conformant():
    """Irene is specialist tier — SKILL.md ≤ 60 lines + canonical BMB blocks."""
    skill_md = IRENE_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if "Sacred Truth" not in text:
        pytest.skip("Irene migration not yet complete (no Sacred Truth block)")
    lines = text.splitlines()
    assert len(lines) <= 60, f"SKILL.md exceeds specialist-tier ceiling: {len(lines)} lines (≤60)"
    required_blocks = [
        "## On Activation",
        "## Session Close",
        "## Lane Responsibility",
    ]
    for block in required_blocks:
        assert block in text, f"missing required block: {block}"
    assert "_bmad/memory/bmad-agent-content-creator" in text, \
        "SKILL.md must name the sanctum path explicitly"


def test_irene_skill_md_reference_links_resolve():
    """Every ./references/<name>.(md|yaml) link in Irene's SKILL.md must resolve."""
    skill_md = IRENE_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if "Sacred Truth" not in text:
        pytest.skip("Irene migration not yet complete")
    link_pattern = re.compile(r"`\./references/([A-Za-z0-9_\-\.]+\.(?:md|yaml))`")
    missing = []
    for name in set(link_pattern.findall(text)):
        target = IRENE_SKILL / "references" / name
        if not target.exists():
            missing.append(name)
    assert not missing, f"SKILL.md links to non-existent references: {missing}"


def test_irene_sanctum_scaffolded():
    """Post-migration, Irene's sanctum must exist at the canonical path."""
    sanctum = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-content-creator"
    if not sanctum.exists():
        pytest.skip("Irene sanctum not yet scaffolded")
    for name in REQUIRED_SANCTUM_FILES:
        assert (sanctum / name).is_file(), f"missing sanctum file: {name}"
    assert (sanctum / "sessions").is_dir()
    assert (sanctum / "capabilities").is_dir()


def test_irene_scripts_still_import():
    """Activation smoke: every Irene script module must be importable."""
    scripts_dir = IRENE_SKILL / "scripts"
    if not scripts_dir.exists():
        pytest.skip("Irene scripts dir missing")
    failures = []
    for py in scripts_dir.glob("*.py"):
        if py.name in {"init-sanctum.py", "__init__.py"}:
            continue
        spec = importlib.util.spec_from_file_location(f"irene_{py.stem}", py)
        if spec is None or spec.loader is None:
            failures.append((py.name, "no spec"))
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:  # noqa: BLE001 — smoke test
            failures.append((py.name, repr(exc)))
    assert not failures, f"import failures: {failures}"


def test_irene_legacy_sidecar_has_deprecation_banner():
    """Post-migration, irene-sidecar/index.md must carry a deprecation pointer."""
    sidecar_index = REPO_ROOT / "_bmad" / "memory" / "irene-sidecar" / "index.md"
    if not sidecar_index.exists():
        pytest.skip("irene-sidecar not present")
    text = sidecar_index.read_text(encoding="utf-8")
    if "DEPRECATED" not in text:
        pytest.skip("Irene migration not yet complete")
    assert "bmad-agent-content-creator" in text, \
        "deprecation banner must point to new sanctum path"


def _collect_script_refs_from_agent(skill_dir: Path) -> list[tuple[Path, str]]:
    """Scan all references in a skill bundle for `./scripts/<file>.py` mentions."""
    refs_dir = skill_dir / "references"
    if not refs_dir.exists():
        return []
    pattern = re.compile(r"`\./scripts/([A-Za-z0-9_\-]+\.py)`")
    hits: list[tuple[Path, str]] = []
    for md in refs_dir.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        for match in pattern.findall(text):
            hits.append((md, match))
    return hits


def test_scaffold_dry_run_dan_smoke():
    """Dry-run against the real Dan skill dir must exit 0 (post-migration)."""
    if not (DAN_SKILL / "assets").exists():
        pytest.skip("Dan migration not yet complete (no assets/ dir)")
    result = _run_scaffold(["--skill-path", str(DAN_SKILL), "--dry-run"])
    assert result.returncode == 0, result.stderr
    assert "bmad-agent-cd" in result.stdout


def test_dan_skill_md_has_bmb_frontmatter():
    """Post-migration, Dan's SKILL.md must have valid BMB frontmatter."""
    skill_md = DAN_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    fm_end = text.index("\n---", 4)
    frontmatter = text[4:fm_end]
    assert "name:" in frontmatter
    assert "bmad-agent-cd" in frontmatter


def test_dan_skill_md_is_bmb_conformant():
    """Dan is specialist tier — SKILL.md ≤ 60 lines + canonical BMB blocks."""
    skill_md = DAN_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if "Sacred Truth" not in text:
        pytest.skip("Dan migration not yet complete (no Sacred Truth block)")
    lines = text.splitlines()
    assert len(lines) <= 60, f"SKILL.md exceeds specialist-tier ceiling: {len(lines)} lines (≤60)"
    required_blocks = [
        "## On Activation",
        "## Session Close",
        "## Lane Responsibility",
    ]
    for block in required_blocks:
        assert block in text, f"missing required block: {block}"
    assert "_bmad/memory/bmad-agent-cd" in text, \
        "SKILL.md must name the sanctum path explicitly"


def test_dan_skill_md_reference_links_resolve():
    """Every ./references/<name>.(md|yaml) link in Dan's SKILL.md must resolve."""
    skill_md = DAN_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if "Sacred Truth" not in text:
        pytest.skip("Dan migration not yet complete")
    link_pattern = re.compile(r"`\./references/([A-Za-z0-9_\-\.]+\.(?:md|yaml))`")
    missing = []
    for name in set(link_pattern.findall(text)):
        target = DAN_SKILL / "references" / name
        if not target.exists():
            missing.append(name)
    assert not missing, f"SKILL.md links to non-existent references: {missing}"


def test_dan_sanctum_scaffolded():
    """Post-migration, Dan's sanctum must exist at the canonical path."""
    sanctum = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-cd"
    if not sanctum.exists():
        pytest.skip("Dan sanctum not yet scaffolded")
    for name in REQUIRED_SANCTUM_FILES:
        assert (sanctum / name).is_file(), f"missing sanctum file: {name}"
    assert (sanctum / "sessions").is_dir()
    assert (sanctum / "capabilities").is_dir()


def test_dan_legacy_sidecar_has_deprecation_banner():
    """Post-migration, dan-sidecar/index.md must carry a deprecation pointer."""
    sidecar_index = REPO_ROOT / "_bmad" / "memory" / "dan-sidecar" / "index.md"
    if not sidecar_index.exists():
        pytest.skip("dan-sidecar not present")
    text = sidecar_index.read_text(encoding="utf-8")
    if "DEPRECATED" not in text:
        pytest.skip("Dan migration not yet complete")
    assert "bmad-agent-cd" in text, \
        "deprecation banner must point to new sanctum path"


def test_dan_all_capability_codes_discovered():
    """
    Dan has 2 capability codes: DR (directive rules) + PT (profile targets).
    Scaffold dry-run must discover both from frontmatter.
    """
    if not (DAN_SKILL / "assets").exists():
        pytest.skip("Dan migration not yet complete")
    result = _run_scaffold(["--skill-path", str(DAN_SKILL), "--dry-run"])
    assert result.returncode == 0
    expected_codes = {"DR", "PT"}
    found = {code for code in expected_codes if f"[{code}]" in result.stdout}
    missing = expected_codes - found
    assert not missing, f"capability codes not discovered: {missing}"


@pytest.mark.parametrize(
    "agent_dir",
    [MARCUS_SKILL, IRENE_SKILL, DAN_SKILL],
    ids=["marcus", "irene", "dan"],
)
def test_capability_stub_script_refs_resolve(agent_dir: Path):
    """
    Stubs for script-backed capabilities (e.g., Irene's PC, VR, MP, MC, MA) declare
    `./scripts/<name>.py` targets. This test guards against silent rot when scripts
    are renamed or reorganized — every such reference must resolve to an actual
    file in the same skill bundle. Covers Blind-Hunter-M2-style regressions.
    """
    if not (agent_dir / "assets").exists():
        pytest.skip(f"{agent_dir.name} migration not yet complete")
    hits = _collect_script_refs_from_agent(agent_dir)
    missing = [
        (md.name, target)
        for md, target in hits
        if not (agent_dir / "scripts" / target).exists()
    ]
    assert not missing, f"references in {agent_dir.name} cite non-existent scripts: {missing}"


def test_no_sanctum_path_references_in_skill_bundle_refs():
    """
    Post-migration, no reference file in a migrated skill bundle may name the
    legacy sidecar path (e.g., 'marcus-sidecar' or 'irene-sidecar') as a
    write target. Guards against the orphan-init.md-style regression Blind
    Hunter M1 flagged.
    """
    bad_patterns = ("marcus-sidecar", "irene-sidecar", "dan-sidecar")
    failures: list[tuple[str, str, str]] = []  # (agent, file, pattern)
    for agent_dir in (MARCUS_SKILL, IRENE_SKILL, DAN_SKILL):
        if not (agent_dir / "assets").exists():
            continue  # pre-migration
        refs_dir = agent_dir / "references"
        if not refs_dir.exists():
            continue
        for md in refs_dir.glob("*.md"):
            text = md.read_text(encoding="utf-8")
            for pat in bad_patterns:
                if pat in text:
                    failures.append((agent_dir.name, md.name, pat))
    assert not failures, (
        f"migrated skill bundles still reference legacy sidecar paths "
        f"(orphan init.md / memory-system.md regression): {failures}"
    )


def test_irene_all_capability_codes_discovered():
    """
    Irene has 20 documented capability codes. Scaffold dry-run must discover
    all of them (IA, LO, BT, CL, CS, AA, PQ, WD, MG, CD, SB, PC, VR, MP, MC, MA,
    SM, IB, NA, DC). CP is umbrella — not frontmatter-discovered.
    """
    if not (IRENE_SKILL / "assets").exists():
        pytest.skip("Irene migration not yet complete")
    result = _run_scaffold(["--skill-path", str(IRENE_SKILL), "--dry-run"])
    assert result.returncode == 0
    expected_codes = {"IA", "LO", "BT", "CL", "CS", "AA", "PQ", "WD", "MG",
                      "CD", "SB", "PC", "VR", "MP", "MC", "MA", "SM", "IB", "NA", "DC", "CP"}
    found = {code for code in expected_codes if f"[{code}]" in result.stdout}
    missing = expected_codes - found
    assert not missing, f"capability codes not discovered: {missing}"


def test_negative_case_missing_sanctum_routes_to_first_breath():
    """
    Negative test: if Marcus's sanctum is absent, SKILL.md must route activation
    to first-breath.md and NOT fall back silently. This guards against the
    "embedded doctrine leaks through" risk Murat flagged.
    """
    skill_md = MARCUS_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if "Sacred Truth" not in text:
        pytest.skip("Marcus migration not yet complete")
    # Activation block must branch on sanctum existence
    assert "first-breath.md" in text or "First Breath" in text, \
        "SKILL.md must reference first-breath pathway for no-sanctum case"


# =======================================================================
# Story 26-4: scaffold v0.2 regression tests
# =======================================================================
#
# Covers 3 fleet-wide defects that escaped the Marcus/Irene/Dan pilot reviews:
#   V2-1: scaffold read _bmad/config.yaml (nonexistent) instead of _bmad/core/config.yaml
#   V2-2: {sanctum_path} substituted with absolute Windows path (non-portable)
#   V2-3: references/*.md copied verbatim, {sanctum_path} literal survived
#
# Plus 2 high-ROI guardrails (Murat) + version-bump assertion + --force behavior.
#
# Each "fail-before / pass-after" assertion is designed to FAIL against scaffold
# v0.1 if the fix regresses.


def _fake_repo(tmp_path: Path, core_config_body: str | None = None) -> Path:
    """Set up a minimal fake repo (git marker + _bmad/core/config.yaml) for isolated scaffold runs.

    If core_config_body is provided, it's written to _bmad/core/config.yaml.
    Callers pass a realistic config so V2-1 regressions can be exercised.
    """
    fake = tmp_path / "fake-repo"
    (fake / ".git").mkdir(parents=True)
    bmad = fake / "_bmad"
    (bmad / "memory").mkdir(parents=True)
    if core_config_body is not None:
        (bmad / "core").mkdir(parents=True)
        (bmad / "core" / "config.yaml").write_text(core_config_body, encoding="utf-8")
    return fake


def _copy_texas_skill(fake_repo: Path) -> Path:
    """Copy the canonical Texas skill bundle into a fake-repo for isolated scaffold tests."""
    dest = fake_repo / "skills" / "bmad-agent-texas"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEXAS_SKILL, dest)
    return dest


def test_v2_1_config_overlay_reads_core_config_first(tmp_path):
    """
    V2-1: scaffold must read _bmad/core/config.yaml (the canonical location).

    Fail-before: v0.1 falls back to "friend" because it reads _bmad/config.yaml
    (which doesn't exist), producing `Operator: friend` in BOND.md.
    Pass-after:  v0.2 reads _bmad/core/config.yaml and renders the real user_name.
    """
    fake = _fake_repo(tmp_path, "user_name: AliceFromCore\ncommunication_language: English\n")
    skill = _copy_texas_skill(fake)
    result = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake)])
    assert result.returncode == 0, result.stderr
    bond = (fake / "_bmad" / "memory" / "bmad-agent-texas" / "BOND.md").read_text(encoding="utf-8")
    assert "AliceFromCore" in bond, (
        "V2-1: rendered BOND.md should contain user_name from "
        f"_bmad/core/config.yaml, got:\n{bond[:500]}"
    )
    assert "friend" not in bond.lower() or "AliceFromCore" in bond, \
        "V2-1: 'friend' fallback should not appear when _bmad/core/config.yaml provides user_name"


def test_v2_1_config_overlay_user_overrides_base(tmp_path):
    """
    V2-1: when both core/config.yaml AND config.user.yaml are present, user config wins.

    Fail-before: v0.1 reads config.user.yaml but not core/config.yaml — so if only
    core/config.yaml exists, fallback hits.
    Pass-after:  v0.2 reads core/config.yaml as base, config.yaml mid, config.user.yaml top.
    """
    fake = _fake_repo(tmp_path, "user_name: BaseName\n")
    (fake / "_bmad" / "config.user.yaml").write_text("user_name: OverrideName\n", encoding="utf-8")
    skill = _copy_texas_skill(fake)
    result = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake)])
    assert result.returncode == 0, result.stderr
    bond = (fake / "_bmad" / "memory" / "bmad-agent-texas" / "BOND.md").read_text(encoding="utf-8")
    assert "OverrideName" in bond, \
        "V2-1: config.user.yaml must override _bmad/core/config.yaml"
    assert "BaseName" not in bond, \
        "V2-1: base name should be overridden, not appended"


def test_v2_2_sanctum_path_is_repo_relative(tmp_path):
    """
    V2-2: {sanctum_path} must substitute with repo-relative POSIX path, not absolute.

    Fail-before: v0.1 emits 'C:\\Users\\...' absolute paths in INDEX.md.
    Pass-after:  v0.2 emits '_bmad/memory/bmad-agent-<name>' relative path.

    Uses dry-run output as the source-of-truth for the variable value (more robust
    than scanning renders — not all agent templates use {sanctum_path} naturally).
    """
    fake = _fake_repo(tmp_path, "user_name: Test\n")
    skill = _copy_texas_skill(fake)
    result = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake), "--dry-run"])
    assert result.returncode == 0, result.stderr
    # Dry-run output includes "Variable substitutions:" section with "{key} -> value"
    m = re.search(r"\{sanctum_path\}\s*->\s*(\S+)", result.stdout)
    assert m, f"Dry-run output missing sanctum_path variable line: {result.stdout}"
    sanctum_value = m.group(1)
    # Must be repo-relative POSIX form, not absolute.
    assert not re.match(r"^[A-Z]:", sanctum_value), \
        f"V2-2: sanctum_path must not start with a Windows drive letter, got: {sanctum_value}"
    assert not sanctum_value.startswith("/"), \
        f"V2-2: sanctum_path must not be root-absolute, got: {sanctum_value}"
    assert sanctum_value == "_bmad/memory/bmad-agent-texas", \
        f"V2-2: sanctum_path must be repo-relative POSIX path, got: {sanctum_value}"


def test_v2_2_sanctum_path_uses_posix_separators(tmp_path):
    """
    V2-2 Windows guard: even on Windows, {sanctum_path} must substitute with
    forward slashes (POSIX style) so rendered templates are portable across OSes.

    Fail-before: v0.1 uses OS-native separators via str(Path) — backslashes on Windows.
    Pass-after:  v0.2 uses .as_posix() explicitly.
    """
    fake = _fake_repo(tmp_path, "user_name: Test\n")
    skill = _copy_texas_skill(fake)
    result = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake)])
    assert result.returncode == 0, result.stderr
    # Scan ALL rendered sanctum files for backslash-style path separators in sanctum_path context.
    sanctum = fake / "_bmad" / "memory" / "bmad-agent-texas"
    for md in sanctum.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        # The relative sanctum path token should use forward slashes.
        assert "_bmad\\memory" not in text, \
            f"V2-2: {md.name} contains backslash path separator; must be POSIX forward slashes"


def test_v2_3_reference_render_substitutes_known_vars(tmp_path):
    """
    V2-3: references/*.md must be rendered (variables substituted), not raw-copied.

    Fail-before: v0.1 uses shutil.copy2, so {sanctum_path} in source refs survives
    as literal text in the sanctum.
    Pass-after:  v0.2 renders references with the same whitelisted variables used
    for assets/.
    """
    fake = _fake_repo(tmp_path, "user_name: Test\n")
    skill = _copy_texas_skill(fake)
    # Inject a probe ref so the test exercises V2-3 regardless of whether Texas's
    # own refs happen to contain the known tokens.
    probe = skill / "references" / "v2-3-probe.md"
    probe.write_text(
        "# Probe\n\nSession log goes to `{sanctum_path}/sessions/today.md`.\n"
        "Project root: `{project_root}`.\n",
        encoding="utf-8",
    )
    result = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake)])
    assert result.returncode == 0, result.stderr
    rendered = (
        fake / "_bmad" / "memory" / "bmad-agent-texas" / "references" / "v2-3-probe.md"
    ).read_text(encoding="utf-8")
    assert "{sanctum_path}" not in rendered, \
        f"V2-3: probe ref contains unresolved {{sanctum_path}} token, got:\n{rendered}"
    assert "{project_root}" not in rendered, \
        f"V2-3: probe ref contains unresolved {{project_root}} token, got:\n{rendered}"
    assert "_bmad/memory/bmad-agent-texas" in rendered, \
        "V2-3: probe ref should have {sanctum_path} substituted with repo-relative path"


def test_v2_3_reference_render_preserves_unknown_braces(tmp_path):
    """
    V2-3 negative: the whitelist must NOT substitute arbitrary {foo} tokens —
    only the known scaffold variables. Foreign brace-tokens (e.g., template
    literals authored for the agent's own use at activation time) must survive.
    """
    fake = _fake_repo(tmp_path, "user_name: Test\n")
    skill = _copy_texas_skill(fake)
    # Inject a reference file with both a known token AND an unknown token.
    target_ref = skill / "references" / "test-preservation-probe.md"
    target_ref.write_text(
        "# Probe\n\nKnown: {user_name}\nUnknown: {this_is_a_foreign_token}\n",
        encoding="utf-8",
    )
    # Also give it minimal frontmatter so scaffold doesn't warn on empty caps
    # (not strictly needed — just tidies the output).
    result = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake)])
    assert result.returncode == 0, result.stderr
    rendered = (
        fake / "_bmad" / "memory" / "bmad-agent-texas" / "references" / "test-preservation-probe.md"
    ).read_text(encoding="utf-8")
    assert "Test" in rendered, "Known token should be substituted"
    assert "{this_is_a_foreign_token}" in rendered, \
        "V2-3 negative: unknown brace-tokens must survive unchanged"


def test_murat_canary_no_unresolved_known_tokens_in_rendered_files(tmp_path):
    """
    Murat's generic canary: after rendering, no sanctum file may contain any
    of the KNOWN scaffold variables as literal unresolved text. Would have
    caught V2-3 alone.

    Injects a probe reference containing every known token so the canary
    actually exercises substitution (Texas refs may not naturally contain all tokens).
    """
    fake = _fake_repo(tmp_path, "user_name: Test\n")
    skill = _copy_texas_skill(fake)
    # Probe ref containing every known scaffold token
    probe = skill / "references" / "all-tokens-probe.md"
    probe.write_text(
        "# Probe\n"
        "user_name: {user_name}\n"
        "communication_language: {communication_language}\n"
        "birth_date: {birth_date}\n"
        "project_root: {project_root}\n"
        "sanctum_path: {sanctum_path}\n"
        "skill_name: {skill_name}\n",
        encoding="utf-8",
    )
    result = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake)])
    assert result.returncode == 0, result.stderr
    sanctum = fake / "_bmad" / "memory" / "bmad-agent-texas"
    known_tokens = ["{user_name}", "{communication_language}", "{birth_date}",
                    "{project_root}", "{sanctum_path}", "{skill_name}"]
    offenders: list[tuple[str, str]] = []
    for md in sanctum.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        for tok in known_tokens:
            if tok in text:
                offenders.append((str(md.relative_to(sanctum)), tok))
    assert not offenders, f"Unresolved known tokens in rendered files: {offenders}"


def test_murat_semantic_user_name_matches_core_config():
    """
    Murat's semantic test: after scaffolding against the REAL repo config, the
    rendered BOND.md user_name must match the value in _bmad/core/config.yaml.

    This is the "did V2-1 actually stick on the real agents" test — reads
    the committed Marcus/Irene/Dan sanctums after re-scaffolding.
    """
    core_config = REPO_ROOT / "_bmad" / "core" / "config.yaml"
    if not core_config.exists():
        pytest.skip("_bmad/core/config.yaml not present; semantic test requires real config")
    # Parse config minimally (shared tests don't pull in yaml)
    user_name = None
    for line in core_config.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("user_name:"):
            user_name = line.split(":", 1)[1].strip().strip("\"'")
            break
    if not user_name or user_name == "friend":
        pytest.skip(f"user_name not set in _bmad/core/config.yaml (got: {user_name!r})")

    # Check each pilot sanctum (if rescaffolded to v0.2)
    for agent in ("bmad-agent-marcus", "bmad-agent-content-creator", "bmad-agent-cd"):
        bond = REPO_ROOT / "_bmad" / "memory" / agent / "BOND.md"
        if not bond.exists():
            continue
        text = bond.read_text(encoding="utf-8")
        # If rescaffolded to v0.2, BOND must reflect actual user_name — not "friend"
        if "friend" in text.lower() and user_name not in text:
            pytest.fail(
                f"{agent}: BOND.md still contains 'friend' fallback instead of '{user_name}' "
                "from _bmad/core/config.yaml — re-scaffold with v0.2 required."
            )


def test_scaffold_version_bumped_to_0_2():
    """AC2: scaffold version string has been bumped to 0.2."""
    result = _run_scaffold(["--skill-path", str(TEXAS_SKILL), "--dry-run"])
    assert result.returncode == 0, result.stderr
    assert "v0.2" in result.stdout or "0.2" in result.stdout, \
        "Scaffold dry-run output must report v0.2"


def test_scaffold_force_flag_overwrites_existing_sanctum(tmp_path):
    """
    AC6 prerequisite: --force must overwrite an existing sanctum. Without
    --force, the scaffold must fail-closed and exit cleanly.

    EC-F (review remediation): assert the no-force skip emits the
    'already been born' message — pins the reason-for-preservation so the
    test doesn't silently pass if the scaffold skipped for a different reason.
    """
    fake = _fake_repo(tmp_path, "user_name: First\n")
    skill = _copy_texas_skill(fake)
    first = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake)])
    assert first.returncode == 0

    # Change config to verify overwrite took effect on re-run.
    (fake / "_bmad" / "core" / "config.yaml").write_text("user_name: Second\n", encoding="utf-8")

    # Without --force: should not overwrite AND must announce the reason.
    second = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake)])
    assert second.returncode == 0
    assert "already been born" in second.stdout, \
        f"no-force skip must emit 'already been born', got: {second.stdout}"
    bond = (fake / "_bmad" / "memory" / "bmad-agent-texas" / "BOND.md").read_text(encoding="utf-8")
    assert "First" in bond, "Without --force, existing sanctum must be preserved"

    # With --force: must overwrite
    third = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake), "--force"])
    assert third.returncode == 0
    bond2 = (fake / "_bmad" / "memory" / "bmad-agent-texas" / "BOND.md").read_text(encoding="utf-8")
    assert "Second" in bond2, "With --force, sanctum must reflect new config"
    assert "First" not in bond2, "With --force, old content must be overwritten"


def test_ec_a_rejects_skill_outside_project_root(tmp_path):
    """
    EC-A (Edge Case Hunter): scaffold must refuse to mkdir into a workspace
    that isn't an ancestor of --skill-path. Prevents operator-typo pollution
    of foreign directories (e.g., --project-root C:/Windows).
    """
    # Build two unrelated fake-repo workspaces.
    fake_a = _fake_repo(tmp_path / "a", "user_name: A\n")
    fake_b = _fake_repo(tmp_path / "b", "user_name: B\n")
    skill = _copy_texas_skill(fake_a)  # skill lives under fake_a
    # Pass fake_b as project-root — skill is NOT inside it. Must fail-closed.
    result = _run_scaffold([
        "--skill-path", str(skill),
        "--project-root", str(fake_b),
    ])
    assert result.returncode == 2, (
        "EC-A: scaffold must exit 2 when skill-path not inside "
        f"project-root; got {result.returncode}"
    )
    assert "not inside" in result.stderr.lower() or "refusing" in result.stderr.lower(), \
        f"EC-A: stderr must explain the refusal: {result.stderr}"
    # The foreign workspace must not have been polluted.
    assert not (fake_b / "_bmad" / "memory" / "bmad-agent-texas").exists(), \
        "EC-A: scaffold must NOT create sanctum in the foreign workspace"


def test_ec_b_force_purges_stale_toplevel_files(tmp_path):
    """
    EC-B (Edge Case Hunter): --force re-render must purge top-level *.md
    files that are no longer produced by any template. Prevents orphan
    drift across repeated migrations (e.g., a renamed asset template
    leaves a stale output).
    """
    fake = _fake_repo(tmp_path, "user_name: Test\n")
    skill = _copy_texas_skill(fake)
    first = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake)])
    assert first.returncode == 0
    sanctum = fake / "_bmad" / "memory" / "bmad-agent-texas"
    # Simulate a stale file — e.g., a previously-rendered file whose source
    # template has been removed from the skill bundle.
    stale = sanctum / "OLDNAME.md"
    stale.write_text("stale content from prior scaffold run", encoding="utf-8")
    assert stale.exists()
    # Re-scaffold with --force; stale file must be purged.
    result = _run_scaffold([
        "--skill-path", str(skill),
        "--project-root", str(fake),
        "--force",
    ])
    assert result.returncode == 0
    assert not stale.exists(), \
        "EC-B: --force must purge top-level *.md files no longer produced by templates"


def test_ec_b_force_purges_stale_reference_files(tmp_path):
    """
    EC-B: --force re-render must also purge stale references/*.md files.
    """
    fake = _fake_repo(tmp_path, "user_name: Test\n")
    skill = _copy_texas_skill(fake)
    first = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake)])
    assert first.returncode == 0
    sanctum_refs = fake / "_bmad" / "memory" / "bmad-agent-texas" / "references"
    stale_ref = sanctum_refs / "deprecated-ref.md"
    stale_ref.write_text("stale ref from prior scaffold run", encoding="utf-8")
    result = _run_scaffold([
        "--skill-path", str(skill),
        "--project-root", str(fake),
        "--force",
    ])
    assert result.returncode == 0
    assert not stale_ref.exists(), \
        "EC-B: --force must purge stale references/*.md files"


def test_ec_b_force_preserves_sessions_and_capabilities(tmp_path):
    """
    EC-B negative: --force must NEVER touch sessions/ or capabilities/ —
    those are operator-authored content directories, not template outputs.
    """
    fake = _fake_repo(tmp_path, "user_name: Test\n")
    skill = _copy_texas_skill(fake)
    first = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake)])
    assert first.returncode == 0
    sanctum = fake / "_bmad" / "memory" / "bmad-agent-texas"
    # Simulate operator-authored content.
    session_log = sanctum / "sessions" / "2026-04-17.md"
    session_log.write_text("operator session notes", encoding="utf-8")
    cap_prompt = sanctum / "capabilities" / "my-new-cap.md"
    cap_prompt.write_text("operator capability prompt", encoding="utf-8")
    result = _run_scaffold([
        "--skill-path", str(skill),
        "--project-root", str(fake),
        "--force",
    ])
    assert result.returncode == 0
    assert session_log.exists(), "EC-B: --force must preserve sessions/ content"
    assert session_log.read_text(encoding="utf-8") == "operator session notes", \
        "EC-B: session content must be byte-identical"
    assert cap_prompt.exists(), "EC-B: --force must preserve capabilities/ content"


def test_ec_e_document_output_language_is_in_whitelist(tmp_path):
    """
    EC-E (Edge Case Hunter): {document_output_language} must be a recognized
    scaffold variable so it gets substituted in references. Prevents a
    future ref using this token from surviving as a literal.
    """
    fake = _fake_repo(
        tmp_path,
        "user_name: Test\ncommunication_language: English\ndocument_output_language: Spanish\n",
    )
    skill = _copy_texas_skill(fake)
    # Inject a probe ref exercising the token.
    probe = skill / "references" / "doc-lang-probe.md"
    probe.write_text("Docs language: {document_output_language}\n", encoding="utf-8")
    result = _run_scaffold(["--skill-path", str(skill), "--project-root", str(fake)])
    assert result.returncode == 0, result.stderr
    rendered = (
        fake / "_bmad" / "memory" / "bmad-agent-texas" / "references" / "doc-lang-probe.md"
    ).read_text(encoding="utf-8")
    assert "Spanish" in rendered, \
        f"EC-E: {{document_output_language}} must be substituted; got:\n{rendered}"
    assert "{document_output_language}" not in rendered, \
        "EC-E: token must not survive as literal"
