"""Exception types raised by the manifest loader + compiler.

Separated from `schema.py` so error paths can be imported without pulling the
full Pydantic graph in at import time (keeps the `app.manifest` import
footprint small for CLIs + tooling that only needs to catch).
"""

from __future__ import annotations


class ManifestValidationError(ValueError):
    """Raised by `app.manifest.loader.load()` on malformed manifest input.

    Subclasses `ValueError` rather than `pydantic.ValidationError` because
    Pydantic's `ValidationError` cannot be instantiated directly (pydantic-core
    constraint). The loader catches Pydantic's `ValidationError` internally
    and re-raises as this type, preserving the named-violation path in the
    message.
    """


class CompileError(Exception):
    """Raised by `app.manifest.compiler.compile()` on compile-time contract violations.

    Examples: missing `model_config.yaml` referenced by a node, unknown
    condition name on a conditional edge, missing `runtime/graphs/v{version}/`
    directory for `frozen_graph_version`, unresolved `specialist_id`.
    """


class ManifestSchemaImportError(CompileError):
    """Raised when a manifest dotted-reference cannot be imported safely.

    Story 3.2 uses this for `edge.decision_card_schema` references of the form
    `<module>:<ClassName>`. The error subclasses `CompileError` so manifest
    callers can continue to treat schema-import failures as compile-time
    contract violations.
    """


__all__ = ["CompileError", "ManifestSchemaImportError", "ManifestValidationError"]
