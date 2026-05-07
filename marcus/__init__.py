"""Reverse-shim: legacy `marcus` -> `app.marcus` (pre-Trial-3 S2 collapse 2026-05-07).

Package-level shim. Sub-modules are individually shimmed to `app.marcus.*` siblings.
"""

from app.marcus import *  # noqa: F401, F403

import app.marcus as _src  # noqa: E402
import sys as _sys  # noqa: E402

_sys.modules[__name__].__dict__.update(
    {k: v for k, v in _src.__dict__.items() if not k.startswith("__")}
)
# Mirror module docstring so docstring-discovery tests find canonical content.
__doc__ = _src.__doc__
