"""ModalityProducer ABC (Story 31-3 AC-B.3).

Audience: producer implementers (31-4 blueprint-producer, future Gary retrofit,
Kira narration, Tracy research). Abstract base class every concrete modality
producer subclasses.

Contract:
    - ``modality_ref: ClassVar[str]`` — pinned by the subclass; one of the
      closed ``ModalityRef`` set when wiring into :data:`MODALITY_REGISTRY`.
    - ``status: ClassVar[Literal["ready", "pending"]]`` — pinned by the subclass.
    - ``produce(self, plan_unit, context) -> ProducedAsset`` — abstract method.
      MUST NOT mutate ``plan_unit`` or ``context``. MUST emit a
      :class:`ProducedAsset` with ``fulfills`` set per AC-B.7 regex.

M-AM-2 (Murat R2 BINDING) enforcement: CPython does NOT validate
``ClassVar[...]`` type hints at class-definition or instantiation time. This
module wires an explicit ``__init_subclass__`` hook that rejects subclasses
missing or malformed ``modality_ref`` / ``status`` class attributes at class
body execution time — before the first instantiation can succeed. See
:meth:`ModalityProducer.__init_subclass__`.

ABC membership is enforced separately (via :mod:`abc`); missing ``produce``
raises ``TypeError`` at instantiation per Python's ABC rules.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Final, Literal

from app.marcus.lesson_plan.produced_asset import ProducedAsset, ProductionContext
from app.marcus.lesson_plan.schema import PlanUnit

SCHEMA_VERSION: Final[str] = "1.0"
"""ModalityProducer ABC schema version (AC-B.9)."""


_VALID_STATUS: Final[frozenset[str]] = frozenset({"ready", "pending"})


class ModalityProducer(ABC):
    """Abstract base class for atomic modality producers.

    Concrete producers (31-4 blueprint-producer lands first; Gary/Gamma
    slides-producer adopts via separate amendment story) subclass this and
    implement :meth:`produce`. ``modality_ref`` + ``status`` are class
    attributes pinned by the subclass; the base enforces presence and type at
    class-definition time via :meth:`__init_subclass__` (M-AM-2).

    Example subclass shape (concrete producer — not shipped in 31-3)::

        class BlueprintProducer(ModalityProducer):
            modality_ref = "blueprint"
            status = "ready"

            def produce(self, plan_unit, context):
                return ProducedAsset(
                    asset_ref=f"blueprint-{plan_unit.unit_id}",
                    modality_ref=self.modality_ref,
                    source_plan_unit_id=plan_unit.unit_id,
                    asset_path=f"artifacts/{plan_unit.unit_id}.md",
                    fulfills=f"{plan_unit.unit_id}@{context.lesson_plan_revision}",
                )
    """

    modality_ref: ClassVar[str]
    status: ClassVar[Literal["ready", "pending"]]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """M-AM-2: enforce ClassVar presence + validity at class-definition time.

        CPython does not check ``ClassVar[...]`` type hints; this hook is the
        actual contract. Subclasses of :class:`ModalityProducer` that omit
        ``modality_ref`` / ``status``, declare them with the wrong type, or use
        an invalid ``status`` string raise :class:`TypeError` at the moment
        ``class Foo(ModalityProducer): ...`` is executed.
        """
        super().__init_subclass__(**kwargs)
        # modality_ref: must be set in the subclass body AND a str.
        if "modality_ref" not in cls.__dict__:
            raise TypeError(
                f"ModalityProducer subclass {cls.__name__!r} must define "
                "class attribute 'modality_ref: ClassVar[str]'"
            )
        modality_ref_val = cls.__dict__["modality_ref"]
        if not isinstance(modality_ref_val, str):
            raise TypeError(
                f"ModalityProducer subclass {cls.__name__!r} attribute "
                f"'modality_ref' must be a str; got "
                f"{type(modality_ref_val).__name__!r} "
                f"(value={modality_ref_val!r})"
            )
        # status: must be set in the subclass body AND in the closed set.
        if "status" not in cls.__dict__:
            raise TypeError(
                f"ModalityProducer subclass {cls.__name__!r} must define "
                "class attribute 'status: ClassVar[Literal[\"ready\", \"pending\"]]'"
            )
        status_val = cls.__dict__["status"]
        if status_val not in _VALID_STATUS:
            raise TypeError(
                f"ModalityProducer subclass {cls.__name__!r} attribute 'status' "
                f"must be one of {sorted(_VALID_STATUS)!r}; got {status_val!r}"
            )

    @abstractmethod
    def produce(
        self,
        plan_unit: PlanUnit,
        context: ProductionContext,
    ) -> ProducedAsset:
        """Produce a single asset for ``plan_unit`` per the modality contract.

        Implementations MUST NOT mutate ``plan_unit`` or ``context`` and MUST
        emit a :class:`ProducedAsset` with ``fulfills`` set to
        ``f"{plan_unit.unit_id}@{context.lesson_plan_revision}"`` (AC-B.7
        regex + Q-R2-A cross-field invariant). Concrete implementations MAY
        raise custom exceptions on produce failure; the ABC does not constrain
        error surfaces.
        """


__all__ = [
    "SCHEMA_VERSION",
    "ModalityProducer",
]
