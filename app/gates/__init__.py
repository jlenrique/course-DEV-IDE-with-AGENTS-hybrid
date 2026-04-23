"""Gate package — HIL verdict substrate (architecture §D3).

Exports the `resume_api.resume_from_verdict` entry point. Import-linter
Contract C3 constrains this module's importers to the three authorized
verdict-bridge modules named in architecture §D3 (`app.mcp_server.tools.gate_decide`,
`app.http.gate_endpoint`, `app.marcus.cli.gate_cli`). Slab 3 creates those
bridges; Slab 1 ships the substrate.
"""

from app.gates import resume_api

__all__ = ["resume_api"]
