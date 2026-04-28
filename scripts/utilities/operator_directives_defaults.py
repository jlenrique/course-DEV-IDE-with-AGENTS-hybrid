"""Prior-run defaults for Prompt 02A operator directives."""

from __future__ import annotations

import importlib.util
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
    content: str


def _valid_directives(path: Path) -> bool:
    try:
        result = validate_operator_directives(path)
    except Exception:
        return False
    return bool(result.get("valid") is True)


def _load_bundle_constants(bundle: Path):
    try:
        return load_run_constants(bundle, verify_paths_exist=False)
    except (RunConstantsError, OSError):
        return None


def _default_from_bundle(
    bundle: Path,
    *,
    source: DirectiveDefaultSource,
) -> OperatorDirectivesDefault | None:
    constants = _load_bundle_constants(bundle)
    directives_path = bundle / "operator-directives.md"
    if constants is None or not _valid_directives(directives_path):
        return None
    stat = directives_path.stat()
    return OperatorDirectivesDefault(
        source=source,
        run_id=constants.run_id,
        lesson_slug=constants.lesson_slug,
        bundle_path=bundle.resolve(),
        directives_path=directives_path.resolve(),
        modified_at_utc=datetime.fromtimestamp(stat.st_mtime, tz=UTC),
        content=directives_path.read_text(encoding="utf-8"),
    )


def _candidate_sort_key(default: OperatorDirectivesDefault) -> tuple[int, str]:
    mtime_ns = default.directives_path.stat().st_mtime_ns
    return mtime_ns, default.run_id


def discover_step_02a_directives_default(
    bundle_root: Path,
    *,
    search_root: Path | None = None,
) -> OperatorDirectivesDefault | None:
    """Return current-run directives or latest valid same-lesson prior default.

    The helper is intentionally narrow: it scans sibling bundle directories for
    `operator-directives.md` with the same `lesson_slug`, excludes the current
    bundle, and breaks identical-mtime ties by lexicographic `run_id` descending.
    It does not call Marcus PR-* capability surfaces.
    """

    bundle = Path(bundle_root).resolve()
    current = _default_from_bundle(bundle, source=DirectiveDefaultSource.CURRENT_RUN)
    if current is not None:
        return current

    current_constants = _load_bundle_constants(bundle)
    if current_constants is None:
        return None

    root = Path(search_root).resolve() if search_root else bundle.parent
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
        candidate = _default_from_bundle(
            resolved_candidate,
            source=DirectiveDefaultSource.PRIOR_RUN,
        )
        if candidate is None or candidate.lesson_slug != current_constants.lesson_slug:
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
        content = default.content
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
    target.write_text(content.rstrip() + "\n", encoding="utf-8")
    result = validate_operator_directives(target)
    if not result.get("valid"):
        with suppress(OSError):
            target.unlink()
        issues = "; ".join(str(issue) for issue in result.get("issues", []))
        raise ValueError(f"written operator directives failed validation: {issues}")
    return target
