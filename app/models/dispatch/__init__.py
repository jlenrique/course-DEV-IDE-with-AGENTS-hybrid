"""Typed dispatch contracts for Slab 2b specialists.

14 specialists × 3 shapes (input / receipt / error) = 42 Pydantic v2 classes.
Per-specialist subdirectory layout per Story 2b.15 AC-A (one-class-per-file
convention from app/models/state/). Receipts strict-type the previously
loose-typed return-shape extensions accumulated across 2b.1-2b.14 per R4.

Roster authority: _bmad-output/planning-artifacts/slab-2-roster-reconciliation.md.
Canonical specialist→graph mapping: state/config/dispatch-registry.yaml (interim;
M5 forward-port replaces with primary's PR-R registry).
"""

from app.models.dispatch.aria.error import AriaDispatchError
from app.models.dispatch.aria.input import AriaDispatchInput
from app.models.dispatch.aria.receipt import AriaDispatchReceipt
from app.models.dispatch.cd.error import CdDispatchError
from app.models.dispatch.cd.input import CdDispatchInput
from app.models.dispatch.cd.receipt import CdDispatchReceipt
from app.models.dispatch.desmond.error import DesmondDispatchError
from app.models.dispatch.desmond.input import DesmondDispatchInput
from app.models.dispatch.desmond.receipt import DesmondDispatchReceipt
from app.models.dispatch.enrique.error import EnriqueDispatchError
from app.models.dispatch.enrique.input import EnriqueDispatchInput
from app.models.dispatch.enrique.receipt import EnriqueDispatchReceipt
from app.models.dispatch.gary.error import GaryDispatchError
from app.models.dispatch.gary.input import GaryDispatchInput
from app.models.dispatch.gary.receipt import GaryDispatchReceipt
from app.models.dispatch.irene.error import IreneDispatchError
from app.models.dispatch.irene.input import IreneDispatchInput
from app.models.dispatch.irene.receipt import IreneDispatchReceipt
from app.models.dispatch.kim.error import KimDispatchError
from app.models.dispatch.kim.input import KimDispatchInput
from app.models.dispatch.kim.receipt import KimDispatchReceipt
from app.models.dispatch.mira.error import MiraDispatchError
from app.models.dispatch.mira.input import MiraDispatchInput
from app.models.dispatch.mira.receipt import MiraDispatchReceipt
from app.models.dispatch.quinn_r.error import QuinnRDispatchError
from app.models.dispatch.quinn_r.input import QuinnRDispatchInput
from app.models.dispatch.quinn_r.receipt import QuinnRDispatchReceipt
from app.models.dispatch.tamara.error import TamaraDispatchError
from app.models.dispatch.tamara.input import TamaraDispatchInput
from app.models.dispatch.tamara.receipt import TamaraDispatchReceipt
from app.models.dispatch.tracy.error import TracyDispatchError
from app.models.dispatch.tracy.input import TracyDispatchInput
from app.models.dispatch.tracy.receipt import TracyDispatchReceipt
from app.models.dispatch.vera.error import VeraDispatchError
from app.models.dispatch.vera.input import VeraDispatchInput
from app.models.dispatch.vera.receipt import VeraDispatchReceipt
from app.models.dispatch.vyx.error import VyxDispatchError
from app.models.dispatch.vyx.input import VyxDispatchInput
from app.models.dispatch.vyx.receipt import VyxDispatchReceipt
from app.models.dispatch.wanda.error import WandaDispatchError
from app.models.dispatch.wanda.input import WandaDispatchInput
from app.models.dispatch.wanda.receipt import WandaDispatchReceipt

__all__ = [
    "AriaDispatchError",
    "AriaDispatchInput",
    "AriaDispatchReceipt",
    "CdDispatchError",
    "CdDispatchInput",
    "CdDispatchReceipt",
    "DesmondDispatchError",
    "DesmondDispatchInput",
    "DesmondDispatchReceipt",
    "EnriqueDispatchError",
    "EnriqueDispatchInput",
    "EnriqueDispatchReceipt",
    "GaryDispatchError",
    "GaryDispatchInput",
    "GaryDispatchReceipt",
    "IreneDispatchError",
    "IreneDispatchInput",
    "IreneDispatchReceipt",
    "KimDispatchError",
    "KimDispatchInput",
    "KimDispatchReceipt",
    "MiraDispatchError",
    "MiraDispatchInput",
    "MiraDispatchReceipt",
    "QuinnRDispatchError",
    "QuinnRDispatchInput",
    "QuinnRDispatchReceipt",
    "TamaraDispatchError",
    "TamaraDispatchInput",
    "TamaraDispatchReceipt",
    "TracyDispatchError",
    "TracyDispatchInput",
    "TracyDispatchReceipt",
    "VeraDispatchError",
    "VeraDispatchInput",
    "VeraDispatchReceipt",
    "VyxDispatchError",
    "VyxDispatchInput",
    "VyxDispatchReceipt",
    "WandaDispatchError",
    "WandaDispatchInput",
    "WandaDispatchReceipt",
]
