"""Reverse-shim: legacy `marcus.dispatch.contract` -> `app.marcus.dispatch.contract` (pre-Trial-3 S2 collapse 2026-05-07).

This module is a thin re-export shim. Production content lives at `app.marcus.dispatch.contract`.
Will be deleted at S2 close once all consumers migrate to `app.marcus.*` paths.
Retained as bridge during S2 to keep 108-150 test-file imports green during transition.

Mirror pattern: re-exports the full `app.marcus.dispatch.contract` namespace (public + select non-`__all__`
attributes that backward-compat callers depend on, e.g., test-only helpers).
"""

from app.marcus.dispatch.contract import *  # noqa: F401, F403

import app.marcus.dispatch.contract as _src  # noqa: E402
import sys as _sys  # noqa: E402

# Mirror everything (except dunder attrs) so `from marcus.dispatch.contract import X` works
# for both `__all__` exports AND non-public-but-test-imported names.
_sys.modules[__name__].__dict__.update(
    {k: v for k, v in _src.__dict__.items() if not k.startswith("__")}
)
# Mirror module docstring so docstring-discovery tests find canonical content.
__doc__ = _src.__doc__
