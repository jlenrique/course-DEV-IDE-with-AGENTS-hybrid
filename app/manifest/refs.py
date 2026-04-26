"""Manifest dotted-reference resolution helpers."""

from __future__ import annotations

import importlib
from typing import Any

from app.manifest.exceptions import ManifestSchemaImportError


def resolve_dotted_ref(
    dotted_ref: str,
    *,
    expected_base_class: type[Any] | None = None,
) -> Any:
    """Resolve `<module>:<attribute>` to a live Python object.

    Args:
        dotted_ref: Import target in `<module>:<attribute>` form.
        expected_base_class: Optional class that the resolved target must
            subclass. Used by Story 3.2 to validate DecisionCard schema refs.

    Returns:
        The imported attribute.

    Raises:
        ManifestSchemaImportError: If the ref is malformed, import fails,
            attribute lookup fails, or the resolved target is not a subclass of
            `expected_base_class`.
    """
    if ":" not in dotted_ref:
        raise ManifestSchemaImportError(
            f"manifest dotted ref must use '<module>:<attribute>' syntax; got {dotted_ref!r}"
        )

    module_name, attribute_name = dotted_ref.split(":", 1)
    if not module_name or not attribute_name:
        raise ManifestSchemaImportError(
            f"manifest dotted ref must include both module and attribute; got {dotted_ref!r}"
        )

    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        raise ManifestSchemaImportError(
            "failed to import manifest dotted-ref module "
            f"{module_name!r} from {dotted_ref!r}: {exc}"
        ) from exc

    try:
        resolved = getattr(module, attribute_name)
    except AttributeError as exc:
        raise ManifestSchemaImportError(
            f"manifest dotted ref {dotted_ref!r} resolved module {module_name!r} "
            f"but missing attribute {attribute_name!r}"
        ) from exc

    if expected_base_class is not None and (
        not isinstance(resolved, type) or not issubclass(resolved, expected_base_class)
    ):
        raise ManifestSchemaImportError(
            f"manifest dotted ref {dotted_ref!r} must resolve to a subclass of "
            f"{expected_base_class.__name__}"
        )

    return resolved


__all__ = ["resolve_dotted_ref"]
