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
# Module-qualified per Murat R2 (dp-v1.2 rider): a new class reusing a
# bare excluded name in another module must NOT inherit the exclusion.
EXCLUSIONS: frozenset[str] = frozenset(
    {
        # raised pre-dispatch by the runner walk (criterion-5 leg)
        "app.marcus.orchestrator.package_builders.BuilderInputError",
        # aria/kim/mira/tamara/vyx (unexercised seams)
        "app.specialists.aria.graph.OperatorInstructionsParseError",
        "app.specialists.kim.graph.OperatorInstructionsParseError",
        "app.specialists.mira.graph.OperatorInstructionsParseError",
        "app.specialists.tamara.graph.OperatorInstructionsParseError",
        "app.specialists.vyx.graph.OperatorInstructionsParseError",
        "app.specialists.cd.graph.CdDirectiveParseError",
        "app.specialists.dan._act.DanAuxParseError",
        "app.specialists.desmond.graph.HandoffParseError",
        # legacy-probe path only
        "app.specialists.enrique.elevenlabs_dispatch.ElevenlabsDispatchError",
        "app.specialists.gary._act.GaryActError",
        "app.specialists.gary.graph.ReceiptParseError",
        "app.specialists.kira._act.KiraActError",
        "app.specialists.texas._act.BundleParseError",
        # ManifestParseError is an in-module alias of RetrievalIntentParseError
        "app.specialists.tracy._act.ManifestParseError",
        "app.specialists.tracy._act.RetrievalIntentParseError",
        "app.specialists.vera._act.FTRParseError",
        "app.specialists.wanda._act.WandaActError",
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
            if f"{module.__name__}.{name}" in EXCLUSIONS:
                continue
            if _takes_tag(obj) and not issubclass(obj, SpecialistDispatchError):
                violations.append(f"{module.__name__}.{name}")
    assert violations == [], (
        "Tagged error class(es) outside the SpecialistDispatchError family "
        f"(the cycle-5 crash class): {sorted(set(violations))} — re-base them "
        "so failures error-pause recoverably instead of killing the walk."
    )


def test_exclusions_rows_still_name_live_bare_classes() -> None:
    """Murat R2 follow-through (review patch): shrink-only means a row must
    retire when its class re-bases, renames, or disappears — a stale
    module-qualified row excludes nothing, invisibly, forever."""
    stale: list[str] = []
    for entry in sorted(EXCLUSIONS):
        module_name, _, class_name = entry.rpartition(".")
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            stale.append(f"{entry} (module gone)")
            continue
        obj = vars(module).get(class_name)
        if not (isinstance(obj, type) and issubclass(obj, Exception)):
            stale.append(f"{entry} (class gone)")
        elif issubclass(obj, SpecialistDispatchError) or not _takes_tag(obj):
            stale.append(f"{entry} (re-based or untagged — retire the row)")
    assert stale == [], f"Stale EXCLUSIONS row(s): {stale}"


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
