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
        # 2026-06-17 WAVE-0 tranche 2 RETIRED: BuilderInputError re-based to
        # SpecialistDispatchError + both run_builder_node call sites wrapped
        # in error-pause (the last live-walk dispatch leg; node-06 starvation
        # now pauses recoverably instead of killing the trial). Row removed
        # per the reverse-existence pin (red observed before deletion).
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
        # 2026-06-12 live-path tranche RETIRED: GaryActError,
        # ReceiptParseError, BundleParseError, KiraActError, FTRParseError
        # re-based to SpecialistDispatchError (rows removed; shrink-only).
        # ManifestParseError is an in-module alias of RetrievalIntentParseError
        "app.specialists.tracy._act.ManifestParseError",
        "app.specialists.tracy._act.RetrievalIntentParseError",
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
    """Re-based classes pinned by name: the five the cycle-5 crash convicted,
    the five of the live-path tranche (gary/texas/kira/vera, 2026-06-12),
    BuilderInputError (WAVE-0 tranche 2, 2026-06-17 — the last live-walk
    dispatch leg), and the contracts-triage row-20 pair (2026-07-02:
    VoiceProviderTextError enhanced-VO v3 leaf + StyleguideError gamma
    styleguide spine — both born non-compliant, re-based per the ratchet).
    Membership AND constructor semantics — issubclass alone would pass with a
    broken (message, *, tag) ctor (blind-hunter review patch);
    BuilderInputError and the row-20 pair inherit the base ctor, so this pin
    proves the INHERITED ctor still carries the tag."""
    assert issubclass(SpecialistDispatchError, RuntimeError)
    from app.marcus.orchestrator.package_builders import BuilderInputError
    from app.specialists._shared.voice_provider_text import VoiceProviderTextError
    from app.specialists.compositor._act import CompositorActError
    from app.specialists.enrique._act import EnriqueActError
    from app.specialists.gary._act import GaryActError
    from app.specialists.gary.graph import ReceiptParseError
    from app.specialists.gary.styleguide_library import StyleguideError
    from app.specialists.kira._act import KiraActError
    from app.specialists.quinn_r.graph import QRRParseError
    from app.specialists.quinn_r.quality_control_dispatch import (
        CoverageGapError,
        WpmThresholdError,
    )
    from app.specialists.texas._act import BundleParseError
    from app.specialists.vera._act import FTRParseError

    for cls in (
        CoverageGapError,
        WpmThresholdError,
        QRRParseError,
        EnriqueActError,
        CompositorActError,
        GaryActError,
        ReceiptParseError,
        BundleParseError,
        KiraActError,
        FTRParseError,
        BuilderInputError,
        VoiceProviderTextError,
        StyleguideError,
    ):
        assert issubclass(cls, SpecialistDispatchError), cls.__name__
        # Base is RuntimeError-derived: existing handlers keep working.
        assert issubclass(cls, RuntimeError), cls.__name__
        instance = cls("msg", tag="t")
        assert instance.tag == "t", cls.__name__
        assert str(instance) == "msg", cls.__name__
    # Dual base preserved: existing ValueError handlers keep working.
    assert issubclass(CoverageGapError, ValueError)
    assert issubclass(WpmThresholdError, ValueError)
