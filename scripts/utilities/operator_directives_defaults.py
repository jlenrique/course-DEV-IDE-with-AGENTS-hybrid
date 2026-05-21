"""Prior-run defaults for Prompt 02A operator directives."""

from __future__ import annotations

import importlib.util
import os
import re
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from scripts.utilities.run_constants import RunConstantsError, load_run_constants

_VALIDATOR_PATH = Path(__file__).with_name("validate-operator-directives.py")
_VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "_operator_directives_validator", _VALIDATOR_PATH
)
if _VALIDATOR_SPEC is None or _VALIDATOR_SPEC.loader is None:  # pragma: no cover
    raise ImportError(f"cannot load operator directives validator from {_VALIDATOR_PATH}")
_VALIDATOR_MODULE = importlib.util.module_from_spec(_VALIDATOR_SPEC)
_VALIDATOR_SPEC.loader.exec_module(_VALIDATOR_MODULE)
validate_operator_directives = _VALIDATOR_MODULE.validate_operator_directives

_DIRECTIVE_SECTION_NAMES = (
    "focus_directives",
    "exclusion_directives",
    "special_treatment_directives",
)


class DirectiveDefaultSource(StrEnum):
    """Source type for a Step 02A default candidate."""

    CURRENT_RUN = "current-run"
    PRIOR_RUN = "prior-run"


@dataclass(frozen=True)
class OperatorDirectivesDefault:
    """Named operator directives default with attribution."""

    source: DirectiveDefaultSource
    run_id: str
    lesson_slug: str
    bundle_path: Path
    directives_path: Path
    modified_at_utc: datetime
    modified_at_ns: int
    content: str


class InvalidCurrentBundleDirectivesError(ValueError):
    """Current bundle directives exist but fail validation."""


class InvalidNewDirectivesError(ValueError):
    """New directives content failed validation before replacement."""


def _validation_failure_message(result: dict) -> str:
    issues = result.get("issues") or []
    issue_text = "; ".join(str(issue) for issue in issues)
    reason = str(result.get("reason") or "validation failed")
    if issue_text:
        return f"{reason}: {issue_text}"
    return reason


def _validate_directives(path: Path) -> dict | None:
    try:
        result = validate_operator_directives(path)
    except (FileNotFoundError, PermissionError, OSError):
        return None
    except Exception as exc:
        return {"valid": False, "reason": str(exc), "issues": [str(exc)]}
    return result


def _valid_directives(path: Path) -> bool:
    result = _validate_directives(path)
    return bool(result and result.get("valid") is True)


def _load_bundle_constants(bundle: Path):
    try:
        return load_run_constants(bundle, verify_paths_exist=False)
    except (RunConstantsError, OSError):
        return None


def _default_from_bundle(
    bundle: Path,
    *,
    source: DirectiveDefaultSource,
    require_tracked: bool = False,
) -> OperatorDirectivesDefault | None:
    constants = _load_bundle_constants(bundle)
    directives_path = bundle / "operator-directives.md"
    if constants is None:
        return None
    if require_tracked and constants.execution_mode != "tracked/default":
        return None
    if not _valid_directives(directives_path):
        return None
    try:
        stat = directives_path.stat()
        content = directives_path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, OSError):
        return None
    return OperatorDirectivesDefault(
        source=source,
        run_id=constants.run_id,
        lesson_slug=constants.lesson_slug,
        bundle_path=bundle.resolve(),
        directives_path=directives_path.resolve(),
        modified_at_utc=datetime.fromtimestamp(stat.st_mtime, tz=UTC),
        modified_at_ns=stat.st_mtime_ns,
        content=content,
    )


def _candidate_sort_key(default: OperatorDirectivesDefault) -> tuple[int, str]:
    return default.modified_at_ns, default.run_id


def _is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def _current_bundle_validation_result(bundle: Path) -> dict | None:
    directives_path = bundle / "operator-directives.md"
    try:
        exists = directives_path.exists()
    except OSError:
        return None
    if not exists:
        return None
    return _validate_directives(directives_path)


def _extract_directive_sections(content: str) -> str:
    section_pattern = re.compile(
        rf"^({'|'.join(re.escape(name) for name in _DIRECTIVE_SECTION_NAMES)}):\s*$"
    )
    lines = content.splitlines()
    extracted: list[str] = []
    seen: set[str] = set()
    index = 0
    while index < len(lines):
        match = section_pattern.match(lines[index])
        if match is None:
            index += 1
            continue
        section_name = match.group(1)
        seen.add(section_name)
        extracted.append(lines[index])
        index += 1
        while index < len(lines):
            line = lines[index]
            if line and not line[0].isspace() and re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", line):
                break
            extracted.append(line)
            index += 1
    missing = [name for name in _DIRECTIVE_SECTION_NAMES if name not in seen]
    if missing:
        raise InvalidNewDirectivesError(
            "accepted prior directives missing directive sections: " + ", ".join(missing)
        )
    return "\n".join(extracted).rstrip()


def _current_run_accept_content(bundle_root: Path, default: OperatorDirectivesDefault) -> str:
    constants = load_run_constants(bundle_root, verify_paths_exist=False)
    accepted_at = datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    directive_sections = _extract_directive_sections(default.content)
    return "\n".join(
        [
            f"run_id: {constants.run_id}",
            f"timestamp: {accepted_at}",
            f"poll_started_utc: {accepted_at}",
            f"reply_eligible_utc: {accepted_at}",
            f"poll_close_utc: {accepted_at}",
            "poll_status: submitted",
            "operator: prior-run-default-accept",
            "source_attribution:",
            f"  prior_run_id: {default.run_id}",
            f"  prior_bundle_path: {default.bundle_path.as_posix()}",
            f"  accepted_at: {accepted_at}",
            directive_sections,
            "",
        ]
    )


def _write_validated(target: Path, content: str) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(f".{target.name}.tmp.{os.getpid()}")
    try:
        temp.write_text(content.rstrip() + "\n", encoding="utf-8")
        result = validate_operator_directives(temp)
        if not result.get("valid"):
            raise InvalidNewDirectivesError(
                "new operator directives failed validation at "
                f"{temp}: {_validation_failure_message(result)}"
            )
        os.replace(temp, target)
    finally:
        with suppress(OSError):
            temp.unlink()
    return target


def discover_step_02a_directives_default(
    bundle_root: Path,
    lesson_slug: str,
) -> OperatorDirectivesDefault | None:
    """Return current-run directives or latest valid same-lesson prior default.

    The helper is intentionally narrow: it scans sibling bundle directories for
    `operator-directives.md` with the same `lesson_slug`, excludes the current
    bundle, and breaks identical-mtime ties by lexicographic `run_id` descending.
    It does not call Marcus PR-* capability surfaces.
    """

    bundle = Path(bundle_root).resolve()
    current_validation = _current_bundle_validation_result(bundle)
    if current_validation is not None and not current_validation.get("valid"):
        failure = _validation_failure_message(current_validation)
        raise InvalidCurrentBundleDirectivesError(
            f"invalid current bundle operator directives at "
            f"{bundle / 'operator-directives.md'}: {failure}"
        )
    current = _default_from_bundle(bundle, source=DirectiveDefaultSource.CURRENT_RUN)
    if current is not None and current.lesson_slug == lesson_slug:
        return current

    current_constants = _load_bundle_constants(bundle)
    if current_constants is None:
        return None

    root = bundle.parent.resolve()
    if not root.is_dir():
        return None

    candidates: list[OperatorDirectivesDefault] = []
    for candidate_bundle in sorted(root.iterdir(), key=lambda p: p.name):
        try:
            resolved_candidate = candidate_bundle.resolve()
        except OSError:
            continue
        if resolved_candidate == bundle or not candidate_bundle.is_dir():
            continue
        if not _is_relative_to(resolved_candidate, root):
            continue
        candidate = _default_from_bundle(
            resolved_candidate,
            source=DirectiveDefaultSource.PRIOR_RUN,
            require_tracked=True,
        )
        if candidate is None or candidate.lesson_slug != lesson_slug:
            continue
        candidates.append(candidate)

    if not candidates:
        return None
    return max(candidates, key=_candidate_sort_key)


def render_step_02a_default_prompt(
    default: OperatorDirectivesDefault,
    *,
    bundle_root: Path,
) -> str:
    """Render the named-default block Marcus should present in Step 02A."""

    source_label = (
        "current run"
        if default.source == DirectiveDefaultSource.CURRENT_RUN
        else "prior run"
    )
    try:
        relative_source = default.directives_path.relative_to(Path(bundle_root).resolve().parent)
    except ValueError:
        relative_source = default.directives_path
    timestamp = default.modified_at_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return "\n".join(
        [
            "Step 02A named operator-directives defaults:",
            f"- source type: {source_label}",
            f"- run_id: {default.run_id}",
            f"- lesson_slug: {default.lesson_slug}",
            f"- source bundle: {default.bundle_path.as_posix()}",
            f"- source path: {relative_source.as_posix()}",
            f"- source modified UTC: {timestamp}",
            "",
            "Default directives content:",
            "```yaml",
            default.content.rstrip(),
            "```",
        ]
    )


def write_operator_directives_from_choice(
    bundle_root: Path,
    *,
    choice: str,
    default: OperatorDirectivesDefault | None,
    modified_content: str | None = None,
    replacement_content: str | None = None,
) -> Path:
    """Write `operator-directives.md` after an explicit accept/modify/replace."""

    normalized_choice = choice.strip().lower()
    if normalized_choice == "accept":
        if default is None:
            raise ValueError("accept requires a discovered default")
        content = (
            _current_run_accept_content(Path(bundle_root), default)
            if default.source == DirectiveDefaultSource.PRIOR_RUN
            else default.content
        )
    elif normalized_choice == "modify":
        if modified_content is None:
            raise ValueError("modify requires modified_content")
        content = modified_content
    elif normalized_choice == "replace":
        if replacement_content is None:
            raise ValueError("replace requires replacement_content")
        content = replacement_content
    else:
        raise ValueError("choice must be one of: accept, modify, replace")

    target = Path(bundle_root) / "operator-directives.md"
    return _write_validated(target, content)
