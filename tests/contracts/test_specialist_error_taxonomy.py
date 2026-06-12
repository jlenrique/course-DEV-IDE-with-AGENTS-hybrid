"""PIN-AUD-3T — specialist error-taxonomy ratchet (audio-arc, 2026-06-12).

Cycle-5 died at node 13 because CoverageGapError was a bare ValueError:
no error-pause, no persisted progress, a dead process where a recoverable
pause belonged. This ratchet kills the CLASS: every Exception type defined
in a production specialist/orchestrator module whose constructor takes a
``tag`` keyword (the dispatch-error calling convention) MUST be a
SpecialistDispatchError subclass — discovery by module walk, so future
error classes auto-enroll the day they are written.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil

import app.specialists
from app.specialists.dispatch_errors import SpecialistDispatchError

# Modules outside the app.specialists package that participate in the
# dispatch-error convention.
EXTRA_MODULES = (
    "app.marcus.orchestrator.storyboard_publisher",
    "app.marcus.orchestrator.package_builders",
)

# Classes that carry a tag but are NOT yet dispatch-family. SHRINK-ONLY
# seed list (audio-arc 2026-06-12): these 18 pre-date the taxonomy ratchet;
# each is the cycle-5 crash class waiting for its node to be exercised.
# Systematic re-base (with per-class catch-site greps) is a filed
# deferred-inventory rider; rows retire as their classes re-base. New
# tagged classes get NO exclusion — they must be born dispatch-family.
EXCLUSIONS: frozenset[str] = frozenset(
    {
        "BuilderInputError",  # raised pre-dispatch by the runner walk (criterion-5 leg)
        "OperatorInstructionsParseError",  # aria/kim/mira/tamara/vyx (unexercised seams)
        "CdDirectiveParseError",
        "DanAuxParseError",
        "HandoffParseError",
        "ElevenlabsDispatchError",  # legacy-probe path only
        "GaryActError",
        "ReceiptParseError",
        "KiraActError",
        "BundleParseError",
        "ManifestParseError",
        "RetrievalIntentParseError",
        "FTRParseError",
        "WandaActError",
    }
)


def _walk_specialist_modules():
    for info in pkgutil.walk_packages(
        app.specialists.__path__, prefix="app.specialists."
    ):
        yield importlib.import_module(info.name)
    for name in EXTRA_MODULES:
        yield importlib.import_module(name)


def _takes_tag(cls: type) -> bool:
    try:
        return "tag" in inspect.signature(cls.__init__).parameters
    except (TypeError, ValueError):
        return False


def test_every_tagged_error_class_is_dispatch_family() -> None:
    violations: list[str] = []
    for module in _walk_specialist_modules():
        for name, obj in vars(module).items():
            if not (isinstance(obj, type) and issubclass(obj, Exception)):
                continue
            if obj.__module__ != module.__name__:
                continue  # re-exports are checked at their defining module
            if name in EXCLUSIONS:
                continue
            if _takes_tag(obj) and not issubclass(obj, SpecialistDispatchError):
                violations.append(f"{module.__name__}.{name}")
    assert violations == [], (
        "Tagged error class(es) outside the SpecialistDispatchError family "
        f"(the cycle-5 crash class): {sorted(set(violations))} — re-base them "
        "so failures error-pause recoverably instead of killing the walk."
    )


def test_known_rebased_classes() -> None:
    """The five classes the cycle-5 crash convicted, pinned by name."""
    from app.specialists.compositor._act import CompositorActError
    from app.specialists.enrique._act import EnriqueActError
    from app.specialists.quinn_r.graph import QRRParseError
    from app.specialists.quinn_r.quality_control_dispatch import (
        CoverageGapError,
        WpmThresholdError,
    )

    for cls in (
        CoverageGapError,
        WpmThresholdError,
        QRRParseError,
        EnriqueActError,
        CompositorActError,
    ):
        assert issubclass(cls, SpecialistDispatchError), cls.__name__
    # Dual base preserved: existing ValueError handlers keep working.
    assert issubclass(CoverageGapError, ValueError)
    assert issubclass(WpmThresholdError, ValueError)
